import pygame
import time
import pytmx
from settings import *
from general import *


class Tile(pygame.sprite.Sprite):   # Базовый класс для каждого тайла
    def __init__(self, image, pos_x, pos_y):
        super().__init__(all_sprites)
        self.image = image          # Изображение тайла
        self.rect = self.image.get_rect().move(TILE_SIZE * pos_x, TILE_SIZE * pos_y)    # Позиция на карте


class Batut(Tile):  # Собственный класс для "батута"
    def __init__(self, image, pos_x, pos_y):
        super().__init__(image, pos_x, pos_y)
        self.images = splitUpscaleList('data/res/batut.png')    # Разделение изображения, для легкой смены изображений
        self.image = self.images[0]
        self.rect = self.image.get_rect().move(TILE_SIZE * pos_x, TILE_SIZE * pos_y)

    def jump(self, player_pos):     # Функция прыжка на батуте
        if (player_pos[0] > self.rect.x - TILE_SIZE + 8 and player_pos[0] <= self.rect.x + TILE_SIZE) and \
                (player_pos[1] >= self.rect.y and player_pos[1] <= self.rect.y + TILE_SIZE):
            self.image = self.images[1]     # Меняем изображение на сжатый батут
            return True
        elif player_pos[1] < self.rect.y - 32 or player_pos[1] > self.rect.y + TILE_SIZE:
            self.image = self.images[0]     # Возвращаем исходное изображение
            return False


class StrawBerry(Tile):     # Класс для тайла "клубники", дающий + очки
    def __init__(self, image, pos_x, pos_y):
        super().__init__(image, pos_x, pos_y)
        self.image = image
        self.rect = self.image.get_rect().move(TILE_SIZE * pos_x, TILE_SIZE * pos_y)
        self.touchable = True   # Можно ли собрать

    def touch(self, player_pos):    # Функция касания "клубники"
        if (player_pos[0] > self.rect.x - TILE_SIZE and player_pos[0] <= self.rect.x + TILE_SIZE) and \
                (player_pos[1] >= self.rect.y and player_pos[1] <= self.rect.y + TILE_SIZE) and self.touchable:
            return True


class Baloon(pygame.sprite.Sprite):     # Класс тайла шарика, дающий возможность двойного рывка
    def __init__(self, image, x, y):
        super().__init__(baloons)
        self.rootimage = image
        self.image = self.rootimage
        self.rect = self.image.get_rect().move(TILE_SIZE * x, TILE_SIZE * y)
        self.visible = True         # Видимость шара
        self.last_disappeared = 0   # Время последнего исчезновения
        self.respawn_time = 3       # Время до повторного появления

    def update(self, player):       # Обновление состояние шара
        if self.visible and self.rect.colliderect(player.rect):
            self.visible = False
            self.last_disappeared = time.time()
        if not self.visible and time.time() - self.last_disappeared >= self.respawn_time:
            self.visible = True

    def draw(self, screen):         # Отрисовка шара в зависимости от его видимости
        if self.visible:
            self.image = self.rootimage
            screen.blit(self.image, self.rect)
        else:
            self.image = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            self.image.fill((0, 0, 0, 0))
        screen.blit(self.image, self.rect)


class Map:      # Главный класс уровня
    def __init__(self, filename, free_tiles, player_tile, finish_tile):
        self.map = pytmx.load_pygame(f'{MAPS_DIR}/{filename}')
        self.width = self.map.width
        self.height = self.map.height
        self.tile_size = self.map.tilewidth * UPSCALE
        self.free_tiles = free_tiles
        self.player_tile = player_tile  # Позиция появление игрока
        self.finish_tile = finish_tile  # Позиция конца уровня
        self.layersList = list(self.map.layernames.keys())

    def render(self, screen):       # Отрисовка карты
        player_y = player_x = 0
        clearLayers(allGroups)      # Очищаем слои перед отрисовкой
        for i in self.layersList:   # Перебираем все тайлы по слоям
            for y in range(self.height):
                for x in range(self.width):
                    image = self.map.get_tile_image(x, y, self.layersList.index(i)) # Получаем изображение
                    # Обработка позиции игрока на карте
                    try:
                        if i == 'walls':
                            if self.map.tiledgidmap[self.map.get_tile_gid(x, y, self.layersList.index(i))] \
                                    in self.player_tile:
                                player_x = x
                                player_y = y
                                image = None
                    except KeyError:
                        continue
                    if image:   # Если это не пустой тайл, распределяем его по слоям и группам
                        img = pygame.transform.scale(image, (self.tile_size, self.tile_size))
                        tile = Tile(img, x, y)
                        if i == 'walls':
                            tile_group.add(tile)
                        elif i == 'deco':
                            deco_layer.add(tile)
                        elif i == 'spikes':
                            spikes_layer.add(tile)
                        elif i == 'secret':
                            secret_layer.add(tile)
                        elif i == 'specials':
                            if self.get_tile_id((x, y), 'specials') == 17:
                                tile = Batut(tile.image, x, y)
                            if self.get_tile_id((x, y), 'specials') == 27:
                                tile = StrawBerry(tile.image, x, y)
                            if self.get_tile_id((x, y), 'specials') == 50:
                                tile = Baloon(tile.image, x, y)
                                baloons.add(tile)
                            specials_layer.add(tile)

                        all_sprites.add(tile)
                        screen.blit(img, (x * self.tile_size, y * self.tile_size))
        return (player_x, player_y)         # Возвращаем позицию игрока

    def get_tile_id(self, position, i):     # Получение id тайла
        try:
            id = self.map.tiledgidmap[self.map.get_tile_gid(position[0], position[1], self.layersList.index(i))]
            if id:
                return id
        except Exception:
            return

    def is_free(self, position):            # Проверка, свободный ли тайл
        return self.get_tile_id(position) in self.free_tiles
