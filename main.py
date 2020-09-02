import sys
import pygame as pg
import json

from classes import *
from constants import *


'''
TODO list
- nodes
- processes
- node details
'''


def loadNodes(file):
    arr = []

    with open(file) as nodes:
        rawObjects = json.load(nodes)
        for obj in rawObjects['nodes']:
            if obj[2] == 0:
                r = 12
                t = BASE_NODE_STR
            else:
                r = 6
                t = PROCESS_NODE_STR

            try:
                arr.append(Node(obj[0], obj[1], r, t, obj[3], obj[3], obj[4], obj[5]))
            except IndexError:
                arr.append(Node(obj[0], obj[1], r, t, obj[3], obj[3], obj[4]))
        obj = 0
        del obj

    return arr


def loadMenu():
    arr = []

    with open("objects.json") as objs:
        rawObjects = json.load(objs)
        for obj in rawObjects['textured']:
            try:
                arr.append(
                    TexturedObject(rawObjects['textured'][obj][0], rawObjects['textured'][obj][1],
                                   "graphics/" + obj + ".png", obj, rawObjects['textured'][obj][2]))
            except IndexError:
                arr.append(
                    TexturedObject(rawObjects['textured'][obj][0], rawObjects['textured'][obj][1],
                                   "graphics/" + obj + ".png", obj))
        del obj

    return arr


def main():
    pg.init()
    scr = Screen(800, 600, (0, 0, 0))
    clock = pg.time.Clock()
    objectArr = []

    objectArr.append(InputBox(260, 50, 50, 50, text='lorem ipsum'))

    objectArr += loadMenu()
    n = loadNodes('save1.json')
    if n:
        objectArr += n

    mx, my = -1, -1
    dmx, dmy = 0, 0
    SCI = 0

    nodeCount = [0]

    draggedNode = (-1, -1, -1)  # type, structure, id
    selectedNode = (-1, -1, -1, -1, -1)  # type, structure, id, x, y

    selectedInput = False
    rButtonDown = False
    skipMove = False
    updatedText = False

    currentText = ''

    while 1:
        moved = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    rButtonDown = True
            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    rButtonDown = False
                if draggedNode != (-1, -1, -1):
                    draggedNode = (-1, -1, -1)
            if event.type == pg.MOUSEMOTION:
                x, y = event.pos
                if draggedNode != (-1, -1, -1):
                    if event.pos[0] < 250:
                        x = 250
                    if event.pos[1] < 120:
                        y = 120
                    pg.mouse.set_pos(x, y)

                dmx = x - mx
                dmy = y - my
                mx, my = x, y
                moved = True
            if event.type == pg.KEYDOWN:
                if selectedInput:
                    if event.key == pg.K_RETURN:
                        currentText = ''
                    elif event.key == pg.K_BACKSPACE:
                        currentText = currentText[:-1]
                    else:
                        currentText += event.unicode
                    updatedText = True

        if not moved or skipMove:
            dmx = 0
            dmy = 0

        skipMove = False
        skipConnect = False

        for obj in objectArr:
            try:
                if obj.d and draggedNode == (-1, -1, -1):
                    obj.d = False
                    selectedNode = (-1, -1, -1, -1, -1)
                    #  print(obj.x, obj.y)
                elif obj.d:
                    obj.move(dmx, dmy)
            except AttributeError:
                pass

            if updatedText:
                try:
                    if obj.textTexture and obj.clicked:
                        obj.textUpdate(currentText)
                        updatedText = False
                except AttributeError:
                    pass

            try:
                if not obj.mouseOver() and rButtonDown:
                    try:
                        if obj.textTexture and selectedInput:
                            selectedInput = False
                            obj.clicked = False
                    except AttributeError:
                        pass
                if obj.mouseOver() and rButtonDown:
                    try:
                        if obj.textTexture and not selectedInput:
                            obj.clicked = True
                            currentText = obj.text
                            selectedInput = True
                    except AttributeError:
                        pass
                    if draggedNode == (-1, -1, -1):
                        obj.clicked = True
                elif not (obj.mouseOver() and rButtonDown):
                    try:
                        if obj.textTexture:
                            pass
                    except AttributeError:
                        obj.clicked = False
            except AttributeError:
                pass

            try:
                if obj.name == 'Add_node' and obj.clicked and draggedNode == (-1, -1, -1):
                    pg.mouse.set_pos(475, 360)
                    newNode = Node(475, 360, 12, BASE_NODE_STR, SCI, nodeCount[SCI])
                    #  print((475, 360, 12, BASE_NODE_STR, SCI, nodeCount[SCI]))
                    objectArr.append(newNode)
                    newNode.d = True
                    draggedNode = (0, SCI, nodeCount[SCI])
                    nodeCount[SCI] += 1
                    skipMove = True
            except AttributeError:
                pass

            if not skipConnect:
                try:
                    if obj.type == BASE_NODE_STR and obj.clicked and selectedNode == (-1, -1, -1, -1, -1):
                        selectedNode = (0, obj.strID, obj.id, obj.x, obj.y)
                        #  print(selectedNode)
                    elif obj.type == BASE_NODE_STR and obj.clicked and selectedNode != (0, obj.strID, obj.id, obj.x, obj.y):
                        objectArr.append(Line(selectedNode[3]+obj.r, selectedNode[4]+obj.r, obj.x+obj.r, obj.y+obj.r, (0, 0, 0), 5))
                        selectedNode = (-1, -1, -1, -1, -1)
                        skipConnect = True
                        #  print(selectedNode)
                except AttributeError:
                    pass
        #  print()
        dt = clock.tick(60)
        scr.update(objectArr, dt)


if __name__ == '__main__':
    main()
