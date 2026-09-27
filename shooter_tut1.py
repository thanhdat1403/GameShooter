import pygame
from pygame import mixer
import os
import random
import csv
import button

mixer.init()

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

#Đặt tốc độ khung hình
clock = pygame.time.Clock()
FPS = 60

# Xác định các biến trò chơi
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False


# Định nghĩa các biến hành động của người chơi
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_throw = False

# Tải nhạc và âm thanh
pygame.mixer.music.load('Shooter-main/Shooter-main/audio/music2.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fix = pygame.mixer.Sound('Shooter-main/Shooter-main/audio/jump.wav')
jump_fix.set_volume(0.5)
shot_fix = pygame.mixer.Sound('Shooter-main/Shooter-main/audio/shot.wav')
shot_fix.set_volume(0.5)
grenade_fix = pygame.mixer.Sound('Shooter-main/Shooter-main/audio/grenade.wav')
grenade_fix.set_volume(0.5)


# Tải hình ảnh
# Hình ảnh nút
start_img = pygame.image.load('Shooter-main/Shooter-main/img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('Shooter-main/Shooter-main/img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('Shooter-main/Shooter-main/img/restart_btn.png').convert_alpha()
#background
pine1_img = pygame.image.load('Shooter-main/Shooter-main/img/background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('Shooter-main/Shooter-main/img/background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('Shooter-main/Shooter-main/img/background/mountain.png').convert_alpha()
sky_img = pygame.image.load('Shooter-main/Shooter-main/img/background/sky_cloud.png').convert_alpha()

#lưu trữ các ô trong danh sách
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'Shooter-main/Shooter-main/img/Tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

# viên đạn
bullet_img = pygame.image.load('Shooter-main/Shooter-main/img/icons/bullet.png').convert_alpha()
#lựu đạn
grenade_img = pygame.image.load('Shooter-main/Shooter-main/img/icons/grenade.png').convert_alpha()

#Load ảnh mìn
mine_img = pygame.image.load('Shooter-main/Shooter-main/img/icons/dynamite_8278347.png').convert_alpha()
mine_img = pygame.transform.scale(mine_img,(20,20))

# Load hiệu ứng nổ mìn
explosion_mine_image = []
for file in sorted(os.listdir('Shooter-main/Shooter-main/img/explosion_mine')):
    img = pygame.image.load(f'Shooter-main/Shooter-main/img/explosion_mine/{file}').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE * 2, TILE_SIZE * 2))
    explosion_mine_image.append(img)

#nhận hộp
health_box_img = pygame.image.load('Shooter-main/Shooter-main/img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('Shooter-main/Shooter-main/img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('Shooter-main/Shooter-main/img/icons/grenade_box.png').convert_alpha()
item_boxes = {
    'Health'   : health_box_img,
    'Ammo'     : ammo_box_img,
    'Grenade'  : grenade_box_img
}

# Xác định màu sắc
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)
#xác định phông chữ
font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#Hàm vẽ backgroud
def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))

# Hàm để đặt lại cấp độ
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    #tạo danh sách ô trống
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data

