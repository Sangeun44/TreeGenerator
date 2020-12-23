#test.py
import sys
import maya.cmds as cmds
import numpy as np
import scipy as sp
import functools

from scipy.spatial import Voronoi, voronoi_plot_2d
from scipy.spatial import Delaunay
import math

from anytree import Node, RenderTree, NodeMixin

def createUI( pWindowTitle, pApplyCallback) :
    
    windowID = 'myWindowID'
    
    if cmds.window(windowID, exists=True):
        cmds.deleteUI(windowID)
    
    cmds.window( windowID, title=pWindowTitle, sizeable=False, resizeToFitChildren=True )
    
    cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[(1,150), (2, 60), (3,60)], columnOffset=[(1, 'right', 3)] )
    
    cmds.text(label='# Atraction points:')
    attractPts = cmds.intField(value=900)
    cmds.separator(h=10,style='none')

    cmds.text(label='# Iterations:')
    iter = cmds.intField(value=15)
    cmds.separator(h=10,style='none')
    
    cmds.text(label='# Initial Nodes:')
    int_node = cmds.intField(value=12)
    cmds.separator(h=10,style='none')

    cmds.text(label='Influence distance:')
    i_rad = cmds.floatField(value=0.83)
    cmds.separator(h=10,style='none')

    cmds.text(label='Kill distance:')
    k_rad = cmds.floatField(value=0.8)
    cmds.separator(h=10,style='none')    
        
    cmds.text(label='Height of Trunk:')
    trunk = cmds.floatField(value=1)
    cmds.separator(h=10,style='none')
    
    cmds.text(label='gravity:')
    grav = cmds.floatField(value=0.09)
    cmds.separator(h=10,style='none')
    
    cmds.text(label='')
    circ = cmds.checkBox('Circle', value=False)
    cmds.separator(h=10,style='none')
    
    def cancelCallback(*pArgs):
        if cmds.window(windowID, exists=True):
            cmds.deleteUI(windowID)
            
    cmds.button(label='Apply', command=functools.partial(pApplyCallback, attractPts, iter, int_node, i_rad, k_rad, trunk, circ, grav))
    cmds.button(label='Cancel', command=cancelCallback)
    cmds.showWindow()
   

class Point:
    def __init__(self, pos):        
        self.pos = pos

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
            
def getPoint(x1, x2, x3, t) :
    u = np.random.rand() * 100
    
    mag = math.sqrt(x1*x1 + x2*x2 + x3*x3)
    x1 /= mag; x2 /= mag; x3 /= mag
    c = u ** (1. / 3)

    return [x1*c, x2*c, x3*c]

                        
def algorithm(pPts, pIter, pInit, pIR, pKR, pTrunk, pCirc, pGrav): 
    
    #make a list of spheres/points--------------------------------------------------

    cmds.polySphere(r=0.07)
    result = cmds.ls(orderedSelection = True)
    transformName = result[0]
    instanceGroupName = cmds.group(empty=True, name=transformName+'_instance_grp#')
    
    #create instances and add to group    
    list_pts = []
    
    if pCirc == False:
        N = pPts
        x = -7 + 7 * np.random.rand(N)
        y = pTrunk + 5 * np.random.rand(N)
        z = -7 + 7 * np.random.rand(N)
        for i in range(N):   
            instanceResult = cmds.instance(transformName, name=transformName+'_instance#')
            cmds.parent(instanceResult, instanceGroupName)
            cmds.move(x[i], y[i], z[i], instanceResult)
            list_pts.append(Point([ x[i], y[i], z[i] ]))
    else:
        for i in range(pPts):   
            x1 = -7 + 28 * np.random.rand()
            x2 = pTrunk + 5 * np.random.rand()
            x3 = -7 + 28 * np.random.rand()
            pt = getPoint( x1, x2, x3, pTrunk )
            #spt = [x1,x2,x3]
            instanceResult = cmds.instance(transformName, name=transformName+'_instance#')
            cmds.parent(instanceResult, instanceGroupName)
            cmds.move(pt[0], pt[1], pt[2], instanceResult)
            list_pts.append(Point(pt)) 
                  
    cmds.hide(transformName)

    
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
    init_num = pInit
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
 
    #space colonization---------------------------------------------------------
    
    #radius of influence/kill distance
    i_d = pIR
    k_d = pKR

    #check through the pts and find the closest tree node
    cmds.select( clear=True )
    result = cmds.ls(orderedSelection = True)
    iter = pIter
    for i in range(iter):  
        #np array of points
        points_np = np.asarray(points)
    
        #create voronoi with the points
        vor = Voronoi(points_np)
    
        #find points closest to a node in the voronoi in influence distance
        #save in sets
        for pt in list_pts:
            point_index = np.argmin(np.sum((points_np - pt.pos)**2, axis=1))
            point = vor.points[point_index] #closest node point 
    
            for node in list_node:
                if node.pos[0] == point[0] and node.pos[1] == point[1] and node.pos[2] == point[2]:
                    if distance(pt.pos, node.pos) < i_d:
                        node.addPts(pt) #add to this node's list of points
    
        #create new list of new nodes
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
                
                vec = [vec[0], vec[1]-pGrav, vec[2]]
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
        new_points_np = np.asarray(points)
        vor2 = Voronoi(new_points_np)

        points_to_remove = []
        for pt in list_pts:
            point_index = np.argmin(np.sum((new_points_np - pt.pos)**2, axis=1))
            point_pos = vor2.points[point_index]
            dist = distance(pt.pos, point_pos)
            if dist <= k_d:
                points_to_remove.append(pt)                    
        
        for point in points_to_remove:
            list_pts.remove(point)
        
        for node in list_node:
            node.pts = []   
    
        list_node.extend(list_newnodes)
    

    #Create tree cylinders---------------------------------------------------------------------

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

 
def applyCallback(pPts, pIter, pInit, pIR, pKR, pTrunk, pCirc, pGrav, *pArgs):
    print('Apply button pressed')
    
    a_pts = cmds.intField(pPts, query=True, value=True)
    iter = cmds.intField(pIter, query=True, value=True)
    init = cmds.intField(pInit, query=True, value=True)
    ir = cmds.floatField(pIR, query=True, value=True)
    kr = cmds.floatField(pKR, query=True, value=True)
    trunk = cmds.floatField(pTrunk, query=True, value=True)
    grav = cmds.floatField(pGrav, query=True, value=True)
    circ = cmds.checkBox(pCirc, query=True, value=True )

    print("attraction pts:", a_pts)
    print("iteration:", iter)
    print("intL", init)
    print("ir:", ir)
    print("kr:", kr)
    print("grav:", grav)
    print("circ:", circ)
    
    algorithm(a_pts, iter, init, ir, kr, trunk, circ, grav)


createUI('My Title', applyCallback)
