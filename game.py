import tkinter
import time
import math
import sys

from graphics_objects import Line, Polygon, ObjectFile
from graphics import Engine
from spaceship import SpaceShip

# constants
WIDTH = 600
HEIGHT = 600

class Asteroid():
    def __init__(self,polygons):
        self.polygons = polygons
    def get_polygons(self):
        return self.polygons
    def init(self,engine):
        for i in range(len(self.polygons)):
            self.polygons[i].set_engine(engine)
    def update(self):
        pass
    
class Game():
    def __init__(self,root,canvas,cursor_scroll=False):
        # tkinter properties that are passed down
        self.root = root
        self.canvas = canvas
        # 3d graphics engine
        self.engine = Engine(self.canvas,WIDTH,HEIGHT)
        self.stopped = False

        self.cursor_scroll = cursor_scroll

        ### BEGIN SETTINGS values ###
        self.fps_speed_adjustment = 4000

        # movement
        self.speed = 1
        self.rot_velocity = math.pi/180/5
        self.noclip = False
        ###  END SETTINGS values  ###

        self.objects = []

        # key bindings / checking
        self.keys_down = []
        self.key_mapping = {
            87 : self.forward, # w
            83 : self.backward, # s
            65 : self.left, # a
            68 : self.right, # d
            16 : self.down, # SHIFT
            32 : self.up, # SPACE
            27 : self.stop, # ESC
            82 : self.reset, # r
            37 : self.rot_left,
            39 : self.rot_right,
            38 : self.rot_up,
            40: self.rot_down
        }

        # methods to be run once a key has stopped being pressed
        self.key_up_mapping = {
            87 : self.kill_zvelocity,
            83 : self.kill_zvelocity,
            65 : self.kill_xvelocity,
            68 : self.kill_xvelocity,
            16 : self.kill_yvelocity,
            32 : self.kill_yvelocity,
            84 : self.toggle_noclip
        }

        # rotation based on whether or not the mouse will be used
        # event bindings
        self.canvas.bind("<KeyPress>",self.keydown)
        self.canvas.bind("<KeyRelease>",self.keyup)
        if self.cursor_scroll:
            self.canvas.bind("<Motion>",self.rot)

        # camera init values
        self.xvelocity = 0
        self.zvelocity = 0
        self.yvelocity = 0

        # camera's offset from the spaceship's position
        self.xoffset = 10
        self.yoffset = 20
        self.zoffset = -10

        # space ship
        self.ship = SpaceShip(
            (0,0,0),
            self.speed,
            self.rot_velocity,
            self.engine,
            ObjectFile("spaceship.obj",
                scale=0.25,
                pos=(10,0,20)
            )
        )
        self.objects.append(self.ship)

        # game stats
        self.fps = 0
        self.mousex = 0
        self.mousey = 0
        
        # init canvas
        self.canvas.pack()
        self.canvas.focus_set()

    def add_object(self,obj):
        obj.init(self.engine)
        self.objects.append(obj)

    def reset(self):
        self.engine.roty = 0
        self.engine.rotz = 0

    def get_adjusted_speed(self,speed):
        """Returns the speed adjusted to the frame rate, so if frames drop or spike, the in game speed remains the same."""
        # for whatever reason, I've found that the relationship between speed and fps
        # does not feel normal when it is linear, so I've played around and landed on this equation that feels natural
        return speed * math.sqrt(self.fps_speed_adjustment/self.fps)

    def toggle_noclip(self):
        self.noclip = not self.noclip
    def rot_up(self):
        if self.noclip:
            self.engine.roty += self.get_adjusted_speed(self.rot_velocity)
        else:
            self.ship.rot_up()
    def rot_down(self):
        if self.noclip:
            self.engine.roty -= self.get_adjusted_speed(self.rot_velocity)
        else:
            self.ship.rot_down()
    def rot_left(self):
        if self.noclip:
            self.engine.rotz -= self.get_adjusted_speed(self.rot_velocity)
        else:
            self.ship.rot_left()
    def rot_right(self):
        if self.noclip:
            self.engine.rotz += self.get_adjusted_speed(self.rot_velocity)
        else:
            self.ship.rot_right()
    def up(self):
        if self.noclip:
            self.yvelocity = self.get_adjusted_speed(self.speed)
        else:
            self.ship.up()

    def down(self):
        if self.noclip:
            self.yvelocity = -self.get_adjusted_speed(self.speed)
        else:
            self.ship.down()

    def stop(self):
        self.root.destroy()
        self.stopped = True
        sys.exit(0)

    def rot(self,event):
        win32api.SetCursorPos((int(WIDTH/2),int(HEIGHT/2)))
        x,y = event.x, event.y
        self.mousex += x - WIDTH/2
        self.mousey += y - HEIGHT/2
        if self.noclip:
            self.engine.rotz = self.mousex*(math.pi*2/WIDTH) 
            self.engine.roty = -(self.mousey*(math.pi*2/HEIGHT))

    def forward(self):
        if self.noclip:
            self.zvelocity = self.get_adjusted_speed(self.speed)
        else:
            self.ship.forward()

    def backward(self):
        if self.noclip:
            self.zvelocity = -self.get_adjusted_speed(self.speed)
        else:
            self.ship.backward()

    def right(self):
        if self.noclip:
            self.xvelocity = self.get_adjusted_speed(self.speed)
        else:
            self.ship.right()

    def left(self):
        if self.noclip:
            self.xvelocity = -self.get_adjusted_speed(self.speed)
        else:
            self.ship.left()

    def kill_zvelocity(self):
        if self.noclip:
            self.zvelocity = 0
        else:
            self.ship.kill_zvelocity()

    def kill_xvelocity(self):
        if self.noclip:
            self.xvelocity = 0
        else:
            self.ship.kill_xvelocity()

    def kill_yvelocity(self):
        if self.noclip:
            self.yvelocity = 0
        else:
            self.ship.kill_yvelocity()

    def update_pos(self):
        """
        Update the camera's position based velocity, 
        as well as incorperating the direction to make xz axis movement feel natural.
        """
        if self.noclip:
            xv, zv, yv = self.xvelocity, self.zvelocity, self.yvelocity
            rotz = self.engine.rotz
            self.engine.x += zv*math.sin(rotz) + xv*math.cos(rotz)
            self.engine.z += zv*math.cos(rotz) - xv*math.sin(rotz)
            self.engine.y += yv
        else:
            self.ship.update_pos()

    def move_to_ship(self):
        if not self.noclip:
            x = self.ship.x
            y = self.ship.y
            z = self.ship.z

            # rotate camera around ship
            # find the mid point of the xy axis to rotate around
            midx = x + (self.ship.upperx-self.ship.lowerx)/2
            midy = y + (self.ship.uppery-self.ship.lowery)/2
            midz = z + (self.ship.upperz-self.ship.lowerz)*0.75 # slightly off the middle to make it look nicer


            x += self.xoffset
            y += self.yoffset
            z += self.zoffset

            x -= midx
            y -= midy
            z -= midz

            y,z = self.engine.rot2d((y,z),-self.ship.roty)
            x,z = self.engine.rot2d((x,z),-self.ship.rotz)

            x += midx
            y += midy
            z += midz

            self.engine.x = x
            self.engine.y = y
            self.engine.z = z
            
            self.engine.rotz = self.ship.rotz
            self.engine.roty = self.ship.roty

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

    def update_objects(self):
        objects = []
        for o in self.objects:
            o.update()
            objects += o.get_polygons()
        self.engine.update_objects(objects)

    def render(self):
        # clear the current screen
        self.engine.clear()
        # re load all the objects
        self.engine.render_objects()

    def run(self):
        t = time.clock()
        if self.cursor_scroll:
            win32api.SetCursorPos((int(WIDTH/2),int(HEIGHT/2)))

        fps_text = self.canvas.create_text(10,10,text="",font="ansifixed",anchor="w",fill="white")
        zs = self.canvas.create_text(10,20,text="",font="ansifixed",anchor="w",fill="white")
        xs = self.canvas.create_text(10,30,text="",font="ansifixed",anchor="w",fill="white")
        rzs = self.canvas.create_text(10,40,text="",font="ansifixed",anchor="w",fill="white")

        while not self.stopped:
            # update the keys that are down
            self.run_key_events()
            # move the camera/spaceship based on keys
            self.update_pos()
            # move the camera based on the spaceship
            self.move_to_ship()

            # update all objects in the Game and the Engine
            self.update_objects()
            # then render
            self.render()

            # updating fps
            t2 = time.clock()
            self.fps = 1/(t2-t)

            # debugging messages
            self.canvas.itemconfig(fps_text,text="fps: " + str(int(self.fps)))
            self.canvas.itemconfig(zs,text="zs: " + str(self.ship.zvelocity))
            self.canvas.itemconfig(xs,text="xs: " + str(self.ship.xvelocity))
            self.canvas.itemconfig(rzs,text="rzs: " + str(self.ship.rotz_velocity))
            # keep track of time for fps
            t = time.clock()
            # update the tkinter window (draw the buffer to the display)
            self.root.update()

