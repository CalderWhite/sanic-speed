import tkinter
import time
import math
import win32api
import sys
import bisect

# constants
WIDTH = 600
HEIGHT = 600

class Line():
    def __init__(self, v1, v2, color):
        self.color = color
        
        self.v1 = v1
        self.v2 = v2

        self.coords_cache = []

        self.id = None
        
        # this will be initialized when the object is added to the game
        self.engine = None

    def update_pos(self):
        self.coords_cache = []
        self.coords_cache += [
            self.engine.modify_point(self.v1),
            self.engine.modify_point(self.v2)
        ]
    def get_2d_coords(self):
        coords = self.engine.project_line(
            self.coords_cache[0],
            self.coords_cache[1]
        )
        return coords

    def draw(self):
        coords = self.get_2d_coords()
        if coords != None:
            self.id = self.engine.canvas.create_line(coords, fill=self.color,width=1)

class Polygon():
    def __init__(self,verticies,color):
        self.color = color

        self.verticies = verticies

        self.coords_cache = []

        self.id = None
        # this will be initialized when the object is added to the game
        self.engine = None

    def update_pos(self):
        """Update the coordinate cache based on the engine's camera position/rotation."""
        self.coords_cache = []
        for i in self.verticies:
            self.coords_cache.append(
                self.engine.modify_point(i)
            )

    def get_2d_coords(self):
        """Returns a list of coordinates that are projected onto the screen. Given that (0,0) is the top left."""

        coords = []
        for i in range(len(self.verticies)):
            projected = self.engine.project_line(
                self.coords_cache[i],
                self.coords_cache[(i+1) % len(self.coords_cache)],
                polygon=True
            )
            if projected != None:
                coords += projected
        if coords == []:
            return None

        return coords

    def draw(self):
        """Render the object to the tkinter screen."""
        coords = self.get_2d_coords()
        if coords != None:
            self.id = self.engine.canvas.create_polygon(coords,fill=self.color,width=1)

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

        # the farthest a line/polygon can be rendered outside of the tkinter window before the engine begins clipping it
        self.SCREEN_CLIP_MAX = 5000

        self.canvas = canvas
        self.objects = []

    def add_object(self, obj):
        self.objects.append(obj)

    def clear(self):
        # clear the screen
        # TODO: this isn't really efficient. It's better to configure them / change coords
        for i in range(len(self.objects)):
            if type(self.objects[i].id) == list:
                for j in self.objects[i].id:
                    self.canvas.delete(j)
                self.objects[i].id = []
            else:
                self.canvas.delete(self.objects[i].id)
                self.objects[i].id = None

    def set_coords(self,x,y,z):
        # update the coordinates of the camera
        self.x = x
        self.y = y
        self.z = z

    def rot2d(self,pos,rad):
        x,y=pos
        s,c = math.sin(rad),math.cos(rad)

        return x*c-y*s, y*c+x*s
    def clip_3d_line(self,v1,v2):
        """Calder White's proprietary method for finding the intersection of a line and the z axis."""
        x1,y1,z1 = v1
        x2,y2,z2 = v2
        slopex = (x1 - x2)/(z1 - z2)
        bx = ((x1+x2)-slopex*(z1+z2))/2

        slopey = (y1 - y2)/(z1 - z2)
        by = ((y1+y2)-slopey*(z1+z2))/2

        # in the famous words of Mr. Schattman, graphics is just a series of optical illusions and cheating
        z = 0.001

        return (bx,by,z)
    def clip_2d_line(self,v1,v2):
        """Clips a 2d line to a built in max and min for x and y."""
        x1,y1 = v1
        x2,y2 = v2

        slope = (y1 - y2)/(x1 - x2)
        b = (y1+y2-slope*(x1+x2))/2

        constant = self.SCREEN_CLIP_MAX
        if y1 > HEIGHT:
            y1 = HEIGHT + constant
            if slope != 0:
                # if the slope is 0, no modification to x is required
                x1 = (y1-b)/slope
        if y1 < 0:
            y1 = -constant
            # if the slope is 0, no modification to x is required
            if slope != 0:
                x1 = (y1-b)/slope

        if x1 > WIDTH:
            x1 = WIDTH + constant
            y1 = slope*x1 + b
        if x1 < 0:
            x1 = -constant
            y1 = slope*x1 + b

        return ((x1,y1),(x2,y2))

    def modify_point(self,v):
        """
        Adjusts a vertex's position based on the camera's position and rotation.
        """
        x,y,z = v
        # move the point basd on the camera's position
        x -= self.x
        y -= self.y
        z -= self.z
        # rotate on both axis
        x,z = self.rot2d((x,z),self.rotz)
        y,z = self.rot2d((y,z),self.roty)

        return (x,y,z)
    def project_line(self,v1,v2,polygon=False):
        """
        Project a 3d line onto a 2d plane and z axis clipping.
        Also clips to a built in max/min for the 2d coordinates to compensate for a tkinter create_polygon bug.
        """

        # debugging
        try:
            # don't render a line that's out of screen
            if v1[2] < 0 and v2[2] < 0:
                return None
            elif v1[2] < 0:
                v1 = self.clip_3d_line(v1,v2)
            elif v2[2] < 0:
                v2 = self.clip_3d_line(v2,v1)
        except ZeroDivisionError:
            pass
        # incorperate z and field of view,
        # then move points to originate from the center of the screen, since that's what the algorithm
        # is designed to generate points for
        f1 = self.FOV/v1[2]
        p1 = (v1[0]*f1 + WIDTH/2,-v1[1]*f1 + HEIGHT/2)

        f2 = self.FOV/v2[2]
        p2 = (v2[0]*f2 + WIDTH/2,-v2[1]*f2 + HEIGHT/2)

        # if the line is for a polygon, clip the 2d version as well, since there is a tkinter error with very large 
        # numbers that need to be clipped. (So we do it our selves)
        if polygon:
            p1,p2 = self.clip_2d_line(p1,p2)
            p2,p1 = self.clip_2d_line(p2,p1)

        return (p1,p2)

    def render_objects(self):
        """Sorts faces and then draws the sorted faces onto the tkinter canvas."""
        # sort the faces first
        sorted_faces = []
        sorted_z_values = []
        for face in self.objects:
            # modify the coords based on the camera
            face.update_pos()

            # get the highest z value of the face
            z = face.coords_cache[0][2]
            for i in face.coords_cache:
                if i[2] > z:
                    z = i[2]

            # find the index that it should be inserted at in the sorted list of z values
            i = bisect.bisect_left(sorted_z_values,z)

            # insert it 
            sorted_z_values.insert(i,z)
            sorted_faces.insert(i,face)
        # then render them
        for i in range(len(sorted_faces)-1,-1,-1):
            sorted_faces[i].draw()
    
