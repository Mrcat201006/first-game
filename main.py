import pygame
import sys
import random
import map

ROW_COUNT = 15
COLUMN_COUNT = 27
TILE_SIZE_WIDTH_FLOOR = 32
TILE_SIZE_HEIGHT_FLOOR = 12

TILE_SIZE_BLOCK = 32

GAME_WIDTH = COLUMN_COUNT * TILE_SIZE_BLOCK
GAME_HEIGHT = ROW_COUNT * TILE_SIZE_BLOCK
GAME_MAP = map.GAME_MAP2


PLAYER_X = GAME_WIDTH // 3
PLAYER_Y = GAME_HEIGHT // 2
PLAYER_WIDTH = 42
PLAYER_HEIGHT = 42
GRAVITY = 0.5
FRICTION = 0.4
PLAYER_VELOCITY_Y = -13
PLAYER_VELOCITY_X = 5

PLAYER_BULLET = 8
PLAYER_BULLET_VELOCITY_X = 8

MONSTER_BULLET = 8
MONSTER_BULLET_VELOCITY_X = 2
MONSTER_BULLET_VELOCITY_Y = MONSTER_BULLET_VELOCITY_X


LIFE_ENERGY_WIDTH = 12
LIFE_ENERGY_HEIGHT = 12
BIG_LIFE_ENERGY_WIDTH = 24
BIG_LIFE_ENERGY_HEIGHT = 24
ITEM_VELOCITY_Y = -11 #item flies up first and gravity pulls it down


pygame.init()
screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
clock = pygame.time.Clock()
pygame.font.init()
game_font = pygame.font.Font("Planes_ValMore.ttf", 24)

game_over = False

#costom event
invincible_end = pygame.USEREVENT + 0
shooting_end  = pygame.USEREVENT + 1

def load_image(image_name, scale=None): 
    image = pygame.image.load(image_name).convert_alpha()
    if scale:
        image = pygame.transform.scale(image, scale)
    return image



bg = load_image("image/bg/background 1.png", (GAME_WIDTH, GAME_HEIGHT))
floor_tile = load_image("image/bg/road1.png", (TILE_SIZE_WIDTH_FLOOR, TILE_SIZE_HEIGHT_FLOOR))
floor_block =load_image("image/bg/blok1.png",(TILE_SIZE_BLOCK, TILE_SIZE_BLOCK))
life_energy_image = load_image("image/bg/life_energy.png", (LIFE_ENERGY_WIDTH, LIFE_ENERGY_HEIGHT))
big_life_energy_image = load_image("image/bg/life_energy.png", (BIG_LIFE_ENERGY_WIDTH, BIG_LIFE_ENERGY_HEIGHT))
spike_image = load_image("image/bg/spike.png", (TILE_SIZE_BLOCK, TILE_SIZE_BLOCK))

# Спрайты смотрящие вправо герой (теперь из папки left)
player_imageL_stand = load_image("image/left/Pink_Monster_L.png", (PLAYER_WIDTH, PLAYER_HEIGHT))
player_imageL_attack = [load_image(f"image/left/Pink_Monster_Attack_{i}_L.png", (PLAYER_WIDTH, PLAYER_HEIGHT)) for i in range(1, 3)]
player_imageL_jump1 = load_image("image/left/Pink_Monster_Jump_L1.png", (PLAYER_WIDTH, PLAYER_HEIGHT))
player_imageL_run = [load_image(f"image/left/Pink_Monster_Run_L{i}.png", (PLAYER_WIDTH, PLAYER_HEIGHT)) for i in range(1, 6)]


# Спрайты смотрящие влево герой (теперь из папки right)
player_imageR_stand = load_image("image/right/Pink_Monster.png", (PLAYER_WIDTH, PLAYER_HEIGHT))
player_imageR_attack = [load_image(f"image/right/Pink_Monster_Attack_{i}_R.png", (PLAYER_WIDTH, PLAYER_HEIGHT))for i in range(1, 3)]
player_imageR_jump1 = load_image("image/right/Pink_Monster_Jump_R1.png", (PLAYER_WIDTH, PLAYER_HEIGHT))
player_imageR_run = [load_image(f"image/right/Pink_Monster_Run_R{i}.png", (PLAYER_WIDTH, PLAYER_HEIGHT)) for i in range(1, 6)]


