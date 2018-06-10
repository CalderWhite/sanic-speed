import tkinter
import time
from math import sin, cos, pi, sqrt
import win32api
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
        
        # this will be initialized when the object is added to the game
        self.engine = None

    def is_valid(self):
        return True#not(v1 and v2)

    def get_2d_coords(self):
        coords = self.engine.project_line(
            (self.x1,self.y1,self.z1),
            (self.x2,self.y2,self.z2)
        )
        return coords

    def draw(self):
        self.id = self.engine.canvas.create_line(self.get_2d_coords(), fill=self.color,width=1)

class Triangle():
    def __init__(self,v1,v2,v3,color):
        self.color = color

        self.v1 = v1
        self.v2 = v2
        self.v3 = v3

        self.id = None
        # this will be initialized when the object is added to the game
        self.engine = None

    def is_valid(self):
        v1 = self.engine.pos_valid(*self.v1)
        v2 = self.engine.pos_valid(*self.v2)
        v3 = self.engine.pos_valid(*self.v3)
        self.engine.dv = (v1,v2,v3)
        return v1 or v2 or v3

    def get_2d_coords(self):
        coords = (
            self.engine.get2d(*self.v1),
            self.engine.get2d(*self.v2),
            self.engine.get2d(*self.v3)
        )
        return coords

    def draw(self):
        self.id = self.engine.canvas.create_polygon(self.get_2d_coords(),fill=self.color,width=0)

