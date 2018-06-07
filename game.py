import tkinter
import time
from math import sin, cos, pi, sqrt
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
    def pos_valid(self,x,y,z):
        x -= self.x
        y -= self.y
        z -= self.z
        
        x,z = self.rot2d((x,z),self.roty)
        return z > 0
    def object_is_valid(self,i):
        obj = self.objects[i]
        v1 = self.pos_valid(obj.x1,obj.y1,obj.z1) > 0
        v2 = self.pos_valid(obj.x2,obj.y2,obj.z2) > 0
        
        return v1 and v2
    def rot2d(self,pos,rad):
        x,y=pos
        s,c = sin(rad),cos(rad)
        return x*c-y*s, y*c+x*s
    def get2d(self,x,y,z):
        # implement rotation
        #print(x,z)
        # factor in user player position
        x -= self.x
        y -= self.y
        z -= self.z
        
        x,z = self.rot2d((x,z),self.roty)
        # convert to 2d
        #outx = x/z
        #outy = y/z
        f = 200/z
        outx = x*f
        outy = y*f

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
        self.stopped = False

        # key bindings / checking
        self.keys_down = []
        self.key_mapping = {
            87 : self.forward, # w
            83 : self.backward, # s
            65 : self.left, # a
            68 : self.right, # d
            27: self.stop # ESC
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
        self.canvas.bind("<Motion>",self.rot)
        self.canvas.bind("<1>",self.test)
        self.canvas.bind("<Double-1>",self.t2)

        # player init values
        self.xvelocity = 0
        self.zvelocity = 0
        self.speed = 0.1

        self.mousex = 0
        self.mousey = 0
        #self.rot_speed = pi/(180*20)
        
        # init canvas
        self.canvas.pack()
        self.canvas.focus_set()
    def stop(self):
        self.root.destroy()
        self.stopped = True
        sys.exit(0)
    def rot(self,event):
        x,y = event.x, event.y
        self.mousey += event.y
        self.engine.roty = -x*(pi*2/WIDTH)
    def forward(self):
        self.zvelocity = self.speed
    def backward(self):
        self.zvelocity = -self.speed
    def right(self):
        self.xvelocity = self.speed
    def left(self):
        self.xvelocity = -self.speed
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
        t = time.clock()
        _id = self.canvas.create_text(10,10,text="",font="ansifixed",anchor="w")
        while not self.stopped:
            #print(self.keys_down)
            # update the keys that are down
            self.run_key_events()
            # move the player based
            self.update_pos()
            # update the tkinter buffer
            self.render()
            t2 = time.clock()
            fps = 1/(t2-t)
            self.canvas.itemconfig(_id,text="fps: " + str(fps))
            # update the tkinter window (draw the buffer to the display)
            self.root.update()
            t = time.clock()
        pass

def setInitialValues():
    global g, WIDTH, HEIGHT
    fullscreen = True
    root = tkinter.Tk()
    if fullscreen:
        root.attributes('-fullscreen',True)
        WIDTH = root.winfo_screenwidth()
        HEIGHT = root.winfo_screenheight()
    s = tkinter.Canvas(root,
                       width=WIDTH,
                       height=HEIGHT,
                       background="white",
                       cursor="none"
    )
    g = Game(root,s)
    #l = Line(0,0,5,0,100,5,"black")
    #g.add_object(l)
    l = Line(10,0,20,100,40,20,"black")
    g.add_object(l)
    l = Line(100,40,20,200,0,20,"black")
    g.add_object(l)
    l = Line(200,0,20,10,0,20,"black")
    g.add_object(l)
def runGame():
    global g
    g.run()
setInitialValues()
try:
    runGame()
except SystemExit:
    pass
