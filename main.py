
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

    with open(file, 'r') as F:

        rawObjects = json.load(F)
        print(rawObjects)
        rawObjects['nodes'].sort(key=lambda x: x[3])
        print(rawObjects)
        for obj in rawObjects['nodes']:
            if obj[2] == BASE_NODE_STR:
                r = 12
            else:
                r = 6

            try:
                arr.append(Node(obj[0], obj[1], r, obj[2], obj[3], obj[3], startValue=obj[4]))
            except IndexError:
                arr.append(Node(obj[0], obj[1], r, obj[2], obj[3], obj[3]))
        if 'obj' in locals():
            del obj

        for conn in rawObjects['connections']:
            a = arr[conn[0] - 1]
            b = arr[conn[1] - 1]
            arr.append(Line(a.x + a.r, a.y + a.r, b.x + b.r, b.y + b.r, (0, 0, 0), 5))

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


visited = {}


def ss(w, c, i, oa):
    global visited
    visited[w] = True
    for ob in oa:
        if type(ob) == Node and ob.type == BASE_NODE_STR and ob.id == w:
            ob.ci = i
    if c[w]:
        for a in c[w]:
            try:
                if visited[a]:
                    pass
            except KeyError:
                ss(a, c, i, oa)


def main():
    #  initializing pygame
    init()
    scr = Screen(800, 600, (0, 0, 0))
    clock = time.Clock()

    #  array holding all renderable objects
    menuArr = []
    objectArr = []

    #  loading menu objects
    menuArr += loadMenu()

    connections = [[]]
    connectionsList = []

    mx, my = -1, -1
    dmx, dmy = 0, 0
    ID = 1

    draggedNode = (-1, -1)  # type, id
    selectedNode = (-1, -1, -1, -1)  # type, id, x, y

    selectedInput = False
    rButtonDown = False
    skipMove = False
    updatedText = False
    editedGraph = False

    currentText = ''
    ib = InputBox(270, 70, 100, 30)
    ib.hide = True
    objectArr.append(ib)
    nt = Text(255, 5, text='Selected Node: ')
    nt.hide = True
    menuArr.append(nt)
    cit = Text(255, 48, text='Node CI: ', size=32)
    cit.hide = True
    menuArr.append(cit)

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
                if draggedNode != (-1, -1):
                    draggedNode = (-1, -1)
                    editedGraph = True
            if eve.type == MOUSEMOTION:
                x, y = eve.pos
                if draggedNode != (-1, -1):
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

        for obj in menuArr+objectArr:
            #  Click check
            try:
                #  Check for 'InputBoxes' to be unselected
                if not obj.mouseOver() and rButtonDown:
                    if type(obj) == InputBox and selectedInput:
                        selectedInput = False
                        obj.clicked = False
                #  Check if object is being clicked
                if obj.mouseOver() and rButtonDown:
                    #  Set objects clicked only if no items are added
                    if draggedNode == (-1, -1):
                        #  Selecting input box
                        if type(obj) == InputBox and not selectedInput:
                            obj.clicked = True
                            currentText = obj.text
                            selectedInput = True
                        else:
                            obj.clicked = True
                #  'unclicking' object if it is not 'InputBox'
                elif not (obj.mouseOver() and rButtonDown) and type(obj) != InputBox:
                    obj.clicked = False
            except AttributeError:
                pass

            #  Nodes
            #  Handling dragged node
            try:
                #  'undragging' dragged node
                if obj.d and draggedNode == (-1, -1):
                    obj.d = False
                    selectedNode = (-1, -1, -1, -1)
                    ib.hide = True
                    nt.hide = True
                    cit.hide = True
                    for ob in menuArr:
                        if type(ob) == TexturedObject and ob.name == 'Title':
                            ob.hide = False
                #  moving dragged node
                elif obj.d:
                    obj.move(dmx, dmy)
            except AttributeError:
                pass

            #  Connecting nodes
            if not skipConnect:
                try:
                    #  If no node is selected, selects one
                    if obj.type == BASE_NODE_STR and obj.clicked and selectedNode == (-1, -1, -1, -1):
                        selectedNode = (0, obj.id, obj.x, obj.y)
                        ib.hide = False
                        nt.textUpdate('Selected Node: ' + str(obj.id))
                        nt.hide = False
                        cit.textUpdate('Node CI: ' + str(obj.ci))
                        cit.hide = False
                        for ob in menuArr:
                            if type(ob) == TexturedObject and ob.name == 'Title':
                                ob.hide = True

                    #  If node is selected and current clicked node is not that one then connects
                    elif obj.type == BASE_NODE_STR and obj.clicked and selectedNode != (0, obj.id, obj.x, obj.y):
                        if obj.id not in connections[selectedNode[1]]:
                            objectArr.append(Line(selectedNode[2] + obj.r, selectedNode[3] + obj.r, obj.x + obj.r, obj.y + obj.r, (0, 0, 0), 5))
                            skipConnect = True
                            connections[selectedNode[1]].append(obj.id)
                            connections[obj.id].append(selectedNode[1])
                            connectionsList.append([obj.id, selectedNode[1]])
                            selectedNode = (-1, -1, -1, -1)
                            ib.hide = True
                            nt.hide = True
                            cit.hide = True
                            for ob in menuArr:
                                if type(ob) == TexturedObject and ob.name == 'Title':
                                    ob.hide = False
                            editedGraph = True
                except AttributeError:
                    pass

            #  Adding node
            if type(obj) == TexturedObject:
                #  Checking if 'Add_node' button is clicked and no node is added right then
                if obj.name == 'Add_node' and obj.clicked and draggedNode == (-1, -1):
                    #  Moves cursor to middle of map
                    mouse.set_pos(475, 360)
                    #  Creates node object
                    newNode = Node(475, 360, 12, BASE_NODE_STR, ID)
                    #  Adds node object to render array
                    objectArr.append(newNode)
                    #  Setting values to know which node is currently added
                    newNode.d = True
                    draggedNode = (0, ID)
                    skipMove = True
                    connections.append([])
                    ID += 1

            #  Deselect node
            if type(obj) == TexturedObject and obj.name == 'Deselect' and obj.clicked:
                selectedNode = (-1, -1, -1, -1)
                ib.hide = True
                nt.hide = True
                cit.hide = True
                for ob in menuArr:
                    if type(ob) == TexturedObject and ob.name == 'Title':
                        ob.hide = False

            #  Text
            #  Updates currently selected text
            if updatedText:
                if type(obj) == InputBox and obj.clicked:
                    obj.textUpdate(currentText)
                    updatedText = False

            #  Load
            try:
                if obj.name == 'Load' and obj.clicked:
                    n = loadNodes('save1.json')
                    if n:
                        objectArr = n
                    else:
                        objectArr = []
            except AttributeError:
                pass

            #  Save
            try:
                if obj.clicked and obj.name == 'Save':
                    print('hi')
                    a = {'nodes': [], 'connections': connectionsList}
                    for ob in objectArr:
                        if type(ob) == Node:
                            a['nodes'].append([ob.x, ob.y, ob.type, ob.id, ob.v])
                    with open('save1.json', 'w') as F:
                        F.write(json.dumps(a))
            except AttributeError:
                pass

        if editedGraph:
            global visited
            it = 1
            for x in range(1, ID):
                try:
                    if visited[x]:
                        pass
                except KeyError:
                    ss(x, connections, it, objectArr)
                    it += 1
            visited = {}
            editedGraph = False

        #  Updating screen
        dt = clock.tick(60)
        scr.update(menuArr + objectArr, dt)


if __name__ == '__main__':
    main()