class Engine():
    def __init__(self, canvas):
        # camera rotation
        self.rotz = 0
        self.roty = 0
        # camera coords
        self.x = 0
        self.y = 0
        self.z = 0

        # Field of View
        self.FOV = 400

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

    def rot2d(self,pos,rad):
        x,y=pos
        s,c = sin(rad),cos(rad)

        return x*c-y*s, y*c+x*s
    def get_clip(self,v1,v2):
        x1,y1,z1 = v1
        x2,y2,z2 = v2
        slopex = (x1 - x2)/(z1 - z2)
        bx = ((x1+x2)-slopex*(z1+z2))/2

        slopey = (y1 - y2)/(z1 - z2)
        by = ((y1+y2)-slopey*(z1+z2))/2

        #self.dv = (x1-x2,y1-y2,z1-z2)
        z = 0.001

        return (bx,by,z)
    def modify_point(self,v):
        x,y,z = v
        # move the point basd on the camera's position
        x -= self.x
        y -= self.y
        z -= self.z
        # rotate on both axis
        x,z = self.rot2d((x,z),self.rotz)
        y,z = self.rot2d((y,z),self.roty)

        return (x,y,z)
    def project_line(self,v1,v2):
        """Project a 3d line onto a 2d plane."""
        v1 = self.modify_point(v1)
        v2 = self.modify_point(v2)

        # debugging
        try:
            if v1[2] < 0:
                v1 = self.get_clip(v1,v2)
            elif v2[2] < 0:
                v2 = self.get_clip(v2,v1)
        except ZeroDivisionError:
            pass

        f1 = self.FOV/v1[2]
        p1 = (v1[0]*f1 + WIDTH/2,-v1[1]*f1 + HEIGHT/2)

        f2 = self.FOV/v2[2]
        p2 = (v2[0]*f2 + WIDTH/2,-v2[1]*f2 + HEIGHT/2)

        return (p1,p2)

    def render_objects(self):
        self.dv = False
        for i in range(len(self.objects)):
            if self.objects[i].is_valid():
                self.objects[i].draw()
    
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
            16 : self.down, # SHIFT
            32 : self.up, # SPACE
            27: self.stop, # ESC
            82: self.reset # r
        }
        # methods to be run once a key has stopped being pressed
        self.key_up_mapping = {
            87 : self.kill_zvelocity,
            83 : self.kill_zvelocity,
            65 : self.kill_xvelocity,
            68 : self.kill_xvelocity,
            16 : self.kill_yvelocity,
            32 : self.kill_yvelocity
        }
        # event bindings
        self.canvas.bind("<KeyPress>",self.keydown)
        self.canvas.bind("<KeyRelease>",self.keyup)
        self.canvas.bind("<Motion>",self.rot)

        # player init values
        self.xvelocity = 0
        self.zvelocity = 0
        self.yvelocity = 0
        self.speed = 0.25

        # game stats
        self.fps = 0
        self.mousex = 0
        self.mousey = 0
        #self.rot_speed = pi/(180*20)
        
        # init canvas
        self.canvas.pack()
        self.canvas.focus_set()

    def reset(self):
        self.engine.roty = 0
        self.engine.rotz = 0

    def up(self):
        self.yvelocity = self.speed * (4000/self.fps)

    def down(self):
        self.yvelocity = -self.speed * (4000/self.fps)

    def stop(self):
        self.root.destroy()
        self.stopped = True
        sys.exit(0)

    def rot(self,event):
        win32api.SetCursorPos((int(WIDTH/2),int(HEIGHT/2)))
        x,y = event.x, event.y
        self.mousex += x - WIDTH/2
        self.mousey += y - HEIGHT/2

        self.engine.rotz = self.mousex*(pi*2/WIDTH) 
        self.engine.roty = -(self.mousey*(pi*2/HEIGHT))

    def forward(self):
        self.zvelocity = self.speed * (4000/self.fps)

    def backward(self):
        self.zvelocity = -self.speed * (4000/self.fps)

    def right(self):
        self.xvelocity = self.speed * (4000/self.fps)

    def left(self):
        self.xvelocity = -self.speed * (4000/self.fps)

    def kill_zvelocity(self):
        self.zvelocity = 0

    def kill_xvelocity(self):
        self.xvelocity = 0

    def kill_yvelocity(self):
        self.yvelocity = 0

    def update_pos(self):
        xv, zv, yv = self.xvelocity, self.zvelocity, self.yvelocity
        rotz = self.engine.rotz
        self.engine.x += zv*sin(rotz) + xv*cos(rotz)
        self.engine.z += zv*cos(rotz) - xv*sin(rotz)
        self.engine.y += yv
        
    def add_object(self,obj):
        obj.engine = self.engine
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
        win32api.SetCursorPos((int(WIDTH/2),int(HEIGHT/2)))

        _id = self.canvas.create_text(10,10,text="",font="ansifixed",anchor="w")
        rottext = self.canvas.create_text(10,20,text="",font="ansifixed",anchor="w")
        rottext1 = self.canvas.create_text(10,30,text="",font="ansifixed",anchor="w")
        out = self.canvas.create_text(10,40,text="",font="ansifixed",anchor="w")
        out2 = self.canvas.create_text(10,50,text="",font="ansifixed",anchor="w")
        keytext = self.canvas.create_text(10,60,text="",font="ansifixed",anchor="w")

        self.engine.jiggy = None
        while not self.stopped:
            # update the keys that are down
            self.run_key_events()
            # move the player based
            self.update_pos()
            # update the tkinter buffer
            self.render()
            #time.sleep(0.03)
            t2 = time.clock()
            self.fps = 1/(t2-t)
            self.canvas.itemconfig(_id,text="fps: " + str(self.fps))
            self.canvas.itemconfig(rottext,text="rotz: " + str(self.engine.rotz))
            self.canvas.itemconfig(rottext1,text="roty: " + str(self.engine.roty))
            self.canvas.itemconfig(out,text="Out of Bounds: " + str(self.engine.dv))
            self.canvas.itemconfig(out2,text="f: " + str(self.engine.jiggy))
            self.canvas.itemconfig(keytext,text="keys: " + str(self.keys_down))

            # update the tkinter window (draw the buffer to the display)
            self.root.update()
            t = time.clock()

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
    l = Line(0,0,5,30,10,5,"black")
    g.add_object(l)
    """
    t = Triangle((10,0,20),(100,40,105),(200,0,20),"black")
    g.add_object(t)
    t = Triangle((10,0,210),(100,40,105),(200,0,210),"red")
    g.add_object(t)
    t = Triangle((10,0,20),(100,40,105),(10,0,210),"blue")
    g.add_object(t)
    t = Triangle((200,0,20),(100,40,105),(200,0,210),"yellow")
    g.add_object(t)
    """
def runGame():
    global g
    g.run()
setInitialValues()
try:
    runGame()
except SystemExit:
    pass
