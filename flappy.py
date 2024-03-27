import pygame
from pygame.locals import *
import random 

pygame.init()

Clock = pygame.time.Clock()
fps = 60

#SCREEN 
screen_width = 400
screen_height = 700

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Bird")

# Font
font = pygame.font.SysFont('monospaced', 60)

# Colour
white = (255, 255, 255)


# Define Game Varibales
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_freuqncy = 1500 #mil
last_pipe = pygame.time.get_ticks() - pipe_freuqncy
score = 0
trigger = False
scoring_points = pygame.mixer.Sound("D:/audio/Mobile - Flappy Bird - Sound Effects/Everything/sfx_point.wav")
flappy_whoosh = pygame.mixer.Sound("D:/audio/woosh.mp3")
flappy_hit = pygame.mixer.Sound("D:/audio/Mobile - Flappy Bird - Sound Effects/Everything/sfx_hit.wav")

#BACKGROUND IMG
bg = pygame.image.load('D:/img/bg.png')
ground = pygame.image.load('D:/img/ground.png')
button_img = pygame.image.load('D:/img/restart.png')


def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def rest_game():
	pipe_group.empty()
	flappy.rect.x = 100
	flappy.rect.y = int(screen_height / 2)
	score = 0
	return score

class Bird(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		self.index = 0
		self.counter = 0
		for num in range(1, 4):
			img = pygame.image.load(f'D:/img/bird{num}.png')
			self.images.append(img)
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.vel = 0 
		self.clicked = False

	def update(self):

		if flying == True:
			#gravity
			self.vel += 0.5
			if self.vel > 8:
				self.vel = 8
			if self.rect.bottom < 768:
				self.rect.y += int(self.vel)

		if game_over == False:
			#jump
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				self.vel = -10
				flappy_whoosh.play() 
			if pygame.mouse.get_pressed()[0] == 0:
				self.clicked = False

			#handle the animation
			self.counter += 1
			flap_cooldown = 5

			if self.counter > flap_cooldown:
				self.counter = 0
				self.index += 1
				if self.index >= len(self.images):
					self.index = 0
			self.image = self.images[self.index]

			#rotate the bird
			self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
		else:
			self.image = pygame.transform.rotate(self.images[self.index], -90)	

class Pipe(pygame.sprite.Sprite):
	def __init__(self, x, y, position):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('D:/img/pipe_files/pipe.png')
		self.rect = self.image.get_rect()
		#position 1 is from the top, -1 is from the bottom
		if position == 1:
			self.image = pygame.transform.flip(self.image, False, True)
			self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
		if position == -1:
			self.rect.topleft = [x, y + int(pipe_gap / 2)]

	def update(self):
		self.rect.x -= scroll_speed
		if self.rect.right < 0:
			self.kill()


class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
	def draw(self):

		action = False

		#get mouse postion
		pos = pygame.mouse.get_pos()

		# Check if mouse is over the button
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1:
				action = True

		# draw the button
		screen.blit(self.image, (self.rect.x, self.rect.y))

		return action									

bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))

bird_group.add(flappy)
 
#restart button
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)


# GAME LOOP
run = True
while run:

	Clock.tick(fps)

	#draw background
	screen.blit(bg, (0,0))
	
	#Drawing stuff	
	bird_group.draw(screen)
	bird_group.update()
	pipe_group.draw(screen)

	#draw the ground
	screen.blit(ground, (ground_scroll, 590))

	#Check the score
	if len(pipe_group ) > 0:
		if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
		   and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
		   and trigger == False:
			trigger = True
		if trigger == True:
			if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
				score += 1
				trigger = False
				scoring_points.play()

	draw_text(str(score), font, white, int(screen_width / 2), 20)		

    # collison
	if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
		game_over = True
	# Check if flappy has fall to the ground
	if flappy.rect.bottom >= 590:
		game_over = True
		flying = False

	if game_over == False and flying == True:
		
		#genrating new pipes
		time_now = pygame.time.get_ticks()
		if time_now - last_pipe > pipe_freuqncy:
			pipe_random = random.randint(-100,100)
			btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_random, -1)
			top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_random, 1)
			pipe_group.add(btm_pipe)
			pipe_group.add(top_pipe)
			last_pipe = time_now

		#Draw and scroll the ground
		ground_scroll -= scroll_speed
		if abs(ground_scroll) > 35:
			ground_scroll = 0
		pipe_group.update()

	#check for game over and reset
	if game_over == True:
		if button.draw() == True:
			game_over = False
			score = rest_game()

    # Event Handler
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.MOUSEBUTTONDOWN and flying == False and flying == False and game_over == False:
			flying = True
			if flappy .rect.bottom < screen_height/2:
				game_over = True

	pygame.display.update()

pygame.quit()