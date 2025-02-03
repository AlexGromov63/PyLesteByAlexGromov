import pygame
import random
import math
from settings import *


class SnowParticle:     # Класс частицы снега
    def __init__(self, pos, radius, speed, wave_speed, time_offset, opacity):
        self.pos = pos
        self.radius = radius
        self.speed = speed
        self.wave_speed = wave_speed
        self.time_offset = time_offset
        self.opacity = int(opacity * 255)   # Для удобства, прозрачность задается от 0 до 1

    def draw(self, screen):
        pygame.draw.circle(screen, pygame.Color(255, 255, 255, self.opacity), self.pos, self.radius)

    def update(self, dt, time):     # Обновление состояния снежинки
        self.pos[0] -= self.speed * dt
        if self.pos[0] < -100:      # Если снежинка ушла далеко за экран - переносим ее обратно
            self.pos[0] = WIDTH + 100
            if self.pos[1] < -100 or self.pos[1] > HEIGHT:
                self.pos[1] = random.randint(100, HEIGHT - 100)
        self.pos[1] += math.sin(time + self.time_offset)    # Выщитываем волнообразное движение


class SquareParticle:   # Класс частицы в анимации эффекта смерти
    def __init__(self, center, side, speed, brightness, angle):
        self.center = list(center)
        self.side = side
        self.speed = speed
        self.brightness = int(brightness / 100 * 255)   # Для удобства, яркость задается от 0 до 100
        self.angle = angle

    def draw(self, screen):
        pygame.draw.rect(screen, pygame.Color(255, self.brightness, self.brightness),
                         (self.center[0] - (self.side / 2), self.center[1] - (self.side / 2), self.side, self.side))

    def update(self):   # Обновление состояния частицы
        if self.brightness - 8 < 0: # Постепенное затухания яркости у снежинки
            self.brightness = 0
        else:
            self.brightness -= 8
        self.speed += GRAVITY   # Скорость полета частицы равна гравитации
        self.side += 0.7        # Постепенное величение частицы
        self.center[0] += self.speed * math.cos(math.radians(self.angle))   # Выщитываем углы направления полета чатсицы
        self.center[1] += self.speed * math.sin(math.radians(self.angle))


class SnowParticlesTogether:    # Общий класс обработки снега
    def __init__(self, opacity):
        self.particles = []
        self.opacity = opacity

    def add_particles(self):    # Создание снежинок и добавление в общий список
        for _ in range(PARTICLES_COUNT):
            particle = SnowParticle([random.randint(-100, WIDTH),
                                    random.randint(0, HEIGHT)],
                                    random.randint(3, 6), random.randint(13, 25) / FPS,
                                    random.randint(-20, 20) / 10, random.randint(-4, 3), self.opacity)
            self.particles.append(particle)

    def update(self, dt, time):
        for i in self.particles:
            i.update(dt, time)

    def draw(self, screen):
        for i in self.particles:
            i.draw(screen)


class DeathParticlesTogether:   # Общий класс анимации частиц смерти
    def __init__(self):
        self.particles = []

    def add_particles(self, player_pos):    # Создание чатсиц и добавление в общий список
        for i in range(8):      # Частиц - 8
            particle = SquareParticle(player_pos, 8, 5, 100, i * (360 / 8))
            self.particles.append(particle)

    def update(self):
        for i in self.particles:
            i.update()

    def draw(self, screen):
        for i in self.particles:
            i.draw(screen)
