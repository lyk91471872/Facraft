import pygame, random, math, sys, sqlite3


# Classes
class Bullet():
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
            self.rect.y = y+40-self.image.get_height()/2
        else:
            self.rect.x -= self.dx
            self.rect.y -= 20

class Enemy:
    def __init__(self, type='byg', hp=2, dx=99999, dy=3, x=-1, y=-100, score=1):
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
        self.rect.y = y
        self.existence = True
        self.mask = pygame.mask.from_surface(self.image)

    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

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

class Player_targeting_bullet(Enemy):
    def move(self):
        x, y = pygame.mouse.get_pos()
        dx = x - self.rect.x
        if dx>10: dx = 10
        if dx<-10: dx = -10
        self.dx = dx
        self.rect.x += self.dx
        self.rect.y += self.dy

class Boss(Enemy):
    def move(self):
        if self.timer<0:
            if self.timer<-3:
                self.rect.y += 20
            elif self.timer==-3:
                self.rect.y += 15
            elif self.timer==-2:
                self.rect.y += 10
            elif self.timer==-1:
                self.rect.y += 5
            self.timer += 1
        else:
            self.rect.x = math.sin(self.timer) * 500 + 600
            self.rect.y = math.sin(2 * self.timer) * 100 + 170
            self.timer += 0.05


# Preparation
player = input('Enter player name: ')
fps = int(input('Enter fps: '))

# create a new pygame window
pygame.init()
screen = pygame.display.set_mode((1280, 800), 0, 0)
pygame.display.set_caption('Facraft')

# load images
background = pygame.image.load('bg.png').convert()
dlg_drinking_image = pygame.image.load('dlg_drinking.png').convert_alpha()
dlg_image = pygame.image.load('dlg.png').convert_alpha()

# initialize variables to manage states
bullet_timer = 0
enemy_timer = 0
bullets = []
enemies = []
boss = False
game_over = False
victory = False
paused = False
ccps_counter = 0
special_attack = False
bullet_type = 'a'
bullet_dmg = 1
bullet_pattern = 1
score = 0

# determine fps
clock = pygame.time.Clock()
#if len(sys.argv)==1:
#    fps = 20
#else:
#    fps = int(sys.argv[1])

# set player
fa = pygame.sprite.Sprite()
fa.image = pygame.image.load('fa.png').convert_alpha()
fa.shoot_image = pygame.image.load('fa_shoot.png').convert_alpha()
fa.rect = fa.image.get_rect()