class Game():
    def __init__(self,root,canvas):
        # tkinter properties that are passed down
        self.root = root
        self.canvas = canvas
        # 3d graphics engine
        self.engine = Engine(self.canvas)
        self.stopped = False

        # settings values
        self.fps_speed_adjustment = 4000

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
        self.speed = 0.1

        # game stats
        self.fps = 0
        self.mousex = 0
        self.mousey = 0
        
        # init canvas
        self.canvas.pack()
        self.canvas.focus_set()

    def reset(self):
        self.engine.roty = 0
        self.engine.rotz = 0

    def get_adjusted_speed(self):
        """Returns the speed adjusted to the frame rate, so if frames drop or spike, the in game speed remains the same."""
        # for whatever reason, I've found that the relationship between speed and fps
        # does not feel normal when it is linear, so I've played around and landed on this equation that feels natural
        return self.speed * math.sqrt(self.fps_speed_adjustment/self.fps**1.05)

    def up(self):
        self.yvelocity = self.get_adjusted_speed()

    def down(self):
        self.yvelocity = -self.get_adjusted_speed()

    def stop(self):
        self.root.destroy()
        self.stopped = True
        sys.exit(0)

    def rot(self,event):
        win32api.SetCursorPos((int(WIDTH/2),int(HEIGHT/2)))
        x,y = event.x, event.y
        self.mousex += x - WIDTH/2
        self.mousey += y - HEIGHT/2

        self.engine.rotz = self.mousex*(math.pi*2/WIDTH) 
        self.engine.roty = -(self.mousey*(math.pi*2/HEIGHT))

    def forward(self):
        self.zvelocity = self.get_adjusted_speed()

    def backward(self):
        self.zvelocity = -self.get_adjusted_speed()

    def right(self):
        self.xvelocity = self.get_adjusted_speed()

    def left(self):
        self.xvelocity = -self.get_adjusted_speed()

    def kill_zvelocity(self):
        self.zvelocity = 0

    def kill_xvelocity(self):
        self.xvelocity = 0

    def kill_yvelocity(self):
        self.yvelocity = 0

    def update_pos(self):
        """
        Update the camera's position based velocity, 
        as well as incorperating the direction to make xz axis movement feel natural.
        """
        xv, zv, yv = self.xvelocity, self.zvelocity, self.yvelocity
        rotz = self.engine.rotz
        self.engine.x += zv*math.sin(rotz) + xv*math.cos(rotz)
        self.engine.z += zv*math.cos(rotz) - xv*math.sin(rotz)
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

        fps_text = self.canvas.create_text(10,10,text="",font="ansifixed",anchor="w",fill="white")

        while not self.stopped:
            # update the keys that are down
            self.run_key_events()
            # move the player based
            self.update_pos()
            # update the tkinter buffer
            self.render()

            # updating fps
            t2 = time.clock()
            self.fps = 1/(t2-t)

            # debugging messages
            self.canvas.itemconfig(fps_text,text="fps: " + str(int(self.fps)))
            # keep track of time for fps
            t = time.clock()
            # update the tkinter window (draw the buffer to the display)
            self.root.update()

def setInitialValues():
    global g, WIDTH, HEIGHT
    fullscreen = True

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
    g = Game(root,s)

    # add testing objects
    t = Line((10,0,300),(10,20,300),"orange")
    g.add_object(t)
    t = Polygon(((10,0,20),(100,40,105),(200,0,20)),"red")
    g.add_object(t)
    t = Polygon(((10,0,20),(100,40,105),(10,0,200)),"blue")
    g.add_object(t)

def runGame():
    global g
    g.run()

setInitialValues()
try:
    runGame()
except SystemExit:
    pass
 