# Define Soldier class(lớp tạo lính)
class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed # tốc độ
        self.ammo = ammo #đạn
        self.start_ammo = ammo #đạn
        self.shoot_cooldown = 0 #thời gian hồi chiêu or hồi đạn
        self.grenades = grenades # lựu đạn
        self.mines = 3 # giới hạn mìn ban đầu vào game
        self.health = 100 #sự sống
        self.max_health = self.health # sự sống tối đa
        self.direction = 1 # phương hướng
        self.vel_y = 0
        self.jump = False # nhảy
        self.in_air = True
        self.flip = False
        self.animation_list = [] # List hình hoạt
        self.frame_index = 0 # Khung giao diện
        self.action = 0 # hành động
        self.update_time = pygame.time.get_ticks()
        #ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0
        

        # Tải tất cả hình ảnh cho trình phát
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            # đặt lại danh sách hình ảnh tạm thời
            temp_list = []
            # Đếm số lượng tệp trong thư mục
            num_of_frames = len(os.listdir(f'Shooter-main/Shooter-main/img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'Shooter-main/Shooter-main/img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        # Cập nhật thời gian hồi chiêu
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

	#Hàm di chuyển
    def move(self, moving_left, moving_right):
        #đặt lại các biến chuyển động
        screen_scroll = 0
        dx = 0
        dy = 0
        #Gán các biến chuyển động nếu di chuyển sang trái hoặc phải
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        #nhảy
        if self.jump and not self.in_air:
            self.vel_y = -14
            self.jump = False
            self.in_air = True

        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Kiểm tra va chạm
        for tile in world.obstacle_list:
            # Sau đó kiểm tra va chạm theo hướng x.
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                #Nếu AI gặp phải bế tắc thì hãy bắt nó quay đầu
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            # Kiểm tra va chạm theo hướng trục y trước
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:  # Nếu nhảy lên
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0: # Nếu bị ngã xuống
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        #kiểm tra va chạm với nước
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        #kiểm tra va chạm với lối ra
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True


        #kiểm tra xem có bị rơi khỏi bản đồ không
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0



        #Kiểm tra xem có bị tràn ra ngoài màn hình không
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        #cập nhật vị trí hình chữ nhật
        self.rect.x += dx
        self.rect.y += dy

        #Cập nhật cuộn dựa trên vị trí của người chơi
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH) or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll,level_complete


	#Hàm bắn 
    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20  # Đặt thời gian chờ sau khi bắn
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1
            shot_fix.play()

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0) #0: nhàn rỗi
                self.idling = True
                self.idling_counter = 50
            #Kiểm tra xem ai có ở gần người chơi hay không
            if self.vision.colliderect(player.rect):
                #Ngừng chạy và đối mặt với người chơi.
                self.update_action(0)#0: idle
                #bắn
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)#1: run
                    self.move_counter += 1
                    #Cập nhật tầm nhìn AI khi kẻ địch di chuyển
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        #cuộn
        self.rect.x +=  screen_scroll



    def update_animation(self):
        #cập nhật hoạt hình
        ANIMATION_COOLDOWN = 100
        #Cập nhật hình ảnh tùy thuộc vào khung hình hiện tại
        self.image = self.animation_list[self.action][self.frame_index]
        #Kiểm tra xem đã đủ thời gian kể từ lần cập nhật cuối cùng chưa 
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            #Nếu hoạt ảnh kết thúc, hãy đặt lại về trạng thái ban đầu
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        #Kiểm tra xem hành động mới có khác với hành động trước đó hay không
        if new_action != self.action:
            self.action = new_action
            #cập nhật cài đặt hoạt ảnh
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
            

	#Hàm kiểm tra sự sống
    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)



    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

#Lớp tạo thế giới
class World():
    def __init__(self):
        self.obstacle_list = []
    #Hàm xử lý dữ liệu
    def process_data(self, data):
        self.level_length = len(data[0])
        # Lặp qua từng giá trị trong tệp dữ liệu cấp độ
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    # if tile >= 0 and tile <= 8:
                    if tile >= 0 and tile <= 8 or tile == 12: #Thùng là 12.png -> tile = 12 nếu để <=8 thì player sẽ đi // với vật thể chiếc thùng
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:#tạo người chơi
                        player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5) # đối tượng người chơi hay cũng chính là Lính(nhân vật chơi)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:#tạo kẻ thù
                        enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0) # kẻ thù
                        enemy_group.add(enemy)
                    elif tile == 17:#tạo hộp đạn
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:#tạo hộp lựu đạn
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:#tạo hộp sức khỏe
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:# tạo lối thoát
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
        return player,health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])

# Lớp trang trí bối cảnh
class Decoration(pygame.sprite.Sprite):# lớp trang trí bối cảnh cây cỏ hoa lá cành,..
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    
    def update(self):
        self.rect.x += screen_scroll

#Lớp tạo nước
class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


# Lớp tạo hộp vật phẩm
class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        #cuộn
        self.rect.x += screen_scroll
        #Kiểm tra xem người chơi đã nhặt hộp chưa
        if pygame.sprite.collide_rect(self, player):
            #Kiểm tra xem đó là loại hộp nào
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3
            #xóa hộp mục
            self.kill()

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
        
    def draw(self, health):
        #Cập nhật thông tin sức khỏe mới
        self.health = health
        #tính toán tỷ lệ sức khỏe
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


