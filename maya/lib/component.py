
class ComponentData(dict):
    def __init__(self):
        pass


    def save(self):
        pass


    def load(self):
        pass


class ComponentError(Exception):
    pass


class Component(object):
    DATA = ComponentData

    def __init__(self, name=None):
        self.name = str(name)
        self._data = None


    @staticmethod
    def isComponent(name):
        raise NotImplementedError


    @classmethod
    def create(cls):
        raise NotImplementedError


    @classmethod
    def createFromData(cls):
        raise NotImplementedError


    def data(self):
        if self._data is None:
            self._data =


    def _syncData(self):
        pass


    def _syncScene(self):
        pass


    def __str__(self):
        return self.name


    def __repr__(self):
        return "<{} '{}'>".format(self.__class__.__name__, self.name)


    def __hash__(self):
        return hash(self.name)


    def __eq__(self, other):
        return str(self) == str(other)
