import pygame
import random
import os

# 設置每秒幀數
FPS = 100

#顏色參數
WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,0,0)
YELLOW = (255,255,0)
BLACK = (0,0,0)

#視窗高低
WIDTH = 500
HEIGHT = 700

#初始化
pygame.init()

#遊戲視窗
screen = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("first game")
font = pygame.font.Font(None,36)

#載入圖片
image_folder = r"C:\Users\a0974\OneDrive\桌面\pygame\圖片"

bullet_img = pygame.image.load(os.path.join(image_folder, "bullets.png")).convert()
background_img = pygame.image.load(os.path.join(image_folder, "background.png")).convert()
player_img = pygame.image.load(os.path.join(image_folder, "player.png")).convert()
player_mini_img = pygame.transform.scale(player_img,(45,38))
player_mini_img.set_colorkey(BLACK)
pygame.display.set_icon(player_mini_img)
rock_imgs = []
for i in range(4):
    rock_imgs.append(pygame.image.load(os.path.join(image_folder, f"rock{i}.png")).convert())

#爆炸動畫
expl_anim = {"lg": [], "sm": [], "player" : []}
for i in range(9):
    expl_img = pygame.image.load(os.path.join(image_folder, f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim["lg"].append(pygame.transform.scale(expl_img, (75, 75)))
    expl_anim["sm"].append(pygame.transform.scale(expl_img, (30, 30)))

    player_expl_img = pygame.image.load(os.path.join(image_folder, f"player_expl{i}.png")).convert()
    player_expl_img.set_colorkey(BLACK)
    expl_anim["player"].append(pygame.transform.scale(player_expl_img, (100, 100)))

#道具圖片
power_imgs = {"shield": [], "gun": []}
power_imgs['shield'] = pygame.image.load(os.path.join(image_folder, "shield.png")).convert()
power_imgs['gun'] = pygame.image.load(os.path.join(image_folder, "gun.png")).convert()

#顯示文字
def draw_text(surf, text, size, x, y):
    font_path = r"C:\Windows\Fonts\msjh.ttc"
    font = pygame.font.Font(font_path, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surf.blit(text_surface, text_rect)

#增加新石頭
def now_rock():
    r = Rock()
    all_sprites.add(r)
    rocks.add(r)
    
#顯示血量
def draw_health(surf,hp,x,y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    fill = (hp/100)*BAR_LENGTH
    outline_rect = pygame.Rect(x,y,BAR_LENGTH,BAR_HEIGHT)
    fill_rect = pygame.Rect(x,y,fill,BAR_HEIGHT)
    pygame.draw.rect(surf,GREEN,fill_rect)
    pygame.draw.rect(surf,WHITE,outline_rect,2)

#顯示生命數
def draw_lives(surf,lives,img,x,y):
    for i in range(lives) : 
        img_rect = img.get_rect()
        img_rect.x = x-35 + 45*i
        img_rect.y = y
        surf.blit(img,img_rect)

#初始畫面
def draw_init():
    screen.blit(background_img,(0,0))
    draw_text(screen,'太空戰機',80,WIDTH/2,HEIGHT/4)
    draw_text(screen,'<-->控制方向,空白艦發射子彈',30,WIDTH/2,HEIGHT/2)
    draw_text(screen,'按任意鍵開始',40,WIDTH/2,HEIGHT*3/4)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:
                waiting = False
                return False

                
#玩家類別
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = player_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 30

        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT
        self.health = 100 #玩家血量
        self.lives = 3 #生命數
        self.hidden = False #死亡後隱藏
        self.hide_time = 0 #死亡持續時間

        self.gun = 1 #武器等級
        self.gun_time = 0 #等級持續時間



    def update(self):
        now = pygame.time.get_ticks() #取得現在時間
        if self.gun > 1 and now - self.gun_time > 5000: #武器升級持續五秒
            self.gun -= 1
            self.gun_time = now

        if  self.hidden and now - self.hide_time > 1000: #死亡隱藏持續一秒
            self.hidden = False
            self.rect.centerx = WIDTH/2
            self.rect.bottom = HEIGHT 

        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_RIGHT]: #右移
            self.rect.x += 10
        if key_pressed[pygame.K_LEFT]:#左移
            self.rect.x -= 10
 
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    #射擊
    def shoot(self):
        if not(self.hidden):
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx,self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
            elif self.gun >= 2:
                bullet1 = Bullet(self.rect.left,self.rect.centery)
                bullet2 = Bullet(self.rect.right,self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)

    #死亡後隱藏
    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2,HEIGHT+500)

    #武器升級
    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()

#石頭類別
class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_ori = random.choice(rock_imgs)
        self.image_ori.set_colorkey(BLACK)
        self.image = self.image_ori.copy()
        self.rect = self.image.get_rect()
        self.radius = 15
        self.rect.x = random.randrange(0,WIDTH - self.rect.width)
        self.rect.y = random.randrange(-180,-100)
        self.speedx = random.randrange(-1,2)
        self.speedy = random.randrange(1,5)
        self.total_degree = 0
        self.rot_degree = 3

    #旋轉
    def rotate(self):
        self.total_degree += self.rot_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_ori,self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
       self.rotate()
       self.rect.y += self.speedy
       self.rect.x += self.speedx
       if self.rect.top > HEIGHT:
            self.rect.x = random.randrange(0,WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100,-40)
            self.speedy = random.randrange(9,10)

#子彈類別
class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speedy = -10


    def update(self):
       self.rect.y += self.speedy
       if self.rect.bottom < 0:
           self.kill()

#爆炸類別
class Explosion(pygame.sprite.Sprite):
    def __init__(self,center,size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50


    def update(self):
       now = pygame.time.get_ticks()
       if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center

#道具類別
class Power(pygame.sprite.Sprite):
    def __init__(self,center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield','gun'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3


    def update(self):
       self.rect.y += self.speedy
       if self.rect.top > HEIGHT:
           self.kill()             
               

show_init = True #是否進入初始畫面
running = True
while running:
    if show_init:
        close = draw_init()
        if close:
            break
        show_init = False
        all_sprites = pygame.sprite.Group()
        cals = pygame.sprite.Group()
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powers = pygame.sprite.Group()

        player = Player()
        all_sprites.add(player)
        for i in range(8):
            now_rock()

        score = 0

    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()


    all_sprites.update()
    hits = pygame.sprite.spritecollide(player,rocks,True,pygame.sprite.collide_circle) # 回傳碰撞數量
    for hit in hits:
        player.health -= hit.radius*2
        now_rock()
        expl = Explosion(hit.rect.center,'sm')
        all_sprites.add(expl)
        if player.health <= 0:
            die = Explosion(player.rect.center,'player')
            all_sprites.add(die)
            player.lives -= 1
            player.health = 100
            player.hide()
           

    
    out = pygame.sprite.groupcollide(rocks,bullets,True,True) 
    for i in out:
        score += i.radius
        now_rock()
        expl = Explosion(i.rect.center,'lg')
        all_sprites.add(expl)
        if random.random() > 0.9: #回傳 0 - 1
            pow = Power(i.rect.center)
            all_sprites.add(pow)
            powers.add(pow)

    hits = pygame.sprite.spritecollide(player,powers,True) # 回傳數量
    for hit in hits:
        if hit.type == 'shield':
            player.health += 20
            if player.health > 100:
                player.health = 100
        elif hit.type == 'gun':
            player.gunup()


    if player.lives == 0:
        show_init = True

    screen.fill(BLACK)
    screen.blit(background_img,(0,0))
    all_sprites.draw(screen)
    draw_text(screen,str(score),18,WIDTH/2,10)
    draw_health(screen,player.health,5,18)
    draw_lives(screen,player.lives,player_mini_img,WIDTH-100,15)
    pygame.display.update()

pygame.quit()
