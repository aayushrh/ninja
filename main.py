import sys
import pygame, random, math

pygame.init()

WIDTH, HEIGHT = 1024, 576
TDIMS = 32
GRAVITY = -0.5

FPS = 60
CLOCK = pygame.time.Clock()
TRUE_SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
SCREEN = pygame.Surface((WIDTH, HEIGHT))

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

new_level = False

def clamp(num, max, min):
    if num > max:
        return max
    elif num < min:
        return min
    else:
        return num

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, width, amongus = True):
        super().__init__()
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

    def update(self):
        if self.type == "reg":
            pass



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

    def update(self, tiles, rightclick, enemy_group):
        global new_level
        self.cooldown_counter -= 1
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0] and self.cooldown_counter <= 0:
            angle = math.atan2(self.rect.centery - mouse_pos[1], self.rect.centerx - mouse_pos[0])
            self.rect.centerx -= math.cos(angle) * 300
            self.rect.centery -= math.sin(angle) * 300
            self.cooldown_counter = 50
            for e in enemy_group:
                if abs((math.atan2(self.rect.centery - e.rect.centery, self.rect.centerx - e.rect.centerx)) - angle) <= 0.01:
                    if math.sqrt((self.rect.centery - e.rect.centery)**2 + (self.rect.centerx - e.rect.centerx)**2) <= 300:
                        e.kill()

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
        self.rect.centery = clamp(self.rect.centery, HEIGHT, 64)
        if self.rect.right == 1024 and len(enemy_group) == 0:
            new_level = True
            self.rect.right = 64

    def draw(self):
        SCREEN.blit(self.image, self.rect)


def main():
    global new_level
    player = Player()

    tilegroup = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()

    start = [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

    x, y = 0, 0
    for r in start:
        for t in r:
            if t == 1:
                tilegroup.add(Tile(x, y, 32))
            x += 32
        y += 32
        x = 0

    while True:
        SCREEN.fill(BLACK)
        rightclick = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        player.update(tilegroup, rightclick, enemy_group)
        # tilegroup.update()

        if new_level:
            for i in tilegroup:
                if not i.amongus:
                    i.kill()
            for i in range(32, WIDTH, 32):
                for j in range(32, HEIGHT, 32):
                    if random.randint(1, 100) == 1:
                        new_tile = Tile(i, j, 128, False)
                        tilegroup.add(new_tile)
                        new_enemy = Enemy(i + 128/2, j - 32)
                        enemy_group.add(new_enemy)
            new_level = False

        player.draw()
        enemy_group.draw(SCREEN)
        tilegroup.draw(SCREEN)

        TRUE_SCREEN.blit(pygame.transform.scale(SCREEN, TRUE_SCREEN.get_size()), (0, 0))
        pygame.display.flip()
        CLOCK.tick(FPS)


if __name__ == "__main__":
    main()
