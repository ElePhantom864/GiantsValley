import pygame as pg
from enum import Enum


class Direction(Enum):
    UP = 'Up'
    DOWN = 'Down'
    LEFT = 'Left'
    RIGHT = 'Right'


class Items(Enum):
    SWORD = 'sword'
    HEALTH_POTION = 'health_potion'


# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# game settings
WIDTH = 15 * 32   # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 15 * 32  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Tilemap Demo"
BGCOLOR = DARKGREY

TILESIZE = 32

# player settings
PLAYER_SPEED = 150
PLAYER_KNOCKBACK = 15
PLAYER_HIT_RECT = pg.Rect(0, 0, 21, 23)
PLAYER_HEALTH = 6
DAMAGE_ALPHA = [i for i in range(0, 255, 25)]
PLAYER_IMAGES = {
    Direction.UP: [
        'LinkUp1.png',
        'LinkUp2.png',
        'LinkUp3.png'
    ],
    Direction.DOWN: [
        'LinkDown1.png',
        'LinkDown2.png',
        'LinkDown3.png'
    ],
    Direction.LEFT: [
        'LinkLeft1.png',
        'LinkLeft2.png',
        'LinkLeft3.png'
    ],
    Direction.RIGHT: [
        'LinkRight1.png',
        'LinkRight2.png',
        'LinkRight3.png'
    ],
}

# mob settings
COBRA_SPEED = 100
COBRA_IMAGES = {
    Direction.UP: [
        'CobraUp1.png',
        'CobraUp2.png'
    ],
    Direction.DOWN: [
        'CobraDown1.png',
        'CobraDown2.png'
    ],
    Direction.LEFT: [
        'CobraLeft1.png',
        'CobraLeft2.png'
    ],
    Direction.RIGHT: [
        'CobraRight1.png',
        'CobraRight2.png'
    ],
}

# layers
PLAYER_LAYER = 0
PUSH_LAYER = -2
ENEMY_LAYER = -2
DOOR_LAYER = -2
ACTIVATOR_LAYER = -4
