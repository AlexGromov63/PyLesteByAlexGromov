import pygame
import sys
import random
from score import TimerScreen, add_to_score, return_score_change
from player import Player
from particles import SnowParticlesTogether, DeathParticlesTogether
from general import *
from level import Map

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)


def reloadMap(current_map, sfx=None, player=True):   # Перезагрузка карты и создание нового игрока
    map = Map(current_map, 0, [1, 2, 3, 4, 5, 6, 7], 75)
    if player:
        player_pos = map.render(screen)
        player = Player(player_pos[0] * TILE_SIZE, player_pos[1] * TILE_SIZE, sfx)
    return map, player  # Возвращаем карту и игрока


def main():     # Основной игровой цикл
    pygame.display.set_caption('Pyleste')
    icon = pygame.image.load('data/res/icon.png')
    pygame.display.set_icon(icon)
    clock = pygame.time.Clock()
    sfx = initSounds()  # Инициализация звуков
    mapnum = 0          # Счетчик урвыней
    map, player = reloadMap(maplist[mapnum], sfx)   # Загружаем карту и игрока
    timer = TimerScreen((255, 255, 255), (WIDTH // 2, 30))  # Создание объекта таймера
    SnowParticles = SnowParticlesTogether(0.8)      # Создание частиц снега
    SnowParticles.add_particles()
    DeathParticles = DeathParticlesTogether()       # Создание частиц для анимации смерти
    # Инициализация кнопок
    menuBut, exitBut = Button('menuBut.png', (10, 10)), Button('exitBut.png', (WIDTH // 2 - 80, HEIGHT // 2 - 48))
    dt = 0      # Счетчик тиков
    left = right = up = upFly = down = False        # Элементы управления
    dash = score = deaths = strawberries = 0        # Элементы специальных событий
    isdashing = wiggle = iswalljump = isdeathanim = paused = drawscoreChange = False    # Элементы состояния игрока
    fadeanimate = startfadeanim = True              # Элементы состояния анимаций
    running = True
    timer_start_time = pygame.time.get_ticks()    # Обнуление таймера тиков
    timer_time = 0
    level_start_score = 0                           # Обнуление счетчика очков
    while running:
        dt = clock.tick(FPS)    # Ограничение FPS
        current_time = pygame.time.get_ticks()
        if mapnum < mapnum + player.if_finish(map):     # Проверяем, завершил ли игрок уровень
            mapnum += player.if_finish(map)
            if mapnum == len(maplist):
                sfx['gameover'].play()
            if mapnum >= len(maplist):
                mapnum = len(maplist) + 1
                FadeAnim(screen, current_time - timer_start_time, False)    # Анимация завершения игры
                if current_time - timer_start_time >= 2000:
                    running = False
                pygame.display.flip()
                continue
            map, player = reloadMap(maplist[mapnum], sfx)
            strawberries = 0
            score_change = 100 * mapnum
            score_timer = current_time
            score += score_change
            level_start_score = score
            drawscoreChange = True
        if player.strawBerry:   # Проверка касания клубники
            score_change = 1000
            score_timer = current_time
            score += score_change
            drawscoreChange = True
            strawberries += 1
            sfx['strawberry'].play()
        if player.onGround:     # Обнуление счетчика рывка, если игрок на земле
            dash = 0
        if isdashing and current_time - timer_start_time >= 100 and wiggle:     # Остановка тряски экрана
            wiggle = False
        if startfadeanim and current_time - timer_start_time >= 2000:           # Остановка анимации старта
            startfadeanim = False
            fadeanimate = False
        if wiggle and not isdashing and current_time - timer_start_time >= 100:     # Остановка тряски экрана при рывке
            wiggle = False
        if isdashing and current_time - timer_start_time >= 200:                # Остановка рывка
            isdashing = False
        # Остановка прыжка от стены
        if iswalljump and (current_time - timer_start_time >= 220 or player.onGround or player.onWall):
            iswalljump = False
        if isdeathanim and current_time - timer_start_time >= 300:              # Перезагрузка уровня при смерти персонажа
            map, player = reloadMap(maplist[mapnum], sfx)
            DeathParticles.particles = []
            isdeathanim = False
        for event in pygame.event.get():    # Проверка событий
            if event.type == pygame.QUIT:
                running = False
                sys.exit()
            if not isdashing and not paused:    # Обработка управления игрока
                if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                    left = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
                    up = True
                    if player.onWall:
                        iswalljump = True
                        timer_start_time = current_time
                        sfx['jump'].play()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                    upFly = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                    right = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                    down = True
            if event.type == pygame.KEYUP and event.key == pygame.K_z:
                up = False
            if event.type == pygame.KEYUP and event.key == pygame.K_UP:
                upFly = False
            if event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
                down = False
            if event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
                right = False
            if event.type == pygame.KEYUP and event.key == pygame.K_LEFT:
                left = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_x:    # Работа с рывком
                dash += 1
                if dash == 1:
                    isdashing = True
                    timer_start_time = current_time
                    wiggle = True
                    sfx['dash'].play()
            if event.type == pygame.MOUSEBUTTONDOWN and not fadeanimate:    # Обработка нажатий на кнопки
                menuBut.is_clicked(event.pos)
                exitBut.is_clicked(event.pos)
            if event.type == pygame.MOUSEBUTTONUP and not fadeanimate:
                if menuBut.is_clicked(event.pos):
                    paused = not paused
                if exitBut.is_clicked(event.pos):
                    timer_start_time = current_time
                    fadeanimate = True
        if player.death:    # Проверка смерти игрока и ее обработка
            sfx['death'].play()
            player.death = False
            isdeathanim = True
            player_death_pos = player.rect.center
            wiggle = True
            timer_start_time = current_time
            score_timer = current_time
            score_change = -(int(level_start_score / 10))
            strawberries = 0
            deaths += 1
            score = level_start_score + score_change
            level_start_score = score
            drawscoreChange = True
            DeathParticles.add_particles(player_death_pos)
        # Создания surface для работы с общим изображением
        CapturedScreen = pygame.Surface(screen.get_size()).convert_alpha()
        for i in baloons:   # Отрисовка шариков по отдельности
            if i.visible and i.rect.colliderect(player.rect):
                dash = 0
            i.update(player)
            i.draw(CapturedScreen)
        # Распределения порядка отрисовки слоёв, для правильного их наложения друг на друга
        all_sprites.update(player)
        deco_layer.draw(CapturedScreen)
        SnowParticles.update(dt, 20)
        SnowParticles.draw(CapturedScreen)
        drawAll(CapturedScreen)
        menuBut.draw(CapturedScreen)
        intense = random.randint(-17, 17)
        if paused:      # Отрисовка экрана при паузе
            darken = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            darken.fill((0, 0, 0, 120))
            player.draw(CapturedScreen)
            screen.blit(CapturedScreen, (0, 0))
            screen.blit(darken, (0, 0))
            exitBut.draw(screen)
            if fadeanimate:
                FadeAnim(screen, current_time - timer_start_time, False)
                if current_time - timer_start_time >= 2000:
                    running = False
            pygame.display.flip()
            continue

        if drawscoreChange:     # Отрисовка изменения состояния очков
            return_score_change(CapturedScreen, score_change)
            if current_time - score_timer > 2000:
                drawscoreChange = False

        if not isdeathanim:     # Отрисовка игрока, если он жив
            player.update(left, right, up, upFly, down, isdashing, iswalljump, dash)
            player.draw(CapturedScreen)
            intense = random.randint(-8, 8)
        if wiggle:              # Тряска экрана
            screen.blit(CapturedScreen, (intense, intense))
        else:
            screen.blit(CapturedScreen, (0, 0))
        if isdeathanim:         # Анимация смерти персонажа
            deathAnim(screen, DeathParticles)
        if fadeanimate and not paused:  # Анимация затухания
            FadeAnim(CapturedScreen, current_time - timer_start_time, True)
        timer_time += dt
        timer.draw(screen, timer_time)
        pygame.display.flip()

    add_to_score(player_name, mapnum, score, timer.time, deaths)    # Добавление очков в базу данных


if __name__ == '__main__':
    main()
