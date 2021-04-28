# KidsCanCode - Game Development with Pygame video series

# Tile-based game - Part 1
# Project setup
# Video link: https://youtu.be/3UxnelT9aCo
import pygame as pg
import sys
import json
import Zsettings as s
import Zsprites as spr
from Ztilemap import TiledMap, Camera
from os import path
import pygame_gui
from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.core import ObjectID
from pygame_gui.core import IncrementalThreadedResourceLoader
from pygame_gui import UI_TEXT_BOX_LINK_CLICKED
from itertools import chain
import random
import time

vec = pg.math.Vector2


class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode(
            (s.WIDTH, s.HEIGHT), flags=pg.RESIZABLE | pg.SCALED | pg.SRCALPHA | pg.HWACCEL)
        pg.display.set_caption(s.TITLE)
        self.clock = pg.time.Clock()
        self.pause_game = False
        self.dialog_text_chunks = None
        pg.key.set_repeat(100, 100)
        self.load_data()

    def load_data(self):
        self.game_folder = path.dirname(__file__)
        snd_folder = path.join(self.game_folder, 'snd')
        self.music_folder = path.join(self.game_folder, 'music')
        self.img_folder = path.join(self.game_folder, 'img')
        self.map_folder = path.join(self.game_folder, 'maps')

        # Image Loading
        self.sword_img = pg.image.load(path.join(self.img_folder, 'TempSword.png')).convert_alpha()
        self.heart_img = pg.image.load(path.join(self.img_folder, 'Heart.png')).convert_alpha()
        self.half_heart_img = pg.image.load(path.join(self.img_folder, 'Half_Heart.png')).convert_alpha()
        self.empty_heart_img = pg.image.load(path.join(self.img_folder, 'Empty_Heart.png')).convert_alpha()
        self.orb_img = pg.image.load(path.join(self.img_folder, 'Orb.png')).convert_alpha()
        self.UI_orb_img = pg.image.load(path.join(self.img_folder, 'Full_Orb.png')).convert_alpha()
        self.empty_orb_img = pg.image.load(path.join(self.img_folder, 'Empty_Orb.png')).convert_alpha()
        self.boot_img = pg.image.load(path.join(self.img_folder, 'Boot.png')).convert_alpha()
        self.stomp_img = pg.image.load(path.join(self.img_folder, 'Stomp.png')).convert_alpha()
        self.explosions = []
        for i in range(1, 7):
            self.explosions.append(
                pg.image.load(path.join(self.img_folder, 'Explosion' + str(i) + ".png")).convert_alpha())
        self.player_images = {}
        for direction, images in s.PLAYER_IMAGES.items():
            self.player_images[direction] = list(map(lambda img: pg.image.load(
                path.join(self.img_folder, img)).convert_alpha(), images))
        self.mob_images = {}

        loader = IncrementalThreadedResourceLoader()
        self.ui_manager = UIManager((s.WIDTH, s.HEIGHT), path.join(self.game_folder, 'data/themes/theme_1.json'),
                                    resource_loader=loader)
        self.ui_manager.add_font_paths("Montserrat",
                                       path.join(self.game_folder, "data/fonts/Montserrat-Regular.ttf"),
                                       path.join(self.game_folder, "data/fonts/Montserrat-Bold.ttf"),
                                       path.join(self.game_folder, "data/fonts/Montserrat-Italic.ttf"),
                                       path.join(self.game_folder, "data/fonts/Montserrat-BoldItalic.ttf"))

        self.ui_manager.preload_fonts([{'name': 'Montserrat', 'html_size': 4.5, 'style': 'bold'},
                                       {'name': 'Montserrat', 'html_size': 4.5, 'style': 'regular'},
                                       {'name': 'Montserrat', 'html_size': 2, 'style': 'regular'},
                                       {'name': 'Montserrat', 'html_size': 2, 'style': 'italic'},
                                       {'name': 'Montserrat', 'html_size': 6, 'style': 'bold'},
                                       {'name': 'Montserrat', 'html_size': 6, 'style': 'regular'},
                                       {'name': 'Montserrat', 'html_size': 6, 'style': 'bold_italic'},
                                       {'name': 'Montserrat', 'html_size': 36, 'style': 'bold'},
                                       {'name': 'Montserrat', 'html_size': 36, 'style': 'regular'},
                                       {'name': 'Montserrat', 'html_size': 36, 'style': 'bold_italic'},
                                       {'name': 'Montserrat', 'html_size': 4, 'style': 'bold'},
                                       {'name': 'Montserrat', 'html_size': 4, 'style': 'regular'},
                                       {'name': 'Montserrat', 'html_size': 4, 'style': 'italic'},
                                       {'name': 'fira_code', 'html_size': 2, 'style': 'regular'},
                                       {'name': 'fira_code', 'html_size': 2, 'style': 'bold'},
                                       {'name': 'fira_code', 'html_size': 2, 'style': 'bold_italic'}
                                       ])
        loader.start()
        finished_loading = False
        while not finished_loading:
            finished_loading, progress = loader.update()
        self.ui = UI(self)

    def new(self, load=False):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.teleports = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.sword = pg.sprite.Group()
        self.interactables = pg.sprite.Group()
        self.activators = pg.sprite.Group()
        self.pushers = pg.sprite.Group()
        self.sounds = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.player = spr.Player(
            self, 0, 0)
        self.current_music = None
        self.open_chests = []
        self.sound_cache = {}
        self.current_sounds = pg.sprite.Group()
        if not load:
            self.load_map('Zelda.tmx', 'playerCenter')

    def load_map(self, map_name, playerLocation):
        self.all_sprites.empty()
        self.walls.empty()
        self.teleports.empty()
        self.enemies.empty()
        self.sword.empty()
        self.interactables.empty()
        self.activators.empty()
        self.pushers.empty()
        self.sounds.empty()
        self.items.empty()
        self.player.add([self.pushers, self.all_sprites])

        self.current_map = [map_name, playerLocation]

        self.current_interactable = None
        self.map = TiledMap(path.join(self.map_folder, map_name))
        if 'music' in self.map.tmxdata.properties and self.current_music != self.map.tmxdata.properties['music']:
            # Music Loading
            pg.mixer.music.fadeout(1000)
            self.current_music = self.map.tmxdata.properties['music']
            pg.mixer.music.load(path.join(self.music_folder, self.map.tmxdata.properties['music']))
            pg.mixer.music.play(-1)

        self.camera = Camera(self.map.width, self.map.height)
        self.map_top_img, self.map_bottom_img = self.map.make_map()
        self.map_rect = self.map_bottom_img.get_rect()
        self.objects_by_id = {}
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2,
                             tile_object.y + tile_object.height / 2)
            if tile_object.name == playerLocation:
                self.player.set_pos(obj_center.x, obj_center.y)
            if tile_object.name == 'wall':
                obstacle = spr.Obstacle(
                    self, tile_object.x, tile_object.y, tile_object.width,
                    tile_object.height, False)
                self.objects_by_id[tile_object.id] = obstacle
            if tile_object.name == 'activator':
                sounds = tile_object.properties['sound']
                activator = spr.Activator(
                    self, obj_center.x, obj_center.y, tile_object.width,
                    tile_object.height, tile_object.image, tile_object.type, sounds)
                self.objects_by_id[tile_object.id] = activator
            if tile_object.name == 'pushable':
                spr.Obstacle(
                    self, obj_center.x, obj_center.y, tile_object.width,
                    tile_object.height, True, tile_object.image, tile_object.type)
            if tile_object.name == 'door':
                activator_id = tile_object.properties['activator']
                door = spr.Door(
                    self, tile_object.x, tile_object.y, tile_object.width,
                    tile_object.height, activator_id, tile_object.type, tile_object.image)
                self.objects_by_id[tile_object.id] = door
            if tile_object.type == 'mob':
                routes = []
                passive = False
                if 'passive' in tile_object.properties:
                    passive = True
                for i in range(1, 100):
                    route_name = 'route' + str(i)
                    if route_name not in tile_object.properties:
                        break
                    route = self.map.tmxdata.get_object_by_id(tile_object.properties[route_name])
                    routes.append(vec(route.x, route.y))
                self.load_mob_images(tile_object.name)
                health = tile_object.properties['health']
                speed = tile_object.properties['speed']
                damage = tile_object.properties['damage']
                knockback = tile_object.properties['knockback']
                if 'activator' in tile_object.properties:
                    activator_id = tile_object.properties['activator']
                    spr.Spawner(
                        self, obj_center.x, obj_center.y, self.mob_images[tile_object.name], health, speed, damage,
                        knockback, routes, activator_id, tile_object.name, passive)
                else:
                    spr.Enemy(
                        self, obj_center.x, obj_center.y, self.mob_images[tile_object.name], health, speed, damage,
                        knockback, routes, tile_object.name, passive)
            if tile_object.type == 'Teleport':
                spr.Teleport(
                    self, tile_object.x, tile_object.y,
                    tile_object.width, tile_object.height,
                    tile_object.name, tile_object.properties['playerLocation'])
            if tile_object.name == 'Interact':
                txt: str = tile_object.properties["text"]
                activator_id = 0
                snd = tile_object.properties['sound'].split(',')
                used = False
                activated = False
                item: str = ""
                if 'item' in tile_object.properties:
                    item = tile_object.properties['item']
                if 'activator' in tile_object.properties:
                    activator_id = tile_object.properties['activator']
                if [tile_object.x, tile_object.y] in self.open_chests:
                    used = True
                    activated = True
                text = spr.TextBox(
                    self, tile_object.x, tile_object.y, tile_object.width,
                    tile_object.height, txt, snd, tile_object.type, activator_id, item, used, activated)
                self.objects_by_id[tile_object.id] = text
            if tile_object.name == 'Sound':
                spr.SoundBox(
                    self, tile_object.x, tile_object.y,
                    tile_object.width, tile_object.height,
                    tile_object.properties['sound'], tile_object.properties['chance'], tile_object.id)
            if tile_object.name == 'Boss':
                spr.LavaBoss(self)

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(s.FPS) / 1000
            self.events()
            self.ui_manager.update(self.dt)
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop

        if not self.pause_game:
            self.all_sprites.update()
        self.camera.update(self.player)
        hits = pg.sprite.spritecollide(self.player, self.teleports, False)
        for hit in hits:
            self.load_map(hit.destination, hit.location)
            return
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            hit.activate()
            return
        hits = pg.sprite.spritecollide(self.player, self.sounds, False)
        for hit in hits:
            if self.current_sounds.has(hit):
                pass
            else:
                self.current_sounds.add(hit)
                if random.randrange(0, hit.chance) == 0:
                    hit.play()
        # check if sounds stopped colliding
        sounds_still_colliding = set(pg.sprite.spritecollide(self.player, self.current_sounds, False))
        for sound in self.current_sounds:
            if sound not in sounds_still_colliding:
                sound.stop()
                self.current_sounds.remove(sound)

        hits = pg.sprite.spritecollide(self.player, self.enemies, False)
        die_on_hit = ['Fire', 'Homing']
        for enemy in hits:
            self.player.hit(enemy)
            if enemy.name in die_on_hit:
                enemy.kill()
        hits = pg.sprite.spritecollide(self.player, self.interactables, False)
        if not hits and self.current_interactable:
            self.current_interactable.text.kill()
            self.current_interactable = False
        for hit in hits:
            if self.current_interactable != hit:
                self.current_interactable = hit
                self.current_interactable.text = UITextBox('<font face=Montserrat size=2 color=#FFFFFF><b>E</b> Read',
                                                           self.camera.apply_rect(
                                                               pg.Rect((self.player.rect.left - 10,
                                                                        self.player.rect.top - 20), (120, 45))),
                                                           manager=self.ui_manager)

    def draw_grid(self):
        for x in range(0, s.WIDTH, s.TILESIZE):
            pg.draw.line(self.screen, s.LIGHTGREY,
                         (x, 0), (x, s.HEIGHT))
        for y in range(0, s.HEIGHT, s.TILESIZE):
            pg.draw.line(self.screen, s.LIGHTGREY,
                         (0, y), (s.WIDTH, y))

    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.blit(self.map_bottom_img, self.camera.apply_rect(self.map_rect))
        self.player.draw_ui(self.screen)
        sprites = sorted(self.all_sprites, key=lambda spr: spr._layer)
        for sprite in sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        self.screen.blit(self.map_top_img, self.camera.apply_rect(self.map_rect))
        self.ui_manager.draw_ui(self.screen)
        pg.display.flip()

    def start_presenting_text(self):
        self.pause_game = True
        self.current_interactable.used = True
        self.open_chests.append([self.current_interactable.x, self.current_interactable.y])
        sounds = self.current_interactable.sound
        snd = self.get_sound(random.choice(sounds))
        snd.play()
        self.dialog_text_chunks = chain(self.current_interactable.texts.split("\n"))

    def present_text(self):
        if not self.dialog_text_chunks:
            return
        try:
            text = next(self.dialog_text_chunks)
            sounds = self.current_interactable.sound
            snd = self.get_sound(random.choice(sounds))
            snd.play()
            self.current_interactable.text.kill()
            self.current_interactable.text = UITextBox(
                '<font face=Montserrat size=4 color=#000000>' + text,
                pg.Rect((10,
                         s.HEIGHT - 75), (s.WIDTH - 20, 55)),
                manager=self.ui_manager, object_id='#text_box_2')
        except StopIteration:
            self.stop_presenting_text()

    def stop_presenting_text(self):
        self.current_interactable.text.kill()
        self.current_interactable.activated = not self.current_interactable.activated
        if self.current_interactable.type == "Item":
            self.player.add_item_by_name(self.current_interactable.item)
        elif self.current_interactable.type == "Activator":
            self.objects_by_id[self.current_interactable.activator_id].activated\
                = not self.objects_by_id[self.current_interactable.activator_id].activated
        self.dialog_text_chunks = None
        self.pause_game = False

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYUP and event.key != pg and self.current_interactable:
                self.present_text()
            if event.type == pg.KEYUP:
                if event.key == pg.K_F5 and self.player.items[s.Items.RESPAWN_ORB] > 0:
                    self.player.items[s.Items.RESPAWN_ORB] -= 1
                    self.save()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_e and self.current_interactable and not self.current_interactable.used:
                    self.start_presenting_text()
                    # self.present_text()
            if not self.pause_game:
                self.player.handle_event(event)
            self.ui_manager.process_events(event)

    def get_sound(self, sound):
        if sound not in self.sound_cache:
            try:
                self.sound_cache[sound] = pg.mixer.Sound(path.join(self.music_folder, sound))
            except FileNotFoundError:
                print("No sound file", sound)
                self.sound_cache[sound] = pg.mixer.Sound(path.join(self.music_folder, "silence.mp3"))
        return self.sound_cache[sound]

    def show_start_screen(self):
        return self.ui.run(self.ui.start_game)

    def show_go_screen(self):
        pass

    def wait_for_key(self):
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(s.FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False

    def load_mob_images(self, mob_name):
        if mob_name not in self.mob_images:
            self.mob_images[mob_name] = {}
            for direction in [s.Direction.UP, s.Direction.DOWN, s.Direction.LEFT, s.Direction.RIGHT]:
                self.mob_images[mob_name][direction] = []
                for i in [1, 2, 3]:
                    img = mob_name + direction.value + str(i) + ".png"
                    try:
                        loaded_image = pg.image.load(
                            path.join(self.img_folder, img)).convert_alpha()
                        self.mob_images[mob_name][direction].append(loaded_image)
                    except FileNotFoundError as e:
                        print("Mob image is missing", e)

    def save(self):
        save_file = path.join(self.game_folder, 'saves', 'save.json')
        state = {
            'map': [self.current_map[0], self.current_map[1]],
            'player': [self.player.health, self.player.max_health, self.player.items, self.player.max_lives],
            'chests': self.open_chests
        }
        with open(save_file, 'w') as outfile:
            json.dump(state, outfile)

    def load(self):
        save_file = path.join(self.game_folder, 'saves', 'save.json')
        with open(save_file, 'r') as infile:
            state = json.load(infile)
        self.new(load=True)
        self.player.health = state['player'][0]
        self.player.max_health = state['player'][1]
        self.player.items = state['player'][2]
        self.player.max_lives = state['player'][3]
        self.open_chests = state['chests']
        self.load_map(state['map'][0], state['map'][1])


class UI:
    def __init__(self, game):
        self.game = game

    def game_over(self):
        self.game.screen.fill(s.BLACK)
        self.title = UIButton(
            pg.Rect((0, 100), (s.WIDTH, 50)),
            'Game Over',
            manager=self.game.ui_manager, object_id='#game_over')
        self.load = UIButton(
            pg.Rect((40, 200), (s.WIDTH - 80, 50)),
            'Load Game',
            manager=self.game.ui_manager, object_id=ObjectID('#load_game', '@ok_button'))
        self.new = UIButton(
            pg.Rect((40, 255), (s.WIDTH - 80, 50)),
            'New Game',
            manager=self.game.ui_manager, object_id=ObjectID('#new_game', '@ok_button'))
        self.quit = UIButton(
            pg.Rect((40, 310), (s.WIDTH - 80, 50)),
            'QUIT',
            manager=self.game.ui_manager, object_id=ObjectID('#quit_game', '@ok_button'))

    def start_game(self):
        start_bg = pg.Surface((0, 0))
        image = pg.image.load(path.join(self.game.img_folder, 'Start.png')).convert_alpha()
        image = pg.transform.scale(image, (s.WIDTH, s.HEIGHT))
        image_rect = image.get_rect()
        self.game.screen.blit(image, image_rect)
        self.title = UIButton(
            pg.Rect((0, 100), (s.WIDTH, 75)),
            "Giant's Valley",
            manager=self.game.ui_manager, object_id='#start_game')
        self.title.disable()
        self.load = UIButton(
            pg.Rect((100, 200), (s.WIDTH - 200, 50)),
            'Load Game',
            manager=self.game.ui_manager, object_id=ObjectID('#load_game', '@ok_button'))
        self.new = UIButton(
            pg.Rect((100, 255), (s.WIDTH - 200, 50)),
            'New Game',
            manager=self.game.ui_manager, object_id=ObjectID('#new_game', '@ok_button'))
        self.quit = UIButton(
            pg.Rect((100, 310), (s.WIDTH - 200, 50)),
            'QUIT',
            manager=self.game.ui_manager, object_id=ObjectID('#quit_game', '@ok_button'))

    def new_game(self):
        self.game.screen.fill(s.BLACK)
        text = UITextBox(
            '<font face=Montserrat size=4 color=#FF0000> New Game', pg.Rect((0, 0), (s.WIDTH, s.HEIGHT)),
            manager=self.game.ui_manager, object_id='#text_box_3')

    def run(self, draw_screen):
        # game loop - set self.playing = False to end the game
        self.state = None
        pg.mixer.music.stop()
        self.playing = True
        self.ui_manager = UIManager((s.WIDTH, s.HEIGHT), path.join(self.game.game_folder, 'data/themes/theme_1.json'))
        draw_screen()
        while self.playing:
            self.dt = self.game.clock.tick(s.FPS) / 1000
            self.events()
            self.game.ui_manager.update(self.dt)
            self.game.ui_manager.draw_ui(self.game.screen)
            pg.display.update()

        return self.state

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_object_id == '#load_game':
                        try:
                            self.game.load()
                            self.state = s.UIGameState.LOAD
                        except FileNotFoundError:
                            print('No save exists, starting new game')
                            self.game.new()
                            self.game.save()
                        self.playing = False
                        self.title.kill()
                        self.load.kill()
                        self.new.kill()
                        self.quit.kill()
                    if event.ui_object_id == '#new_game':
                        self.state = s.UIGameState.NEW
                        self.game.new()
                        self.game.save()
                        self.playing = False
                        self.title.kill()
                        self.load.kill()
                        self.new.kill()
                        self.quit.kill()
                    if event.ui_object_id == '#quit_game':
                        self.game.quit()
            if event.type == pg.QUIT:
                self.game.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.game.quit()
            self.game.ui_manager.process_events(event)


# create the game object
g = Game()
g.show_start_screen()
while True:
    g.run()
    g.new()
