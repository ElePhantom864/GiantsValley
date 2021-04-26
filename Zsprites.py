import time
import pygame as pg
import Zsettings as s
from Ztilemap import collide_hit_rect
from itertools import chain
import pytweening as tween
from os import path
from collections import defaultdict
import math
import random
vec = pg.math.Vector2


def collide_with_walls(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(
            sprite, group, False, collide_hit_rect)
        if hits:
            for hit in hits:
                if hit != sprite:
                    if hit.rect.centerx > sprite.hit_rect.centerx:
                        sprite.pos.x = hit.rect.left - sprite.hit_rect.width / 2
                    if hit.rect.centerx < sprite.hit_rect.centerx:
                        sprite.pos.x = hit.rect.right + sprite.hit_rect.width / 2

                if sprite.__class__ == Player:
                    hit.push()
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(
            sprite, group, False, collide_hit_rect)
        if hits:
            for hit in hits:
                if hit != sprite:
                    if hit.rect.centery > sprite.hit_rect.centery:
                        sprite.pos.y = hit.rect.top - sprite.hit_rect.height / 2
                    if hit.rect.centery < sprite.hit_rect.centery:
                        sprite.pos.y = hit.rect.bottom + \
                            sprite.hit_rect.height / 2

                if sprite.__class__ == Player:
                    hit.push()
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = s.PLAYER_LAYER
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.facing = s.Direction.DOWN
        self.is_moving = False
        self.image = self.game.player_images[self.facing][1]
        self.rect = self.image.get_rect()
        self.set_pos(x, y)
        self.animation = True
        self.vel = vec(0, 0)
        self.next_animation_tick = 0
        self.animation_phase = 0
        self.is_sword = False
        self.max_health = s.PLAYER_HEALTH
        self.health = s.PLAYER_HEALTH
        self.max_lives = 3
        self.damaged = False
        self.items = defaultdict(int)
        self.add_item(s.Items.RESPAWN_ORB)

    def set_pos(self, x, y):
        self.pos = vec(x, y)
        self.rect.center = self.pos
        self.hit_rect = s.PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center

    def hit(self, enemy):
        if self.damaged:
            return
        if self.rect.left < enemy.rect.right and self.rect.right > enemy.rect.right:
            self.pos.x += s.PLAYER_KNOCKBACK // 2
            self.rect.center = self.pos
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
        elif self.rect.right > enemy.rect.left and self.rect.left < enemy.rect.left:
            self.pos.x -= s.PLAYER_KNOCKBACK // 2
            self.rect.center = self.pos
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
        elif self.rect.top < enemy.rect.bottom and self.rect.bottom > enemy.rect.bottom:
            self.pos.y += s.PLAYER_KNOCKBACK // 2
            self.rect.center = self.pos
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
        elif self.rect.bottom > enemy.rect.top and self.rect.top < enemy.rect.top:
            self.pos.y -= s.PLAYER_KNOCKBACK // 2
            self.rect.center = self.pos
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')

        self.rect.center = self.pos
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

        self.damaged = True
        self.damage_alpha = chain(s.DAMAGE_ALPHA * 2)
        self.health -= enemy.damage
        if self.health <= 0:
            self.kill()
            new_state = self.game.ui.run(self.game.ui.game_over)

    def draw_health(self, surface):
        if self.items[s.Items.PHOENIX_GEM] >= 4:
            self.max_lives += 1
            self.items[s.Items.PHOENIX_GEM] -= 4
        if self.items[s.Items.DRAGON_SCALE] >= 4:
            self.items[s.Items.DRAGON_SCALE] -= 4
            self.max_health += 2
            self.health += 2
        if (self.health % 2) == 0:
            x = 2
            ran = self.health // 2
            for i in range(ran):
                surface.blit(self.game.heart_img, (x, 2))
                x += 37
            ran1 = (self.max_health - self.health) // 2
            for i in range(ran1):
                surface.blit(self.game.empty_heart_img, (x, 2))
                x += 37
        else:
            x = 2
            ran = self.health // 2
            for i in range(ran):
                surface.blit(self.game.heart_img, (x, 2))
                x += 37
            surface.blit(self.game.half_heart_img, (x, 2))
            x += 37
            ran1 = (self.max_health - self.health) // 2
            for i in range(ran1):
                surface.blit(self.game.empty_heart_img, (x, 2))
                x += 37
        if self.items[s.Items.RESPAWN_ORB] > self.max_lives:
            self.items[s.Items.RESPAWN_ORB] -= 1
        x = 2
        ran = self.items[s.Items.RESPAWN_ORB]
        for i in range(ran):
            surface.blit(self.game.UI_orb_img, (x, 37))
            x += 12
        ran1 = self.max_lives - self.items[s.Items.RESPAWN_ORB]
        for i in range(ran1):
            surface.blit(self.game.empty_orb_img, (x, 37))
            x += 12

    def add_item(self, item, qty=1):
        self.items[item] += qty

    def add_item_by_name(self, item_name, qty=1):
        self.add_item(s.Items.item_by_name(item_name))

    def remove_item(self, item, qty=1):
        self.items[item] -= qty

    def has_item(self, item):
        return self.items[item] > 0

    def sword(self):
        if self.has_item(s.Items.SWORD):
            self.is_sword = True
            snd = self.game.get_sound(random.choice(s.PLAYER_SOUNDS['SWORD']))
            snd.play()
            if self.facing == s.Direction.DOWN:
                pos = vec(self.rect.centerx, self.rect.bottom - 10)
                rot = 45
                Sword(self.game, pos, rot, (self._layer + 2))
            if self.facing == s.Direction.UP:
                pos = vec(self.rect.centerx, self.rect.top + 10)
                rot = -135
                Sword(self.game, pos, rot, (self._layer - 2))
            if self.facing == s.Direction.RIGHT:
                pos = vec(self.rect.right - 10, self.rect.centery)
                rot = 135
                Sword(self.game, pos, rot, (self._layer - 2))
            if self.facing == s.Direction.LEFT:
                pos = vec(self.rect.left + 10, self.rect.centery)
                rot = -45
                Sword(self.game, pos, rot, (self._layer - 2))

    def animate_movement(self):
        if pg.time.get_ticks() < self.next_animation_tick:
            return
        snd = self.game.get_sound(s.PLAYER_SOUNDS['WALK'][0])
        if self.is_moving:
            if snd.get_num_channels() == 0:
                snd.play()
            self.image = self.game.player_images[self.facing][self.animation_phase]
            self.animation_phase += 1
            if self.animation_phase == 1:
                self.animation_phase = 2
            if self.animation_phase > 2:
                self.animation_phase = 0
            self.next_animation_tick = pg.time.get_ticks() + 150
        else:
            self.image = self.game.player_images[self.facing][1]
            snd.stop()

    def handle_event(self, event: pg.event.Event):
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.vel.x = -s.PLAYER_SPEED
            self.facing = s.Direction.LEFT
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vel.x = s.PLAYER_SPEED
            self.facing = s.Direction.RIGHT
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel.y = -s.PLAYER_SPEED
            self.facing = s.Direction.UP
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel.y = s.PLAYER_SPEED
            self.facing = s.Direction.DOWN

        if event.type in [pg.KEYDOWN, pg.KEYUP]:
            if event.type in [pg.K_w, pg.K_a, pg.K_s, pg.K_d, pg.K_UP, pg.K_LEFT, pg.K_DOWN, pg.K_RIGHT]:
                self.is_moving = True
            else:
                self.is_moving = False
            if event.key == pg.K_LEFT or event.key == pg.K_a:
                self.facing = s.Direction.LEFT
                if event.type == pg.KEYDOWN:
                    self.vel.x = -s.PLAYER_SPEED

            if event.key == pg.K_RIGHT or event.key == pg.K_d:
                self.facing = s.Direction.RIGHT
                if event.type == pg.KEYDOWN:
                    self.vel.x = s.PLAYER_SPEED

            if event.key == pg.K_UP or event.key == pg.K_w:
                self.facing = s.Direction.UP
                if event.type == pg.KEYDOWN:
                    self.vel.y = -s.PLAYER_SPEED

            if event.key == pg.K_DOWN or event.key == pg.K_s:
                self.facing = s.Direction.DOWN
                if event.type == pg.KEYDOWN:
                    self.vel.y = s.PLAYER_SPEED

            if event.key == pg.K_SPACE and not self.is_sword:
                self.sword()

        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.facing = s.Direction.LEFT
            self.is_moving = True
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.is_moving = True
            self.facing = s.Direction.RIGHT
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.is_moving = True
            self.facing = s.Direction.UP
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.is_moving = True
            self.facing = s.Direction.DOWN

        if self.damaged:
            try:
                opacity = next(self.damage_alpha)
                new_image = self.game.player_images[self.facing][self.animation_phase].copy()
                new_image.fill((255, 0, 0, opacity),
                               special_flags=pg.BLEND_RGBA_MULT)
                self.image = new_image
            except StopIteration:
                self.damaged = False
                self.image = self.game.player_images[self.facing][self.animation_phase]
        if not self.is_sword and not self.damaged:
            self.animate_movement()
            self.pos += self.vel * self.game.dt

        self.rect.center = self.pos
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, pushable, image=None, typ=None):
        self.groups = game.walls
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.pushable = pushable
        self.type = typ
        if pushable:
            self.image = image
            self.rect = self.image.get_rect()
            self.groups = game.walls, game.pushers, game.all_sprites
            self._layer = s.PUSH_LAYER
            self.pos = vec(x, y)
            self.rect.center = self.pos
            self.hit_rect = self.rect
            self.hit_rect.center = self.rect.center
        pg.sprite.Sprite.__init__(self, self.groups)

    def push(self):
        if not self.pushable:
            return
        self.vel = self.game.player.vel
        direction = None
        angle = math.degrees(math.atan2(self.game.player.pos.y - self.pos.y, self.game.player.pos.x - self.pos.x))
        if angle < 0:
            angle = angle + 360
        if 150 < angle < 210:
            # detect if player collides from left
            direction = "x"
        elif 270 < angle < 300:
            # detect if player collides from top
            direction = "y"
        elif 60 < angle < 120:
            # detect if player collides from bottom
            direction = "y"
        elif angle > 330 or angle < 30:
            direction = "x"

        if direction == "x":
            self.pos.x += self.vel.x * self.game.dt
            self.rect.center = self.pos
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
        if direction == "y":
            self.pos.y += self.vel.y * self.game.dt
            self.rect.center = self.pos
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')

        self.rect.center = self.hit_rect.center


