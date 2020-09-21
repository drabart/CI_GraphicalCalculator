import json

from classes import *
from constants import *
from pygame import *
from sys import exit
from copy import deepcopy


def loadNodes(file):
    arr = []

    with open(file, 'r') as F:

        rawObjects = json.load(F)
        print(rawObjects)
        rawObjects['nodes'].sort(key=lambda x: x[3])
        print(rawObjects)
        for obj in rawObjects['nodes']:
            if obj[2] == BASE_NODE_STR:
                r = 24
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
            if arr[len(arr)-1].name == "Exit" or arr[len(arr)-1].name == "Node":
                arr[len(arr)-1].hide = True
        del obj

    return arr


def main():
    #  Variables initialization
    if True:
        #  initializing pygame
        init()
        scr = Screen(800, 600, (0, 0, 0))
        clock = time.Clock()

        #  array holding all renderable objects
        menuArr = []
        objectArr = []

        #  loading menu objects
        menuArr += loadMenu()

        Wconnections = [[]]
        WconnectionsList = []

        Infrastructures = [0]

        mx, my = -1, -1
        dmx, dmy = 0, 0
        ID = 1
        NID = 1
        WID = 1
        pastWeatherUpdate = time.get_ticks()
        ln = time.get_ticks()
        currentConnection = 0
        weatherNode = 0

        draggedNode = (-1, -1)  # type, id
        startWeatherNode = (-1, -1)  # type, id

        selectedInput = False
        rButtonDown = False
        skipMove = False
        updatedText = False
        addingWeather = False
        editingSSN = False
        editingPN = False
        editingSR = False
        editingNTW = False
        addingNodes = False
        editingNode = False
        new = False

        currentText = ''
        ib = InputBox(565, 78, 100, 30)
        ib.hide = True
        objectArr.append(ib)
        cit = Text(255, 5, text='Critical Infrastructure  ', size=32)
        cit.hide = True
        menuArr.append(cit)
        cin = Text(255, 83, text='Number of safety states', size=32)
        cin.hide = True
        menuArr.append(cin)
        plt = Text(255, 83, text='Risk function permitted level', size=32)
        plt.hide = True
        menuArr.append(plt)
        srt = Text(255, 83, text='Safety state R', size=32)
        srt.hide = True
        menuArr.append(srt)
        ntwt = Text(255, 84, text='How many assets need to work', size=30)
        ntwt.hide = True
        menuArr.append(ntwt)
        ant = Text(255, 84, text='Add new node', size=30)
        ant.hide = True
        menuArr.append(ant)
        alt = Text(255, 84, text='Asset lifetimes in safety states', size=30)
        alt.hide = True
        menuArr.append(alt)

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
            if eve.type == MOUSEMOTION:
                x, y = eve.pos
                if draggedNode != (-1, -1) or addingWeather:
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

        for obj in menuArr + objectArr:
            #  Click check
            if not addingWeather:
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

            #  ------------------------------------
            #  Nodes
            #  Handling dragged node
            if not addingWeather:
                try:
                    #  'undragging' dragged node
                    if obj.d and draggedNode == (-1, -1):
                        obj.d = False
                        ib.hide = False
                        addingNodes = False
                        editingNode = True
                        alt.hide = False
                    #  moving dragged node
                    elif obj.d:
                        obj.move(dmx, dmy)
                except AttributeError:
                    pass

            #  Adding CI
            if type(obj) == TexturedObject:
                #  Checking if 'Add_node' button is clicked and no node is added right then
                if obj.name == 'Add_CI' and obj.clicked and not new:
                    ci = CriticalInfrastructure()
                    Infrastructures.append(ci)
                    new = True
                    editingSSN = True
                    ib.hide = False
                    cit.textUpdate('Critical Infrastructure  ' + str(ID))
                    cit.hide = False
                    cin.hide = False
                    plt.hide = True
                    srt.hide = True
                    ntwt.hide = True
                    ant.hide = True
                    alt.hide = True
                    for ob in menuArr:
                        if type(ob) == TexturedObject and ob.name == 'Title':
                            ob.hide = True
                        if type(ob) == TexturedObject and ob.name == 'Exit':
                            ob.hide = False
                        if type(ob) == TexturedObject and ob.name == 'Node':
                            ob.hide = False
                    for ob in objectArr:
                        if type(ob) == Node and ob.type == BASE_NODE_STR:
                            ob.ciid = ID
                            ob.updateColor()
                    NID = 1

            #  -------------------------------------
            #  Adding weather process
            #  Moving node
            if True:
                if addingWeather and type(obj) == Node and obj.d and obj.type == PROCESS_NODE_STR:
                    obj.move(dmx, dmy)
                    if currentConnection != 0:
                        currentConnection.p[1][0] += dmx
                        currentConnection.p[1][1] += dmy

                #  Adding first
                if not addingWeather and not new:
                    if type(obj) == TexturedObject:
                        #  Checking if 'Add_process' button is clicked
                        if obj.name == 'Add_process' and obj.clicked and draggedNode == (-1, -1):
                            #  Moves cursor to middle of map
                            mouse.set_pos(475, 360)
                            #  Creates node object
                            newNode = Node(475, 360, 6, PROCESS_NODE_STR, WID)
                            #  Adds node object to render array
                            objectArr.append(newNode)
                            #  Setting values to know which node is currently added
                            newNode.d = True
                            startWeatherNode = (1, WID)
                            skipMove = True
                            Wconnections.append([])
                            WID += 1
                            addingWeather = True
                            pastWeatherUpdate = time.get_ticks()
                            weatherNode = deepcopy(newNode)
                            Wconnections.append([])

                #  Adding next and ending
                elif rButtonDown and pastWeatherUpdate <= time.get_ticks() - 300 and type(obj) == Node and obj.d and obj.type == PROCESS_NODE_STR:
                    e = False
                    for ob in objectArr:
                        if obj != ob and type(ob) == Node and ob.type == PROCESS_NODE_STR and ob.id == startWeatherNode[1] and ob.mouseOver():
                            addingWeather = False
                            objectArr.remove(obj)
                            currentConnection.p[1] = (ob.x + ob.r, ob.y + ob.r)
                            connection = deepcopy(currentConnection)
                            objectArr.remove(currentConnection)
                            objectArr.append(connection)
                            Wconnections[weatherNode.id].append(ob.id)
                            Wconnections[ob.id].append(weatherNode.id)
                            WconnectionsList.append([ob.id, weatherNode.id])
                            e = True
                            currentConnection = 0
                    if not e:
                        obj.d = False
                        newNode = Node(mx, my, 6, PROCESS_NODE_STR, WID)
                        #  Adds node object to render array
                        objectArr.append(newNode)
                        #  Setting values to know which node is currently added
                        newNode.d = True
                        Wconnections.append([])
                        WID += 1
                        pastWeatherUpdate = time.get_ticks()
                        if currentConnection == 0:
                            currentConnection = Line(newNode.x + newNode.r, newNode.y + newNode.r, mx, my, (73, 104, 235), 2)
                            objectArr.append(currentConnection)
                        else:
                            currentConnection.p[1] = (newNode.x + newNode.r, newNode.y + newNode.r)
                            connection = deepcopy(currentConnection)
                            objectArr.remove(currentConnection)
                            objectArr.append(connection)
                            currentConnection = Line(newNode.x + newNode.r, newNode.y + newNode.r, mx, my, (73, 104, 235), 2)
                            objectArr.append(currentConnection)
                            Wconnections[weatherNode.id].append(newNode.id)
                            Wconnections[newNode.id].append(weatherNode.id)
                            WconnectionsList.append([newNode.id, weatherNode.id])
                            weatherNode = deepcopy(newNode)

            #  -------------------------------------
            #  Deselect node
            '''
            if type(obj) == TexturedObject and obj.name == 'Deselect' and obj.clicked:
                ib.hide = True
                cit.hide = True
                cin.hide = True
                ifd.hide = True
                for ob in menuArr:
                    if type(ob) == TexturedObject and ob.name == 'Title':
                        ob.hide = False
                    if type(ob) == TexturedObject and ob.name == 'Infrastructure':
                        ob.hide = True
                    if type(ob) == TexturedObject and ob.name == 'Node':
                        ob.hide = True
            '''

            if type(obj) == Node and obj.clicked and draggedNode == (-1, -1):
                if obj not in Infrastructures[ID].elements:
                    Infrastructures[ID].elements.append(obj)
                    obj.ci.append(ID)
                    obj.updateColor()
                    addingNodes = False
                    ib.hide = False
                    editingNode = True
                    ant.hide = True
                    alt.hide = False

            #  Change input type
            if type(obj) == TexturedObject and obj.name == 'Node' and obj.clicked and ln <= time.get_ticks() - 300:
                if editingSSN:
                    editingSSN = False
                    editingPN = True
                    cin.hide = True
                    plt.hide = False
                elif editingPN:
                    editingPN = False
                    editingSR = True
                    plt.hide = True
                    srt.hide = False
                elif editingSR:
                    editingSR = False
                    editingNTW = True
                    srt.hide = True
                    ntwt.hide = False
                elif editingNTW:
                    editingNTW = False
                    addingNodes = True
                    ntwt.hide = True
                    ant.hide = False
                    ib.hide = True
                elif editingNode:
                    ib.hide = True
                    ant.hide = False
                    addingNodes = True
                    editingNode = False
                    alt.hide = True
                elif addingNodes and draggedNode == (-1, -1):
                    ant.hide = True
                    #  Moves cursor to middle of map
                    mouse.set_pos(475, 360)
                    #  Creates node object
                    newNode = Node(475, 360, 24, BASE_NODE_STR, NID)
                    #  Adds node object to render array
                    newNode.ci.append(ID)
                    newNode.ciid = ID
                    newNode.updateColor()
                    objectArr.append(newNode)
                    #  Setting values to know which node is currently added
                    Infrastructures[ID].elements.append(newNode)
                    newNode.d = True
                    draggedNode = (0, NID)
                    skipMove = True
                    NID += 1
                ln = time.get_ticks()
            # redo to exit
            if type(obj) == TexturedObject and obj.name == 'Exit' and obj.clicked:
                if len(Infrastructures[ID].elements):
                    ID += 1
                else:
                    Infrastructures.pop(len(Infrastructures)-1)
                ib.hide = True
                cit.hide = True
                cin.hide = True
                plt.hide = True
                srt.hide = True
                ntwt.hide = True
                ant.hide = True
                alt.hide = True
                for ob in menuArr:
                    if type(ob) == TexturedObject and ob.name == 'Title':
                        ob.hide = False
                    if type(ob) == TexturedObject and ob.name == 'Exit':
                        ob.hide = True
                    if type(ob) == TexturedObject and ob.name == 'Node':
                        ob.hide = True
                editingSSN = False
                editingPN = False
                editingSR = False
                editingNTW = False
                addingNodes = False
                editingNode = False
                new = False
                for ob in objectArr:
                    if type(ob) == Node and ob.type == BASE_NODE_STR:
                        ob.ciid = 0
                        ob.updateColor()

            if True:
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
                        a = {'nodes': []}
                        for ob in objectArr:
                            if type(ob) == Node:
                                a['nodes'].append([ob.x, ob.y, ob.type, ob.id, ob.v])
                        with open('save1.json', 'w') as F:
                            F.write(json.dumps(a))
                except AttributeError:
                    pass

        #  Updating screen
        dt = clock.tick(60)
        scr.update(menuArr + objectArr, dt)


if __name__ == '__main__':
    main()
