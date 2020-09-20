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
            # obj.mouseOver()
            if not obj.hide:
                obj.render(self.screen, deltaTime)


class Entity:
    def __init__(self, positionX, positionY, width, height):
        self.x, self.y = positionX, positionY
        self.w, self.h = width, height
        self.rect = pg.Rect(positionX, positionY, width, height)

        self.clicked = False

        self.hide = False

    def mouseOver(self):
        if self.hide:
            return False
        mx, my = pg.mouse.get_pos()
        #  print(mx, my)

        if self.rect.top <= my <= self.rect.bottom and self.rect.left <= mx <= self.rect.right:
            return True

    def move(self, x, y):
        self.x += x
        self.y += y
        self.rect.x += x
        self.rect.y += y


class TexturedObject(Entity):
    def __init__(self, positionX, positionY, texturePath, name, priority=0):
        self.texture = pg.image.load(texturePath)

        rect = self.texture.get_rect()
        rect.x += positionX
        rect.y += positionY
        super().__init__(positionX, positionY, rect.width, rect.height)

        self.name = name

        self.priority = priority

    def render(self, screen, deltaTime):
        screen.blit(self.texture, self.rect)


class Node(Entity):
    minScale = 0.0
    maxScale = 100.0

    def __init__(self, positionX, positionY, radius, nodeType, nodeID, priority=0, startValue=100):
        super().__init__(positionX-radius, positionY-radius, radius*2, radius*2)

        if nodeType == BASE_NODE_STR:
            self.font = pg.font.Font("arial-unicode-ms.ttf", 18)
            self.textTexture = self.font.render('', True, (0, 0, 0))
        self.id = nodeID
        self.ci = self.id
        self.r = radius

        self.type = nodeType

        self.color = 0, 0, 0

        self.v = startValue
        self.d = False

        if nodeType == BASE_NODE_STR:
            priority += 50
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
        if self.type == BASE_NODE_STR:
            pg.draw.circle(screen, self.color, (self.x+self.r, self.y+self.r), self.r, 2)
            s = ''
            a = 8320
            mod = 10
            for x in range(len(str(self.id))):
                a = int(8320 + (self.id % mod - self.id % (mod/10)) / (mod/10))
                s = chr(a) + s
                mod *= 10
            s = 'A' + s
            self.textTexture = self.font.render(s, True, (0, 0, 0))
            screen.blit(self.textTexture, (self.x + 15, self.y + 10))
        else:
            pg.draw.circle(screen, self.color, (self.x + self.r, self.y + self.r), self.r)


class Line:
    def __init__(self, x1, y1, x2, y2, color, width=1):
        self.p = []
        self.p.append([x1, y1])
        self.p.append([x2, y2])

        self.w = width

        self.color = color

        self.hide = False
        self.priority = -1
        if color[0] != 0:
            self.priority -= 1

    def render(self, screen, deltaTime):
        pg.draw.line(screen, self.color, self.p[0], self.p[1], self.w)


class InputBox(Entity):
    def __init__(self, positionX, positionY, width, height, color=(0, 0, 0), text='', font=None, priority=101):
        super().__init__(positionX, positionY, width, height)

        self.font = pg.font.Font(font, 32)
        self.text = ''
        self.textTexture = None
        self.color = color

        self.clicked = False

        self.textUpdate(text)

        self.priority = priority

    def textUpdate(self, newText):
        self.text = newText
        self.textTexture = self.font.render(self.text, True, self.color)
        self.w = max(200, self.textTexture.get_width() + 10)
        self.rect.w = self.w

    def render(self, screen, deltaTime):
        pg.draw.rect(screen, (255, 255, 255), self.rect)
        screen.blit(self.textTexture, (self.x + 5, self.y + 5))
        pg.draw.rect(screen, self.color, self.rect, 2)


class Text(Entity):
    def __init__(self, positionX, positionY, size=48, color=(0, 0, 0), text='', font=None, priority=101):
        self.font = pg.font.Font(font, size)
        self.text = text
        self.color = color
        self.textTexture = self.font.render(self.text, True, self.color)

        self.name = ''
        self.clicked = False

        rect = self.textTexture.get_rect()
        rect.x += positionX
        rect.y += positionY
        super().__init__(positionX, positionY, rect.width, rect.height)

        self.priority = priority

    def textUpdate(self, newText):
        self.text = newText
        self.textTexture = self.font.render(self.text, True, self.color)

    def render(self, screen, deltaTime):
        screen.blit(self.textTexture, (self.x, self.y))


class CriticalInfrastructure:
    def __init__(self):
        self.elements = []
        self.representative = 0
