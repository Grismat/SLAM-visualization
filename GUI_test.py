import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from gaphas import Canvas, GtkView
from gaphas.examples import Box
from gaphas.painter import DefaultPainter
from gaphas.item import Line
from gaphas.segment import Segment
from gaphas.tool import HandleTool, PlacementTool

import numpy as np

from landmark import Landmark, Landmark2D
from edge import Edge, Factor_pl_2D, Factor_pp_2D
from pose import Pose2D

from random import randint




def add_landmark(canvas):
    #builder.get_object("MainWindow").set_cursor(Gtk.Cursor.new(Gtk.CursorType.CROSSHAIR))
    def wrapper():
        landmark = Landmark2D()
        canvas.add(landmark)
        return landmark

    return wrapper

def add_edge(canvas):
    edge = Edge()
    edge.matrix.translate(randint(50, 350), randint(50, 350))
    canvas.add(edge)
    edge.handles()[1].pos = (40, 40)


def add_factor_pp(canvas, observation, cov_matrix):
    def wrapper():
        factor = Factor_pp_2D(observation, cov_matrix)
        canvas.add(factor)
        return factor
    
    return wrapper

def add_factor_pl(canvas, observation, cov_matrix):
    def wrapper():
        factor = Factor_pl_2D(observation, cov_matrix)
        canvas.add(factor)
        return factor

    return wrapper

def add_pose(canvas, position):
    def wrapper():
        pose = Pose2D(position)
        canvas.add(pose)
        return pose

    return wrapper

def handle_changed(view, item, what):
    stack = builder.get_object("PropertiesStack")
    if (type(item) is Landmark):
        stack.set_visible_child_name("LandmarkFrame")
    else:
        stack.set_visible_child_name("EmptyFrame")

class Handler:
    def __init__(self, view):
        self.view = view    
        self.canvas = view.canvas
        self.pose_landmark_matrix = np.empty((2, 2), dtype=np.float64)
        self.pose_pose_matrix = np.empty((3, 3), dtype=np.float64)
        self.are_cov_matrices_set = False


    def on_MainWindow_destroy(self, *args):
        Gtk.main_quit()

    def on_NewLandmarkBtn_clicked(self, button):
        self.view.tool.grab(PlacementTool(self.view, add_landmark(self.canvas), HandleTool(), 0))

    def on_btn2_clicked(self, button):
        add_edge(self.canvas)

    def on_btn3_clicked(self, button):
        item = self.view.focused_item
        if type(item) is Edge:
            h1, h2 = item.handles()
            #print(type(self.canvas.get_connection(h1)))
            print(self.canvas.get_connection(h1))
            print(self.canvas.get_connection(h2))

    

    def on_NewPoseBtn_clicked(self, button):
        stack = builder.get_object("PropertiesStack")
        stack.set_visible_child_name("NewPose2DFrame")



    def on_AddPoseButton_clicked(self, button):
        position = np.empty((3, 1), dtype=np.float64)

        for i in range(1, 4):
            entry = builder.get_object("NewPose2DEntry{}".format(i))
            text = entry.get_text()
            print(text)

            try:
                value = float(text)
            except:
                print("Error in entry {}".format(i))
                entry.set_text("")
                return

            position[i-1] = value
        
        self.view.tool.grab(PlacementTool(self.view, add_pose(self.canvas, position), HandleTool(), 0))

        

    
    def on_NewFactorPPBtn_clicked(self, button):
        stack = builder.get_object("PropertiesStack")
        stack.set_visible_child_name("NewFactor2DPPFrame")


    
    def on_AddFactor2DPPBtn_clicked(self, button):
        observation = np.empty((3, 1), dtype=np.float64)    

        if (not self.are_cov_matrices_set):
            print("set cov matrices!!!")
            return

        for i in range(1, 4):
            entry = builder.get_object("NewFactor2DPPEntry{}".format(i))
            try:
                value = float(entry.get_text())
            except:
                print("Error in entry {}".format(i))
                entry.set_text("")
                return
            observation[i-1] = value

        self.view.tool.grab(PlacementTool(self.view, add_factor_pp(self.canvas, observation, self.pose_pose_matrix), HandleTool(), 1))#???? 1 or 0



    def on_SetCovMatricesBtn_clicked(self, button):
        stack = builder.get_object("PropertiesStack")
        stack.set_visible_child_name("SetCovMatrices2DFrame")



    def on_ApplyCovMatrices2DBtn_clicked(self, button):
        for i in range(1, 3):
            for j in range(1, 3):
                entry = builder.get_object("PL2DMatrixEntry{}{}".format(i, j))
                try:
                    value = float(entry.get_text())
                except:
                    print("Error in PL matrix entry {}, {}".format(i, j))
                    entry.set_text("")
                    return
                self.pose_landmark_matrix[i-1, j-1] = value

        for i in range(1, 4):
            for j in range(1, 4):
                entry = builder.get_object("PP2DMatrixEntry{}{}".format(i, j))
                try:
                    value = float(entry.get_text())
                except:
                    print("Error in PP matrix entry {}, {}".format(i, j))
                    entry.set_text("")
                    return
                self.pose_pose_matrix[i-1, j-1] = value

        self.are_cov_matrices_set = True


    
    def on_NewFactorPLBtn_clicked(self, button):
        stack = builder.get_object("PropertiesStack")
        stack.set_visible_child_name("NewFactor2DPLFrame")



    def on_AddFactor2DPLBtn_clicked(self, button):
        observation = np.empty((2, 1), dtype=np.float64)    

        if (not self.are_cov_matrices_set):
            print("set cov matrices!!!")
            return

        for i in range(1, 3):
            entry = builder.get_object("NewFactor2DPLEntry{}".format(i))
            try:
                value = float(entry.get_text())
            except:
                print("Error in entry {}".format(i))
                entry.set_text("")
                return
            observation[i-1] = value

        self.view.tool.grab(PlacementTool(self.view, add_factor_pl(self.canvas, observation, self.pose_landmark_matrix), HandleTool(), 1))

        

    def focus_changed(self, view, item, what):
        view.focused_item = item
        stack = builder.get_object("PropertiesStack")
        if (type(item) is Landmark):
            stack.set_visible_child_name("LandmarkFrame")
        else:
            stack.set_visible_child_name("EmptyFrame")

def Main():
    global builder

    builder = Gtk.Builder()
    builder.add_from_file("GUI_test.glade")

    view = GtkView() #Gtk widget
    view.painter = DefaultPainter()

    view.canvas = Canvas()

    handler = Handler(view)
    builder.connect_signals(handler)
    view.connect("focus-changed", handler.focus_changed, "focus")

    gaphas_window = builder.get_object("GaphasWindow")
    gaphas_window.add(view)

    window = builder.get_object("MainWindow")
    window.show_all()
    Gtk.main()

if __name__ == "__main__":
    Main()