import math
from graphics_objects import Polygon

class SpaceShip():
    def __init__(self,pos,speed,rot_velocity,engine,model):

    	# init camera related values
        self.x = 0
        self.y = 0
        self.z = 0

        self.rotz = 0
        self.roty = 0
        self.rotx = 0

        self.xvelocity = 0
        self.zvelocity = 0
        self.yvelocity = 0

        self.deceleration = 0.9
        self.acceleration = 1.75

        self.xdeceleration = 0.75
        self.xacceleration = 1.5
        self.xmax_velocity = 10


        self.base_speed = 0.5
        self.max_velocity = 20
        self.min_velocity = 0.1#self.base_speed

        # init movement related values
        self.speed = speed
        self.rot_velocity = rot_velocity

        # I apologize for this ugly backwards dependancy
        self.engine = engine

        self.object = model

        x = []
        y = []
        z = []
        for p in model.polygons:
            for i in p.verticies:
                x.append(i[0])
                y.append(i[1])
                z.append(i[2])

        self.lowerx = min(x)
        self.upperx = max(x)
        self.lowery = min(y)
        self.uppery = max(y)
        self.lowerz = min(z)
        self.upperz = max(z)

        self.polygons = []

        for i in self.object.polygons:
        	p = Polygon(i.verticies,i.color)
        	p.set_engine(engine)
        	p.set_dynamic(True)

        	self.polygons.append(p)

    def get_polygons(self):
    	return self.polygons

    def rot_up(self):
        self.roty += self.get_adjusted_speed(self.rot_velocity)
    def rot_down(self):
        self.roty -= self.get_adjusted_speed(self.rot_velocity)
    def rot_left(self):
        self.rotz -= self.get_adjusted_speed(self.rot_velocity)
    def rot_right(self):
        self.rotz += self.get_adjusted_speed(self.rot_velocity)
    def up(self):
        self.yvelocity = self.get_adjusted_speed(self.speed)

    def down(self):
        self.yvelocity = -self.get_adjusted_speed(self.speed)

    def rot(self,event):
        win32api.SetCursorPos((int(WIDTH/2),int(HEIGHT/2)))
        x,y = event.x, event.y
        self.mousex += x - WIDTH/2
        self.mousey += y - HEIGHT/2

        self.rotz = self.mousex*(math.pi*2/WIDTH) 
        self.roty = -(self.mousey*(math.pi*2/HEIGHT))

    def forward(self):
        v = self.zvelocity

        if v == 0:
            v = self.acceleration
        elif v < -1:
            v *= self.deceleration
        elif v < 0:
            v = self.base_speed
        else:
            v *= self.acceleration

        self.zvelocity = min(v,self.max_velocity)

    def backward(self):
        v = self.zvelocity

        if v == 0:
            v = -self.base_speed
        elif v > 1:
            v *= self.deceleration
        elif v > 0:
            v = -self.base_speed
        else:
            v *= self.acceleration

        self.zvelocity = max(v,-self.max_velocity)
    def right(self):
        v = self.xvelocity

        if v == 0:
            v = self.xacceleration
        elif v < -1:
            v *= self.xdeceleration
        elif v < 0:
            v = self.base_speed
        else:
            v *= self.xacceleration

        self.xvelocity = min(v,self.xmax_velocity)

    def left(self):
        v = self.xvelocity

        if v == 0:
            v = -self.base_speed
        elif v > 1:
            v *= self.xdeceleration
        elif v > 0:
            v = -self.base_speed
        else:
            v *= self.xacceleration

        self.xvelocity = max(v,-self.xmax_velocity)

    def kill_zvelocity(self):
        #self.zvelocity = 0
        pass

    def kill_xvelocity(self):
        #self.xvelocity = 0
        pass

    def kill_yvelocity(self):
        self.yvelocity = 0

    def update_pos(self):
        """
        Update the camera's position based velocity, 
        as well as incorperating the direction to make xz axis movement feel natural.
        """
        xv, zv, yv = self.xvelocity, self.zvelocity, self.yvelocity
        rotz = self.rotz
        self.x += zv*math.sin(rotz) + xv*math.cos(rotz)
        self.z += zv*math.cos(rotz) - xv*math.sin(rotz)
        self.y += yv
    def update(self):
        self.zvelocity *= self.deceleration
        self.xvelocity *= self.deceleration

        if abs(self.zvelocity) < self.min_velocity:
            self.zvelocity = 0
        if abs(self.xvelocity) < self.min_velocity:
            self.xvelocity = 0

        # calculate values for fancy ship rotation

        # find the mid point of the xy axis to rotate around
        midx = (self.upperx-self.lowerx)/2
        midy = (self.uppery-self.lowery)/2
        midz = (self.upperz-self.lowerz)*0.75
        # calculate the x rotation based on the velocity
        # and don't let it exceed 90 degrees
        xrot = -self.xvelocity * (0.5*math.pi/self.max_velocity)
        xrot = max(xrot,-0.5*math.pi)
        xrot = min(xrot,0.5*math.pi)

        # calculate the z rotation.
        # only rotate backwards if the ship is trying to go backwards
        zrot = self.zvelocity * (0.5*math.pi/self.max_velocity)
        zrot = min(zrot,0.05*math.pi)
        zrot = max(zrot,-0.1*math.pi)

        for p in range(len(self.polygons)):
            ref = self.object.polygons[p]
            for i in range(len(self.polygons[p].verticies)):
                x = self.polygons[p].verticies[i][0] = ref.verticies[i][0]
                y = self.polygons[p].verticies[i][1] = ref.verticies[i][1]
                z = self.polygons[p].verticies[i][2] = ref.verticies[i][2]

                # fancy rotation based on x/z velocity

                # in order to rotate around that point, we have to move it to the origin
                x -= midx
                y -= midy
                z -= midz

                # rotate the points
                x,y = self.engine.rot2d((x,y),xrot)
                y,z = self.engine.rot2d((y,z),zrot)

                # move back to the point of rotation
                x += midx
                y += midy
                z += midz

                x += self.x
                y += self.y
                z += self.z

                self.polygons[p].verticies[i][0] = x
                self.polygons[p].verticies[i][1] = y
                self.polygons[p].verticies[i][2] = z
            self.polygons[p].set_engine(self.engine)