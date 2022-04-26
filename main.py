import sys
import pygame, random, math

pygame.init()

WIDTH, HEIGHT = 1024, 576
TDIMS = 32
GRAVITY = -1

FPS = 60
CLOCK = pygame.time.Clock()
TRUE_SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
SCREEN = pygame.Surface((WIDTH, HEIGHT))

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

new_level = False

def clamp(num, max, min):
    if num > max:
        return max
    elif num < min:
        return min
    else:
        return num

class Enemy_Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, x_speed, y_speed):
        self.rect = pygame.Rect((x, y), (10, 10))
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.image = pygame.Surface((10, 10))
        self.image.fill(RED)

    def update(self):
        self.rect.x += self.x_speed
        self.rect.y += self.y_speed

class Slash(pygame.sprite.Sprite):
    def __init__(self, p1, p2):
        super().__init__()
        self.p1 = p1
        self.p2 = p2
        self.lifetime = 10

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

    def draw(self, screen):
        pygame.draw.line(screen, WHITE, self.p1, self.p2, 5)


class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, width, amongus = True):
        super().__init__()
        if amongus == False:
            self.image = pygame.Surface((width, 2))
        else:
            self.image = pygame.Surface((width, TDIMS))
        self.image.fill(WHITE)
        self.rect = pygame.Rect((x, y), self.image.get_size())
        self.amongus = amongus


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, type = "reg"):
        super().__init__()
        self.rect = pygame.Rect((x, y), (32, 32))
        self.image = pygame.Surface((32, 32))
        self.image.fill(WHITE)
        self.type = type
        self.angle = 0
        self.cooldown = 10

    def update(self, player, enemybulletgroup):
        if self.type == "reg":
            pass
        if self.type == "shield":
            self.cooldown -= 1
            if self.cooldown <= 0:
                self.angle = (self.angle + 2*math.pi/50)%(math.pi * 2)
                self.cooldown = 1
        if self.type == "ranged":
            angle = math.atan2(self.rect.centery - player.rect.centery, self.rect.centerx - player.rect.centerx)
            self.cooldown -= 1
            if math.dist((self.rect.centerx, self.rect.centery), (player.rect.centerx, player.rect.centery)) <= 600 and self.cooldown <= 0:
                new_bullet = Enemy_Bullet(self.rect.centerx, self.rect.centery, math.cos(angle) * 15, math.sin(angle) * 15)
                enemybulletgroup.add(new_bullet)

    def draw_shield(self, screen):
        image = pygame.Surface((20, 20))
        image.fill(WHITE)
        img_rect = pygame.Rect((self.rect.centerx - math.cos(self.angle) * 50 - 10, self.rect.centery - math.sin(self.angle) * 50 - 10), (20, 20))
        screen.blit(image, img_rect)



class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((TDIMS, TDIMS))
        self.rect = pygame.Rect((WIDTH/2, HEIGHT/2), self.image.get_size())
        self.image.fill(WHITE)

        self.xacel = 0
        self.yacel = 0
        self.friction = 0.9
        self.onground = False
        self.speed = 1
        self.jump = 16
        self.cooldown_counter = 0

    def update(self, tiles, slashgroup, enemy_group):
        global new_level
        self.cooldown_counter -= 1
        killed = False
        mouse_pos = pygame.mouse.get_pos()
        angle = math.atan2(self.rect.centery - mouse_pos[1], self.rect.centerx - mouse_pos[0])
        for i in range(0, 300, 10):
            if FPS == 10:
                surf = pygame.Surface((4, 4))
                surf.fill(pygame.color.Color("#FF0000"))
                SCREEN.blit(surf, (self.rect.centerx - math.cos(angle) * i, self.rect.centery - math.sin(angle) * i))
        if pygame.mouse.get_pressed()[0] and self.cooldown_counter <= 0:
            angle = math.atan2(self.rect.centery - mouse_pos[1], self.rect.centerx - mouse_pos[0])
            new_slash = Slash((self.rect.centerx, self.rect.centery), ((self.rect.centerx - math.cos(angle) * 300, self.rect.centery - math.sin(angle) * 300)))
            slashgroup.add(new_slash)
            self.rect.centerx -= math.cos(angle) * 300
            self.rect.centery -= math.sin(angle) * 300
            for i in range(0, 300, 10):
                point = ((self.rect.centerx + math.cos(angle) * 300) - math.cos(angle) * i, (self.rect.centery + math.sin(angle) * 300) - math.sin(angle) * i)
                for e in enemy_group:
                    print(abs(e.angle - angle) >= 1)
                    if e.rect.collidepoint(point):
                        if e.type == "shield":
                            rect = pygame.Rect((e.rect.centerx - math.cos(e.angle) * 50, e.rect.centery - math.sin(angle) * 50), (20, 20))
                            if not rect.collidepoint(point):
                                e.kill()
                                killed = True
                        else:
                            e.kill()
                            killed = True
            if not killed:
                self.cooldown_counter = 100
            else:
                self.cooldown_counter = 10

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.xacel -= self.speed
        if keys[pygame.K_d]:
            self.xacel += self.speed
        if keys[pygame.K_SPACE] and self.onground:
            self.yacel -= self.jump
            self.onground = False
            self.rect.bottom -= 1

        self.onground = False
        col = pygame.sprite.spritecollide(self, tiles, False)
        for i in col:
            if self.rect.bottom < i.rect.top or self.rect.top > i.rect.bottom:
                if self.rect.centerx < i.rect.centerx:
                    self.rect.right = i.rect.left
                elif self.rect.centerx > i.rect.centerx:
                    self.rect.left = i.rect.right
        for t in tiles.sprites():
            if self.rect.colliderect(t.rect):
                if self.rect.y >= t.rect.y:
                    self.yacel = -GRAVITY
                    self.onground = False
                elif self.rect.bottom > t.rect.top:
                    self.yacel = 0
                    self.rect.bottom = t.rect.top + 1
                    self.onground = True
                else:
                    if self.rect.centerx > t.rect.centerx:
                        while self.rect.colliderect(t.rect):
                            self.rect.x += 1

        if self.onground:
            self.yacel = 0
        else:
            self.yacel -= GRAVITY

        self.xacel *= self.friction
        self.rect.x += round(self.xacel)
        self.rect.y += round(self.yacel)

        self.rect.right = clamp(self.rect.right, WIDTH, 64)
        if self.rect.right == 1024 and len(enemy_group) == 0:
            new_level = True
            self.rect.right = 64
        if self.rect.bottom > 545:
            self.rect.bottom = 545


    def draw(self):
        SCREEN.blit(self.image, self.rect)


