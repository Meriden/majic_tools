import maya.cmds as mc

    
def undo(func):
    def wrapper(*args, **kwargs):
        mc.undoInfo(openChunk=True)
        try:
            ret = func(*args, **kwargs)
        finally:
            mc.undoInfo(closeChunk=True)
        return ret
    return wrapper

#--------------------------------------------------------------------------------------------------#

class ComponentError(Exception):
    pass


class Component(object): 
    
    def __init__(self, name=None):
        self.name = str(name)

    
    def create(self):
        raise NotImplementedError
    
    
    def createFromData(self):
        raise NotImplementedError

    #------------------------------------------------------------------------------------------#

    
    @staticmethod
    def isComponent(name):
        raise NotImplementedError
    
    #------------------------------------------------------------------------------------------#
    
    def __str__(self):
        return self.name
    
    
    def __repr__(self):
        return "<{} '{}'>".format(self.__class__.__name__, self.name)


    def __hash__(self):
        return hash(self.name)


    def __eq__(self, other):
        return str(self) == str(other)
