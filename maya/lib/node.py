import maya.cmds as mc

from majic_tools.maya.lib.component import Component, ComponentError, ComponentData
import majic_tools.maya.utils.constants as constants

class NodeData(ComponentData):



class NodeError(ComponentError):
    pass


class Node(Component):
    @staticmethod
    def isComponent(name):
        """
        Returns true if given node will work with the Node Class. As the class works on any
        maya nodes, as long as it exist isComponent returns True.

        :param str name: the name of the node to check

        :return bool: True if name is an existing maya node
        """
        if mc.objExists(name):
            return True
        raise False


    @classmethod
    def create(cls, name, node_type, increment_name=False):
        """
        Creates a maya node of given type, and wraps the instance.

        :param str name: name of the new node
        :param str node_type: node type to create e.g. multDoubleLinear, plusMinusAverage
        :param bool increment_name: if true, will create a node with an incremented name if node
                                    already exist

        :return Node: instance of this class.
        """
        if mc.objExists(name) and not increment_name:
            raise NodeError("Node {} already exists. Unique name required.".format(name))

        return cls(mc.createNode(node_type, n=name))


    @classmethod
    def createFromData(cls, name):
        raise NotImplemented


    def duplicate(self, new_name):
        """
        Duplicate the node with given name.

        :param new_name: name of duplicate object.

        :return: Node: instance of this class wrapping duplicate node.
        """
        return self.__class__(mc.duplicate(self.name, name=new_name)[0])


    @property
    def type(self):
        """
        :return str: the object type of the node
        """
        return mc.objectType(self.name)


    @property
    def exists(self):
        """
        :return bool: True if node exists, else False
        """
        return mc.objExists(self.name)


    def rename(self, new_name, increment_name=False):
        """
        Renames the node to the given name. New name is set on the instance.
        :param str new_name: new node name
        """
        if mc.objExists(new_name) and not increment_name:
            raise NodeError("Node {} already exists. Unique name required.".format(new_name))

        self.name = mc.rename(self.name, new_name)


    def delete(self):
        """
        Delete the node, and set the component to None.
        """
        mc.delete(self.name)
        self.name = None

    # -----------------------------------------------------------------------------------------#

    def getAttr(self, attribute, **kwargs):
        """
        Wrapper of maya commands getAttr.

        :param str attribute: name of the attribute

        :return : result of getAttr command
        """
        return mc.getAttr('{}.{}'.format(self.name, attribute), **kwargs)


    def setAttr(self, attribute, *args, **kwargs):
        """
        Wrapper of maya commands setAttr.

        :param str attribute: name of the attribute
        """
        node_attribute = '{}.{}'.format(self.name, attribute)

        # if no value being set, must be setting kwargs only
        if not args and kwargs:
            mc.setAttr(node_attribute, **kwargs)
            return

        value = args[0]

        if isinstance(value, (float, int)):
            mc.setAttr(node_attribute, value, **kwargs)

        elif hasattr(value, '__iter_'):
            if len(value) == 16:
                mc.setAttr(node_attribute, value, type='matrix', **kwargs)
            else:
                mc.setAttr(node_attribute, *value, **kwargs)

        elif isinstance(value, (str, unicode)):
            mc.setAttr(node_attribute, value, type='string', **kwargs)

        else:
            raise NodeError('Error in setAttr. Data type not supported.')


    def addAttr(self, *args, **kwargs):
        """
        Wrapper of maya commands addAttr.
        """
        return mc.addAttr(self.name, *args, **kwargs)


    def deleteAttr(self, attribute, *args, **kwargs):
        """
        Wrap for deleteAttr
        """
        return mc.deleteAttr('{}.{}'.format(self.name, attribute), *args, **kwargs)


    def attributeQuery(self, attribute, *args, **kwargs):
        """
        Wrapper for attributeQuery

        :param attribute: name of the attribute
        :return:
        """
        kwargs['node'] = self.name
        return mc.attributeQuery(attribute, *args, **kwargs)


    def attr(self, attribute):
        """
        Return the full node attribute as a string. e.g. pSphere1.translateX

        :param attribute:
        :return str: full attribute plug
        """
        node_attribute = '{}.{}'.format(self.name, attribute)
        if not mc.objExists(node_attribute):
            raise NodeError("Attribute '{}' does not exist.".format(node_attribute))
        return node_attribute


    def addStringAttr(self, attribute, string):
        """
        Adds a string attribute to node.

        :param str attribute: the name of the attribute
        :param str string: the string value
        """
        node_attribute = '{}.{}'.format(self.name, attribute)
        mc.addAttr(self.name, longName=attribute, dt='string', hidden=False)
        mc.setAttr(node_attribute, string, type='string')


    def addEnumAttr(self, attribute, values, default=None, keyable=True):
        """
        Adds an enum attribute to the node.

        :param str attribute: the name of the attribute
        :param list values: A list of strings representing the enum values
        :param int default: the default index for the enum
        :param bool keyable: if False the attribute is only displayed in the channel box
        """
        enum_string = ':'.join(values)
        mc.addAttr(self.name, longName=attribute, at='enum', en=enum_string, k=keyable)

        node_attribute = '{}.{}'.format(self.name, attribute)

        if not keyable:
            mc.setAttr(node_attribute, e=True, channelBox=True)

        if default:
            mc.setAttr(node_attribute, default)


    def addVectorAttr(self, attribute, keyable=True, attribute_type='double'):
        """
        Add an attribute with 3 child attributes (XYZ). Defaults to double, but also accepts
        doubleAngle.

        :param str attribute: main name of the attribute
        :param int default: default value of the child attributes
        :param bool keyable: is attribute keyable?
        :param str attribute_type: double or doubleAngle
        """
        if attribute_type not in ('double', 'doubleAngle'):
            raise NodeError('Type {} is not supported by this method'.format(attribute_type))

        # create double3 attribute
        #
        mc.addAttr(self.name, longName=attribute, at='double3', k=keyable)

        # if node is not keyable, make it visible in channel box
        #
        if not keyable:
            mc.setAttr('{}.{}'.format(self.name, attribute), e=True, channelBox=True)

        # add child attributes
        #
        for axis in 'XYZ':
            mc.addAttr(self.name,
                       ln=attribute + axis,
                       at=attribute_type,
                       parent=attribute,
                       k=keyable)


    def addMatrixAttr(self, attribute):
        """
        Add an matrix attribute to the node.

        :param str attribute: the name of the attribute
        """
        mc.addAttr(self.name, ln=attribute, at='matrix')


    def addNumericAttr(self,
                       attribute,
                       attribute_type='double',
                       min_value=None,
                       max_value=None,
                       value=None,
                       keyable=True):
        """
        Add a numeric of attribute of the given type.

        :param str attribute: the name of the attribute
        :param str attribute_type: numeric attribute type e.g. double, long, bool, double3
        :param (float, int) min_value: minimum attribute value if defined
        :param (float, int) max_value: maximum attribute value if defined
        :param (float, int) value: default attribute value if defined
        :param bool keyable: is attribute keyable?
        """
        numeric_types = ('short', 'long', 'double', 'bool', 'float')

        if attribute_type not in numeric_types:
            raise NodeError('Type {} is not supported.'.format(attribute_type))

        mc.addAttr(self.name, longName=name, at=attribute_type, k=keyable)
        node_attribute = '{}.{}'.format(self.name, name)

        if not keyable:
            mc.setAttr(node_attribute, e=True, channelBox=True)

        if min_value is not None:
            mc.addAttr(node_attribute, edit=True, hasMinValue=True, minValue=min_value)

        if max_value is not None:
            mc.addAttr(node_attribute, edit=True, hasMaxValue=True, maxValue=max_value)

        if value is not None:
            mc.addAttr(node_attribute, edit=True, defaultValue=value)
            mc.setAttr(node_attribute, value)


    def addSeparatorAttr(self, attribute):
        """
        Adds an dummy locked attribute to separate other attributes in the channel box.

        :param str attribute: The name displayed as the separator.
        """
        node_attribute = '{}.{}'.format(self.name, attribute)

        if attribute in self.getKeyableAttributes():
            raise NodeError('Attribute {} already exists.'.format(node_attribute))

        mc.addAttr(self.name, longName=attribute, at='enum', en='---', k=False)
        mc.setAttr(node_attribute, e=True, channelBox=True, lock=True)


    def addMeshAttr(self, attribute):
        """
        Add an mesh type of attribute.

        :param str attribute: the name of the attribute
        """
        mc.addAttr(self.name, ln=attribute, dt='mesh')


    def lockAttr(self, attribute, hide=False):
        """
        Lock and hide the specified attribute

        :param str attribute: name of the attribute
        :param bool hide: also hide the attribute
        """
        node_attribute = '{}.{}'.format(self.name, attribute)
        try:
            mc.setAttr(node_attribute, lock=True, keyable=False if hide else True)
        except RuntimeError:
            raise NodeError("Attribute '{}' not found.".format(node_attribute))


    def unlockAttr(self, attribute, show=True):
        """
        Unlock and show an attribute

        :param str attribute: name of the attribute
        :param bool show: if the attribute must be visible
        :return: None
        """
        node_attribute = '{}.{}'.format(self.name, attribute)
        try:
            mc.setAttr(node_attribute, lock=False, keyable=True if show else False)
        except RuntimeError:
            raise NodeError("Attribute '{}' not found.".format(node_attribute))


    def getUserAttr(self, exclude_tags=False):
        """
        :return: all user defined attributes
        """
        user = mc.listAttr(self.name, ud=True)
        if exclude_tags:
            user = [attr for attr in user if constants.TAG not in attr]

        return user if user else []


    def getKeyableAttributes(self):
        """
        :return: all keyable, unlocked attributes
        """
        standard = mc.listAttr(self.name, k=True, unlocked=True)
        user = mc.listAttr(self.name, ud=True, k=True, unlocked=True)

        return standard if standard else [] + user if user else []


    def attributeExists(self, attribute):
        """
        Check if attribute exists on node.

        :param str attribute: name of the attribute

        :return: True if attribute exists, else False
        """
        node_attribute = '{}.{}'.format(self.name, attribute)
        try:
            return mc.objExists(node_attribute)
        except RuntimeError:
            raise NodeError("Attribute '{}' not found.".format(node_attribute))


    def isLockedAttr(self, attribute):
        """
        Check if attribute is locked.

        :param str attribute: name of the attribute

        :return: True if attribute is locked, else False
        """

        try:
            return mc.getAttr(node_attribute, lock=True)
        except RuntimeError:
            raise NodeError("Attribute '{}' not found.".format(node_attribute))


    def isHiddenAttr(self, attribute):
        """
        Check if attribute is hidden.

        :param str attribute: name of the attribute

        :return: True if attribute is locked, else False
        """
        node_attribute = '{}.{}'.format(self.name, attribute)
        try:
            return self.attributeQuery(node_attribute, hidden=True)
        except RuntimeError:
            raise NodeError("Attribute '{}' not found.".format(node_attribute))


    def isKeyableAttr(self, attribute):
        """
        Check if attribute is keyable.

        :param str attribute: name of the attribute

        :return: True if attribute is locked, else False
        """
        node_attribute = '{}.{}'.format(self.name, attribute)
        try:
            return mc.getAttr(node_attribute, keyable=True)
        except RuntimeError:
            raise NodeError("Attribute '{}' not found.".format(node_attribute))


    def connect(self, attribute, dst_node, dst_attribute, force=True):
        """
        Connect the specified attribute to destination node attribute.
        If the attribute is a vector, or a float we have the option to add a multiply divide
        node between the connections

        :param str attribute: The attribute on the node to connect
        :param (Node, str) dst_node: name of the destination node or Node instance
        :param str dst_attribute: The destination attribute to connect to
        :param bool force: force the connection
        """
        mc.connectAttr('{}.{}'.format(self.name, attribute),
                       '{}.{}'.format(dst_node, dst_attribute), f=force)


    def breakConnection(self, attribute, source=True, destination=True):
        """
        Break the connections for the attribute from the specified side.

        :param str attribute: name of the attribute
        :param bool source: break all incoming connections
        :param bool destination: break all outgoing connections
        """
        node_attribute = '{}.{}'.format(self.name, attribute)

        broken_connections = []

        if source:
            for src_node, src_attribute in self.getInputs(node_attribute).items():
                connection = '{}.{}'.format(src_node, src_attribute), node_attribute
                broken_connections.append(connection)

        if destination:
            for dst_node, dst_attribute in self.getOutputs(node_attribute).items():
                connection = node_attribute, '{}.{}'.format(dst_node, dst_attribute)
                broken_connections.append(connection)

        for connection in broken_connections:
            mc.disconnectAttr(*connection)

        return broken_connections


    def getOutputs(self, attribute):
        """
        Get the output connections to the given plug.

        :param str attribute: the attribute to query
        :return dict: Found connected nodes and relative attribute to the specified plug
                      as Nodes: str, you can cast it to a different type if you need.
        """
        return self._getConnection(attribute, False, True)


    def getInputs(self, attribute):
        """
        Get the input connections to the given attribute.

        :param str attribute: The attribute to query
        :return dict: Found connected nodes and relative attribute to the specified plug
                      as Nodes: str, you can cast it to a different type if you need.
        """
        return self._getConnection(attribute, True, False)


    def _getConnection(self, attribute, source, destination):
        node_attribute = '{}.{}'.format(self.name, attribute)

        connected_attributes = mc.listConnections(node_attribute, p=True, s=source, d=destination)

        if not connected_attributes:
            return {}

        nodes = [i.split('.')[0] for i in connected_attributes]
        attributes = ['.'.join(i.split('.'))[1:] for i in connected_attributes]

        return {Node(node): attribute for node, attribute in zip(nodes, attributes)}


    @property
    def tags(self):
        """
        Get all the attributes that starts with the tag prefix

        :return: List of tag attributes if tags or None
        """
        tag_attrs = []
        for user_attr in self.getUserAttr():
            if constants.TAG in user_attr:
                tag_attrs.append(user_attr)

        return tag_attrs


    def hasTag(self, tag_id):
        """
        :param tag_id: The string to search in the tags
        :return bool: fa_rig tag attribute present
        """
        tags = self.tags
        if not tags:
            return False

        return bool([True for tag in tags if tag_id in tag])


    def getTagValue(self, tag_id):
        """
        :param tag_id: The identifier string for this tag
        :return: The stored value for this tag
        """
        return self.getAttr(self._composeTagAttr(tag_id))


    def setTagValue(self, tag_id, value):
        """
        :param tag_id    : tag id to write
        :param str value : the value to write in it
        :return: None
        """
        if self.hasTag(tag_id):
            attr = self._composeTagAttr(tag_id)
            obj_attr = '{}.{}'.format(self.name, attr)
            mc.setAttr(obj_attr, value, type='string')
        else:
            raise NodeError('No tag name found for {}'.format(tag_id))


    def addTagAttribute(self, tag, value=''):
        """
        The tag attribute is an hidden attribute that can be added
        on every node.
        It can be used for adding multiple tag/labels to a maya node.
        Tag can be multiple, but must unique per every object.

        :param str tag   : The tag name to add
        :param str value :  Additional value storage
        """
        current_attr = self.getUserAttr()

        if tag in current_attr:
            raise NodeError('An attribute named {} is already'
                                   ' present on {}.'.format(tag, self.name))
        else:
            attr = self._composeTagAttr(tag)
            obj_attr = '{}.{}'.format(self.name, attr)
            mc.addAttr(self.name, longName=attr, dt='string', hidden=True)
            mc.setAttr(obj_attr, value, type='string')


    def removeTagAttribute(self, tag):
        """
        Remove the specified tag from this object
        :param str tag   : The tag name to remove
        """
        self.deleteAttr(self._composeTagAttr(tag))


    @staticmethod
    def _composeTagAttr(tag):
        """
        Create a string composed from the general tag identifier and the specific
        tag passed as argument.

        :param str tag     : The specific tag string
        :return str : The result tag attribute name
        """
        return '{}_{}'.format(constants.TAG, tag)


    @classmethod
    def findTagged(cls, tag):
        """
        Find maya node with given tag, and return as calling class instance.
        Used to find nodes regardless of name. If multiple nodes found, only
        returns first node.

        :param str tag : The tag to find.
        :return An instance of the calling class set to the found node name.
        """
        nodes = mc.ls('*.{}'.format(cls._composeTagAttr(tag)))
        if not nodes:
            return

        return cls(nodes[0].split('.')[0])


    @classmethod
    def findAllTagged(cls, tag):
        """
        Find all maya node with given tag, and return as calling class instance for each.
        Used to find nodes regardless of name.

        :param str tag : The tag to find.
        :return An instance of the calling class, for each node found.
        """
        nodes = mc.ls('*.{}'.format(cls._composeTagAttr(tag)))
        if not nodes:
            return []

        return [cls(node.split('.')[0]) for node in nodes]


    def __repr__(self):
        return "<{} '{}'>".format(self.type, self.name)

    # def importNode(self, file_type=constants.MAYA_BINARY, inherit=True):
    #     if file_type not in constants.MAYA_FILE_TYPES.values():
    #         raise NodeError(
    #             "Unrecognised file type '{}'.".format(file_type))
    #
    #     self.name = file_export_utils.importNode(self.name,
    #                                              directory=self.FOLDERS,
    #                                              inherit=inherit)
    #     return self
    #
    # def exportNode(self, file_type=constants.MAYA_BINARY):
    #     if file_type not in constants.MAYA_FILE_TYPES.values():
    #         raise NodeError(
    #             "Unrecognised file type '{}'.".format(file_type))
    #
    #     file_export_utils.exportNode(self.name, directory=self.FOLDERS)