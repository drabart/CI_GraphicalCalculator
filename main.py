import pygame
import json

pygame.init()


class Sprite:
    def __init__(self, n, px, py, w, h, m, c): # =(100, 100, 100)):
        self.name = n
        self.posX = px
        self.posY = py
        self.width = w
        self.height = h
        self.mode = m
        self.color = (c[0], c[1], c[2])

    def dist(self, x, y):
        return (abs(self.posX - x) ** 2 + abs(self.posY - y)) ** 0.5

    def render(self, display):
        if self.mode == 0:
            pygame.draw.rect(display, self.color, (self.posX, self.posY, self.width, self.height))
        elif self.mode == 1:
            pygame.draw.circle(display, self.color, (self.posX, self.posY), self.height)

    def cursorAbove(self):
        if self.mode == 0:
            x, y = pygame.mouse.get_pos()
            if self.posX < x < self.posX+self.width and self.posY < y < self.posY+self.height:
                return True
            else:
                return False
        elif self.mode == 1:
            x, y = pygame.mouse.get_pos()
            if self.dist(x, y) < self.height:
                return True
            else:
                return False


screenWidth = 900
screenHeight = 500
mode = 0

win = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("CIcalc")
clock = pygame.time.Clock()

constObjFile = open("constObjects.json", "r")
temporaryItemHolder = json.load(constObjFile)
constObjFile.close()

objects = []


def priority(val):
    return val["priority"]


temporaryItemHolder["objects"] = sorted(temporaryItemHolder["objects"], key=priority, reverse=True)

# print(temporaryItemHolder)
for obj in temporaryItemHolder["objects"]:
    if hasattr(obj, 'color'):
        objects.append(Sprite(obj["name"], obj["x"], obj["y"], obj["w"], obj["h"], obj["m"], obj["color"]))
    else:
        objects.append(Sprite(obj["name"], obj["x"], obj["y"], obj["w"], obj["h"], obj["m"], obj["color"]))
del temporaryItemHolder

player = objects[len(objects)-1]


def changeMode():
    global mode
    for spr in objects:
        if spr.cursorAbove():
            if spr.name == "move":
                mode = 0
            elif spr.name == "add":
                mode = 1


def renderer():
    global mode
    win.fill(0)
    for spr in objects:
        spr.render(win)
    pygame.display.update()


def moving():
    pass


def adding():
    pass


run = True
while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            changeMode()

    if mode == 0:
        moving()
    elif mode == 1:
        adding()

    player.posX, player.posY = pygame.mouse.get_pos()

    renderer()
    print(clock.get_fps())

pygame.quit()

