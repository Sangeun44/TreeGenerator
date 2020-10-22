#test.py
import sys
import maya.cmds as cmds
import numpy as np
import scipy as sp

from scipy.spatial import Voronoi, voronoi_plot_2d
from scipy.spatial import Delaunay
import math

from anytree import Node, RenderTree, NodeMixin

#randomize---------------------------------------------------------------------

N = 10
x = -5 + 5* np.random.rand(N)
y = 0.5 +  5* np.random.rand(N)
z = -5 + 5*np.random.rand(N)

#make a list of spheres/points--------------------------------------------------

class Point:
    def __init__(self, pos):
        self.pos = pos
        
cmds.polySphere(r=0.07)
result = cmds.ls(orderedSelection = True)
transformName = result[0]
instanceGroupName = cmds.group(empty=True, name=transformName+'_instance_grp#')
    
#create instances and add to group    
list_pts = []
for i in range(N):        
    instanceResult = cmds.instance(transformName, name=transformName+'_instance#')
    cmds.parent(instanceResult, instanceGroupName)
    cmds.move(x[i], y[i], z[i], instanceResult)
    list_pts.append(Point([ x[i], y[i], z[i] ]))
 
cmds.hide(transformName)

#with the random points, start from a beginning tree node----------------------------

class MyBaseClass(object):
    foo = 4

class TreeNode(MyBaseClass, NodeMixin):
    def __init__(self, name, pos, rad=None, pts=None, parent=None, children=None):
         super(TreeNode, self).__init__()
         self.name = name
         self.rad = rad
         self.pos = pos
         self.pts = pts
         self.parent = parent
         if children:
             self.children = children
             
    def addChild(self, node):
        if self.children:
            np.append(self.children, node)             
          
    def addPts(self, pos):
        if self.pts == None:
            self.pts = [pos]
        else: 
            self.pts.append(pos)


#tree formation--------------------------------------------------------------
  
boundPts = cmds.exactWorldBoundingBox(transformName+'_instance_grp1')

#midpoint
midx = (boundPts[3] + boundPts[0])/2
midz = (boundPts[5] + boundPts[2])/2

#limits
xmin1 = [boundPts[0], boundPts[1], boundPts[2]]
xmin12 = [boundPts[0], boundPts[1], boundPts[5]]
xmin2 = [boundPts[0], boundPts[4], boundPts[2]]
xmin22 = [boundPts[0], boundPts[4], boundPts[5]]

xmax1 = [boundPts[3], boundPts[1], boundPts[2]]
xmax12 = [boundPts[3], boundPts[1], boundPts[5]]
xmax2 = [boundPts[3], boundPts[4], boundPts[2]]
xmax22 = [boundPts[3], boundPts[4], boundPts[5]]

points_lim = [xmin1, xmin12, xmin2, xmin22, xmax1, xmax12, xmax2, xmax22]

#make initial nodes-----------------------------
cmds.polySphere(r=0.07)
result = cmds.ls(orderedSelection = True)
transformName = result[0]
instanceGroupName = cmds.group(empty=True, name=transformName+'_instance_grp#')

root = TreeNode('root', [midx, 0, midz])

list_node =[root]
init_num = 5
init = root

points=points_lim
points.append(root.pos)

for i in range(1, init_num):
    instanceResult = cmds.polySphere(transformName,r=0.1, name=transformName+'_instance#')    
    cmds.parent(instanceResult, instanceGroupName)
    
    pos = [midx, i*0.3, midz]
    cmds.move(pos[0], pos[1], pos[2], instanceResult) 
   
    node = TreeNode('rootnode:'+str(i), pos, parent=init)
    list_node.append(init)
    init = node
    points.append(pos)

cmds.hide(transformName)

#math functions--------------------------------------------------------------------

def angle(v1, v2):
    return np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
        
def distance (p1, p2):
    return math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2)+((p1[2]-p2[2])**2) )

def length (p1):
    return ( ((p1[0])**2)+((p1[1])**2)+((p1[2])**2) )    