# Xác định lớp Bullet (lớp đạn)
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        #move bullet (đạn chuyển động)
        self.rect.x += (self.direction * self.speed) + screen_scroll
        #check if bullet has gone off screen (kiểm tra xem viên đạn có biến mất khỏi màn hình không)
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        #kiểm tra va chạm với mặt phẳng
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
            
		#check collision with characters (kiểm tra va chạm với các ký tự)
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    # print(enemy.health)
                    self.kill()

#Lớp lựu đạn
class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        #kiểm tra va chạm với mặt phẳng hay vật cản...
        for tile in world.obstacle_list:
            #kiểm tra va chạm với tường
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            #kiểm tra va chạm theo hướng y
            if tile[1].colliderect(self.rect.x + dx, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                #kiểm tra xem có ở dưới mặt đất không, tức là bị ném lên
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #kiểm tra xem có ở trên mặt đất hay không, tức là đang rơi
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom


        #update grenade position (cập nhật vị trí lựu đạn)
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        #bộ đếm ngược
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fix.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            #do damage to anyone that is nearby(gây sát thương cho bất cứ ai ở gần)
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group: # vòng lặp gây sát thương cho kẻ thù
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50



#lớp tạo vụ nổ
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):  # Giả sử bạn có 5 khung hình cho hoạt ảnh vụ nổ
            img = pygame.image.load(f'Shooter-main/Shooter-main/img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        #scroll
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 4 # TỐC ĐỘ NỔ
        #cập nhật hoạt ảnh vụ nổ
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            #Nếu hoạt ảnh hoàn tất thì hãy xóa vụ nổ
            if self.frame_index >= len(self.images):
                self.kill()
            else: 
                self.image = self.images[self.frame_index]

# Lớp tạo mìn
class Mine(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = mine_img # thuộc tính image của đối tượng Mine
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, y)

        self.timer = 180 # 180 = 60 giây x 3 FPS (tức là muốn mìn nổ sau 3 giây), 3 giây (60 FPS) FPS = Frames Per Second tức là 60 FPS -> 1 giây vẽ 60 lần FPS càng cao -> chuyển động càng mượt
        self.exploded = False # exploded(phát nổ) thuộc tính exploded

    def update(self): # phương thức update của lớp mìn (các sprite thường có update() để xử lý logic mỗi khung hình (frame))
        self.timer -=1 # mỗi lần update biến timer sẽ giảm đi 1

        if self.timer <= 0 and not self.exploded: # ktr dk nếu bộ đếm ngược về 0 (>0) và quả mìn chưa nổ thì exploded == fase
            self.explode()

    def explode(self): # phương thức xử lý quả mìn phát nổ
        self.exploded = True

        # explosion = ExplosionMine(self.rect.centerx, self.rect.centery) # tạo đối tượng ExplosionMine tại vị trí tâm (centerx, centery) của quả mìn
        explosion = ExplosionMine(self.rect.centerx, self.rect.midbottom[1])
        explosion_group.add(explosion) # thêm hiệu ứng nổ vào explosion_group để pygame quản lý và vẽ hiệu ứng nổ trên màn hình

        #kiểm tra va chạm định
        for enemy in enemy_group:
            #Tính khoảng cách giữa tâm quả mìn và tâm kẻ địch bằng công thức khoảng cách Euclid: distance = căn[(Xenemy - Xmine)^2 + (Yenemy - Ymine)^2]
            distance = ((enemy.rect.centerx - self.rect.centerx) ** 2 +
                    (enemy.rect.centery - self.rect.centery) ** 2) ** 0.5
            
            #Nếu khoảng cách nhở hơn 2 lần kích thước ô (TILE_SIZE * 2), tức là kẻ địch lằm trong vùng chịu ảnh hưởng
            if distance < TILE_SIZE * 2:
                enemy.health = 0 # máu địch về 0 tức là bị tiêu diệt
        self.kill() # xóa mìn sau vụ nổ

# Lớp tạo mìn phát nổ
class ExplosionMine(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.images = explosion_mine_image
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x,y) #set vị trí mìn nổ chân vụ nổ mìn nằm trên mặt đất

        self.counter = 0
    def update(self):
        explosion_speed = 4
        self.counter += 1

        if self.counter >= explosion_speed:
            self.counter = 0
            self.frame_index += 1

            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]
     

