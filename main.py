import sys
import pygame as pg
import json

from classes import *


pg.init()
scr = Screen(800, 600, (0, 0, 0))
clock = pg.time.Clock()
objectArr = []

with open("objects.json") as objs:
    rawObjects = json.load(objs)
    for obj in rawObjects:
        try:
            objectArr.append(
                Object(rawObjects[obj][0], rawObjects[obj][1], "graphics/"+obj+".png", obj, rawObjects[obj][2]))
        except IndexError:
            objectArr.append(
                Object(rawObjects[obj][0], rawObjects[obj][1], "graphics/" + obj + ".png", obj))

while 1:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()

    dt = clock.tick(60)
    scr.update(objectArr, dt)