def setInitialValues():
    global g, WIDTH, HEIGHT
    fullscreen = True
    cursor_scroll = True

    if cursor_scroll:
        global win32api
        import win32api
    # create the tkinter window
    root = tkinter.Tk()
    if fullscreen:
        root.attributes('-fullscreen',True)
        WIDTH = root.winfo_screenwidth()
        HEIGHT = root.winfo_screenheight()
    # create the tkinter canvas based on some settings
    s = tkinter.Canvas(root,
                       width=WIDTH,
                       height=HEIGHT,
                       background="black",
                       cursor="none",
                       bd=0,
                       highlightthickness=0,
                       relief="ridge"
    )
    g = Game(root,s,cursor_scroll=cursor_scroll)

    # add testing objects
    #t = Line((10,0,300),(10,20,300),"orange")
    #g.add_object(t)
    colors = ["blue","red","yellow","green"]
    polys = []
    for i in range(40):
        z = i*300 + 60
        polys.append(Polygon(((10,0,z),(100,40,z),(200,0,z)),colors[i%len(colors)]))
    a = Asteroid(polys)
    g.add_object(a)

    #g.add_object(t)
    #t = Polygon(((10,0,20),(100,40,105),(10,0,200)),"blue")
    #g.add_object(t)

    #obj = ObjectFile("spaceship.obj",scale=0.25,pos=(10,0,20))
    #obj.polygons[1].color = "blue"
    #for i in obj.polygons:
        #print(i.verticies)
    #    g.add_object(i)

def runGame():
    global g
    g.run()

setInitialValues()
try:
    runGame()
except SystemExit:
    pass
 
