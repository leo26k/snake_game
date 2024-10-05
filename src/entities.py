import pygame
from pygame import gfxdraw
import json
from random import randint



class Button():
	def __init__(self, position, scale, image1, image2):
		#main button color 28a196
		#secondary button color 28a196
		height=image1.get_height()
		width=image1.get_width()
		self.position=position
		self.image1=pygame.transform.scale(image1, (int(width*scale), int(height*scale))) # obicna slika
		self.image2=pygame.transform.scale(image2, (int(width*scale), int(height*scale))) # slika ko se miska dotika gumba
		self.rect=self.image1.get_rect()
		self.rect.center=position
		self.active=False #pove ali je gumb v uporabi
		self.safe=False #pove ali je varno klikniti gumb, klub temu da je v uporabi
	def draw(self, screen):

		mouse=pygame.mouse.get_pos() # koordinate miske
		if self.rect.collidepoint(mouse): #ali se miska dotika gumba
			screen.blit(self.image2, (self.rect.x, self.rect.y))
		else:
			screen.blit(self.image1, (self.rect.x, self.rect.y))
	
	def clicked(self):
		clicked=False
		mouse=pygame.mouse.get_pos() #koordinate miske
		# preverimo pogoje za klik gumba
		if self.rect.collidepoint(mouse) and self.active:
			if pygame.mouse.get_pressed()[0]:
				if self.safe:
					clicked=True
					self.active=False
			else:
				self.safe=True	
		return clicked

class SnakeBody(): # del kace
	def __init__(self, position, dx, dy, img, size):
		super().__init__()
		self.image=pygame.transform.scale(img, (size, size))
		self.dx=dx #premik levo/desno
		self.dy=dy #premik gor/dol
		self.rect=self.image.get_rect()
		self.rect.topleft=position
	def move(self, WIDTH, HEIGHT):
		# premik za dx ali dy
		# ce gremo izven zaslona, se premaknemo na drugo stran
		self.rect.x=(self.rect.x+self.dx)%WIDTH
		self.rect.y=(self.rect.y+self.dy)%HEIGHT
	def draw(self, screen):
		screen.blit(self.image, self.rect)

class Food():
	def __init__(self, position, img):
		super().__init__()
		self.image=pygame.transform.scale(img, (16, 16))
		self.rect=self.image.get_rect()
		self.rect.center=position
	
	def draw(self, screen):
		screen.blit(self.image, self.rect)


class Obstacle():
	def __init__(self, position, size):
		self.surface=pygame.Surface(size)
		self.surface.fill("#ffffff")
		self.surface_rect=self.surface.get_rect()
		self.surface_rect.center=position
		self.rect=pygame.Rect(0, 0, size[0]-16, size[1]-16)
		self.rect.center=position

	def draw(self, screen):
		screen.blit(self.surface, self.surface_rect)
	
		


def write_score(score, mode):
		#preberemo podatke
		with open('src/db.json', 'r') as rfile:
			db = json.load(rfile)
			rfile.close()
		db['high_scores'][mode]=score	
		jo=json.dumps(db, indent=4)
		#na novo zapisemo
		with open("src/db.json", "w") as wfile:
			wfile.write(jo)
			wfile.close()

def get_high_scores(): # pridobimo rekorde
	with open('src/db.json', 'r') as rfile:
		db = json.load(rfile)
		rfile.close()
	high_scores=db['high_scores']
	return high_scores


def get_theme(color): # pridobimo temo
	with open('src/themes.json', 'r') as rfile:
		themes = json.load(rfile)
		rfile.close()
	theme=themes[color]
	return theme