player_image_bullet = load_image("image/bg/Rock2.png")
monster_image_bullet = load_image("image/bg/Rock1.png")

#монстор спрайты
monster_imageL_stand = load_image("image/monster/Dude_Monster_L.png", (PLAYER_WIDTH, PLAYER_HEIGHT))
monster_imageR_stand = load_image("image/monster/Dude_Monster.png", (PLAYER_WIDTH, PLAYER_HEIGHT))
monster_imageL_defends = load_image("image/monster/Dude_Monster_Defends_L.png",(PLAYER_WIDTH, PLAYER_HEIGHT))
monster_imageR_defends = load_image("image/monster/Dude_Monster_Defends_R.png",(PLAYER_WIDTH, PLAYER_HEIGHT))



class Player(pygame.Rect):
    class Bullet(pygame.Rect):
        def __init__(self):
            if player.direction == "left":
                pygame.Rect.__init__(self, player.x, player.y + TILE_SIZE_BLOCK/2,
                                     PLAYER_BULLET, PLAYER_BULLET)
                self.velocity_x = -PLAYER_BULLET_VELOCITY_X
            elif player.direction == "right":
                pygame.Rect.__init__(self, player.x + player.width, player.y + TILE_SIZE_BLOCK/2,
                                     PLAYER_BULLET, PLAYER_BULLET)
                self.velocity_x = PLAYER_BULLET_VELOCITY_X
            self.image = player_image_bullet
            self.used = False
    
    
    def __init__(self):
        super().__init__(PLAYER_X, PLAYER_Y, PLAYER_WIDTH, PLAYER_HEIGHT)

        self.image = player_imageR_stand
        self.velocity_x = 0
        self.velocity_y = 0
        self.direction = "right"
        self.jumping = False
        self.invincible = False
        self.max_health = 28
        self.health = self.max_health
        self.shooting = False
        self.bullets = []
        self.score = 0
        self.running = False
        self.current_run_index = 0
        self.last_updated_run_index = pygame.time.get_ticks()
        self.current_attack_index = 0
        self.last_updated_attack_index = pygame.time.get_ticks()
        
    def update_image(self):
        if self.shooting:
            self.update_attack_animation()
            if self.direction == "right":
                self.image = player_imageR_attack[self.current_attack_index]
            elif self.direction == "left":
                self.image = player_imageL_attack[self.current_attack_index]
        elif self.running and not self.jumping:
            if self.shooting:
                if self.direction == "right":
                    self.image = player_imageR_run[self.current_run_index]
                elif self.direction == "left":
                    self.image = player_imageL_run[self.current_run_index]
            else:
                if self.direction == "right":
                    self.image = player_imageR_run[self.current_run_index]
                elif self.direction == "left":
                    self.image = player_imageL_run[self.current_run_index]
            self.update_running_animation()
        else:
            self.current_run_index = 0

            if self.jumping:
                if self.direction == "right":
                    self.image = player_imageR_jump1
                elif self.direction == "left":
                    self.image = player_imageL_jump1
            else:
                if self.direction == "right":
                    self.image = player_imageR_stand
                elif self.direction == "left":
                    self.image = player_imageL_stand
               
    def update_running_animation(self):
        now = pygame.time.get_ticks()
        if now - self.last_updated_run_index > 250:
            self.last_updated_run_index = now
            self.current_run_index = (self.current_run_index + 1) % len(player_imageR_run)
            
    def update_attack_animation(self):
        now = pygame.time.get_ticks()
        if now - self.last_updated_attack_index > 100:  # можно подобрать скорость под длительность атаки
            self.last_updated_attack_index = now
            self.current_attack_index = (self.current_attack_index + 1) % len(player_imageR_attack)
               
        
    def set_invincible(self, milliseconds = 1000):
        self.invincible = True
        pygame.time.set_timer(invincible_end, milliseconds, 1) #event called , milliseconds , repetitions
        
    def set_attack(self, milliseconds = 250):
        if not self.shooting:
            self.shooting = True
            pygame.time.set_timer(shooting_end, milliseconds, 1) #event called , milliseconds , repetitions
            
    def set_shooting(self):
        if not self.shooting:
            self.shooting = True
            self.bullets.append(Player.Bullet())
            pygame.time.set_timer(shooting_end, 250, 1)
               
