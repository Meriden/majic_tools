from majic_tools.maya.lib.data import Data


class ComponentError(Exception):
    def __init__(self, component, message):
        message = '{}: {}'.format(repr(component), message)
        super(ComponentError, self).__init__(message)


class ComponentData(Data):
    sub_folders = []

    def __init__(self, name):
        self.name = name


    def save(self):
        raise NotImplementedError


    def load(self):
        raise NotImplementedError


    def __repr__(self):
        return "<{} '{}'>".format(self.__class__.__name__, self.name)


    __str__ = __repr__


class Component(object):
    """
    Base Class for all components.
    """
    Data = ComponentData
    Error = ComponentError

    def __init__(self, name=None):
        self.name = str(name)


    @staticmethod
    def isComponent(name):
        raise NotImplementedError


    @classmethod
    def findAll(cls):
        raise NotImplementedError


    @classmethod
    def create(cls):
        raise NotImplementedError


    @classmethod
    def createFromData(cls):
        raise NotImplementedError


    @property
    def data(self):
        return self.Data(self.name)


    def saveData(self):
        self.data.save()


    def loadData(self):
        self.data.load()

    
    def __str__(self):
        return self.name
    
    
    def __repr__(self):
        return "<{} '{}'>".format(self.__class__.__name__, self.name)


    def __hash__(self):
        return hash(self.name)


    def __eq__(self, other):
        return str(self) == str(other)