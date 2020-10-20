#test.py
import sys
import maya.cmds as cmds
import numpy as np
import scipy as sp
from scipy.spatial import Voronoi, voronoi_plot_2d
from scipy.spatial import Delaunay

import math
import vector3d

from anytree import Node, RenderTree, NodeMixin
vector = vector3d.vector.Vector(0,1,0)

N = 900
x = -3 + 3* np.random.rand(N)
y = 2 +  5* np.random.rand(N)
z = -3 + 3*np.random.rand(N)

#make a list of spheres/points
cmds.polySphere(r=0.07)
result = cmds.ls(orderedSelection = True)
transformName = result[0]
instanceGroupName = cmds.group(empty=True, name=transformName+'_instance_grp#')

class Point:
    def __init__(self, pos):
        self.pos = pos 
    
#create instances and add to group    
list_pts = []
for i in range(N):        
    instanceResult = cmds.instance(transformName, name=transformName+'_instance#')
    cmds.parent(instanceResult, instanceGroupName)
    cmds.move(x[i], y[i], z[i], instanceResult)
    list_pts.append(Point([ x[i], y[i], z[i] ]))
   
cmds.hide(transformName)

#with the random points, start from a beginning tree node

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
        #print("added child")
        if self.children:
            np.append(self.children, node)             
          
    def addPts(self, pos):
        #print('added point')
        if self.pts == None:
            self.pts = [pos]
        else: 
            self.pts.append(pos)


#for pre, fill, node in RenderTree(root):
#    print("%s%s" % (pre, node.name)) 
#tree formation     
boundPts = cmds.exactWorldBoundingBox(transformName+'_instance_grp1')
midx = (boundPts[3] + boundPts[0])/2
midz = (boundPts[5] + boundPts[2])/2

cmds.polySphere(r=0.07)
result = cmds.ls(orderedSelection = True)
transformName = result[0]
instanceGroupName = cmds.group(empty=True, name=transformName+'_instance_grp#')

root = TreeNode('root', [midx, 0, midz])

list_node =[root]

init_node_num = 12

init = root

for i in range(1, init_node_num):
    instanceResult = cmds.polySphere(transformName,r=0.1, name=transformName+'_instance#')    
    cmds.parent(instanceResult, instanceGroupName)
    
    pos = [midx, i*0.3, midz]
    cmds.move(pos[0], pos[1], pos[2], instanceResult) 
   
    node = TreeNode('rootnode:'+str(i), pos, parent=init)
    list_node.append(init)
    init = node

#for pre, fill, node in RenderTree(root):
#    print("%s%s" % (pre, node.name)) 
    
cmds.hide(transformName)


def angle(v1, v2):
    return np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
        
def distance (p1, p2):
    return math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2)+((p1[2]-p2[2])**2) )

def length (p1):
    return ( ((p1[0])**2)+((p1[1])**2)+((p1[2])**2) )
    

#try out space colonization:
#radius of influence/kill distance
i_d = 0.5
k_d = 0.4

#check through the pts and find the closest tree node
cmds.select( clear=True )
result = cmds.ls(orderedSelection = True)

iter = 15
it_pts = list_pts

for i in range(iter):  
    #find points close in influence distance
    for pt in it_pts:
        for node in list_node:
            if distance(pt.pos, node.pos) < i_d:
                node.addPts(pt)                
         
    instanceGroupName = cmds.group(empty=True, name='newnode_instance_grp#')
    list_newnodes = []

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
            #print("final vector:",vec)

            #create new node
            instanceResult = cmds.polySphere(transformName,r=0.1, name=transformName+'_instance#')
            cmds.parent(instanceResult, instanceGroupName) 
                                  
            new_loc = [vec[0] + node.pos[0], vec[1] + node.pos[1], vec[2] + node.pos[2]]
            cmds.move(new_loc[0], new_loc[1], new_loc[2], instanceResult) 
            #print("final position:", new_loc)
            list_tri_pos.append(new_loc)

            #add to new nodes list
            new_node = TreeNode(node.name + ' child ' + str(i), new_loc, parent=node)
            #print("this node has a parent:",new_node.parent.name)
            list_newnodes.append(new_node)
            
            #add to tree nodes
            #if node.children:
                #print(node.children)
            #else:
                #node.children = np.array([new_node])

    #check for kill distance
    for node in list_newnodes:
        for pt in list_pts:
            dist = distance(pt.pos, node.pos)
            if dist <= k_d:
                list_pts.remove(pt)
                    
    for node in list_node:
        node.pts = []   
         
    list_node.extend(list_newnodes)
      
    
#for pre, fill, node in RenderTree(root):
#    print("%s%s" % (pre, node.name)) 

#print(list_tri_pos)
#list_triangle = np.asarray(list_tri_pos)
#tri = Delaunay(list_triangle)

#print(tri.simplices)


cmds.polyCylinder(r=0.07, height=0.02)
result = cmds.ls(orderedSelection = True)
transformName = result[0]
instanceGroupName = cmds.group(empty=True, name=transformName+'_branchesGroup#')

def midpoint(p1, p2):
    return [(p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2]
 
#createBranches(root)

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
    