class monster_NPS(pygame.Rect):
    class Bullet(pygame.Rect):
        def __init__(self, metall, velocity_y):
            if metall.direction == "left":
                pygame.Rect.__init__(self, metall.x, metall.y + TILE_SIZE_BLOCK/2,
                                     MONSTER_BULLET, MONSTER_BULLET)
                self.velocity_x = -MONSTER_BULLET_VELOCITY_X
            elif metall.direction == "right":
                pygame.Rect.__init__(self, metall.x + metall.width, metall.y + TILE_SIZE_BLOCK/2,
                                     MONSTER_BULLET, MONSTER_BULLET)
                self.velocity_x = MONSTER_BULLET_VELOCITY_X
            self.velocity_y = velocity_y
            self.image = monster_image_bullet
            self.used = False 
            self.guarding = False
            
            
    def __init__(self, x, y):
        super().__init__(x, y,  PLAYER_WIDTH, PLAYER_HEIGHT)
        self.image = monster_imageL_stand
        self.velocity_y = 0
        self.direction = "left"
        self.jumping = False
        self.health = 8
        self.bullets = []
        self.last_fired = pygame.time.get_ticks() #time in ms after pygame.initialize
        self.guarding = False
        
    def set_shooting(self):
        if abs(self.x - player.x) <= TILE_SIZE_BLOCK*4:
            now = pygame.time.get_ticks()
            if now - self.last_fired > 1000:
                self.last_fired = now
                self.bullets.append(monster_NPS.Bullet(self, -MONSTER_BULLET_VELOCITY_Y))
                self.bullets.append(monster_NPS.Bullet(self, 0))
                self.bullets.append(monster_NPS.Bullet(self, MONSTER_BULLET_VELOCITY_Y))
        
    def update_image(self):
        if self.direction == "right":
            if self.guarding:
                self.image = monster_imageR_defends
            else:
                self.image = monster_imageR_stand
        elif self.direction == "left":
            if self.guarding:
                self.image = monster_imageL_defends
            else:
                self.image = monster_imageL_stand
               
class Tile_Floors(pygame.Rect):
    def __init__(self, x, y, image):
        super().__init__(x, y, TILE_SIZE_WIDTH_FLOOR, TILE_SIZE_HEIGHT_FLOOR) 
        self.image = image             

class Tile_BlocK(pygame.Rect):
    def __init__(self, x, y, image):
        super().__init__(x, y, TILE_SIZE_BLOCK, TILE_SIZE_BLOCK)
        self.image = image
        
class Item(pygame.Rect):
    def __init__(self, x, y, image):
        pygame.Rect.__init__(self, x, y, image.get_width(), image.get_height())
        self.image = image
        self.jumping = False
        self.velocity_y = ITEM_VELOCITY_Y
        self.used = False



def create_map():
    for row, map_row in enumerate(GAME_MAP):
        for column, map_code in enumerate(map_row):

            x = column * TILE_SIZE_BLOCK
            y = row * TILE_SIZE_BLOCK

            if map_code == 0:
                continue

            elif abs(map_code) == 1:
                tile = Tile_Floors(x, y, floor_tile)
                tiles_floors.append(tile)

            elif abs(map_code) == 2:
                tile = Tile_BlocK(x, y, floor_block)
                tiles_blocks.append(tile)

            elif abs(map_code) == 3:
                spikes.append(Item(x, y, spike_image))

            elif abs(map_code) == 4:
                monsters.append(monster_NPS(x, y))
                
                
def reset_game():
    global player, monsters, monster_bullets, tiles_blocks, tiles_floors,\
    items, spikes, game_over
    player = Player()
    monsters = []
    monster_bullets = [] #used to keep bullets active when monster is destroyed
    tiles_blocks = []
    tiles_floors = []
    items = []
    spikes = [] #traps, hazards
    create_map()
    game_over = False
    
        
def check_tile_collision(character):
    for tile in tiles_floors:
        if character.colliderect(tile):
            return tile
    for block in tiles_blocks:
        if character.colliderect(block):
            return block 
    return None


