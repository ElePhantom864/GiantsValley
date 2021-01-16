import time
import pygame as pg
import Zsettings as s
from Ztilemap import collide_hit_rect
from itertools import chain
from os import path
from collections import defaultdict
import math
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
        self.rect.center = self.pos
        self.hit_rect = s.PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.animation = True
        self.vel = vec(0, 0)
        self.next_animation_tick = 0
        self.animation_phase = 0
        self.is_sword = False
        self.max_health = s.PLAYER_HEALTH
        self.health = s.PLAYER_HEALTH
        self.damaged = False
        self.items = defaultdict(int, {s.Items.HEALTH_POTION: 1})

    def set_pos(self, x, y):
        self.pos = vec(x, y)

    def hit(self, enemy):
        if self.damaged:
            return
        if self.rect.left < enemy.rect.right and self.rect.right > enemy.rect.right:
            self.pos.x += s.PLAYER_KNOCKBACK
        if self.rect.right > enemy.rect.left and self.rect.left < enemy.rect.left:
            self.pos.x -= s.PLAYER_KNOCKBACK
        if self.rect.top < enemy.rect.bottom and self.rect.bottom > enemy.rect.bottom:
            self.pos.y += s.PLAYER_KNOCKBACK
        if self.rect.bottom > enemy.rect.top and self.rect.top < enemy.rect.top:
            self.pos.y -= s.PLAYER_KNOCKBACK

        self.damaged = True
        self.damage_alpha = chain(s.DAMAGE_ALPHA * 2)
        self.health -= enemy.damage
        if self.health <= 0:
            self.kill()

    def draw_health(self, surface):
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

    def add_item(self, item, qty=1):
        self.items[item] += qty

    def remove_item(self, item, qty=1):
        self.items[item] -= qty

    def has_item(self, item):
        return self.items[item] > 0

    def sword(self):
        if self.has_item(s.Items.SWORD):
            self.is_sword = True
            if self.facing == s.Direction.DOWN:
                pos = vec(self.rect.centerx, self.rect.bottom - 10)
                rot = 90
                Sword(self.game, pos, rot, (self._layer + 2))
            if self.facing == s.Direction.UP:
                pos = vec(self.rect.centerx, self.rect.top + 10)
                rot = -90
                Sword(self.game, pos, rot, (self._layer - 2))
            if self.facing == s.Direction.RIGHT:
                pos = vec(self.rect.right - 10, self.rect.centery)
                rot = 180
                Sword(self.game, pos, rot, (self._layer - 2))
            if self.facing == s.Direction.LEFT:
                pos = vec(self.rect.left + 10, self.rect.centery)
                rot = 0
                Sword(self.game, pos, rot, (self._layer - 2))

    def animate_movement(self):
        if pg.time.get_ticks() < self.next_animation_tick:
            return
        if self.is_moving:
            self.image = self.game.player_images[self.facing][self.animation_phase]
            self.animation_phase += 1
            if self.animation_phase == 1:
                self.animation_phase = 2
            if self.animation_phase > 2:
                self.animation_phase = 0
            self.next_animation_tick = pg.time.get_ticks() + 150
        else:
            self.image = self.game.player_images[self.facing][1]

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
        elif 240 < angle < 300:
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
        self.x = x
        self.y = y
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
        self.angle += 15
        self.image = pg.transform.rotate(self.game.sword_img, self.rot - self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        if self.angle >= 180:
            self.kill()
            self.game.player.is_sword = False
        hits = pg.sprite.spritecollide(self, self.game.enemies, False)
        for hit in hits:
            if hit not in self.enemies_hit:
                self.enemies_hit.add(hit)
                hit.hit(self.game.player.facing)


class TextBox(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, texts, typ=None):
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
        self.activated = False


class Enemy(pg.sprite.Sprite):
    def __init__(self, game, x, y, images, health, speed, damage, knockback, routes):
        self._layer = s.ENEMY_LAYER
        self.groups = game.enemies, game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.facing = s.Direction.DOWN
        self.images = images
        self.image = self.images[self.facing][1]
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
            self.delay = 1
        self.target = 0
        self.health = health
        self.timeLoop = 0
        self.damage = damage
        self.knockback = knockback

    def animate_movement(self):
        if pg.time.get_ticks() < self.next_animation_tick:
            return
        self.image = self.images[self.facing][self.animation_phase]
        self.animation_phase += 1
        if self.animation_phase > 1:
            self.animation_phase = 0
        self.next_animation_tick = pg.time.get_ticks() + 150

    def hit(self, facing):
        self.routes = [self.game.player.pos]
        self.health -= 1
        if self.health <= 0:
            self.kill()
        if facing == s.Direction.RIGHT:
            self.pos.x += self.knockback
        if facing == s.Direction.LEFT:
            self.pos.x -= self.knockback
        if facing == s.Direction.UP:
            self.pos.y -= self.knockback
        if facing == s.Direction.DOWN:
            self.pos.y += self.knockback

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


class Activator(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, image=None, typ=None):
        self.image = image
        self.game = game
        self.rect = self.image.get_rect()
        self.groups = game.activators, game.all_sprites
        self._layer = s.ACTIVATOR_LAYER
        self.pos = vec(x, y)
        self.rect.center = self.pos
        self.activated = False
        self.type = typ
        pg.sprite.Sprite.__init__(self, self.groups)

    def update(self):
        self.activated = False
        hits = pg.sprite.spritecollide(self, self.game.pushers, dokill=False)
        if hits:
            if self.type is None:
                self.activated = True
            else:
                for hit in hits:
                    if hasattr(hit, "type") and hit.type == self.type:
                        self.activated = True


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
        self.groups = game.walls, game.all_sprites
        self._layer = s.DOOR_LAYER
        self.activator_id = activator_id
        self.type = typ
        pg.sprite.Sprite.__init__(self, self.groups)

    def activate(self):
        self.image.fill(s.RED)
        self.game.walls.remove(self)

    def deactivate(self):
        self.image.fill(s.GREEN)
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
    def __init__(self, game, x, y, images, health, speed, damage, knockback, routes, activator_id):
        self.groups = game.all_sprites
        self._layer = 0
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
        pg.sprite.Sprite.__init__(self, self.groups)

    def update(self):
        activator = self.game.objects_by_id[self.activator_id]
        print(activator.activated)
        if activator.activated:
            self.activate()

    def activate(self):
        Enemy(
            self.game, self.x, self.y, self.images, self.health, self.speed, self.damage,
            self.knockback, self.routes)
        self.kill()