def main():
    global new_level
    global FPS
    player = Player()

    tilegroup = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    slash_group = pygame.sprite.Group()
    enemy_bullet_group = pygame.sprite.Group()

    level = 0
    chance = 100

    font = pygame.font.Font("fonts/fourside.ttf", 75)
    font2 = pygame.font.Font("fonts/fourside.ttf", 35)

    start = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

    x, y = 0, 0
    for r in start:
        for t in r:
            if t == 1:
                tilegroup.add(Tile(x, y, 32))
            x += 32
        y += 32
        x = 0

    oldtime = 0

    while True:
        SCREEN.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    FPS = 10
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT:
                    FPS = 60

        player.update(tilegroup, slash_group, enemy_group)
        slash_group.update()
        enemy_group.update(player, enemy_bullet_group)
        enemy_bullet_group.update()
        if new_level:
            if level == 1:
                oldtime = pygame.time.get_ticks()
            if level == 10:
                print(round((pygame.time.get_ticks() - oldtime)/100)/10)
                sys.exit()
            level += 1
            chance += 5
            for i in tilegroup:
                if not i.amongus:
                    i.kill()
            for i in range(32, WIDTH - 128, 32):
                for j in range(128, HEIGHT, 32):
                    if random.randint(1, chance) == 1:
                        placeable = True
                        for e in enemy_group:
                            if math.sqrt((e.rect.centerx - i + 128/2) ** 2 + (e.rect.centerx - i + 128/2) ** 2) <= 100:
                                placeable = False
                        if placeable:
                            new_tile = Tile(i, j, 128, False)
                            tilegroup.add(new_tile)
                            new_enemy = Enemy(i + 128/2, j - 32, "ranged")
                            enemy_group.add(new_enemy)
            new_level = False

        player.draw()
        enemy_group.draw(SCREEN)
        enemy_bullet_group.draw(SCREEN)
        for e in enemy_group:
            if e.type == "shield":
                e.draw_shield(SCREEN)
        tilegroup.draw(SCREEN)
        for e in slash_group:
            e.draw(SCREEN)
        lvl_txt = font.render(str(level), 1, WHITE)
        lvlpos = lvl_txt.get_rect()
        lvlpos.centerx = WIDTH / 2
        lvlpos.centery = 50
        SCREEN.blit(lvl_txt, lvlpos)

        lvl_txt = font2.render(str(round(max(0, player.cooldown_counter / 200) * 100)), 1, WHITE)
        lvlpos = lvl_txt.get_rect()
        lvlpos.centerx = WIDTH - 50
        lvlpos.centery = 50
        SCREEN.blit(lvl_txt, lvlpos)

        TRUE_SCREEN.blit(pygame.transform.scale(SCREEN, TRUE_SCREEN.get_size()), (0, 0))
        pygame.display.flip()
        CLOCK.tick(FPS)


if __name__ == "__main__":
    main()