def check_tile_collision_x(character):
    tile = check_tile_collision(character)
    if tile is not None:
        if character.velocity_x < 0:
            character.x = tile.x + tile.width
        elif character.velocity_x > 0:
            character.x = tile.x - character.width
        character.velocity_x = 0


def check_tile_collision_y(character):
    tile = check_tile_collision(character)
    if tile is not None:
        if character.velocity_y < 0:
            character.y = tile.y + tile.height
        elif character.velocity_y > 0:
            character.y = tile.y - character.height
            character.jumping = False
        character.velocity_y = 0
        
def drop_item(character):
    random_number = random.randint(1, 100)
    if 0 < random_number <= 20:
        items.append(Item(character.x, character.y, big_life_energy_image))
    elif 20 < random_number <= 50:
        items.append(Item(character.x, character.y, life_energy_image))

def move_player_x(velocity_x):
    move_map_x(velocity_x)
    tile = check_tile_collision(player)
    if tile is not None:
        move_map_x(-velocity_x)

def move_map_x(velocity_x):
    for tile in tiles_floors:
        tile.x += velocity_x
        
    for tile in tiles_blocks:
        tile.x += velocity_x
    
    for monster in monsters:
        monster.x += velocity_x
        for bullet in monster.bullets:
            bullet.x += velocity_x
    
    for bullet in monster_bullets:
        bullet.x += velocity_x
    
    for item in items:
        item.x += velocity_x
    
    for spike in spikes:
        spike.x += velocity_x


def move():
    global items, monsters, monster_bullets, game_over
    # X movement
    # if player.direction == "left" and player.velocity_x < 0:
    #     player.velocity_x += FRICTION
    # elif player.direction == "right" and player.velocity_x > 0:
    #     player.velocity_x -= FRICTION
    # else:
    #     player.velocity_x = 0
    
    # player.x += player.velocity_x
    
    
    # if player.x < 0:
    #     player.x = 0
    # elif player.x + PLAYER_WIDTH > GAME_WIDTH:
    #     player.x = GAME_WIDTH - PLAYER_WIDTH
    
    # check_tile_collision_x(player)
    
    # Y movement
    player.velocity_y += GRAVITY
    player.y += player.velocity_y
    check_tile_collision_y(player)
    
    for spike in spikes:
        if player.colliderect(spike):
            player.health = 0 #game over
    
    #bullets
    for bullet in player.bullets:
        bullet.x += bullet.velocity_x
        for monster in monsters:
            if monster.health > 0 and not bullet.used and bullet.colliderect(monster):
                bullet.used = True
                if not monster.guarding:
                    monster.health -=1
                    if monster.health <= 0:
                        drop_item(monster)
                        monster_bullets += monster.bullets
                        player.score += 500
    
    player.bullets = [bullet for bullet in player.bullets if not bullet.used \
                      and bullet.x + bullet.width > 0 and bullet.x < GAME_WIDTH]
    
    monsters = [monster for monster in monsters if monster.health > 0]
    
    #enemy y movement
    for monster in monsters:
        if player.x < monster.x:
            monster.direction = "left"
        else:
            monster.direction = "right"
            
            
        # Дистанция до игрока    
        distance_to_player = abs(monster.x - player.x)

        # Если игрок дальше 5 блоков (160px), монстр защищается и не получает урон.
        # Если ближе — снимает защиту и атакована/уязвима.
        if distance_to_player > TILE_SIZE_BLOCK * 5:
            monster.guarding = True
        else:
            monster.guarding = False
        
        monster.velocity_y += GRAVITY
        monster.y += monster.velocity_y
        check_tile_collision_y(monster)

        if not player.invincible and player.colliderect(monster):
            player.health -= 1
            player.set_invincible()
    
        #enemy bullets
        monster.set_shooting()
        for bullet in monster.bullets:
            bullet.x += bullet.velocity_x
            bullet.y += bullet.velocity_y
            if not player.invincible and player.colliderect(bullet):
                player.health -= 2
                bullet.used = True
                player.set_invincible()
        
        monster.bullets = [bullet for bullet in monster.bullets if not bullet.used \
                          and bullet.x + bullet.width > 0 and bullet.x < GAME_WIDTH]
        
        
    for bullet in monster_bullets:
        bullet.x += bullet.velocity_x
        bullet.y += bullet.velocity_y
        if not player.invincible and player.colliderect(bullet):
            player.health -= 2
            bullet.used = True
            player.set_invincible()
    
    monster_bullets = [bullet for bullet in monster_bullets if not bullet.used \
                        and bullet.x + bullet.width > 0 and bullet.x < GAME_WIDTH]
    
    for item in items:
        item.velocity_y += GRAVITY
        item.y += item.velocity_y
        check_tile_collision_y(item)
        if player.colliderect(item):
            item.used = True
            if item.image == life_energy_image:
                player.health = min(player.health + 2, player.max_health)
            elif item.image == big_life_energy_image:
                player.health = min(player.health + 8, player.max_health)
    items = [item for item in items if not item.used]
    
    if player.health <= 0 or player.y > GAME_HEIGHT:
        game_over = True
    
    

