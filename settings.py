import os

# Основные константы и значения
SCREEN_SIZE = WIDTH, HEIGHT = 512, 512
UPSCALE = 4
TILE_SIZE = 8 * UPSCALE
FPS = 60
MAPS_DIR = 'data/maps'
SPEED = 240 / FPS
JUMP_POWER = 6.8
WALL_JUMP_POWER = 5
DASH_POWER = 8.5
GRAVITY = 0.4
PARTICLES_COUNT = 70
player_name = os.getlogin()
