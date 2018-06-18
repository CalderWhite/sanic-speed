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


        self.rotz_velocity = 0
        self.roty_velocity = 0

        self.deceleration = 0.9
        self.acceleration = 1.75

        self.xdeceleration = 0.75
        self.xacceleration = 1.5
        self.xmax_velocity = 20

        self.rotzbase_speed = 0.5 * (0.5*math.pi/180)

        self.rotzdeceleration = 0.75# * (0.5*math.pi/180)
        self.rotzacceleration = 1.75# * (0.5*math.pi/180)
        self.rotzmax_velocity = 10 * (0.5*math.pi/180)
        self.rotzmin_velocity = 0.01*(0.5*math.pi/180)

        self.rotyacceleration = 1.4
        #self.rotymax_velcoity


        self.base_speed = 0.5
        self.max_velocity = 40
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
        v = self.roty_velocity

        if v == 0:
            v = self.rotzbase_speed
        elif v < -(0.5*math.pi/180):
            v *= self.rotzdeceleration
        elif v < 0:
            v = self.rotzbase_speed
        else:
            v *= self.rotyacceleration

        self.roty_velocity = min(v,self.rotzmax_velocity)

    def rot_down(self):
        v = self.roty_velocity

        if v == 0:
            v = -self.rotzbase_speed
        elif v > (0.5*math.pi/180):
            v *= self.rotzdeceleration
        elif v > 0:
            v = -self.rotzbase_speed
        else:
            v *= self.rotyacceleration
        self.roty_velocity = max(v,-self.rotzmax_velocity)

    def rot_right(self):
        v = self.rotz_velocity

        if v == 0:
            v = self.rotzbase_speed
        elif v < -(0.5*math.pi/180):
            v *= self.rotzdeceleration
        elif v < 0:
            v = self.rotzbase_speed
        else:
            v *= self.rotzacceleration

        self.rotz_velocity = min(v,self.rotzmax_velocity)

    def rot_left(self):
        v = self.rotz_velocity

        if v == 0:
            v = -self.rotzbase_speed
        elif v > (0.5*math.pi/180):
            v *= self.rotzdeceleration
        elif v > 0:
            v = -self.rotzbase_speed
        else:
            v *= self.rotzacceleration
        self.rotz_velocity = max(v,-self.rotzmax_velocity)

    def up(self):
        #self.yvelocity = self.get_adjusted_speed(self.speed)
        pass

    def down(self):
        #self.yvelocity = -self.get_adjusted_speed(self.speed)
        pass

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
        self.rotz += self.rotz_velocity
        self.roty += -self.roty_velocity
        rotz, roty = self.rotz, self.roty
        #yv = zv*math.sin(roty) + yv*math.cos(roty)
        #zv = zv*math.cos(roty) - yv*math.sin(roty)
        ny = zv*math.sin(roty) + yv*math.cos(roty)
        nz = zv*math.cos(roty) - yv*math.sin(roty)

        nx = zv*math.sin(rotz) + xv*math.cos(rotz)
        nz = zv*math.cos(rotz) - xv*math.sin(rotz)
        self.x += nx
        self.z += nz
        self.y += ny
    def update(self):
        self.zvelocity *= self.deceleration
        self.xvelocity *= self.xdeceleration

        self.rotz_velocity *= self.deceleration
        self.roty_velocity *= self.deceleration

        if abs(self.zvelocity) < self.min_velocity:
            self.zvelocity = 0
        if abs(self.xvelocity) < self.min_velocity:
            self.xvelocity = 0
        if abs(self.rotz_velocity) < self.rotzmin_velocity:
            self.rotz_velocity = 0

        # calculate values for fancy ship rotation

        # find the mid point of the xy axis to rotate around
        midx = (self.upperx-self.lowerx)/2
        midy = (self.uppery-self.lowery)/2
        midz = (self.upperz-self.lowerz)*0.75 # slightly off the middle to make it look nicer
        
        # calculate the x rotation based on the velocity
        # and don't let it exceed 90 degrees
        rotx = -self.xvelocity * (0.5*math.pi/self.max_velocity)
        rotx = max(rotx,-0.5*math.pi)
        rotx = min(rotx,0.5*math.pi)

        # calculate the z rotation.
        # only rotate backwards if the ship is trying to go backwards
        roty = self.zvelocity * (0.5*math.pi/self.max_velocity)
        roty = min(roty,0.05*math.pi)
        roty = max(roty,-0.1*math.pi)

        # add in the rotation to the rotation based on the velocities
        rotx += -self.rotz_velocity*10
        # make a new rotation and midpoint for the pulling rotation (looks like the ship is pulling up)
        # since we need to rotate it around a new z value
        pullz = (self.upperz-self.lowerz)*0.9
        pullrot = -abs(self.rotz_velocity)*2.5

        roty += -self.roty


        # get the xz orientation of the ship so we can rotate it to face that way
        rotz = -self.rotz


        for p in range(len(self.polygons)):
            ref = self.object.polygons[p]
            for i in range(len(self.polygons[p].verticies)):
                x = ref.verticies[i][0]
                y = ref.verticies[i][1]
                z = ref.verticies[i][2]

                # pull rotation
                x -= midx
                y -= midy
                z -= pullz

                y,z = self.engine.rot2d((y,z),pullrot)

                x += midx
                y += midy
                z += pullz

                # fancy rotation based on x/z velocity

                # in order to rotate around that point, we have to move it to the origin
                x -= midx
                y -= midy
                z -= midz

                # rotate the points 
                # NOTE: the order of operations is key here.
                # you must do the xz axis last, otherwise it will tip the ship forwards,
                # not the direction it is facing. solution? tip it and then move it to the 
                # direction you wish
                x,y = self.engine.rot2d((x,y),rotx)
                y,z = self.engine.rot2d((y,z),roty)
                x,z = self.engine.rot2d((x,z),rotz)

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