def draw():
    screen.fill((0, 0, 0))
    screen.blit(bg, (0, 0))
    
    for tile in background_tiles:
        if tile.x > GAME_WIDTH:
            continue
        screen.blit(tile.image, tile)

    for tile in tiles_blocks:
        if tile.x > GAME_WIDTH:
            continue
        screen.blit(tile.image, tile)
        
    for tile in tiles_floors:
        if tile.x > GAME_WIDTH:
            continue
        screen.blit(tile.image, tile)
    
    for spike in spikes:
        if spike.x > GAME_WIDTH:
            continue
        screen.blit(spike.image, spike)

    player.update_image()
    screen.blit(player.image, player)

    for bullet in player.bullets:
        screen.blit(bullet.image, bullet)

    for monster in monsters:
        if monster.x > GAME_WIDTH:
            continue
        monster.update_image()
        screen.blit(monster.image, monster)
        for bullet in monster.bullets:
            screen.blit(bullet.image, bullet)
            
    for bullet in monster_bullets:
        screen.blit(bullet.image, bullet)       
            
    for item in items:
        if item.x > GAME_WIDTH:
            continue
        screen.blit(item.image, item)
    
            
    pygame.draw.rect(screen, "black", (28, 30, 10.4*player.max_health, 15))       
    pygame.draw.rect(screen, "red", (TILE_SIZE_BLOCK, TILE_SIZE_BLOCK, 10*player.max_health, 10))
    pygame.draw.rect(screen, "green", (TILE_SIZE_BLOCK, TILE_SIZE_BLOCK, 10*player.health, 10))
    text_score = str(player.score)
    
    while len(text_score) < 7: #7 digits in score
        text_score = "0" + text_score
    text_surface = game_font.render(text_score, False, "white")
    screen.blit(text_surface, (GAME_WIDTH/2, TILE_SIZE_BLOCK/2))
    
    if game_over:
        text_surface = game_font.render("Game Over:", False, "white")
        screen.blit(text_surface, (GAME_WIDTH/8, GAME_HEIGHT/2))
        text_surface = game_font.render("Press [Enter] to Restart", False, "white")
        screen.blit(text_surface, (GAME_WIDTH/8, GAME_HEIGHT/2 + TILE_SIZE_BLOCK))
    

player = Player()
background_tiles = []
spikes = []
items = []
monsters = []
monster_bullets = [] #used to keep bullets active when monster is destroyed
tiles_floors = []
tiles_blocks = []
create_map()
   
    
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        if event.type == invincible_end:
            player.invincible = False
        elif event.type == shooting_end:
            player.shooting = False
    
    
    keys = pygame.key.get_pressed()
    if (keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER]) and game_over:
        reset_game()
    
    if (keys[pygame.K_UP] or keys[pygame.K_w]) and not player.jumping:
        player.velocity_y = PLAYER_VELOCITY_Y
        player.jumping = True
        
    if keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.running = True
    else:
        player.running = False


    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        # player.velocity_x = PLAYER_VELOCITY_X
        move_player_x(-PLAYER_VELOCITY_X)
        player.direction = "right"

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        # player.velocity_x = -PLAYER_VELOCITY_X
        move_player_x(PLAYER_VELOCITY_X)
        player.direction = "left"
    if keys[pygame.K_SPACE] or keys[pygame.K_x]:
        player.set_shooting()
       
    
    
    if not game_over:
        move()
        draw()
        pygame.display.update()
        clock.tick(30)
    