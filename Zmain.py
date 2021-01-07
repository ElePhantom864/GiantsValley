# KidsCanCode - Game Development with Pygame video series

# Tile-based game - Part 1
# Project setup
# Video link: https://youtu.be/3UxnelT9aCo
import pygame as pg
import sys
import Zsettings as s
import Zsprites as spr
from Ztilemap import TiledMap, Camera
from os import path
from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.core import IncrementalThreadedResourceLoader
from pygame_gui import UI_TEXT_BOX_LINK_CLICKED
from itertools import chain
import time

vec = pg.math.Vector2


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(
            (s.WIDTH, s.HEIGHT), flags=pg.RESIZABLE | pg.SCALED)
        pg.display.set_caption(s.TITLE)
        self.clock = pg.time.Clock()
        self.pause_game = False
        self.dialog_text_chunks = None
        pg.key.set_repeat(100, 100)
        self.load_data()

    def load_data(self):
        game_folder = path.dirname(__file__)
        snd_folder = path.join(game_folder, 'snd')
        music_folder = path.join(game_folder, 'music')
        self.img_folder = path.join(game_folder, 'img')
        self.map_folder = path.join(game_folder, 'maps')
        self.sword_img = pg.image.load(path.join(self.img_folder, 'TempSword.png')).convert_alpha()
        self.heart_img = pg.image.load(path.join(self.img_folder, 'Heart.png')).convert_alpha()
        self.half_heart_img = pg.image.load(path.join(self.img_folder, 'Half_Heart.png')).convert_alpha()
        self.empty_heart_img = pg.image.load(path.join(self.img_folder, 'Empty_Heart.png')).convert_alpha()
        self.player_images = {}
        for direction, images in s.PLAYER_IMAGES.items():
            self.player_images[direction] = list(map(lambda img: pg.image.load(
                path.join(self.img_folder, img)).convert_alpha(), images))
        self.mob_images = {}

        loader = IncrementalThreadedResourceLoader()
        self.ui_manager = UIManager((s.WIDTH, s.HEIGHT), path.join(game_folder, 'data/themes/theme_1.json'),
                                    resource_loader=loader)
        self.ui_manager.add_font_paths("Montserrat",
                                       path.join(game_folder, "data/fonts/Montserrat-Regular.ttf"),
                                       path.join(game_folder, "data/fonts/Montserrat-Bold.ttf"),
                                       path.join(game_folder, "data/fonts/Montserrat-Italic.ttf"),
                                       path.join(game_folder, "data/fonts/Montserrat-BoldItalic.ttf"))

        self.ui_manager.preload_fonts([{'name': 'Montserrat', 'html_size': 4.5, 'style': 'bold'},
                                       {'name': 'Montserrat', 'html_size': 4.5, 'style': 'regular'},
                                       {'name': 'Montserrat', 'html_size': 2, 'style': 'regular'},
                                       {'name': 'Montserrat', 'html_size': 2, 'style': 'italic'},
                                       {'name': 'Montserrat', 'html_size': 6, 'style': 'bold'},
                                       {'name': 'Montserrat', 'html_size': 6, 'style': 'regular'},
                                       {'name': 'Montserrat', 'html_size': 6, 'style': 'bold_italic'},
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

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.teleports = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.sword = pg.sprite.Group()
        self.interactables = pg.sprite.Group()
        self.activators = pg.sprite.Group()
        self.pushers = pg.sprite.Group()
        self.player = spr.Player(
            self, 0, 0)
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
        self.player.add([self.pushers, self.all_sprites])

        self.current_interactable = None
        self.map = TiledMap(path.join(self.map_folder, map_name))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
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
                activator = spr.Activator(
                    self, tile_object.x, tile_object.y, tile_object.width,
                    tile_object.height, tile_object.image, tile_object.type)
                self.objects_by_id[tile_object.id] = activator
            if tile_object.name == 'pushable':
                spr.Obstacle(
                    self, tile_object.x, tile_object.y, tile_object.width,
                    tile_object.height, True, tile_object.image, tile_object.type)
            if tile_object.name == 'door':
                activator_id = tile_object.properties['activator']
                door = spr.Door(
                    self, tile_object.x, tile_object.y, tile_object.width,
                    tile_object.height, activator_id, tile_object.image)
                self.objects_by_id[tile_object.id] = door
            if tile_object.type == 'mob':
                routes = []
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
                spr.Enemy(
                    self, obj_center.x, obj_center.y, self.mob_images[tile_object.name], health, speed, damage, routes)
            if tile_object.type == 'Teleport':
                spr.Teleport(
                    self, tile_object.x, tile_object.y,
                    tile_object.width, tile_object.height,
                    tile_object.name, tile_object.properties['playerLocation'])
            if tile_object.name == 'Interact':
                txt: str = tile_object.properties["text"]
                text = spr.TextBox(
                    self, tile_object.x, tile_object.y, tile_object.width,
                    tile_object.height, txt, tile_object.type)
                self.objects_by_id[tile_object.id] = text

        self.camera = Camera(self.map.width, self.map.height)

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
        hits = pg.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in hits:
            self.player.hit(enemy)
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
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        sprites = sorted(self.all_sprites, key=lambda spr: spr._layer)
        for sprite in sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        self.ui_manager.draw_ui(self.screen)
        self.player.draw_health(self.screen)
        pg.display.flip()

    def start_presenting_text(self):
        self.pause_game = True
        self.dialog_text_chunks = chain(self.current_interactable.texts.split("\n"))

    def present_text(self):
        if not self.dialog_text_chunks:
            return
        try:
            text = next(self.dialog_text_chunks)
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
        if self.current_interactable.type == "Sword":
            self.player.add_item(s.Items.SWORD)
        elif self.current_interactable.type == "Lever":
            self.current_interactable.activated = True
        self.dialog_text_chunks = None
        self.pause_game = False

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYUP and event.key != pg and self.current_interactable:
                self.present_text()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_e and self.current_interactable:
                    self.start_presenting_text()
                    # self.present_text()
            if not self.pause_game:
                self.player.handle_event(event)
            self.ui_manager.process_events(event)

    def show_start_screen(self):
        pass

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
                for i in [1, 2]:
                    img = mob_name + direction.value + str(i) + ".png"
                    try:
                        loaded_image = pg.image.load(
                            path.join(self.img_folder, img)).convert_alpha()
                        self.mob_images[mob_name][direction].append(loaded_image)
                    except FileNotFoundError as e:
                        print("Mob image is missing", e)


# create the game object
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()
