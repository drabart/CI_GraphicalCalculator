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

    objectArr += loadMenu()
    objectArr += loadNodes('save1.json')

    mx, my = -1, -1
    dmx, dmy = 0, 0
    SCI = 0
    nodeCount = [0]
    draggedNode = (-1, -1, -1)
    rButtonDown = False
    skipMove = False

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

        if not moved or skipMove:
            dmx = 0
            dmy = 0

        skipMove = False

        for obj in objectArr:
            try:
                if obj.d and draggedNode == (-1, -1, -1):
                    obj.d = False
                elif obj.d:
                    obj.move(dmx, dmy)
            except AttributeError:
                pass

            if obj.mouseOver() and rButtonDown:
                obj.clicked = True
            else:
                obj.clicked = False

            try:
                if obj.name == 'Add_node' and obj.clicked and draggedNode == (-1, -1, -1):
                    pg.mouse.set_pos(475, 360)
                    newNode = Node(475, 360, 12, BASE_NODE_STR, SCI, nodeCount[SCI])
                    objectArr.append(newNode)
                    newNode.d = True
                    draggedNode = (0, SCI, nodeCount[SCI])
                    nodeCount[SCI] += 1
                    skipMove = True

            except AttributeError:
                pass

        dt = clock.tick(60)
        scr.update(objectArr, dt)


if __name__ == '__main__':
    main()
