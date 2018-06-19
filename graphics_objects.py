import math

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

    def set_engine(self,engine):
        self.engine = engine

    def set_dynamic(self,d):
        if d:
            self.verticies = [list(i) for i in self.verticies]
        else:
            self.verticies = [tuple(i) for i in self.verticies]

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
            self.id = self.engine.canvas.create_polygon(coords,fill=self.color,outline="red")

class ObjectFile():
    def __init__(self, filename,scale=1,pos=None,pos2=None,fformat="standard"):
        """
        Loads in the veriticies and faces in an object file and converts them to Polygons.
        2 Object file formats are supported: standard and tinkercad.
        This is because when tinkercad exports to obj the format used is slightly different.
        """

        if not pos:
            pos = (0,0,0)
        if not pos2:
            pos2 = (0,0,0)

        self.verticies = []
        self.faces = []
        self.polygons = []

        # parse file
        f = open(filename,'r')
        if fformat == "standard":
            for l in f:
                if l[:2] == "v ":
                    #print(l[2:].split(" "))
                    self.verticies.append(tuple(
                        [
                            float(l[2:].split(" ")[i])*scale + pos[i] 
                            for i in range(len(l[2:].split(" ")))
                        ]
                    ))
                elif l[:2] == "f ":
                    self.faces.append(tuple(
                        [
                            tuple([
                                int(j) for j in i.split("/")
                            ]) for i in l[2:].split(" ")
                        ]
                    ))
            # generate Polygons from it
            for face in self.faces:
                points = []
                for line in face:
                    points.append(self.verticies[line[0]-1])
                self.polygons.append(Polygon(tuple(points),color="white"))

        elif fformat == "tinkercad":
            for l in f:
                l = l.strip().replace("\t","")
                if l[:2] == "v ":
                    self.verticies.append(
                        [
                            float(i)*scale for i in l[2:].split(" ")
                        ]
                    )
                    for i in range(3):
                        self.verticies[-1][i] += pos[i]
                    self.verticies[-1] = tuple(self.verticies[-1])
                elif l[:2] == "f ":
                    self.faces.append(tuple(
                        [
                            int(i) for i in l[2:].split(" ")
                        ]
                    ))
            verts = []
            # generate Polygons from the parsed verticies and faces
            for face in self.faces:
                points = [list(self.verticies[i-1]) for i in face]
                for i in range(len(points)):
                    if (points[i][2]-pos[2])/scale == 40.0:
                        points[i][0] += pos2[0]
                        points[i][1] += pos2[1]
                        points[i][2] += pos2[2]
                self.polygons.append(
                    Polygon(tuple(points),color="#d0d0d0")
                )

        else:
            raise Exception("Unknown .obj file format requested")