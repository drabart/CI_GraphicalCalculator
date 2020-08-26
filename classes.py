import pygame as pg
from constants import *


class Screen:
    def __init__(self, width, height, background):
        self.size = self.w, self.h = width, height
        self.screen = pg.display.set_mode(self.size)
        self.background = background

        self.icon = pg.image.load("graphics/icon.png")
        pg.display.set_icon(self.icon)
        pg.display.set_caption("Critical Infrastructure Calculator")

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


class TexturedObject(Entity):
    def __init__(self, positionX, positionY, texturePath, name, priority=0):
        self.texture = pg.image.load(texturePath)

        self.rect = self.texture.get_rect()
        self.rect.x += positionX
        self.rect.y += positionY
        super().__init__(positionX, positionY, self.rect.width, self.rect.height)

        self.name = name

        self.priority = priority

    def render(self, screen, deltaTime):
        screen.blit(self.texture, self.rect)


class Node(Entity):
    minScale = 0.0
    maxScale = 100.0

    def __init__(self, positionX, positionY, radius, nodeType, structureID, priority=0, startValue=0):
        super().__init__(positionX, positionY, 0, 0)

        self.r = radius

        self.type = nodeType
        self.strID = structureID

        self.color = 0, 0, 0

        self.v = startValue

        self.priority = priority

        self.updateColor()

    def update(self):
        self.updateColor()

    def updateColor(self):
        if self.type == BASE_NODE_STR:
            if self.v >= self.maxScale:
                self.color = 0, 200, 0
            elif self.minScale < self.v < self.maxScale:
                b1 = self.maxScale - (self.maxScale - self.minScale) / 3
                b2 = self.maxScale - (self.maxScale - self.minScale) / 3 * 2
                if self.v >= b1:
                    self.color = int(200.0 * (float(self.maxScale - self.v) / float(self.maxScale - b1))), 200, 0
                elif b2 < self.v < b1:
                    self.color = 200, 200 - int(200.0 * (float(b1 - self.v) / float(b1 - b2))), 0
                else:
                    self.color = 200 - int(200.0 * (float(b2 - self.v) / float(b2 - self.minScale))), 0, 0
            else:
                self.color = 0, 0, 0
        elif self.type == PROCESS_NODE_STR:
            self.color = 73, 104, 235

    def render(self, screen, deltaTime):
        self.update()
        pg.draw.circle(screen, self.color, (self.x, self.y), self.r)
