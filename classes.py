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
    def __init__(self, positionX, positionY, texturePath, name, priority=0):
        self.texture = pg.image.load(texturePath)

        self.rect = self.texture.get_rect()
        self.rect.x += positionX
        self.rect.y += positionY
        super().__init__(positionX, positionY, self.rect.width, self.rect.height)

        self.name = name

        self.speed = [0, 0]
        self.priority = priority

    def set_speed(self, speedX, speedY):
        self.speed = [speedX, speedY]

    def render(self, screen, deltaTime):
        self.rect.x += self.speed[0] * deltaTime
        self.rect.y += self.speed[1] * deltaTime
        screen.blit(self.texture, self.rect)