def midpoint(p1, p2):
    return [(p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2]
 
#try out space colonization---------------------------------------------------------
    
#radius of influence/kill distance
i_d = 1.2
k_d = 0.8

#check through the pts and find the closest tree node
cmds.select( clear=True )
result = cmds.ls(orderedSelection = True)

iter = 2
for i in range(iter):  
    points_np = np.asarray(points)
    vor = Voronoi(points_np)
    #find points close in influence distance
    #save in sets
    for pt in list_pts:
        point_index = np.argmin(np.sum((points_np - pt.pos)**2, axis=1))
        point = vor.points[point_index]
    
        for node in list_node:
            if node.pos[0] == point[0] and node.pos[1] == point[1] and node.pos[2] == point[2]:
                if distance(pt.pos, node.pos) < i_d:
                    node.addPts(pt) 
    
    #create new 
    instanceGroupName = cmds.group(empty=True, name='newnode_instance_grp#')
    list_newnodes = []
    new_points = []
    
    #for each node, find the sum of vectors 
    for node in list_node:
        vec = [0,0,0]  
        if node.pts:
            for pt in node.pts:
                #find vector per each influence point
                diff = [pt.pos[0] - node.pos[0], pt.pos[1] - node.pos[1], pt.pos[2] - node.pos[2]]
                #make the vector into unit vector
                unit_vec = [diff[0]/length(diff), diff[1]/length(diff), diff[2]/length(diff)]
                #add it to the sum of vectors
                vec = [vec[0] + unit_vec[0], vec[1] + unit_vec[1], vec[2]+unit_vec[2]]
                
            #normalize the sum vector
            len = length(vec)
            vec = [vec[0]/len, vec[1]/len, vec[2]/len]

            #create new node
            instanceResult = cmds.polySphere(transformName,r=0.1, name=transformName+'_instance#')
            cmds.parent(instanceResult, instanceGroupName) 
                                  
            new_loc = [vec[0] + node.pos[0], vec[1] + node.pos[1], vec[2] + node.pos[2]]
            cmds.move(new_loc[0], new_loc[1], new_loc[2], instanceResult) 

            #add to new nodes list
            new_node = TreeNode(node.name + ' child ' + str(i), new_loc, parent=node)
            list_newnodes.append(new_node)
            new_points.append(new_loc)
            
    #check for kill distance
    points.extend(new_points)
    
    new_points_np = np.asarray(new_points)
    vor = Voronoi(new_points_np)
    for pt in list_pts:
        point_index = np.argmin(np.sum((new_points_np - pt.pos)**2, axis=1))
        point_pos = vor.points[point_index]
        dist = distance(pt.pos, point_pos)
        if dist <= k_d:
            list_pts.remove(pt)
                    
    for node in list_node:
        node.pts = []   
         
    list_node.extend(list_newnodes)
    

cmds.polyCylinder(r=0.07, height=0.02)
result = cmds.ls(orderedSelection = True)
transformName = result[0]
instanceGroupName = cmds.group(empty=True, name=transformName+'_branchesGroup#')

#calculate radius
def recurse_tree(root) :
    if root.children:
        rad = 0
        n = 2.05
        for node in root.children:
            rad += (recurse_tree(node))**n
        root.rad = rad**(1/n)
    else:
        #no children
        root.rad = 0.05
#    print("name:", root.name, " RADII:", root.rad)
    return root.rad
    

#for pre, fill, node in RenderTree(root):
#    print("%s%s" % (pre, node.name)) 

recurse_tree(root)
       
for pre, fill, node in RenderTree(root):
    if node.parent:
        axis = [node.pos[0]-node.parent.pos[0],node.pos[1]-node.parent.pos[1],node.pos[2]-node.parent.pos[2]] 
        length = distance(node.parent.pos, node.pos)
        pos = midpoint(node.parent.pos, node.pos)
        sphere2 = cmds.polySphere(r=node.rad, name='circle_node#')
        cmds.parent(sphere2, instanceGroupName)                                  
        cmds.move(node.pos[0], node.pos[1], node.pos[2], sphere2)
        
        cylinder2 = cmds.polyCylinder(r=node.rad, axis=axis, height=length, name=transformName+'_branch#')
        cmds.parent(cylinder2, instanceGroupName)                                  
        cmds.move(pos[0], pos[1], pos[2], cylinder2)  

cmds.hide(transformName)
cmds.delete(transformName)