class Game():
	def __init__(self, WIDTH, HEIGHT, speed, size, settings):
		self.speed=speed
		self.size=size
		self.WIDTH, self.HEIGHT=WIDTH, HEIGHT
		self.theme=get_theme(settings['color'])
		self.settings=settings
		self.initializeGame()

	

	def restart_game(self, mode):
		size=self.size
		speed=self.speed
		position=[200, 104] #zacetna pozicija kace
		body=[]
		obstacles=[]
		if mode=='blocks':
			for i in range(10): #ustvarimo deset blokov
				while True:
					obstacle_position=(randint(0, self.WIDTH)//size*size, randint(50, self.HEIGHT)//size*size)
					if not 170<obstacle_position[0]<230: # ovira ne sme ovirati zacetne poti kace
						break
				obstacle=Obstacle(obstacle_position, (50, 50))
				obstacles.append(obstacle)
		elif mode=='cage':
			# ustvarimo meje zaslona kot ovire
			top=Obstacle((self.WIDTH//2, -12), (self.WIDTH, 32))
			bottom=Obstacle((self.WIDTH//2, self.HEIGHT+12), (self.WIDTH, 32))
			left=Obstacle((-12, self.HEIGHT//2), (32, self.HEIGHT))
			right=Obstacle((self.WIDTH+12, self.HEIGHT//2), (32, self.HEIGHT))
			obstacles.append(top)
			obstacles.append(bottom)
			obstacles.append(left)
			obstacles.append(right)
		
		# zacetni premik kace
		dx=0
		dy=speed
		score=0

		head=SnakeBody(position, 0, speed, self.head_img, size) # glava kace
		body.append(head)
		for i in range(3):
			position[1]-=size # vsak novi del ustvarimo nad prejsnjim
			p=SnakeBody(position, 0, speed, self.body_img, size)
			body.append(p)
		food=Food((randint(size, self.WIDTH-size)//size*size, randint(size+40, self.HEIGHT-size)//size*size), self.food_img)
		while food.rect.collideobjects([o.rect for o in obstacles]): # hrana ne sme biti v oviri
			food=Food((randint(size, self.WIDTH-size)//size*size, randint(size+40, self.HEIGHT-size)//size*size), self.food_img)

		return body, obstacles, food, score, dx, dy

	def pouse_game(self, screen):	
		# narisemo veliki simbol za pavzo
		gfxdraw.aacircle(screen, self.WIDTH//2, self.HEIGHT//2, 75, (255, 255, 255))
		gfxdraw.filled_circle(screen, self.WIDTH//2, self.HEIGHT//2, 75, (255, 255, 255))
		pygame.draw.rect(screen, self.theme['background'], self.r1, border_radius=10)
		pygame.draw.rect(screen, self.theme['background'], self.r2, border_radius=10)
		self.home_button.draw(screen)

	def active_game(self, screen):
		screen.fill(self.theme['background'])
		screen.blit(self.score_text, self.score_rect)
		screen.blit(self.high_score_text, self.high_score_rect)


	def main_menu(self, screen):
		screen.fill(self.theme['background'])
		# narisemo ozadja gumbov
		self.play_button.draw(screen)
		self.settings_button.draw(screen)
		self.exit_button.draw(screen)
		# narisemo besedila gumbov
		screen.blit(self.play_text, self.play_rect)
		screen.blit(self.settings_text, self.settings_rect)
		screen.blit(self.exit_text, self.exit_rect)
		screen.blit(self.main_title, self.main_title_rect)
		

	def mode_menu(self, screen):
		screen.fill(self.theme['background'])
		# narisemo gumbe
		self.classic_button.draw(screen)
		self.cage_button.draw(screen)
		self.blocks_button.draw(screen)
		self.back_button.draw(screen)
		#narisemo besedila gumbov
		screen.blit(self.claasic_text, self.classic_rect)
		screen.blit(self.cage_text, self.cage_rect)
		screen.blit(self.blocks_text, self.blocks_rect)
		screen.blit(self.modes_title, self.modes_title_rect)

	def game_over(self, screen, saved_screen, ti):
		screen.fill(self.theme['background'])
		# prve tri sekunde kaca in ovire utripata, nato se pojavi besedilo
		if ti//10>=3:
			screen.blit(saved_screen, (0, 0))
			if ti%10<5: #utripanje vsake pol sekunde
				screen.blit(self.ptc_text, self.ptc_rect)
			screen.blit(self.game_over_text, self.game_over_rect2)
		else:
			screen.blit(self.high_score_text, self.high_score_rect)
			screen.blit(self.score_text, self.score_rect)
			if ti%10<5: #utripanje vsake pol sekunde
				screen.blit(saved_screen, (0, 0))
		self.home_button.draw(screen)


	def settings_menu(self, screen):
		screen.fill(self.theme['background'])
		screen.blit(self.settings_title, self.settings_title_rect)
		self.back_button.draw(screen)
		screen.blit(self.sound_text, self.sound_text_rect)
		if self.settings['sound']:
			self.sound_off.draw(screen)
		else:
			self.sound_on.draw(screen)


	def initializeGame(self):
		self.food_img=pygame.image.load(f"images/{self.theme['food']}").convert_alpha()
		self.body_img=pygame.image.load(f"images/{self.theme['body']}").convert_alpha()
		self.head_img=pygame.image.load(f"images/{self.theme['head']}").convert_alpha()
		# pravokotnika na velikem simbolu za pavzo
		self.r1=pygame.Rect(0, 0, 20, 75)
		self.r1.center=(self.WIDTH//2-20, self.HEIGHT//2)
		self.r2=pygame.Rect(0, 0, 20, 75)
		self.r2.center=(self.WIDTH//2+20, self.HEIGHT//2)

		# ustvarjanje vseh gumbov in njihovih besedil -------------------------------------------------
		bbox1=pygame.image.load(f"images/button_box1.png").convert_alpha() # ozadje navadnega gumba
		bbox2=pygame.image.load(f"images/button_box2.png").convert_alpha() # ozadje gumba ki se ga dotikamo
		button_font = pygame.font.Font('fonts/font_1.ttf', 28) # font za besedilo gumbov
		# gumb za izbiro nacinov igre
		self.play_button=Button((self.WIDTH//2, self.HEIGHT//2-60), 0.3, bbox1, bbox2)
		self.play_text=button_font.render('PLAY', True, self.theme['text'])
		self.play_rect=self.play_text.get_rect()
		self.play_rect.center=self.play_button.rect.center
		# gumb za dostop do nastavitev
		self.settings_button=Button((self.WIDTH//2, self.HEIGHT//2+50), 0.3, bbox1, bbox2)
		self.settings_text=button_font.render('SETTINGS', True, self.theme['text'])
		self.settings_rect=self.settings_text.get_rect()
		self.settings_rect.center=self.settings_button.rect.center
		# gumb za zapiranje programa
		self.exit_button=Button((self.WIDTH//2, self.HEIGHT//2+160), 0.3, bbox1, bbox2)
		self.exit_text=button_font.render('EXIT', True, self.theme['text'])
		self.exit_rect=self.exit_text.get_rect()
		self.exit_rect.center=self.exit_button.rect.center
		# gumb za klasicen nacin
		self.classic_button=Button((self.WIDTH//2, self.HEIGHT//2-60), 0.3, bbox1, bbox2)
		self.claasic_text=button_font.render('CLASSIC', True, self.theme['text'])
		self.classic_rect=self.claasic_text.get_rect()
		self.classic_rect.center=self.classic_button.rect.center
		# gumb za nacin z mejami
		self.cage_button=Button((self.WIDTH//2, self.HEIGHT//2+50), 0.3, bbox1, bbox2)
		self.cage_text=button_font.render('CAGE', True, self.theme['text'])
		self.cage_rect=self.cage_text.get_rect()
		self.cage_rect.center=self.cage_button.rect.center
		# gumb za nacin z bloki
		self.blocks_button=Button((self.WIDTH//2, self.HEIGHT//2+160), 0.3, bbox1, bbox2)
		self.blocks_text=button_font.render('BLOCKS', True, self.theme['text'])
		self.blocks_rect=self.blocks_text.get_rect()
		self.blocks_rect.center=self.blocks_button.rect.center
		#gumb za vrnitev na prvi meni
		home_1=pygame.image.load(f"images/home.png").convert_alpha()	
		home_2=pygame.image.load(f"images/home2.png").convert_alpha()	
		self.home_button=Button((self.WIDTH-35, 25), 0.062, home_1, home_2)
		#gumb za vrnitev na prejsnji meni
		back_1=pygame.image.load(f"images/back.png").convert_alpha()	
		back_2=pygame.image.load(f"images/back2.png").convert_alpha()	
		self.back_button=Button((50, self.HEIGHT-50), 0.122, back_1, back_2)
		# besedila ob koncu igre --------------------------------------------
		font_game_over = pygame.font.Font('fonts/font_1.ttf', 50)
		self.game_over_text=font_game_over.render('GAME OVER', True, self.theme['text'])
		self.game_over_rect2=self.game_over_text.get_rect()
		self.game_over_rect2.center=(self.WIDTH//2, self.HEIGHT//2)
		#
		font_ptc = pygame.font.Font('fonts/font_1.ttf', 20)
		self.ptc_text=font_ptc.render('PRESS SPACE TO PLAY AGAIN', True, self.theme['text'])
		self.ptc_rect=self.ptc_text.get_rect()
		self.ptc_rect.center=(self.WIDTH//2, self.HEIGHT//2+100)
		# besedila za rekorde ------------------------------------------------------
		self.font_score = pygame.font.Font('fonts/font_1.ttf', 22)
		self.score_text = self.font_score.render("0", True, self.theme['text'])
		self.score_rect = self.score_text.get_rect()
		self.score_rect.center=(self.WIDTH//2, 20)		
		#
		self.font_high_score = pygame.font.Font('fonts/font_1.ttf', 22)
		self.high_scores=get_high_scores()
		self.high_score_text=self.font_high_score.render('HIGH SCORE: 0', True, self.theme['text'])
		self.high_score_rect=self.high_score_text.get_rect()
		self.high_score_rect.center=(100, 20)
		#naslovi menijev --------------------------------------------------------
		font_title = pygame.font.Font('fonts/font_1.ttf', 40)
		#
		self.main_title = font_title.render("MAIN MENU", True, self.theme['text'])
		self.main_title_rect = self.main_title.get_rect()
		self.main_title_rect.center=(self.WIDTH//2, 50)	
		#
		self.modes_title = font_title.render("MODES", True, self.theme['text'])
		self.modes_title_rect = self.modes_title.get_rect()
		self.modes_title_rect.center=(self.WIDTH//2, 50)	
		#
		self.settings_title = font_title.render("settings", True, self.theme['text'])
		self.settings_title_rect = self.settings_title.get_rect()
		self.settings_title_rect.center=(self.WIDTH//2, 50)	
		# meni za nastavitve ----------------------------------------------------
		font_sound=pygame.font.Font('fonts/font_1.ttf', 20)
		self.sound_text = font_sound.render("SOUND", True, self.theme['text'])
		self.sound_text_rect = self.sound_text.get_rect()
		self.sound_text_rect.center=(self.WIDTH//4, 200)
		# gumb za vklopitev zvoka
		unticked_1=pygame.image.load(f"images/{self.theme['tick'][0]}").convert_alpha()
		unticked_2=pygame.image.load(f"images/{self.theme['tick'][1]}").convert_alpha()
		self.sound_on=Button((self.WIDTH//2, 200), 0.04, unticked_1, unticked_2)
		# gumb za izklopitev zvoka
		ticked_1=pygame.image.load(f"images/{self.theme['tick'][2]}").convert_alpha()
		ticked_2=pygame.image.load(f"images/{self.theme['tick'][3]}").convert_alpha()
		self.sound_off=Button((self.WIDTH//2, 200), 0.04, ticked_1, ticked_2)	
		# zvoki ------------------------------------------------------------
		self.death_sound=pygame.mixer.Sound("sounds/snake_death.ogg")
		self.food_sound=pygame.mixer.Sound("sounds/food_sound.ogg")
		self.click_sound=pygame.mixer.Sound("sounds/button_click.ogg")


		


		
		
		
		
