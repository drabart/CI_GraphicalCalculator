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


pg.init()
scr = Screen(800, 600, (0, 0, 0))

clock = pg.time.Clock()
objectArr = []

with open("objects.json") as objs:
    rawObjects = json.load(objs)
    for obj in rawObjects['textured']:
        try:
            objectArr.append(
                TexturedObject(rawObjects['textured'][obj][0], rawObjects['textured'][obj][1],
                               "graphics/" + obj + ".png", obj, rawObjects['textured'][obj][2]))
        except IndexError:
            objectArr.append(
                TexturedObject(rawObjects['textured'][obj][0], rawObjects['textured'][obj][1],
                               "graphics/" + obj + ".png", obj))

    for obj in rawObjects['nodes']:
        if obj[2] == 0:
            r = 12
            t = BASE_NODE_STR
        else:
            r = 6
            t = PROCESS_NODE_STR

        try:
            objectArr.append(Node(obj[0], obj[1], r, t, obj[3], obj[3], obj[4]))
        except IndexError:
            objectArr.append(Node(obj[0], obj[1], r, t, obj[3], obj[3]))

while 1:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()

    dt = clock.tick(60)
    scr.update(objectArr, dt)
