import pygame, random
from sys import exit

class Bullet(pygame.sprite.Sprite):
	def __init__(self, type='a', dmg=1, dx=0):
		self.image = pygame.image.load(type+'.png').convert_alpha()
		self.dmg = dmg
		self.dx = dx
		self.existence = True
		self.rect = self.image.get_rect()
		self.rect.x = 0
		self.rect.y = 1000
		self.mask = pygame.mask.from_surface(self.image)

	def move(self):
		if self.rect.x==0 and self.rect.y==1000:
			x, y  = pygame.mouse.get_pos()
			self.rect.x = x-self.image.get_width()/2
			self.rect.y = y-self.image.get_height()/2

		else:
			self.rect.x -= self.dx
			self.rect.y -= 20
		if self.rect.y<-100 or self.rect.x<-100 or self.rect.x>1540:
			self.existence = False

class Enemy:
	def __init__(self, type='byg', hp=2, dx=99999, dy=3, x=-1, score=1):
		self.image = pygame.image.load(type+'.png').convert_alpha()
		self.hp = hp
		self.score = score
		if dx==99999:
			self.dx = (random.random() - 0.5) * 7
		else:
			self.dx = dx
		self.dy = dy
		self.rect = self.image.get_rect()
		if x==-1:
			self.rect.x = random.random() * 1350
		else:
			self.rect.x = x
		self.rect.y = -100
		self.existence = True
		self.mask = pygame.mask.from_surface(self.image)

	def move(self):
		self.rect.x += self.dx
		self.rect.y += self.dy
		if self.rect.y>1540 or self.rect.x<-100 or self.rect.x>1540:
			self.existence = False

class Player_targeting_enemy(Enemy):
	def move(self):
		x, y = pygame.mouse.get_pos()
		dx = x - self.rect.x
		if dx>4: dx = 4
		if dx<-4: dx = -4
		self.dx = dx
		dy = y - self.rect.y
		if dy>8: dy = 8
		if dy<-8: dy = -8
		self.dy = dy
		self.rect.x += self.dx
		self.rect.y += self.dy
		if self.rect.y>1540 or self.rect.x<-100 or self.rect.x>1540:
			self.existence = False

pygame.init()
screen = pygame.display.set_mode((1280, 800), 0, 0)
pygame.display.set_caption('Facraft')
background = pygame.image.load('bg.png').convert()
bullet_timer = 0
enemy_timer = 0
bullets = []
enemies = []
game_over = False
bullet_type = 'a'
bullet_dmg = 1
bullet_pattern = 1
score = 0

fa = pygame.sprite.Sprite()
fa.image = pygame.image.load('fa.png').convert_alpha()
fa.rect = fa.image.get_rect()

# main loop
while True:

	# determine whether to restart/quit
	for event in pygame.event.get():
		if event.type==pygame.QUIT:
			pygame.quit()
			exit()
		elif game_over and event.type==pygame.MOUSEBUTTONUP:
			game_over = False
			score = 0
			bullet_type = 'a'
			bullet_dmg = 1
			bullet_pattern = 1

	screen.blit(background, (0,0))

	score_font = pygame.font.Font('Arial.ttf', 32)
	score_label = score_font.render('score: '+str(score), True, (255, 255, 255))
	screen.blit(score_label, (20, 20))

	if game_over:
		game_over_label = pygame.image.load('game_over.png').convert_alpha()
		screen.blit(game_over_label, (260, 307))
		pygame.display.update()
		continue
	
	# update player position
	x, y = pygame.mouse.get_pos()
	fa.rect.x = x - 50
	fa.rect.y = y - 66
	screen.blit(fa.image, (fa.rect.x, fa.rect.y))

	# level up
	if score==25:
		bullet_pattern = 2
	if score==85:
		bullet_type = 'b'
		bullet_dmg = 2

	# shoot bullets
	bullet_timer += 1
	if bullet_timer==8:
		bullet_timer = 0
		if bullet_pattern==1:
			bullets.append(Bullet(type=bullet_type, dmg=bullet_dmg))
		if bullet_pattern==2:
			bullets.append(Bullet(type=bullet_type, dmg=bullet_dmg, dx=10))
			bullets.append(Bullet(type=bullet_type, dmg=bullet_dmg, dx=0))
			bullets.append(Bullet(type=bullet_type, dmg=bullet_dmg, dx=-10))

	# spawn enemies
	enemy_timer += 1
	if enemy_timer==20:
		enemy_timer = 0
		enemies.append(Enemy())
		enemies.append(Enemy())
		if score>=40:
			enemies.append(Enemy(dy=10))
			enemies.append(Player_targeting_enemy(score=2))

	# update bullets' positions
	i = len(bullets) - 1
	while i>=0:
		bullets[i].move()
		if bullets[i].existence==False:
			del bullets[i]
		else:
			screen.blit(bullets[i].image, (bullets[i].rect.x, bullets[i].rect.y))
		i -= 1

	# update enemies' positions
	i = len(enemies) - 1
	while i>=0:
		enemies[i].move()
		if enemies[i].existence==False:
			del enemies[i]
		else:
			screen.blit(enemies[i].image, (enemies[i].rect.x, enemies[i].rect.y))
		i -= 1

	# detect collisions
	i = len(enemies) - 1
	while i>=0:
		if pygame.sprite.collide_mask(enemies[i], fa)!=None:
			game_over = True
			bullets = []
			enemies = []
			break
		j = len(bullets) - 1
		while j>=0:
			if pygame.sprite.collide_mask(enemies[i], bullets[j])!=None:
				enemies[i].hp -= bullets[j].dmg
				del bullets[j]
				if enemies[i].hp<=0:
					score += enemies[i].score
					del enemies[i]
					break
			j -= 1
		i -= 1

	pygame.display.update()

