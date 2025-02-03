import pygame
import sys
import sqlite3
from general import Button
from particles import SnowParticlesTogether
from datetime import date
from settings import *

name = player_name


class TimerScreen():    # Класс объекта таймера
    def __init__(self, color, center_pos):
        self.font = pygame.font.Font('data/res/font.ttf', 50)
        self.color = color
        self.pos = center_pos
        self.time = ('', 0)

    def draw(self, screen, time):
        seconds = time // 1000
        minutes = seconds // 60
        hours = minutes // 60
        seconds -= minutes * 60 + hours * 3600
        minutes -= hours * 60
        self.time = (f"{hours}:{minutes}:{seconds:02}", self.time[1] + time)
        text = self.font.render(f"{hours}:{minutes}:{seconds:02}", True, self.color)
        shadow_text = self.font.render(f"{hours}:{minutes}:{seconds:02}", True, (0, 0, 0, 120))
        pos = (self.pos[0] - text.get_width() // 2, self.pos[1] - text.get_height() // 2)
        screen.blit(shadow_text, (pos[0] + 4, pos[1] + 4))
        screen.blit(text, pos)


def add_to_score(player_name, map, score, time, deaths):    # Функция добавления статистики в базу данных
    conn = sqlite3.connect('data/res/scores.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO scores (name, map, score, deaths, time, timeAbs, date)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (player_name, map, score, deaths, time[0], time[1], date.today().strftime("%d.%m.%Y")))
    conn.commit()
    conn.close()


def get_scores():   # Поулчение данных из статистики, для их послеующей отрисовки
    conn = sqlite3.connect('data/res/scores.db')
    cursor = conn.cursor()
    res = cursor.execute('''SELECT name, map, score, time, deaths, date FROM scores
                         ORDER BY score DESC, timeAbs ASC, deaths ASC, map DESC''').fetchall()
    conn.close()
    return res


def return_score_change(screen, score_change):  # Отрисовка изменения очков во время игры
    if score_change > 0:
        score_change = f'+{score_change}'
    font = pygame.font.Font('data/res/font.ttf', 14)
    text = font.render(str(score_change), True, (255, 255, 255))
    shadow_text = font.render(str(score_change), True, (0, 0, 0))
    pos = WIDTH - text.get_width() - 10, 10
    screen.blit(shadow_text, (pos[0] + 4, pos[1] + 4))
    screen.blit(text, pos)


def show_scores(screen, scores):    # Отрисовка статистики в окне самой статистики
    font = pygame.font.Font('data/res/font.ttf', 15)
    text = font.render('TOP 5 | Name | Level | Score | Time | Deaths | Date', True, (255, 255, 255))
    shadow_text = font.render('TOP 5 | Name | Level | Score | Time | Deaths | Date', True, (0, 0, 0))
    pos = (WIDTH / 2 - text.get_width() / 2, 50)
    screen.blit(shadow_text, (pos[0] + 4, pos[1] + 4))
    screen.blit(text, pos)
    font = pygame.font.Font('data/res/font.ttf', 16)
    count = 1
    for i in scores[:5]:
        i = [str(j) for j in i]
        text = font.render(f'{count}    {'    '.join(i)}', True, (255, 255, 255))
        shadow_text = font.render(f'{count}    {'    '.join(i)}', True, (0, 0, 0))
        pos = (WIDTH / 2 - text.get_width() / 2, 80 + (count * (text.get_height() + 24)))
        screen.blit(shadow_text, (pos[0] + 4, pos[1] + 4))
        screen.blit(text, pos)
        screen.fill((255, 255, 255), (pos[0] - 10, pos[1] + text.get_height() + 6, text.get_width() + 10, 6))
        count += 1


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    icon = pygame.image.load('data/res/icon.png')
    pygame.display.set_icon(icon)
    clock = pygame.time.Clock()
    pygame.display.set_caption('Pyleste')
    SnowParticles = SnowParticlesTogether(0.4)
    SnowParticles.add_particles()
    menuBut = Button('exitBut.png', (WIDTH // 2 - 80, HEIGHT - 118))

    conn = sqlite3.connect('data/res/scores.db')
    cursor = conn.cursor()
    # Создание базы данных, если ее нет
    cursor.execute('''CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    map INTEGER NOT NULL,
                    score INTEGER NOT NULL,
                    deaths INTEGER NOT NULL,
                    time TEXT NOT NULL,
                    timeAbs INTEGER NOT NULL,
                    date TEXT NOT NULL )''')
    conn.commit()
    conn.close()
    scores = get_scores()
    running = True
    while running:
        alphascreen = pygame.Surface(screen.get_size(), pygame.SRCALPHA).convert_alpha()    # Создание surface с альфа
        dt = clock.tick(FPS)
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                menuBut.is_clicked(event.pos)
            if event.type == pygame.MOUSEBUTTONUP:
                if menuBut.is_clicked(event.pos):
                    running = False
        SnowParticles.update(dt, 20)
        SnowParticles.draw(alphascreen)
        screen.blit(alphascreen, (0, 0))
        menuBut.draw(screen)
        show_scores(screen, scores)
        pygame.display.flip()


if __name__ == '__main__':
    main()