#Lớp tạo màn hình dật mờ dần sau khi bấm start để chơi
class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:#hiệu ứng mờ toàn màn hình
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2:#màn hình dọc mờ dần
            pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True
        return fade_complete


#tạo hiệu ứng chuyển cảnh mờ dần
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)
        


#tạo nút
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)

# Tạo các nhóm sprite
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
#sprite mìn
mine_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()




#tạo danh sách ô trống
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
#Tải dữ liệu cấp độ và tạo thế giới
with open(f'Shooter-main/Shooter-main/level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)


run = True
while run:
    clock.tick(FPS)

    if start_game == False:
        #trình đơn vẽ
        screen.fill(BG)
        #thêm nút
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
    else:
        #cập nhật nền
        draw_bg()
        #vẽ bản đồ thế giới
        world.draw()
        #hiển thị sức khỏe cầu thủ
        health_bar.draw(player.health)
        #show đạn
        draw_text('AMMO: ', font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet_img, (90 + (x * 10), 40))

        #trình diễn lựu đạn
        draw_text('GRENADES: ', font, WHITE, 10, 60)
        for x in range(player.grenades):
            screen.blit(grenade_img, (135 + (x * 15), 60))

        # Trưng bày mìn
        draw_text('MINES: ', font, WHITE, 10, 85)
        for x in range(player.mines):
            screen.blit(mine_img, (100 + (x * 15), 85))

        player.update()
        player.draw()
        
        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        #cập nhật và vẽ nhóm
        # Viên đạn
        bullet_group.update()
        bullet_group.draw(screen)
        #Lựu đạn
        grenade_group.update()
        grenade_group.draw(screen)
        # Mìn
        mine_group.update()
        mine_group.draw(screen)
        # Vụ nổ
        explosion_group.update()
        explosion_group.draw(screen)
        # Hộp phẩm
        item_box_group.update()
        item_box_group.draw(screen)
        #Trang trí
        decoration_group.update()
        decoration_group.draw(screen)
        # Khu vực nước
        water_group.update()
        water_group.draw(screen)
        # Cửa Exit
        exit_group.update()
        exit_group.draw(screen)

        #hiển thị phần giới thiệu
        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        #cập nhật hành động của người chơi
        if player.alive:
            #bắn đạn
            if shoot:
                player.shoot()
            #throw grenades (ném lựu đạn)
            elif grenade and grenade_throw == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),player.rect.top,player.direction)
                grenade_group.add(grenade)
                #reduce grenades (giảm lựu đạn)
                player.grenades -= 1
                grenade_throw = True
                # print(player.grenades)
            if player.in_air:
                player.update_action(2) #2: jump
            elif moving_left or moving_right:
                player.update_action(1) #1: run
            else:
                player.update_action(0) #0: idle
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            #Kiểm tra xem người chơi đã hoàn thành cấp độ chưa
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    #Tải dữ liệu cấp độ và tạo thế giới
                    with open(f'Shooter-main/Shooter-main/level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)

        else:
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    #Tải dữ liệu cấp độ và tạo thế giới
                    with open(f'Shooter-main/Shooter-main/level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        #keyboard presses (bấm bàn phím)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
                shot_fix.play()
            if event.key == pygame.K_q:
                grenade = True
                grenade_fix.play()
            # thêm phím cài mìn
            if event.key == pygame.K_m and player.alive:
                if player.mines > 0:
                    mine = Mine(player.rect.centerx, player.rect.bottom)
                    mine_group.add(mine)
                    player.mines -= 1
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                jump_fix.play()
            if event.key == pygame.K_ESCAPE:
                run = False

        
        #keyboard button released(nút bàn phím được thả ra)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_throw = False

    pygame.display.update()

pygame.quit()
