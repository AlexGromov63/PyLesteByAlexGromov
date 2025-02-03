import os
import pygame
from settings import *
from PIL import Image, ImageOps

# Список карт (уровней), отфильтрованный по расширению .tmx и отсортированный по номеру
maplist = sorted(list(filter(lambda x: x[-4:] == '.tmx' and x.count('-') == 1, os.listdir(MAPS_DIR))),
                 key=lambda x: int(x[x.index('-') + 1:x.index('.')]))


class Button:   # Класс кнопки
    def __init__(self, image, pos):
        self.pos = pos
        self.picture = Image.open(f'data/res/{image}').convert('RGBA')  # Загрузка изобржения с учетом альфа канала
        self.image = pygame.image.fromstring(self.picture.tobytes(), self.picture.size, 'RGBA')

    def draw(self, screen):
        screen.blit(self.image, self.pos)

    def invert(self):   # Инверсия изображения при нажатии (эффект клика)
        r, g, b, a = self.picture.split()
        self.picture = Image.merge("RGBA", (ImageOps.invert(r), ImageOps.invert(g), ImageOps.invert(b), a))
        self.image = pygame.image.fromstring(self.picture.tobytes(), self.picture.size, 'RGBA')

    def is_clicked(self, event_pos):    # Проверка нажатия на кнопку
        x, y = event_pos
        if x > self.pos[0] and x < self.pos[0] + self.image.get_width() and \
                y > self.pos[1] and y < self.pos[1] + self.image.get_height():
            self.invert()
            return True
        return


def FadeAnim(screen, time, inout):  # Функция анимации затемнения экрана
    if inout:   # Появление
        radius = int(time / 2000 * WIDTH)
    else:       # Исчезновение
        radius = WIDTH - int(time / 2000 * WIDTH)
    surface = pygame.Surface(screen.get_size()).convert_alpha()
    pygame.draw.circle(surface, (0, 0, 0, 0), (WIDTH / 2, HEIGHT / 2), radius)
    screen.blit(surface, (0, 0))


def terminate(screen, current_time, timer_start_time):  # Функция завершения игры с анимацией затемнения
    FadeAnim(screen, current_time - timer_start_time, False)
    if current_time - timer_start_time >= 2000:
        return False
    pygame.display.flip()


def screen_wiggle(screen, groups, intensity):   # Функция эффекта тряски экрана
    if intensity:
        for group in groups:
            for sprite in group:
                screen.blit(sprite.image, sprite.rect.topleft + (pygame.Vector2(intensity, intensity)))


def invert(image):  # Функция инверсии цветов изображения
    picture = Image.frombytes('RGBA', image.get_size(), pygame.image.tostring(image, 'RGBA'))
    r, g, b, a = picture.split()
    picture = Image.merge("RGBA", (ImageOps.invert(r), ImageOps.invert(g), ImageOps.invert(b), a))
    return pygame.image.fromstring(picture.tobytes(), picture.size, 'RGBA')


def deathAnim(screen, deathParticles):  # Функция анимации смерти игрока
    deathParticles.draw(screen)
    deathParticles.update()


def load_image(name, color_key=None):   # Функция загрузки изображения
    fullname = os.path.join('data/res', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Failture: ', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


def split_sprites(image_path, sprite_width, sprite_height):     # Разделение изображения на спрайты по размерам
    image = Image.open(image_path)
    return [image.crop((i * sprite_width, 0, (i + 1) * sprite_width, sprite_height))
            for i in range(image.width // sprite_width)]


def splitUpscaleList(image_path, sprite_width=8, sprite_height=8):  # Разделение и увеличение изображения на спрайты
    return [pygame.transform.scale(pygame.image.fromstring(i.tobytes(), i.size, i.mode), (TILE_SIZE, TILE_SIZE))
            for i in split_sprites(image_path, sprite_width, sprite_height)]


def drawAll(screen):    # Отрисовка всех слоев, кроме deco
    for i in notDecoLayers:
        i.draw(screen)


def clearLayers(groups):    # Очистка всех групп спрайтов
    for i in groups:
        i.empty()


def initSounds():   # Инициализация звуков игры
    deathS = pygame.mixer.Sound('data/res/sounds/dying.wav')            # Смерть
    dashS = pygame.mixer.Sound('data/res/sounds/dash.wav')              # Рывок
    jumpS = pygame.mixer.Sound('data/res/sounds/jump.wav')              # Прыжок
    batutJumpS = pygame.mixer.Sound('data/res/sounds/jumpBig.wav')      # Прыжок на батуте
    strawberryS = pygame.mixer.Sound('data/res/sounds/strawberry.wav')  # Взятие клубники
    gameoverS = pygame.mixer.Sound('data/res/sounds/gameover.wav')      # Конец игры
    # Возврат словаря для удобного использования каждого звука
    return {'death': deathS, 'jump': jumpS, 'dash': dashS, 'batut': batutJumpS,
            'strawberry': strawberryS, 'gameover': gameoverS}

# Разделение изображения игрока на отдельные спрайты
player_images = split_sprites('data/res/player.png', 8, 8)

# Создание групп спрайтов
all_sprites = pygame.sprite.Group()     # Общая группа
spikes_layer = pygame.sprite.Group()    # Шипы
deco_layer = pygame.sprite.Group()      # Декорации
tile_group = pygame.sprite.Group()      # Стены
player_group = pygame.sprite.Group()    # Игрок
secret_layer = pygame.sprite.Group()    # Скрытые объекты
baloons = pygame.sprite.Group()         # Шарики
specials_layer = pygame.sprite.Group()  # Специальные объекты
notDecoLayers = [spikes_layer, tile_group, player_group,    # Группы, которые не относятся к декоративным
                 specials_layer, secret_layer, baloons]
allGroups = [all_sprites, spikes_layer, deco_layer, tile_group,     # Все группы
             player_group, specials_layer, secret_layer, baloons]
