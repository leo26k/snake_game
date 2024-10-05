import pygame
from random import randint
from entities import *

# funkcija za sprememebo activnosti skupine gumbov
def change_active(value, buttons):
    for button in buttons:
        button.active = value
# funkcija za sprememebo sigurnosti skupine gumbov
def change_safe(value, buttons):
    for button in buttons:
        button.safe = value
# funkcija za branje nastavitev igre
def get_settings():
    with open('src/settings.json', 'r') as rfile:
        settings = json.load(rfile)
        rfile.close()
    return settings
# funkcija za spreminjanje datoteke nastavitev igre
def write_settings(settings):
    jo = json.dumps(settings, indent=4)
    with open("src/settings.json", "w") as wfile:
        wfile.write(jo)
        wfile.close()

# inicializacija pygame funkcionalnosti
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 816, 704  # velikost zaslona
FPS = 18  # frekvenca igre
clock = pygame.time.Clock()
pygame.display.set_caption('SNAKE')
screen = pygame.display.set_mode((WIDTH, HEIGHT))
# inicijalizacija in nastavljanje igre
speed = 16  # hitrost kace
size = 16  # velikost enega dela kace
settings = get_settings()
game = Game(WIDTH, HEIGHT, speed, size, settings)
change_active(True, 
	[game.play_button, game.settings_button, game.exit_button])
