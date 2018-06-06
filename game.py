from tkinter import Tk, Canvas
from math import sin, cos
import sys

# constants
WIDTH = 600
HEIGHT = 600

class Line():
    def __init__(self,x1,y1,z1,x2,y2,z2, color):
        self.color = color
        
        self.x1 = x1
        self.y1 = y1
        self.z1 = z1

        self.x2 = x2
        self.y2 = y2
        self.z2 = z2

        self.id = None
    def get_2d_coords(self,engine):
        coords = (
            engine.get2d(self.x1, self.y1, self.z1),
            engine.get2d(self.x2, self.y2, self.z2)
        )
        return coords
    
class Engine():
    def __init__(self, canvas):
        self.roty = 0
        self.x = 0
        self.y = 0
        self.z = 0

        self.canvas = canvas
        self.objects = []
    def add_object(self, obj):
        self.objects.append(obj)
    def clear(self):
        # clear the screen
        # TODO: this isn't really efficient. It's better to configure them / change coords
        for i in range(len(self.objects)):
            self.canvas.delete(self.objects[i].id)
            self.objects[i].id = None
    def set_coords(self,x,y,z):
        # update the coordinates of the player
        self.x = x
        self.y = y
        self.z = z
    def object_is_valid(self,i):
        obj = self.objects[i]
        return obj.z1 - self.z != 0 and obj.z2 - self.z != 0
    def get2d(self,x,y,z):
        # implement rotation
        #z = z*cos(self.roty) - x*sin(self.roty)
        #x = z*sin(self.roty) + x*cos(self.roty)
        # factor in user player position
        x -= self.x
        y -= self.y
        z -= self.z
        # convert to 2d
        outx = x/z
        outy = y/z

        # convert to 1 quadrant coords (the formula is for 4 quadrant coords)
        outx = int(outx + WIDTH/2)
        outy = int(-outy + HEIGHT/2)
        return (outx,outy)
    def draw_line(self, line):
        return self.canvas.create_line(line.get_2d_coords(self), fill=line.color,width=1)
    def render_objects(self):
        for i in range(len(self.objects)):
            if self.object_is_valid(i):
                self.objects[i].id = self.draw_line(self.objects[i])
    
class Game():
    def __init__(self,root,canvas):
        # tkinter properties that are passed down
        self.root = root
        self.canvas = canvas
        # 3d graphics engine
        self.engine = Engine(self.canvas)

        # key bindings / checking
        self.keys_down = []
        self.key_mapping = {
            87 : self.forward, # w
            83 : self.backward, # s
            65 : self.left, # a
            68 : self.right # d
        }
        # methods to be run once a key has stopped being pressed
        self.key_up_mapping = {
            87 : self.kill_zvelocity,
            83 : self.kill_zvelocity,
            65 : self.kill_xvelocity,
            68 : self.kill_xvelocity
        }
        # event bindings
        self.canvas.bind("<KeyPress>",self.keydown)
        self.canvas.bind("<KeyRelease>",self.keyup)

        # player init values
        self.xvelocity = 0
        self.zvelocity = 0
        self.speed = 0.01
        
        # init canvas
        self.canvas.pack()
        self.canvas.focus_set()

    def forward(self):
        self.zvelocity = self.speed*0.1
    def backward(self):
        self.zvelocity = -self.speed*0.1
    def right(self):
        self.xvelocity = self.speed*10
    def left(self):
        self.xvelocity = -self.speed*10
    def kill_zvelocity(self):
        self.zvelocity = 0
    def kill_xvelocity(self):
        self.xvelocity = 0
    def update_pos(self):
        self.engine.z += self.zvelocity
        self.engine.x += self.xvelocity
        
    def add_object(self,obj):
        self.engine.add_object(obj)
    def run_key_events(self):
        for i in self.keys_down:
            if i in self.key_mapping:
                self.key_mapping[i]()
    def keydown(self,event):
        """Appends key codes that are being pressed into the object's list, if they are not already there."""
        if event.keycode not in self.keys_down:
            self.keys_down.append(event.keycode)
    def keyup(self,event):
        """Removes key codes that are being pressed when the keys are released."""
        k = event.keycode
        if k in self.keys_down:
            if k in self.key_up_mapping:
                self.key_up_mapping[k]()
            self.keys_down.remove(k)
    def render(self):
        # clear the current screen
        self.engine.clear()
        # re load all the objects
        self.engine.render_objects()
    def run(self):
        while True:
            #print(self.keys_down)
            
            # update the keys that are down
            self.run_key_events()
            # move the player based
            self.update_pos()
            # update the tkinter buffer
            self.render()
            # update the tkinter window (draw the buffer to the display)
            self.root.update()
        pass
def setInitialValues():
    global g
    root = Tk()
    s = Canvas(root, width=WIDTH, height=HEIGHT, background="white")
    g = Game(root,s)
    l = Line(10,0,5,100,40,5,"black")
    g.add_object(l)
    l = Line(100,40,5,200,0,5,"black")
    g.add_object(l)
    l = Line(200,0,5,10,0,5,"black")
    g.add_object(l)
def runGame():
    global g
    g.run()
setInitialValues()
runGame()
