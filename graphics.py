import math
import bisect

class Engine():
    def __init__(self, canvas, width, height):

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
        self.WIDTH = width#canvas.winfo_width()
        self.HEIGHT = height#canvas.winfo_height()
        self.RENDER_DISTANCE = 4000

    def update_objects(self,objects):
        self.objects = objects

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
        x,y = pos
        s,c = math.sin(rad),math.cos(rad)

        return x*c-y*s, y*c+x*s
    @staticmethod
    def dist_3d(v1,v2):
        x1,y1,z1 = v1
        x2,y2,z2 = v2
        return math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)

    @staticmethod
    def clip_3d_line(v1,v2):
        """Calder White's proprietary method for finding the intersection of a line and the z axis."""
        x1,y1,z1 = v1
        x2,y2,z2 = v2
        slopex = (x1 - x2)/(z1 - z2)
        bx = ((x1+x2)-slopex*(z1+z2))/2

        slopey = (y1 - y2)/(z1 - z2)
        by = ((y1+y2)-slopey*(z1+z2))/2

        # in the famous words of Mr. Schattman, "graphics is just a series of optical illusions and cheating"
        # (having a z value that is 0 is bad for the algorithm, so we just make it close to 0)
        z = 0.001

        return (bx,by,z)

    def clip_2d_line(self,v1,v2):
        """Clips a 2d line to a built in max and min for x and y."""
        x1,y1 = v1
        x2,y2 = v2

        constant = self.SCREEN_CLIP_MAX

        if (x1 - x2) == 0:
            if y1 > self.HEIGHT + constant:
                y1 = self.HEIGHT + constant
            if y1 < -constant:
                y1 = -constant
            if x1 > self.WIDTH + constant:
                x1 = self.WIDTH + constant
            if x1 < -constant:
                x1 = -constant
        else:
            slope = (y1 - y2)/(x1 - x2)
            b = (y1+y2-slope*(x1+x2))/2

            if y1 > self.HEIGHT + constant:
                y1 = self.HEIGHT + constant
                if slope != 0:
                    # if the slope is 0, no modification to x is required
                    x1 = (y1-b)/slope
            if y1 < -constant:
                y1 = -constant
                # if the slope is 0, no modification to x is required
                if slope != 0:
                    x1 = (y1-b)/slope

            if x1 > self.WIDTH + constant:
                x1 = self.WIDTH + constant
                y1 = slope*x1 + b
            if x1 < -constant:
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
        p1 = (v1[0]*f1 + self.WIDTH/2,-v1[1]*f1 + self.HEIGHT/2)

        f2 = self.FOV/v2[2]
        p2 = (v2[0]*f2 + self.WIDTH/2,-v2[1]*f2 + self.HEIGHT/2)

        # if the line is for a polygon, clip the 2d version as well, since there is a tkinter error with very large 
        # numbers that need to be clipped. (So we do it our selves)
        if polygon:
            p1,p2 = self.clip_2d_line(p1,p2)
            p2,p1 = self.clip_2d_line(p2,p1)

        return (p1,p2)

    def render_objects(self):
        """Sorts faces and then draws the sorted faces onto the tkinter canvas."""
        # sort the faces first
        # TODO: still some bugs 
        sorted_faces = []
        sorted_coords = []
        for face in self.objects:
            # modify the coords based on the camera
            face.update_pos()

            # get the highest z value of the face
            x = []
            y = []
            z = []
            for i in face.coords_cache:
                x.append(i[0])
                y.append(i[1])
                z.append(i[2])

            x = sum(x)**2
            y = sum(y)**2
            z = sum(z)**2
            
            dist = x+y+z

            if dist-(self.x**2 + self.y**2 + self.z**2) > 3*self.RENDER_DISTANCE**2:
                continue

            i = bisect.bisect_left(sorted_coords,dist)
            # insert it 
            sorted_coords.insert(i,dist)
            sorted_faces.insert(i,face)


        # then render them
        for i in range(len(sorted_faces)-1,-1,-1):
            sorted_faces[i].draw()