import time
import pygame as pg
import Zsettings as s
from Ztilemap import collide_hit_rect
from itertools import chain
from os import path
vec = pg.math.Vector2


def collide_with_walls(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(
            sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            for hit in hits:
                if sprite.__class__ == Player:
                    hit.push()
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(
            sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + \
                    sprite.hit_rect.height / 2
            for hit in hits:
                if sprite.__class__ == Player:
                    hit.push()
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = s.PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.facing = s.Direction.DOWN
        self.is_moving = False
        self.image = self.game.player_images[self.facing][1]
        self.rect = self.image.get_rect()
        self.pos = vec(x, y)
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
        self.health -= 1
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

    def sword(self):
        self.is_sword = True
        if self.facing == s.Direction.DOWN:
            pos = vec(self.rect.centerx, self.rect.bottom - 10)
            rot = 90
            Sword(self.game, pos, rot, (self._layer + 1))
        if self.facing == s.Direction.UP:
            pos = vec(self.rect.centerx, self.rect.top + 10)
            rot = -90
            Sword(self.game, pos, rot, (self._layer - 1))
        if self.facing == s.Direction.RIGHT:
            pos = vec(self.rect.right - 10, self.rect.centery)
            rot = 180
            Sword(self.game, pos, rot, (self._layer - 1))
        if self.facing == s.Direction.LEFT:
            pos = vec(self.rect.left + 10, self.rect.centery)
            rot = 0
            Sword(self.game, pos, rot, (self._layer - 1))

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
    def __init__(self, game, x, y, w, h, pushable, image=None):
        self.groups = game.walls
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.pushable = pushable
        if pushable:
            self.image = image
            self.rect = self.image.get_rect()
            self.groups = game.walls, game.all_sprites
            self._layer = -2
            self.pos = vec(x, y)
            self.rect.center = self.pos
            self.hit_rect = self.rect
            self.hit_rect.center = self.rect.center
        pg.sprite.Sprite.__init__(self, self.groups)

    def push(self):
        if not self.pushable:
            return
        self.vel = self.game.player.vel
        if self.rect.left < self.game.player.rect.right and self.rect.right > self.game.player.rect.right:
            self.pos.x += self.vel.x * self.game.dt
        if self.rect.right > self.game.player.rect.left and self.rect.left < self.game.player.rect.left:
            self.pos.x -= self.vel.x * self.game.dt
        if self.rect.top < self.game.player.rect.bottom and self.rect.bottom > self.game.player.rect.bottom:
            self.pos.y += self.vel.y * self.game.dt
        if self.rect.bottom > self.game.player.rect.top and self.rect.top < self.game.player.rect.top:
            self.pos.y -= self.vel.y * self.game.dt
        self.rect.center = self.pos
        self.hit_rect.centerx = self.pos.x
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
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
        self.groups = game.all_sprites, game.sword
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
    def __init__(self, game, x, y, w, h, texts):
        self.groups = game.interactables
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.texts = texts


class Enemy(pg.sprite.Sprite):
    def __init__(self, game, x, y, image, health, routes):
        self._layer = -2
        self.groups = game.all_sprites, game.enemies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.facing = s.Direction.DOWN
        self.image = self.game.cobra_images[self.facing][1]
        self.rect = self.image.get_rect()
        self.pos = vec(x, y)
        self.rect.center = self.pos
        self.next_animation_tick = 0
        self.animation_phase = 0
        self.routes = routes + [vec(x, y)]
        self.vel = 1
        self.target = 0
        self.health = health

    def animate_movement(self):
        if pg.time.get_ticks() < self.next_animation_tick:
            return
        self.image = self.game.cobra_images[self.facing][self.animation_phase]
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
            self.pos.x += s.COBRA_KNOCKBACK
        if facing == s.Direction.LEFT:
            self.pos.x -= s.COBRA_KNOCKBACK
        if facing == s.Direction.UP:
            self.pos.y -= s.COBRA_KNOCKBACK
        if facing == s.Direction.DOWN:
            self.pos.y += s.COBRA_KNOCKBACK

    def update(self):
        if self.target > len(self.routes) - 1:
            self.target = len(self.routes) - 1
        if self.pos != self.routes[self.target]:
            if self.pos.x < self.routes[self.target].x:
                self.pos.x += self.vel * self.game.dt
                self.facing = s.Direction.RIGHT
            elif self.pos.x > self.routes[self.target].x:
                self.pos.x -= self.vel * self.game.dt
                self.facing = s.Direction.LEFT
            if self.pos.y < self.routes[self.target].y:
                self.pos.y += self.vel * self.game.dt
                self.facing = s.Direction.DOWN
            elif self.pos.y > self.routes[self.target].y:
                self.pos.y -= self.vel * self.game.dt
                self.facing = s.Direction.UP
        else:
            self.target += 1
            if self.target == len(self.routes):
                self.target = 0
        self.rect.center = self.pos
        self.animate_movement()
