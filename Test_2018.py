#test.py
import sys
import maya.cmds as cmds
import numpy as np
import scipy as sp
import math


N = 100
x = -5 + 5* np.random.rand(N)
y = 0.5 + 5 * np.random.rand(N)
z = -5 + 5*np.random.rand(N)

#make a list of spheres/points
cmds.polySphere(r=0.01)
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
    list_pts.append(Point([x[i], y[i], z[i]]))
   
cmds.hide(transformName)
boundPts = cmds.exactWorldBoundingBox(transformName+'_instance_grp1')

#with the random points, start from a beginning tree node

class Node:
    def __init__(self, pos):
        self.pos = pos 
        self.children = []
        self.parent = None
        self.pts = []
    
    def addChild(self, pos):
        print("added child")
        if isinstance(pos, list):
            new_node =(Node(pos))
            new_node.parent = self            
            self.children = new_node
        if isinstance(pos, Node):
            pos.parent = self            
            self.children.append(pos)
    '''    
    def printTree(self):
        if self.children:
            for child in self.children:
                child.printTree()
        print(self.pos)
    '''
    '''
    def addLast(self, pos): 
        root = self      
        if not root.children:
            root.addChild(pos)
        while(root.children):
            root = root.children[0]
            if(len(root.children) == 0):
                root.addChild(pos)
                break
    '''            
    def addPts(self, pos):
        print('added point')
        self.pts.append(pos)
                
                
#tree formation           
list_cyl = []
list_node =[]

midx = (boundPts[3] + boundPts[0])/2
midz = (boundPts[5] + boundPts[2])/2
root = Node([midx,0,midz])

cmds.polySphere(r=0.01)
result = cmds.ls(orderedSelection = True)

transformName = result[0]
instanceGroupName = cmds.group(empty=True, name=transformName+'_instance_grp#')

#create root
for i in range(10):
    instanceResult = cmds.polySphere(transformName,r=0.05, name=transformName+'_instance#')    
    cmds.parent(instanceResult, instanceGroupName)
    cmds.move(midx, i*0.1, midz, instanceResult) 
    list_cyl.append([midx, i*0.1, midz])
 
    node = Node([midx, i*0.1, midz])
    list_node.append(node)
    root = node
    root.addChild([midx, i*0.1, midz])
    
cmds.hide(transformName)

def distance (p1, p2):
    return math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2)+((p1[2]-p2[2])**2) )

def length (p1):
    return math.sqrt( ((p1[0])**2)+((p1[1])**2)+((p1[2])**2) )
    
#try out space colonization:
#radius of influence
i_d = 1
k_d = 3

#check through the pts and find the closest tree node
cmds.select( clear=True )
result = cmds.ls(orderedSelection = True)

iter = 3
print("iter:",iter)

for i in range(iter):    
    #find points close in influence distance
    for pt in list_pts:
        for node in list_node:
            if distance(pt.pos, node.pos) <= i_d:
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
            print("final vector:",vec)

            #create new node
            instanceResult = cmds.polySphere(transformName,r=0.05, name=transformName+'_instance#')
            cmds.parent(instanceResult, instanceGroupName)                       
            new_loc = [vec[0] + node.pos[0], vec[1] + node.pos[1], vec[2] + node.pos[2]]
            cmds.move(new_loc[0], new_loc[1], new_loc[2], instanceResult) 
            
            print("final position:",new_loc)

            #add a new cylinder to list
            list_cyl.append(new_loc)
            node = Node(new_loc)
            
            #add to new nodes list
            list_newnodes.append(node)
            #add to tree nodes
            node.addChild(node)

    #check for kill distance
    for node in list_node:
        if node.children:
            for child in node.children:
                new_pos = child.pos
                for pt in node.pts:
                    dist = distance(pt.pos, new_pos)
                    if dist <= k_d:
                        list_pts.remove(pt)
                    
    for node in list_node:
        node.pts = []    
    list_node.extend(list_newnodes)
 
                                
print('num of nodes now:',len(list_node))        

    

    
   

        
    