class Teleport(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, playerDestination, playerLocation):
        self.groups = game.teleports
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.rect.x = x
        self.rect.y = y
        self.destination = playerDestination
        self.location = playerLocation


class Sword(pg.sprite.Sprite):
    def __init__(self, game, pos, rot, layer):
        self._layer = layer
        self.groups = game.sword, game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.sword_img
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.rot = rot
        self.angle = -5
        self.enemies_hit = set()

    def update(self):
        self.angle += 10
        self.image = pg.transform.rotate(self.game.sword_img, self.rot - self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        if self.angle >= 90:
            self.kill()
            self.game.player.is_sword = False
        hits = pg.sprite.spritecollide(self, self.game.enemies, False)
        for hit in hits:
            if hit not in self.enemies_hit:
                self.enemies_hit.add(hit)
                hit.hit(self.game.player.facing)


class TextBox(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, texts, sound, typ=None, activator_id=None, item=None, used=False,
                 activated=False):
        self.groups = game.interactables
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.texts = texts
        self.type = typ
        self.activator_id = activator_id
        self.activated = activated
        self.used = False
        self.item = item
        self.sound = sound
        self.used = used


class Enemy(pg.sprite.Sprite):
    def __init__(self, game, x, y, images, health, speed, damage, knockback, routes, name, passive):
        self._layer = s.ENEMY_LAYER
        self.groups = game.enemies, game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.facing = s.Direction.DOWN
        self.images = images
        self.image = self.images[self.facing][0]
        self.rect = self.image.get_rect()
        self.pos = vec(x, y)
        self.rect.center = self.pos
        self.next_animation_tick = 0
        self.animation_phase = 0
        self.routes = routes + [vec(x, y)]
        self.vel = min(1, speed)
        self.delay = 60 // max(speed, 1)
        if speed > 60:
            self.vel = speed // 60
            self.delay = 0
        self.target = 0
        self.health = health
        self.timeLoop = 0
        self.damage = damage
        self.knockback = knockback
        self.name = name
        self.passive = passive

    def animate_movement(self):
        if pg.time.get_ticks() < self.next_animation_tick:
            return
        self.image = self.images[self.facing][self.animation_phase]
        self.animation_phase += 1
        if self.animation_phase >= len(self.images[self.facing]):
            self.animation_phase = 0
        self.next_animation_tick = pg.time.get_ticks() + 150

    def hit(self, facing):
        if not self.passive:
            self.routes = [self.game.player.pos]
        self.health -= 1
        if self.health <= 0:
            self.play_sound('Death')
            if random.randrange(0, 10) == 0:
                Item(self.game, self.pos, self.game.heart_img, 'Health')
            elif random.randrange(0, 10) == 0:
                Item(self.game, self.pos, self.game.orb_img, 'Item', s.Items.RESPAWN_ORB)
            self.kill()
        self.play_sound('Hit')
        if facing == s.Direction.RIGHT:
            self.pos.x += self.knockback
        if facing == s.Direction.LEFT:
            self.pos.x -= self.knockback
        if facing == s.Direction.UP:
            self.pos.y -= self.knockback
        if facing == s.Direction.DOWN:
            self.pos.y += self.knockback

    def play_sound(self, sound):
        snd = self.game.get_sound(str(self.name) + sound + '.mp3')
        snd.play()

    def update(self):
        self.timeLoop += 1
        if self.timeLoop >= self.delay:
            self.timeLoop = 0
        else:
            return
        if self.target > len(self.routes) - 1:
            self.target = len(self.routes) - 1
        if self.pos.distance_squared_to(self.routes[self.target]) > 5**2:
            if self.pos.x < self.routes[self.target].x:
                self.pos.x += self.vel
                self.facing = s.Direction.RIGHT
            elif self.pos.x > self.routes[self.target].x:
                self.pos.x -= self.vel
                self.facing = s.Direction.LEFT
            if self.pos.y < self.routes[self.target].y:
                self.pos.y += self.vel
                self.facing = s.Direction.DOWN
            elif self.pos.y > self.routes[self.target].y:
                self.pos.y -= self.vel
                self.facing = s.Direction.UP
        else:
            self.target += 1
            if self.target == len(self.routes):
                self.target = 0
        self.rect.center = self.pos
        self.animate_movement()
        player_dist = self.game.player.pos - self.pos
        if player_dist.length_squared() < s.SOUND_RADIUS**2 and random.randrange(0, 100) == 0:
            self.play_sound('')

    def push(self):
        pass


class Activator(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, image=None, typ=None, sounds=None):
        self.image = image
        self.og_image = image
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.groups = game.activators, game.all_sprites
        self._layer = s.ACTIVATOR_LAYER
        self.pos = vec(x, y)
        self.rect.center = self.pos
        self.activated = False
        self.type = typ
        self.sounds = sounds
        pg.sprite.Sprite.__init__(self, self.groups)

    def activate(self):
        Blank = pg.Surface((0, 0))
        self.image = Blank
        sound = self.game.get_sound(self.sounds)
        sound.play()

    def deactivate(self):
        self.image = self.og_image
        # sound = self.game.get_sound(self.sounds[1])
        # sound.play()

    def update(self):
        self.activated = False
        hits = pg.sprite.spritecollide(self, self.game.pushers, dokill=False)
        if hits:
            if self.type is None:
                self.activated = True
                self.activate()
            else:
                for hit in hits:
                    if hasattr(hit, "type") and hit.type == self.type:
                        self.activated = True
                        self.activate()
        else:
            self.deactivate()


class Door(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, activator_id, typ, image):
        w = int(w)
        h = int(h)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.image = pg.transform.scale(image, (w, h))
        self.og_image = pg.transform.scale(image, (w, h))
        self.groups = game.walls, game.all_sprites
        self._layer = s.DOOR_LAYER
        self.activator_id = activator_id
        self.type = typ
        pg.sprite.Sprite.__init__(self, self.groups)

    def activate(self):
        Blank = pg.Surface((0, 0))
        self.image = Blank
        self.game.walls.remove(self)

    def deactivate(self):
        self.image = self.og_image
        self.game.walls.add(self)

    def update(self):
        activator = self.game.objects_by_id[self.activator_id]
        if self.type == 'Opposite':
            if not activator.activated:
                self.activate()
            else:
                self.deactivate()
        else:
            if activator.activated:
                self.activate()
            else:
                self.deactivate()

    def push(self):
        pass


class Spawner(pg.sprite.Sprite):
    def __init__(self, game, x, y, images, health, speed, damage, knockback, routes, activator_id, name, passive):
        self.groups = game.all_sprites
        self._layer = s.SPAWNER_LAYER
        self.x = x
        self.y = y
        self.game = game
        self.images = images
        self.image = pg.Surface((0, 0))
        self.rect = self.image.get_rect()
        self.health = health
        self.speed = speed
        self.damage = damage
        self.knockback = knockback
        self.routes = routes
        self.activator_id = activator_id
        self.name = name
        self.passive = passive
        pg.sprite.Sprite.__init__(self, self.groups)

    def update(self):
        activator = self.game.objects_by_id[self.activator_id]
        if activator.activated:
            self.activate()

    def activate(self):
        activator = self.game.objects_by_id[self.activator_id]
        Enemy(
            self.game, self.x, self.y, self.images, self.health, self.speed, self.damage,
            self.knockback, self.routes, self.name, self.passive)
        activator.kill()
        self.kill()


class SoundBox(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, sound, chance, identity):
        self.groups = game.sounds
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.rect.x = x
        self.rect.y = y
        self.sound = game.get_sound(sound)
        self.chance = chance
        self.id = identity

    def play(self):
        self.sound.play(loops=-1, fade_ms=500)

    def stop(self):
        self.sound.fadeout(500)


class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, image, Type, item=None):
        self._layer = s.ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = image
        self.rect = self.image.get_rect()
        self.type = Type
        self.pos = pos
        self.rect.center = pos
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1
        self.item = item

    def update(self):
        # bobbing motion
        offset = s.BOB_RANGE * (self.tween(self.step / s.BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += s.BOB_SPEED
        if self.step > s.BOB_RANGE:
            self.step = 0
            self.dir *= -1

    def activate(self):
        if self.type == 'Item':
            self.game.player.add_item(self.item)
        else:
            self.game.player.health += 2
            if self.game.player.health - self.game.player.max_health > 0:
                self.game.player.health -= self.game.player.health - self.game.player.max_health
        self.kill()


class LavaBoss(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = -10
        self.image = pg.Surface((0, 0))
        self.rect = self.image.get_rect()
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.cooldown = 5
        self.counter = 0
        self.active_attack = []
        self.health = 3
        self.phase = 0
        self.game.load_mob_images('Cobra')
        routes = [vec(240, 240), vec(688, 240), vec(240, 688), vec(688, 688)]
        random.shuffle(routes)
        self.vulnerable = Enemy(
            self.game, 464, 464, self.game.mob_images['Cobra'], 10, 50, 1,
            50, routes, 'Cobra', True)

    def update(self):
        self.counter += 1
        if self.vulnerable.health == 0:
            self.health -= 1
            if self.health <= 0:
                print('win')
                self.kill()
            self.phase += 1
            routes = [vec(240, 240), vec(688, 240), vec(240, 688), vec(688, 688)]
            random.shuffle(routes)
            self.vulnerable = Enemy(
                self.game, 464, 464, self.game.mob_images['Cobra'], 10, 50, 1,
                50, routes, 'Cobra', True)
        if self.counter >= self.cooldown * 60:
            self.counter = 0
            attack = random.randrange(0, 7)
            if attack < 2:
                self.attack1()
            elif attack < 4:
                self.attack2()
            elif attack == 5:
                self.attack3()
            elif attack == 6:
                self.attack4()

    def attack1(self):
        for mob in self.active_attack:
            mob.kill()
        self.cooldown = 2
        bubble = [816, 584]
        arm = [1688, 584, vec(0, 584)]
        if random.randrange(0, 2) == 0:
            bubble = [112, 344]
            arm = [-760, 344, vec(928, 344)]
        self.game.load_mob_images('Fire')
        bubble = Enemy(
            self.game, bubble[0], bubble[1], self.game.mob_images['Fire'], 0, 0, 0,
            0, [], 'Fire', True)
        arm = Enemy(
            self.game, arm[0], arm[1], self.game.mob_images['Fire'], 1000, 1000, 1,
            0, [arm[2]], 'Fire', True)
        self.active_attack.append(bubble)
        self.active_attack.append(arm)

    def attack2(self):
        for mob in self.active_attack:
            mob.kill()
        self.cooldown = 2
        bubble = [344, 112]
        leg = [344, -856, vec(344, 928)]
        if random.randrange(0, 2) == 0:
            bubble = [584, 112]
            leg = [584, -856, vec(584, 928)]
        self.game.load_mob_images('Fire')
        bubble = Enemy(
            self.game, bubble[0], bubble[1], self.game.mob_images['Fire'], 0, 0, 0,
            0, [], 'Fire', True)
        leg = Enemy(
            self.game, leg[0], leg[1], self.game.mob_images['Fire'], 1000, 1000, 1,
            0, [leg[2]], 'Fire', True)
        self.active_attack.append(bubble)
        self.active_attack.append(leg)

    def attack3(self):
        for mob in self.active_attack:
            mob.kill()
        self.cooldown = 10 - self.phase * 2
        self.game.load_mob_images('Fire')
        enemy1 = Enemy(
            self.game, 464, 368, self.game.mob_images['Fire'], 9, 40, 1,
            10, [], 'Fire', False)
        enemy1.hit(s.Direction.DOWN)
        self.active_attack.append(enemy1)
        enemy2 = Enemy(
            self.game, 384, 400, self.game.mob_images['Fire'], 5, 50, 1,
            30, [vec(464, 368)], 'Fire', False)
        self.active_attack.append(enemy2)
        enemy3 = Enemy(
            self.game, 352, 464, self.game.mob_images['Fire'], 5, 50, 1,
            30, [vec(384, 400)], 'Fire', False)
        self.active_attack.append(enemy3)
        enemy4 = Enemy(
            self.game, 384, 528, self.game.mob_images['Fire'], 5, 50, 1,
            30, [vec(352, 464)], 'Fire', False)
        self.active_attack.append(enemy4)
        enemy5 = Enemy(
            self.game, 464, 560, self.game.mob_images['Fire'], 5, 50, 1,
            30, [vec(384, 528)], 'Fire', False)
        self.active_attack.append(enemy5)
        enemy6 = Enemy(
            self.game, 544, 528, self.game.mob_images['Fire'], 5, 50, 1,
            30, [vec(464, 560)], 'Fire', False)
        self.active_attack.append(enemy6)
        enemy7 = Enemy(
            self.game, 576, 464, self.game.mob_images['Fire'], 5, 50, 1,
            30, [vec(544, 528)], 'Fire', False)
        self.active_attack.append(enemy7)
        enemy8 = Enemy(
            self.game, 544, 400, self.game.mob_images['Fire'], 5, 50, 1,
            30, [vec(576, 464)], 'Fire', False)
        self.active_attack.append(enemy8)

    def attack4(self):
        for mob in self.active_attack:
            mob.kill()
        self.cooldown = 5 - self.phase
        self.game.load_mob_images('Fire')
        enemy1 = Enemy(
            self.game, 240, 240, self.game.mob_images['Fire'], 9, 70, 1,
            10, [], 'Fire', False)
        enemy1.hit(s.Direction.DOWN)
        enemy2 = Enemy(
            self.game, 688, 240, self.game.mob_images['Fire'], 9, 70, 1,
            10, [], 'Fire', False)
        enemy2.hit(s.Direction.DOWN)
        enemy3 = Enemy(
            self.game, 240, 688, self.game.mob_images['Fire'], 9, 70, 1,
            10, [], 'Fire', False)
        enemy3.hit(s.Direction.DOWN)
        enemy4 = Enemy(
            self.game, 688, 688, self.game.mob_images['Fire'], 9, 70, 1,
            10, [], 'Fire', False)
        enemy4.hit(s.Direction.DOWN)
