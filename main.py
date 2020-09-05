

import json

from classes import *
from constants import *
from pygame import *
from sys import exit

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
        if 'obj' in locals():
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
    #  initializing pygame
    init()
    scr = Screen(800, 600, (0, 0, 0))
    clock = time.Clock()

    #  array holding all renderable objects
    objectArr = []

    #  loading menu objects
    objectArr += loadMenu()

    n = loadNodes('save1.json')
    if n:
        objectArr += n

    mx, my = -1, -1
    dmx, dmy = 0, 0
    SCI = 0

    draggedNode = (-1, -1, -1)  # type, structure, id
    selectedNode = (-1, -1, -1, -1, -1)  # type, structure, id, x, y

    selectedInput = False
    rButtonDown = False
    skipMove = False
    updatedText = False

    currentText = ''

    while 1:
        moved = False
        for eve in event.get():
            if eve.type == QUIT:
                exit()
            if eve.type == MOUSEBUTTONDOWN:
                if eve.button == 1:
                    rButtonDown = True
            if eve.type == MOUSEBUTTONUP:
                if eve.button == 1:
                    rButtonDown = False
                if draggedNode != (-1, -1, -1):
                    draggedNode = (-1, -1, -1)
            if eve.type == MOUSEMOTION:
                x, y = eve.pos
                if draggedNode != (-1, -1, -1):
                    if eve.pos[0] < 250:
                        x = 250
                    if eve.pos[1] < 120:
                        y = 120
                    mouse.set_pos(x, y)

                dmx = x - mx
                dmy = y - my
                mx, my = x, y
                moved = True
            if eve.type == KEYDOWN:
                if selectedInput:
                    if eve.key == K_RETURN:
                        currentText = ''
                    elif eve.key == K_BACKSPACE:
                        currentText = currentText[:-1]
                    else:
                        currentText += eve.unicode
                    updatedText = True

        if not moved or skipMove:
            dmx = 0
            dmy = 0

        skipMove = False
        skipConnect = False

        for obj in objectArr:
            #  Click check
            try:
                #  Check for 'InputBoxes' to be unselected
                if not obj.mouseOver() and rButtonDown:
                    if type(obj) == 'InputBox' and selectedInput:
                        selectedInput = False
                        obj.clicked = False
                #  Check if object is being clicked
                if obj.mouseOver() and rButtonDown:
                    #  Set objects clicked only if no items are added
                    if draggedNode == (-1, -1, -1):
                        #  Selecting input box
                        if type(obj) == 'InputBox' and not selectedInput:
                            obj.clicked = True
                            currentText = obj.text
                            selectedInput = True
                        else:
                            obj.clicked = True
                #  'unclicking' object if it is not 'InputBox'
                elif not (obj.mouseOver() and rButtonDown) and type(obj) != 'InputBox':
                    obj.clicked = False
            except AttributeError:
                pass

            #  Nodes
            #  Handling dragged node
            try:
                #  'undragging' dragged node
                if obj.d and draggedNode == (-1, -1, -1):
                    obj.d = False
                    selectedNode = (-1, -1, -1, -1, -1)
                #  moving dragged node
                elif obj.d:
                    obj.move(dmx, dmy)
            except AttributeError:
                pass

            #  Connecting nodes
            if not skipConnect:
                try:
                    #  If no node is selected, selects one
                    if obj.type == BASE_NODE_STR and obj.clicked and selectedNode == (-1, -1, -1, -1, -1):
                        selectedNode = (0, obj.strID, obj.id, obj.x, obj.y)
                    #  If node is selected and current clicked node is not that one then connects
                    elif obj.type == BASE_NODE_STR and obj.clicked and selectedNode != (0, obj.strID, obj.id, obj.x, obj.y):
                        objectArr.append(Line(selectedNode[3]+obj.r, selectedNode[4]+obj.r, obj.x+obj.r, obj.y+obj.r, (0, 0, 0), 5))
                        selectedNode = (-1, -1, -1, -1, -1)
                        skipConnect = True
                except AttributeError:
                    pass

            #  Adding node
            try:
                #  Checking if 'Add_node' button is clicked and no node is added right then
                if obj.name == 'Add_node' and obj.clicked and draggedNode == (-1, -1, -1):
                    #  Moves cursor to middle of map
                    mouse.set_pos(475, 360)
                    #  Creates node object
                    newNode = Node(475, 360, 12, BASE_NODE_STR, SCI, 0)
                    #  Adds node object to render array
                    objectArr.append(newNode)
                    #  Setting values to know which node is currently added
                    newNode.d = True
                    draggedNode = (0, SCI, 0)
                    skipMove = True
            except AttributeError:
                pass

            #  Text
            #  Updates currently selected text
            if updatedText:
                if type(obj) == 'InputBox' and obj.clicked:
                    obj.textUpdate(currentText)
                    updatedText = False

        #  Updating screen
        dt = clock.tick(60)
        scr.update(objectArr, dt)


if __name__ == '__main__':
    main()