# main loop
while True:
    clock.tick(fps)

    # determine whether to restart/quit
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif (game_over or victory) and event.type==pygame.MOUSEBUTTONUP:
            game_over = False
            victory = False
            enemies = []
            bullets = []
            ccps_counter = 0
            special_attack = False
            if boss:
                del dlg
                boss = False
            score = 0
            bullet_type = 'a'
            bullet_dmg = 1
            bullet_pattern = 1
        elif not(game_over or victory) and event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:
                paused = not(paused)
            elif event.key==pygame.K_EQUALS:
                bullet_type = 'b'
                bullet_pattern = 2
                bullet_dmg = 2
                score = 90

    # level up
    if score>=20 and score<25:
        bullet_pattern = 2
    if score>=85 and score<90:
        bullet_type = 'b'
        bullet_dmg = 2

    if paused: continue

    screen.blit(background, (0,0))

    # show score
    score_font = pygame.font.Font('Arial.ttf', 32)
    score_label = score_font.render('score: '+str(score), True, (255, 255, 255))
    screen.blit(score_label, (20, 20))

    if game_over:
        game_over_label = pygame.image.load('game_over.png').convert_alpha()
        screen.blit(game_over_label, (260, 307))
        pygame.display.update()
        continue

    if boss==True and dlg.hp<=0:
        if not(victory):
            conn = sqlite3.connect('records.db')
            cursor = conn.cursor()
            cursor.execute('create table if not exists records(player text, fps int, score int)')
            cursor.execute('insert into records(player, fps, score) values(\'' + player + '\', ' + str(fps) + ', ' + str(score) +')')
            conn.commit()
            conn.close()
            victory = True
            bullets = []
            enemies = []
        victory_font = pygame.font.Font('Arial.ttf', 200)
        victory_label = victory_font.render('Victory!', True, (0, 0, 0))
        screen.blit(victory_label, (260, 307))
        pygame.display.update()
        continue

    # update player position
    x, y = pygame.mouse.get_pos()
    fa.rect.x = x - 50
    fa.rect.y = y - 66
    if bullet_timer>=6 or bullet_timer==0:
        screen.blit(fa.shoot_image, (fa.rect.x, fa.rect.y))
    else:
        screen.blit(fa.image, (fa.rect.x, fa.rect.y))

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

    # summon boss
    if score>=100 and score<200:
        if boss==False and enemies==[]:
            boss = True
            dlg = Boss(type='dlg', hp=1000, dx=0, dy=0, x=600, score=100)
            dlg.timer = -15
            enemies.append(dlg)
            enemy_timer = 0

    # summon enemies
    enemy_timer += 1
    if enemy_timer==20:
        enemy_timer = 0
        if score<35:
            enemies.append(Enemy())
            enemies.append(Enemy())
        if score>=35 and score<100:
            enemies.append(Enemy())
            enemies.append(Enemy(dy=10))
            enemies.append(Player_targeting_enemy(score=2))
            enemies.append(Player_targeting_enemy(score=2))
        if score>=100 and score<200 and type(enemies[0])==Boss:
            if special_attack==False:
                enemies.append(Player_targeting_bullet(type='knife', hp=1, dx=0, dy=15, x=dlg.rect.x, y=dlg.rect.y, score=0))
            else:
                special_attack = False
                dlg.image = dlg_image
                enemies.append(Player_targeting_bullet(type='knife', hp=1, dx=0, dy=5, x=dlg.rect.x, y=dlg.rect.y, score=0))
                enemies.append(Player_targeting_bullet(type='knife', hp=1, dx=0, dy=10, x=dlg.rect.x, y=dlg.rect.y, score=0))
                enemies.append(Player_targeting_bullet(type='knife', hp=1, dx=0, dy=15, x=dlg.rect.x, y=dlg.rect.y, score=0))

    # update bullets' positions
    i = len(bullets) - 1
    while i>=0:
        bullets[i].move()
        if bullets[i].rect.y<-100 or bullets[i].rect.x<-100 or bullets[i].rect.x>1540:
            del bullets[i]
        else:
            screen.blit(bullets[i].image, (bullets[i].rect.x, bullets[i].rect.y))
        i -= 1

    # update enemies' positions
    i = len(enemies) - 1
    while i>=0:
        if type(enemies[i])==Boss:
            if ccps_counter==20:
                ccps_counter = 0
                dlg.image = dlg_drinking_image
                special_attack = True
                score += 10
                dlg.hp -= 100
        enemies[i].move()
        if enemies[i].rect.y>900 or enemies[i].rect.x<-100 or enemies[i].rect.x>1540:
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
            conn = sqlite3.connect('records.db')
            cursor = conn.cursor()
            cursor.execute('create table if not exists records(player text, fps int, score int)')
            cursor.execute('insert into records(player, fps, score) values(\'' + player + '\', ' + str(fps) + ', ' + str(score) +')')
            conn.commit()
            conn.close()
            break
        if type(enemies[i])==Player_targeting_bullet:
            i -= 1
            continue
        j = len(bullets) - 1
        while j>=0:
            if pygame.sprite.collide_mask(enemies[i], bullets[j])!=None:
                enemies[i].hp -= bullets[j].dmg
                if type(enemies[i])==Boss:
                    ccps_counter += bullets[j].dmg
                del bullets[j]
                if enemies[i].hp<=0:
                    score += enemies[i].score
                    del enemies[i]
                    break
            j -= 1
        i -= 1

    pygame.display.update()

