#test_node.py

from anytree import NodeMixin, RenderTree, Node

udo = Node("Udo")
marc = Node("Marc", parent=udo)
lian = Node("Lian", parent=marc)

print(udo)

for pre, fill, node in RenderTree(udo):
    print("%s%s" % (pre, node.name))
    

class MyBaseClass(object):
    foo = 4

class MyClass(MyBaseClass, NodeMixin):
    def __init__(self, name, length, parent=None, children=None):
         super(MyClass, self).__init__()
         self.name = name
         self.length = length
         self.parent = parent
         if children:
             self.children = children

my0 = MyClass("my0", [0,0,0])
my1 = MyClass("my1", [1,0,0], parent=my0)
my2 = MyClass("my2", [0,2,0], parent=my0)

for pre, fill, node in RenderTree(my0):
    treestr = u"%s%s" % (pre, node.name)
    print(treestr.ljust(8), node.length)