pouse_time = 0
game_status = 'main_menu'
run = True
moved = True
# glavna zamka igre
while run:
    # zamka za sprehod po dogodkih v igri
    for event in pygame.event.get():
        # gumb za zapiranje okna
        if event.type == pygame.QUIT:
            run = False
        # preverjamo dogodke na tipkovnici
        if event.type == pygame.KEYDOWN:
            if game_status == 'active_game':
                if moved:
                    # premik na dol
                    if (event.key == pygame.K_DOWN or event.key == pygame.K_s) and dx != 0:
                        # sprememba smeri kace
                        dx = 0
                        dy = speed
                        # rotcija glave kace
                        body[0].image = pygame.transform.rotate(
                            pygame.transform.scale(game.head_img, (size, size)), 0)
                        moved = False
                    elif (event.key == pygame.K_UP or event.key == pygame.K_w) and dx != 0:
                        dx = 0
                        dy = -speed
                        body[0].image = pygame.transform.rotate(
                            pygame.transform.scale(game.head_img, (size, size)), 180)
                        moved = False
                    elif (event.key == pygame.K_LEFT or event.key == pygame.K_a) and dy != 0:
                        dx = -speed
                        dy = 0
                        body[0].image = pygame.transform.rotate(
                            pygame.transform.scale(game.head_img, (size, size)), -90)
                        moved = False
                    elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and dy != 0:
                        dx = speed
                        dy = 0
                        body[0].image = pygame.transform.rotate(
                            pygame.transform.scale(game.head_img, (size, size)), 90)
                        moved = False

                if event.key == pygame.K_SPACE:  # pauziranje
                    game_status = "pouse_game"
                    change_active(True, [game.home_button])
                    change_safe(False, [game.home_button])
                    pouse_start_time = pygame.time.get_ticks()  # cas pauziranja
                    pygame.mouse.set_visible(True)
            elif game_status == "game_over":
                if event.key == pygame.K_SPACE:  # ponovna igra
                    pygame.mouse.set_visible(False)
                    game.high_score_text = game.font_score.render(
                        f'HIGH SCORE: {game.high_scores[mode]}', True, game.theme['text'])
                    # inicijalizacija nove igre
                    body, obstacles, food, score, dx, dy = game.restart_game(
                        mode)
                    game.score_text = game.font_high_score.render(
                        f"{score}", True, game.theme['text'])
                    food_spawn_time = pygame.time.get_ticks()
                    game_status = 'active_game'
                if event.key == pygame.K_BACKSPACE:  # prehod v prvi meni
                    game_status = 'main_menu'
                    pygame.mouse.set_visible(True)
                    change_active(
                        True, [game.play_button, game.settings_button, game.exit_button])
                    change_safe(False, [game.play_button,
                                game.settings_button, game.exit_button])

            elif game_status == "pouse_game":
                if event.key == pygame.K_SPACE:  # nadaljevanje igre
                    game_status = "active_game"
                    pygame.mouse.set_visible(False)
                    pouse_time += pygame.time.get_ticks()-pouse_start_time
                elif event.key == pygame.K_BACKSPACE:  # prehod v prvi meni
                    game_status = "main_menu"
                    change_active(
                        True, [game.play_button, game.settings_button, game.exit_button])
                    change_safe(False, [game.play_button,
                                game.settings_button, game.exit_button])
    # dogajanja na ekranu odvisno od statusa igre
    if game_status == 'main_menu':
        go = False  # pove ali zapuscamo trnutni status igre
        if game.play_button.clicked():
            if game.settings['sound']:
                game.click_sound.play()
            game_status = 'mode_menu'
            change_active(True, [
                          game.classic_button, game.cage_button, game.blocks_button, game.back_button])
            change_safe(False, [
                        game.classic_button, game.cage_button, game.blocks_button, game.back_button])
            go = True
        if game.settings_button.clicked():
            if game.settings['sound']:
                game.click_sound.play()
                change_active(True, [game.sound_off, game.back_button])
                change_safe(False, [game.sound_off, game.back_button])
            else:
                change_active(True, [game.sound_on, game.back_button])
                change_safe(False, [game.sound_on, game.back_button])
            game_status = 'settings_menu'
            go = True
        if game.exit_button.clicked():
            if game.settings['sound']:
                game.click_sound.play()
            run = False
        if go:
            change_active(False, [game.play_button,
                          game.settings_button, game.exit_button])
        game.main_menu(screen)
    elif game_status == 'mode_menu':
        go = False  # pove ali zapuscamo trnutni status igre
        if game.classic_button.clicked():
            if game.settings['sound']:
                game.click_sound.play()
            mode = 'classic'
            go = True
        if game.cage_button.clicked():
            if game.settings['sound']:
                game.click_sound.play()
            mode = 'cage'
            go = True
        if game.blocks_button.clicked():
            if game.settings['sound']:
                game.click_sound.play()
            mode = 'blocks'
            go = True
        if game.back_button.clicked():
            if game.settings['sound']:
                game.click_sound.play()
            game_status = 'main_menu'
            change_active(False, [game.back_button])
            change_active(
                True, [game.play_button, game.settings_button, game.exit_button])
            change_safe(False, [game.play_button,
                        game.settings_button, game.exit_button])
        if go:
            pygame.mouse.set_visible(False)
            game.high_score_text = game.font_score.render(
                f'HIGH SCORE: {game.high_scores[mode]}', True, game.theme['text'])
            body, obstacles, food, score, dx, dy = game.restart_game(mode)
            game.score_text = game.font_high_score.render(
                f"{score}", True, game.theme['text'])
            food_spawn_time = pygame.time.get_ticks()
            game_status = 'active_game'
            change_active(False, [
                          game.classic_button, game.cage_button, game.blocks_button, game.back_button])
        game.mode_menu(screen)
    elif game_status == 'settings_menu':
        game.settings_menu(screen)

        if game.sound_on.clicked():  # ce je gumb za vklopitev zavoka bil kliknjen
            if game.settings['sound']:
                game.click_sound.play()
            game.settings['sound'] = 1
            write_settings(game.settings)
            change_active(False, [game.sound_on])
            change_active(True, [game.sound_off])
            change_safe(False, [game.sound_off])
        if game.sound_off.clicked():  # ce je gumb za izklopitev zavoka bil kliknjen
            if game.settings['sound']:
                game.click_sound.play()
            game.settings['sound'] = 0
            write_settings(game.settings)
            change_active(False, [game.sound_off])
            change_active(True, [game.sound_on])
            change_safe(False, [game.sound_on])

        if game.back_button.clicked():
            if game.settings['sound']:
                game.click_sound.play()
            game_status = 'main_menu'
            change_active(False, [game.back_button])
            change_active(
                True, [game.play_button, game.settings_button, game.exit_button])
            change_safe(False, [game.play_button,
                        game.settings_button, game.exit_button])
    elif game_status == 'game_over':
        ti = (pygame.time.get_ticks()-death_time)//100
        if game.home_button.clicked():
            if game.settings['sound']:
                game.click_sound.play()
            game_status = 'main_menu'
            change_active(False, [game.home_button])
            change_active(
                True, [game.play_button, game.settings_button, game.exit_button])
            change_safe(False, [game.play_button,
                        game.settings_button, game.exit_button])
        game.game_over(screen, saved_screen, ti)
    elif game_status == 'pouse_game':
        if game.home_button.clicked():
            if game.settings['sound']:
                game.click_sound.play()
            game_status = 'main_menu'
            change_active(False, [game.home_button])
            change_active(
                True, [game.play_button, game.settings_button, game.exit_button])
            change_safe(False, [game.play_button,
                        game.settings_button, game.exit_button])
        game.pouse_game(screen)
    elif game_status == 'active_game':

        game.active_game(screen)
        for part in body[::-1]:  # sprehodimo se po obrnjenem seznamu
            part.draw(screen)
        for obstacle in obstacles:
            obstacle.draw(screen)

        # cas ki je hrana bila na zaslonu
        fti = (pygame.time.get_ticks()-food_spawn_time-pouse_time)//100
        if fti >= 70:  # ce je hrana bila na zaslonu 7 sekund, naredimo novo, pri cemer stara izgine
            food = Food((randint(size, WIDTH-size)//size*size,
                        randint(size+40, HEIGHT-size)//size*size), game.food_img)
            food_spawn_time = pygame.time.get_ticks()
        elif fti > 40:  # ce je hrana na zaslonu vec kot 4 sekunce, utripa vsake pol sekunde
            if fti % 10 < 5:
                food.draw(screen)
        else:
            food.draw(screen)

        # premikamo kaco
        new_dx, new_dy = dx, dy
        for part in body:
            old_dx, old_dy = part.dx, part.dy
            part.dx, part.dy = new_dx, new_dy
            part.move(WIDTH, HEIGHT)  # premik dela kace
            new_dx, new_dy = old_dx, old_dy
        moved = True
        obstacle_rects=[o.rect for o in obstacles]
        # ali se je kaca dotaknila hrane
        if food.rect.colliderect(body[0].rect):
            if game.settings['sound']:
                game.food_sound.play()
            new_part = SnakeBody(
                (part.rect.x-part.dx, part.rect.y-part.dy), new_dx, new_dy, game.body_img, size)
            body.append(new_part)  # dodamo novi del na konec kace
            food = Food((randint(size, WIDTH-size)//size*size, randint(size +
                        40, HEIGHT-size)//size*size), game.food_img)  # nova hrana
            # hrana ne sme biti v oviri
            while food.rect.collideobjects(obstacle_rects):
                food = Food((randint(size, WIDTH-size)//size*size,
                            randint(size+40, HEIGHT-size)//size*size), game.food_img)
            score += 1
            game.score_text = game.font_score.render(
                f"{score}", True, game.theme['text'])
            food_spawn_time = pygame.time.get_ticks()

        # če se je kaca dotaknila ovire ali same sebe
        if body[0].rect.collideobjects(obstacle_rects) or body[0].rect.collideobjects([p.rect for p in body[1:]]):
            if game.settings['sound']:
                game.death_sound.play()
            game_status = 'game_over'
            pygame.mouse.set_visible(True)
            saved_screen = screen.subsurface(
                screen.get_rect()).copy()  # shranimo trnutni zaslon
            # ce je to novi rekord, ga zapisemo
            if score > game.high_scores[mode]:
                game.high_scores[mode] = score
                write_score(score, mode)
            death_time = pygame.time.get_ticks()
            pouse_time = 0
            change_active(True, [game.home_button])
            change_safe(False, [game.home_button])

     # posodobimo zaslon
    #posodobimo zaslon
    pygame.display.update() 
    clock.tick(FPS)

pygame.quit()
