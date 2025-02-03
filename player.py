import pygame
from settings import *
from general import *
from level import *


class Player(pygame.sprite.Sprite):     # Создание класса игрока
    def __init__(self, x, y, sfx):
        pygame.sprite.Sprite.__init__(all_sprites, player_group)
        self.dx, self.dy = 0, 0
        self.onGround = False
        self.onWall = False
        self.startX, self.startY = x, y
        self.particleCast = 0
        self.direction = True
        self.death = False
        # Создание списка изображений с разными состояниями персонажа
        self.images = [pygame.image.fromstring(i.tobytes(), i.size, i.mode) for i in player_images]
        self.images = [pygame.transform.scale(i, (TILE_SIZE, TILE_SIZE)) for i in self.images]
        self.image = self.images[0]     # Установка исходного изображения
        self.rect = pygame.Rect(self.startX, self.startY, TILE_SIZE, TILE_SIZE)
        self.score = 0
        self.strawBerry = self.baloon = False
        self.sfx = sfx  # Передача словаря для работы со звуками

    def update(self, left, right, up, upFly, down, isdashing, iswalljump, dashNum):     # Обновление состояния игрока
        self.strawBerry = self.baloon = False
        gravity = GRAVITY   # Создание переменной gravity для ее обработки, не изменяя установленное
        self.image = self.images[0]
        if self.onWall:     # Ослабление гравитации при скольжении по стене
            gravity /= 3
        elif isdashing:     # Временное отключение гравитации при рывке
            gravity = 0
        # Работа с управлением персонажа
        if left and not iswalljump:
            self.dx = -SPEED
            if self.direction:      # Если персонаж развернулся в другую сторону - отражаем изображения
                self.images = [pygame.transform.flip(i, True, False) for i in self.images]
                self.image = self.images[0]
            if isdashing:           # Увеличение силы движения игрока при рывке
                self.dx = -DASH_POWER
            self.direction = False  # Установка текущего направления движения
        if right and not iswalljump:
            self.dx = SPEED
            if not self.direction:  # Если персонаж развернулся в другую сторону - отражаем изображения
                self.images = [pygame.transform.flip(i, True, False) for i in self.images]
                self.image = self.images[0]
            if isdashing:           # Увеличение силы движения игрока при рывке
                self.dx = DASH_POWER
            self.direction = True   # Установка текущего направления движения
        # Если рывок произошел без нажатия кнопок упраления, игрок полетит в том направлении, в каком двигался до этого
        if not (left or right):
            self.dx = 0
            if isdashing and not upFly:
                if self.direction:
                    self.dx = DASH_POWER
                else:
                    self.dx = -DASH_POWER

        if up and not iswalljump:   # Обычный прыжок (не от стены)
            if self.onGround:
                self.dy = -JUMP_POWER
                self.onWall = False
                self.sfx['jump'].play()
        if upFly:                   # Обработка стрелки вверх, отвеч. за направление рывка в полете
            if not self.onGround and isdashing:
                self.dy = -DASH_POWER / 1.8
            else:
                self.image = self.images[6]
        if down:
            self.image = self.images[5]     # Стрелка вниз - персонаж смотрит вниз

        if iswalljump:  # Прыжок от стены
            self.dy = -WALL_JUMP_POWER
            if self.direction:
                self.dx = -WALL_JUMP_POWER
            else:
                self.dx = WALL_JUMP_POWER

        if not self.onGround:   # Если игрок в воздухе - заставить его падать
            self.dy += gravity

        if self.onWall:         # Контроль гравитации при скольжении по стене
            if self.dy < 0:
                self.dy /= 1.5
            self.image = self.images[4]

        self.onGround = False   # Обнуление состояний
        self.onWall = False

        self.rect.y += self.dy
        self.collide(0, self.dy)

        self.rect.x += self.dx
        self.collide(self.dx, 0)

        if dashNum >= 1:
            self.image = invert(self.image)

    def collide(self, dx, dy):  # Проверка взаимодействий с другими тайлами
        for tile in pygame.sprite.spritecollide(self, tile_group, False):   # Столкновение со стенами
            if dx > 0:  # Движение вправо
                self.rect.right = tile.rect.left
                self.onWall = True
            elif dx < 0:  # Движение влево
                self.rect.left = tile.rect.right
                self.onWall = True
            if dy > 0:  # Падение
                self.rect.bottom = tile.rect.top
                self.onGround = True
                self.dy = 0
            elif dy < 0:  # Прыжок
                self.rect.top = tile.rect.bottom
                self.dy = 0

        for _ in pygame.sprite.spritecollide(self, spikes_layer, False):    # Взаимодействие с "шипами" (смерть)
            self.death = True

        for i in specials_layer:    # Взаимодействие со специальными объектами: батут, клубника
            if isinstance(i, Batut):
                if i.jump((self.rect.x + dx, self.rect.y + dy)):
                    self.dy = -JUMP_POWER * 1.65 # Заставляем игрока отскакивать
                    self.sfx['batut'].play()
            elif isinstance(i, StrawBerry):
                if i.touch((self.rect.x + dx, self.rect.y + dy)):
                    self.strawBerry = True  # Передаем, что игрок "собрал" клубнику
                    i.kill()                # Удаляем клубнику с уровня

        # Проверка выхода за границы экрана
        if self.rect.left + dx < 0:
            self.rect.left = 0
        if self.rect.right + dx > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top > HEIGHT:
            self.death = True

    def draw(self, screen):     # Отрисовка
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def id_check(self, map, layer):     # Проверка id тайла, в котором находится игрок
        cur_id = map.get_tile_id(((self.rect.x + TILE_SIZE) // TILE_SIZE,
                                  (self.rect.y + TILE_SIZE) // TILE_SIZE), layer)
        return cur_id

    def if_finish(self, map):           # Если игрок коснулся тайла-конца уровня - возвращяем 1
        if self.id_check(map, 'secret') == map.finish_tile:
            return 1
        return 0
