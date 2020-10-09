#test.py
import sys
import maya.cmds as cmds
import numpy as np
import scipy as sp
import math

from anytree import Node, RenderTree, NodeMixin

N = 10
x = -10 + 10* np.random.rand(N)
y = 3 +   10* np.random.rand(N)
z = -10 + 10*np.random.rand(N)

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
    list_pts.append(Point([x[i], y[i], z[i]]))
   
cmds.hide(transformName)
boundPts = cmds.exactWorldBoundingBox(transformName+'_instance_grp1')


#with the random points, start from a beginning tree node

class MyBaseClass(object):
    foo = 4
    
class TreeNode(MyBaseClass, NodeMixin):
    def __init__(self, name, pos, pts=None, parent=None, children=None):
        super(MyClass, self).__init__()        
        self.name = name
        self.pos = pos 
        if children:
            self.children = children
        self.parent = None
        self.pts = pts
    
    def addChild(self, pos):
        print("added child")
        if isinstance(pos, list):
            new_node =(Node(pos))
            new_node.parent = self            
            self.children.append(new_node)
        if isinstance(pos, Node):
            pos.parent = self            
            self.children.append(pos)   
          
    def addPts(self, pos):
        print('added point')
        self.pts.append(pos)

                    
root = TreeNode('0', [0, 0, 0])
node1 = TreeNode('1',[1, 0, 0], parent=root)

#for pre, fill, node in RenderTree(root):
#    print("%s%s" % (pre, node.name)) 
         
#tree formation     
    
list_node =[]

midx = (boundPts[3] + boundPts[0])/2
midz = (boundPts[5] + boundPts[2])/2
#root = Node([midx,0,midz])
list_node.append(root)

cmds.polySphere(r=0.01)
result = cmds.ls(orderedSelection = True)

transformName = result[0]
instanceGroupName = cmds.group(empty=True, name=transformName+'_instance_grp#')

init_node = 10
#create root
for i in range(1, init_node):
    instanceResult = cmds.polySphere(transformName,r=0.1, name=transformName+'_instance#')    
    cmds.parent(instanceResult, instanceGroupName)
    cmds.move(midx, i*0.3, midz, instanceResult) 
 
    node = Node([midx, i*0.3, midz])
    list_node.append(node)
    root.addChild(node)
    root = node

root.printTree()

cmds.hide(transformName)

def distance (p1, p2):
    return math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2)+((p1[2]-p2[2])**2) )

def length (p1):
    return math.sqrt( ((p1[0])**2)+((p1[1])**2)+((p1[2])**2) )
    
#try out space colonization:
#radius of influence
i_d = 1.2
k_d = 0.4

#check through the pts and find the closest tree node
cmds.select( clear=True )
result = cmds.ls(orderedSelection = True)

iter = 1
print("iter:",iter)

for i in range(iter):    
    #find points close in influence distance
    for pt in list_pts:
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
            print("final vector:",vec)

            #create new node
            instanceResult = cmds.polySphere(transformName,r=0.1, name=transformName+'_instance#')
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
    for node in list_newnodes:
        for pt in list_pts:
            dist = distance(pt.pos, node.pos)
            if dist <= k_d:
                list_pts.remove(pt)
                    
    for node in list_node:
        node.pts = []   
         
    list_node.extend(list_newnodes)
    

def createBranches(node):
    if node.children:
        for child in node.children:
            print('node:', child.pos)
    
createBranches(root)


        
    
