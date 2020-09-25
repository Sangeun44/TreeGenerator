#test.py
import sys
import maya.cmds as cmds
import numpy as np
import scipy as sp
import math


sys.stdout.write('Hello world')

N = 100
x = -10 + 10* np.random.rand(N)
y = 10 * np.random.rand(N)
z = -10 + 10*np.random.rand(N)

#make a list of spheres/points
cmds.polySphere(radius=0.05)

#highlighted list of points
result = cmds.ls(orderedSelection = True)

#create a group name for instances
transformName = result[0]
instanceGroupName = cmds.group(empty=True, name=transformName+'_instance_grp#')

class Point:
    def __init__(self, pos):
        self.pos = pos #pos
    
    
        
    
list_sps = []
list_pts = []

#create instances and add to group
for i in range(len(x)):        
    instanceResult = cmds.instance(transformName, name=transformName+'_instance#')
    cmds.parent(instanceResult, instanceGroupName)
    cmds.move(x[i], y[i], z[i], instanceResult)
    scaleFactor = 1
    cmds.scale(scaleFactor, scaleFactor, scaleFactor, instanceResult)
    list_sps.append(instanceResult)
    list_pts.append(Point([x[i], y[i], z[i]]))
   
cmds.hide(transformName)
boundPts = cmds.exactWorldBoundingBox(transformName+'_instance_grp1')

#with the random points, start from a beginning tree node
midx = (boundPts[3] + boundPts[0])/2
midz = (boundPts[5] + boundPts[2])/2

cmds.polyCylinder(r=0.1)
cmds.scale(1,0.1,1)
result = cmds.ls(orderedSelection = True)

transformName = result[0]
instanceGroupName = cmds.group(empty=True, name=transformName+'_instance_grp#')

class Node:
    def __init__(self, pos):
        self.pos = pos #pos
        self.children = []
        self.parent = None
        self.pts = []
    
    def addChild(self, pos):
        print "added child"
        if isinstance(pos, list):
            self.children.append(Node(pos))
            self.parent = self
        if isinstance(pos, Node):
            self.children.append(pos)
            self.parent = self
        
    def printTree(self):
        if self.children:
            for child in self.children:
                child.printTree()
        print(self.pos)
    
    def addLast(self, pos):
        if(len(self.children)==0):
            self.addChild(pos)
        while(len(self.children) > 0):
            self = self.children[0]
            if(len(self.children) == 0):
                self.addChild(pos)
                break;
                
    def addPts(self, pos):
        print 'added point'
        self.pts.append(pos)
                
                
       
                
#tree.PrintTree()

list_cyl = []
list_node =[]
root = Node([midx,0,midz])
   
for i in range(5):
    instanceResult = cmds.instance(transformName, name=transformName+'_instance#')
    cmds.parent(instanceResult, instanceGroupName)
    cmds.move(midx, i*0.5, midz, instanceResult) 
    list_cyl.append([midx, i*0.5, midz])
    node = Node([midx, i*0.5, midz])
    list_node.append(node)
    root.addLast([midx, i*0.5, midz])
    
root.printTree()    

cmds.hide(transformName)
boundTree = cmds.exactWorldBoundingBox(instanceResult)

#radius of influence
i_d = 2
k_d = 5

#check through the pts and find the closest tree node
cmds.select( clear=True )

result = cmds.ls(orderedSelection = True)

def distance (p1, p2):
    return math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2)+((p1[2]-p2[2])**2) )

def length (p1):
    return math.sqrt( ((p1[0])**2)+((p1[1])**2)+((p1[2])**2) )
    
    
for pt in list_pts:
    for node in list_node:
        if distance(pt.pos, node.pos) <= i_d:
            node.addPts(pt)

for node in list_node:
    vec = [0,0,0]
    for pt in node.pts:
        diff = [pt.pos[0] - node.pos[0], pt.pos[1] - node.pos[1], pt.pos[2] - node.pos[2]]
        unit_vec = [diff[0]/length(diff), diff[1]/length(diff), diff[2]/length(diff)]
        vec = [vec[0] + unit_vec[0], vec[1] + unit_vec[1], vec[2]+unit_vec[2]]
        print vec
    instanceResult = cmds.instance(transformName, name=transformName+'_instance#')
    cmds.parent(instanceResult, instanceGroupName)
    new_loc = [vec[0] + node.pos[0], vec[1] + node.pos[1], vec[2] + node.pos[2]]
    cmds.move(vec[0] + node.pos[0], vec[1] + node.pos[1], vec[2] + node.pos[2], instanceResult) 
    list_cyl.append(new_loc)
    node = Node(new_loc)
    list_node.append(node)
    node.addChild(node)
        
        
    
    

    
   

        
    
