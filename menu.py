import pygame
from settings import *
from general import Button, FadeAnim
from main import reloadMap, main as Game
from score import main as Score
from particles import SnowParticlesTogether

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)


def main():     # Главное меню игры
    clock = pygame.time.Clock()
    pygame.display.set_caption('Pyleste')
    icon = pygame.image.load('data/res/icon.png')
    pygame.display.set_icon(icon)
    map = reloadMap('main_menu.tmx', player=False)
    map = map[0]
    SnowParticles = SnowParticlesTogether(0.4)
    SnowParticles.add_particles()
    playBut = Button('playBut.png', (176, 352))
    scoreBut = Button('scoreBut.png', (384, 32))
    running = True
    animate = False
    timer_start_time = pygame.time.get_ticks()
    dt = 0
    pygame.mixer.music.load(f"data/res/sounds/{'backgroundMusic.wav'}")     # Основной саундтрек
    pygame.mixer.music.play(-1)
    while running:
        current_time = pygame.time.get_ticks()
        if animate and current_time - timer_start_time > 2000:      # Анимация перехода из меню в игру
            current_time = 0
            animate = False
            Game()
        alphascreen = pygame.Surface(screen.get_size(), pygame.SRCALPHA).convert_alpha()    # Создания surface с альфа
        for event in pygame.event.get():    # Обработка событий
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and not animate:
                playBut.is_clicked(event.pos)
                scoreBut.is_clicked(event.pos)
            if event.type == pygame.MOUSEBUTTONUP and not animate:
                if playBut.is_clicked(event.pos):
                    timer_start_time = current_time
                    animate = True
                if scoreBut.is_clicked(event.pos):
                    Score()
        screen.fill((0, 0, 0))
        map.render(screen)
        SnowParticles.update(dt, 20)
        SnowParticles.draw(alphascreen)
        screen.blit(alphascreen, (0, 0))
        playBut.draw(screen)
        scoreBut.draw(screen)
        if animate:     # Анимация затухания
            FadeAnim(screen, current_time - timer_start_time, False)
        dt = clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
