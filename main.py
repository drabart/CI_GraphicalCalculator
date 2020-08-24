import sys
import pygame as pg


class Screen:
    def __init__(self, width, height, background):
        self.size = self.w, self.h = width, height
        self.screen = pg.display.set_mode(self.size)
        self.background = background

    def update(self, objects, deltaTime):
        self.screen.fill(self.background)
        self.render(objects, deltaTime)
        pg.display.flip()

    def render(self, objects, deltaTime):
        # lower priority, the faster it renders and lower in layers it becomes
        objects.sort(key=lambda x: x.priority)
        for obj in objects:
            obj.render(self.screen, deltaTime)


class Entity:
    def __init__(self, positionX, positionY, width, height):
        self.x, self.y = positionX, positionY
        self.w, self.h = width, height


class Object(Entity):
    def __init__(self, positionX, positionY, texturePath, priority=0):
        self.texture = pg.image.load(texturePath)
        self.rect = self.texture.get_rect()
        super().__init__(positionX, positionY, self.rect.width, self.rect.height)
        self.speed = [0, 0]
        self.priority = priority

    def set_speed(self, speedX, speedY):
        self.speed = [speedX, speedY]

    def render(self, screen, deltaTime):
        self.rect.x += self.speed[0] * deltaTime
        self.rect.y += self.speed[1] * deltaTime
        screen.blit(self.texture, self.rect)


pg.init()
scr = Screen(800, 600, (0, 0, 0))
clock = pg.time.Clock()
ball = Object(0, 0, "intro_ball.gif")
ball.set_speed(1, 1)
objectArr = [ball]

while 1:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()

    if ball.rect.left < 0 or ball.rect.right > scr.w:
        ball.speed[0] = -ball.speed[0]
    if ball.rect.top < 0 or ball.rect.bottom > scr.h:
        ball.speed[1] = -ball.speed[1]

    dt = clock.tick(60)
    scr.update(objectArr, dt)
