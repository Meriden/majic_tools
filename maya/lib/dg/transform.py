import math
import xml.etree.ElementTree as ET

import maya.cmds as mc
from pymel.core.datatypes import Vector, Matrix
import maya.OpenMaya as om

from fa_rig.components.dg_component import  Node, NodeError, NodeData
from fa_rig.components.hierarchy.constraint import Constraint
from fa_rig.utils.constants import CTRL_SNAP

import fa_rig.utils.file_xml as xml_utils


# ------------------------------------------------------------------------------------------------ #

class TransformError(DGComponentError):
    pass


class Transform(DGComponent):
    """
    The Transform implements specific methods for using transform nodes in a rigging context.
    """
    XFORM_ATTR = ['{}{}'.format(x, y) for x in 'trs' for y in 'xyz']
    FOLDERS = ['hierarchy', 'transforms']

    def __init__(self, name=None):
        super(Transform, self).__init__(name)
        self._snap_items = []

    @classmethod
    def findAll(cls):
        ''' Return a Transform instance for every transform node in the scene. '''
        return [cls(transform_name) for transform_name in mc.ls(type='transform')]

    @staticmethod
    def isComponent(transform_name):
        return mc.nodeType(transform_name) == 'transform'

        # ---------------------------------------------------------------------------------------- #

    def create(self, name=None, parent=None, node_type='transform', solve_name=False):
        '''
        Create an empty transform with the specified name, as a child of the given parent, with
        the desired local transformations.

        :param str name : the name of new transform if provided. Else uses name set on initialization.
        :param str parent : the name of the parent transform if provided. Else parent to world.
        :param str node_type :
        :param bool solve_name :

        :return self
        '''
        super(Transform, self).create(name, node_type, solve_name)

        if parent and mc.objExists(parent):
            mc.parent(self.name, parent)

        return self

    def createFromData(self, name=None, root=None, parent=True, filename=None, inherit=True):
        if not name:
            name = self.name

        root = xml_utils.getRoot(name, root, filename, self.FOLDERS, inherit)

        new_parent = None
        world = False
        if isinstance(parent, (str, unicode)):
            if mc.objExists(parent):
                new_parent = parent
                parent = False
            else:
                world = True
                parent = False

        Transform.create(self, name, new_parent)
        Transform.loadData(self, root, parent=parent, world=world)

        return self

    def duplicate(self, new_name):
        """
        Duplicate the object giving a new name

        :param new_name: String for the new object name

        :return: Transform for the new object
        """
        return self.__class__(mc.duplicate(self.node, name=new_name)[0])

    # -------------------------------------------------------------------------------------------- #

    # -----------------------------------------------------------------------------------------#

    @property
    def translate(self):
        return TransformAttribute(self.node, 'translate')

    @translate.setter
    def translate(self, translate):
        mc.setAttr('{}.t'.format(self.node), *translate)

    t = translate

    @property
    def world_translate(self):
        return WorldAttribute(self.node, 't')

    @world_translate.setter
    def world_translate(self, translate):
        mc.xform(self.node, t=translate, ws=True)

    world_t = world_translate

    # -----------------------------------------------------------------------------------------#

    @property
    def rotate(self):
        return TransformAttribute(self.node, 'rotate')

    @rotate.setter
    def rotate(self, rotate):
        mc.xform(self.node, ro=rotate, os=True)

    r = rotate

    @property
    def world_rotate(self):
        return WorldAttribute(self.node, 'ro')

    @world_rotate.setter
    def world_rotate(self, rotate):
        mc.xform(self.node, ro=rotate, ws=True)

    world_r = world_rotate

    @property
    def rotate_order(self):
        return mc.getAttr('{}.rotateOrder'.format(self.node))

    @rotate_order.setter
    def rotate_order(self, value):
        mc.setAttr('{}.rotateOrder'.format(self.node), value)

    # -----------------------------------------------------------------------------------------#

    @property
    def scale(self):
        return TransformAttribute(self.node, 'scale')

    @scale.setter
    def scale(self, scale):
        mc.xform(self.node, s=scale, os=True)

    s = scale

    @property
    def world_scale(self):
        return WorldAttribute(self.node, 's')

    @world_scale.setter
    def world_scale(self, scale):
        mc.xform(self.node, s=scale, ws=True)

    world_s = world_scale

    # -----------------------------------------------------------------------------------------#

    def setToIdentity(self):
        ''' Will attempt to set translate, rotate and scale back to default values.'''

        self.translate = (0, 0, 0)
        self.rotate = (0, 0, 0)
        self.scale = (1, 1, 1)

    # -----------------------------------------------------------------------------------------#

    @property
    def shear(self):
        return ShearAttribute(self.node, 'shear')

    @shear.setter
    def shear(self, shear):
        mc.xform(self.node, absolute=True, objectSpace=True, shear=shear)

    sh = shear

    # -----------------------------------------------------------------------------------------#

    @property
    def lock(self):
        locked = False
        for attr in self.XFORM_ATTR:
            locked = mc.getAttr('{}.{}'.format(self.name, attr), l=True)
            if locked: break
        return locked

    @lock.setter
    def lock(self, value):
        value = bool(value)
        for attr in self.XFORM_ATTR:
            mc.setAttr('{}.{}'.format(self.name, attr), l=value)

    @property
    def hide(self):
        hidden = True
        for attr in self.XFORM_ATTR:
            hidden = mc.getAttr('{}.{}'.format(self.name, attr), k=True)
            if not hidden: break
        return not (hidden)

    @hide.setter
    def hide(self, value):
        value = not (bool(value))
        for attr in self.XFORM_ATTR:
            mc.setAttr('{}.{}'.format(self.name, attr), k=value)

    # -----------------------------------------------------------------------------------------#

    @property
    def visibility(self):
        attribute = '{}.visibility'.format(self.node)
        visibility = BoolAttribute(mc.getAttr(attribute))
        visibility.attribute = attribute
        return visibility

    @visibility.setter
    def visibility(self, value):
        if not mc.getAttr('{}.visibility'.format(self.node), l=True):
            mc.setAttr('{}.visibility'.format(self.node), value)

    # -----------------------------------------------------------------------------------------#

    @property
    def matrix(self):
        return mc.xform(self.node, q=True, m=True, os=True)

    @matrix.setter
    def matrix(self, matrix):
        mc.xform(self.node, m=matrix, os=True)

    @property
    def world_matrix(self):
        return mc.xform(self.node, q=True, m=True, ws=True)

    @world_matrix.setter
    def world_matrix(self, matrix):
        mc.xform(self.node, m=matrix, ws=True)

    # -----------------------------------------------------------------------------------------#

    @property
    def shapes(self):
        """
        Return the shapes of the current Transform
        :return:
        """
        shapes = mc.listRelatives(self.node, shapes=True)
        if shapes:
            return [DGComponent(shape) for shape in shapes]

        return None

    @property
    def children(self):
        """
        Return all the children under this transform

        :return: list of Transform objects if children, or None if no child
        """
        children = mc.listRelatives(self.node, children=True)

        if children:
            return [Transform(child) for child in children]
        return None

    @property
    def parent(self):
        """
        :return: The parent transform of this transform. None if no parent.
        """
        parent = mc.listRelatives(self.node, parent=True)
        return self.__class__(parent[0]) if parent else None

    @parent.setter
    def parent(self, new_parent=None):
        """
        Move the current transform under a new transform.

        :param new_parent: name of the new parent transform.
        :return: None
        """
        if new_parent is None and self.parent:
            mc.parent(self.node, w=True)
        else:
            mc.parent(self.node, new_parent)

    def listRelatives(self, *args, **kwargs):
        """
        Wrapper for listRelatives command.
        """
        return mc.listRelatives(self.name, *args, **kwargs)

    # -------------------------------------------------------------------------------------------- #

    def aimLook(self, look_obj,
                aim_vector,
                up_vector=(0, 1, 0),
                world_up=(0, 1, 0),
                worldUpObject=None,
                worldUpType=None,
                skip=None,
                mo=False):
        """
        :param Transform look_obj: Object to look at
        :param tuple aim_vector: Really you don't know?
        :param tuple up_vector: Really you don't know?

        :return: Constrain object for the created Aim
        """
        kwargs = {}
        if worldUpObject: kwargs['worldUpObject'] = worldUpObject
        if worldUpType:  kwargs['worldUpType'] = worldUpType
        if skip: kwargs['skip'] = skip

        constraint = mc.aimConstraint(look_obj,
                                      self.node,
                                      mo=mo,
                                      aimVector=aim_vector,
                                      upVector=up_vector,
                                      worldUpVector=world_up,
                                      **kwargs)[0]
        return Constraint(constraint)

    def aimConstrain(self,
                     driven,
                     aim_vector=(1, 0, 0),
                     up_vector=(0, 1, 0),
                     world_up=(0, 1, 0),
                     worldUpObject=None,
                     worldUpType=None,
                     skip=None,
                     mo=False):
        """Added to match the other constraints.. the aim look
        is working the opposite where this node is the driven"""
        kwargs = {}
        if worldUpObject: kwargs['worldUpObject'] = worldUpObject
        if worldUpType:  kwargs['worldUpType'] = worldUpType
        if skip: kwargs['skip'] = skip

        constraint = mc.aimConstraint(self.node,
                                      driven,
                                      mo=mo,
                                      aimVector=aim_vector,
                                      upVector=up_vector,
                                      worldUpVector=world_up,
                                      **kwargs)[0]
        return Constraint(constraint)

    def parentConstrain(self, driven, mo=False, hidden=False):
        return self.constrain(driven, 'parent', mo, hidden)

    def pointConstrain(self, driven, mo=False, hidden=False):
        return self.constrain(driven, 'point', mo, hidden)

    def orientConstrain(self, driven, mo=False, hidden=False):
        return self.constrain(driven, 'orient', mo, hidden)

    def scaleConstrain(self, driven, mo=False, hidden=False):
        return self.constrain(driven, 'scale', mo, hidden)

    def constrain(self, driven, method='parent', mo=False, hidden=False):
        """
        Easy way for creating a constraint from this object. Methods for creating behaviors like
        "weight blending" or "space switching" are available on the returned Constrain object.

        :param Transform driven: Transform name of the object to drive.
        :param str method: Name for connection type, valid methods: parent, scale, point, orient.
        :param bool mo: Maintain the constraint offset.
        :param bool hidden: If true, the constrain will be hidden from the outliner and channel box.

        :return: Constrain object
        """
        if method == 'parent':
            constraint = mc.parentConstraint(self.node, driven, mo=mo, decompRotationToChild=True)[
                0]

        elif method == 'point':
            constraint = mc.pointConstraint(self.node, driven, mo=mo)[0]

        elif method == 'orient':
            constraint = mc.orientConstraint(self.node, driven, mo=mo)[0]

        elif method == 'scale':
            constraint = mc.scaleConstraint(self.node, driven, mo=mo)[0]

        else:
            raise TransformError("The constrain method '{}' is not valid".format(method))

        constraint_obj = Constraint(constraint)

        if hidden:
            constraint_obj.setAttr('hiddenInOutliner', True)
            constraint_obj.setAttr('isHistoricallyInteresting', False)

        return constraint_obj

    # -------------------------------------------------------------------------------------------- #
    def parentMatrixConstrain(self, driven, mo=False):
        """
        :param Transform driven: transform to apply the matrix constraint to
        :param bool mo: maintain offset
        :return DGComponent: decomposeMatrix node:
        """
        return self.matrixConstrain(driven, channels='tr', mo=mo)

    def parentScaleMatrixConstrain(self, driven, mo=False):
        """
        :param Transform driven: transform to apply the matrix constraint to
        :param bool mo: maintain offset
        :return DGComponent: decomposeMatrix node:
        """
        return self.matrixConstrain(driven, channels='trs', mo=mo)

    def scaleMatrixConstrain(self, driven, mo=False):
        """
        :param Transform driven: transform to apply the matrix constraint to
        :param bool mo: maintain offset
        :return DGComponent: decomposeMatrix node:
        """
        return self.matrixConstrain(driven, channels='s', mo=mo)

    def orientMatrixConstrain(self, driven, mo=False):
        """
        :param Transform driven: transform to apply the matrix constraint to
        :param bool mo: maintain offset
        :return DGComponent: decomposeMatrix node:
        """
        return self.matrixConstrain(driven, channels='r', mo=mo)

    def pointMatrixConstrain(self, driven, mo=False):
        """
        :param Transform driven: transform to apply the matrix constraint to
        :param bool mo: maintain offset
        :return DGComponent: decomposeMatrix node:
        """
        if mo:
            mo = 2
        return self.matrixConstrain(driven, channels='t', mo=mo)

    def pointOrientMatrixConstrain(self, driven, mo=False):
        """
        :param Transform driven: transform to apply the matrix constraint to
        :param bool mo: maintain offset
        :return DGComponent: decomposeMatrix node:
        """
        if mo:
            mo = 2
        return self.matrixConstrain(driven, channels='tr', mo=mo)

    def matrixConstrain(self,
                        driven,
                        channels='trsh',
                        mo=0,
                        joint_orient=False,
                        scale_compensate=False,
                        parent_space=None):
        """
        Use the matrixConstraint for faster rigs.
        If you set the channels to 'tr' it will act just as a parentConstraint.
        If you set the channels to 's' it will act just as a scaleConstraint.
        If you set the channels to 'r' it will act just as a orientConstraint.

        there is no blending or multiple targets concept and the driven object MUST have the
        rotate order set to the default xyz or it will not work.

        :param Transform driven: the driven object

        :param str channels: specify if the result should be connected to
                             translate, rotate or/and scale by passing a string with
                             the channels to connect.
                             Example: 'trsh' will connect them all, 'tr' will skip scale and shear

        :param int mo:      Maintain offset, like in the constrains a difference matrix will be
                            held for retaining the driven original position.
                            1 will multiply the offset before the transformations, 2 after.
                            by multiplying it after, the effect will be suitable for a
                            pointConstraint like behavior.

        :param bool joint_orient: Connect joint orient rather than accounting for a fixed value.
                                  This will create significantly more nodes.

        :param bool scale_compensate: Connect the joint inverse scale and scale compensate, rather
                                      than accounting for a fixed value. This will create significantly
                                      more nodes.

        :param Transform parent_space: Use the provided parent space instead of the
        parentInverseMatrix of the driven

        :return DGComponent: decomposeMatrix node
                             TODO containing the information of the constraint network
        """

        def getDagPath(node=None):
            sel = om.MSelectionList()
            sel.add(node)
            d = om.MDagPath()
            sel.getDagPath(0, d)
            return d

        constrain_matrix = DGComponent(mc.createNode('multMatrix'))
        decompose = DGComponent(mc.createNode('decomposeMatrix'))

        # multiply the matrices depending on the options
        #
        matrices_order = ['{}.worldMatrix[0]'.format(self.name)]

        if parent_space:
            # Use the user provided inverse matrix
            #
            matrices_order.append('{}.worldInverseMatrix'.format(parent_space.name))
        else:
            # Get the inverse matrix form the parent for avoiding double transformations
            #
            matrices_order.append('{}.parentInverseMatrix'.format(driven.name))

        # Compute the offset
        #
        if mo:
            if 1 <= mo <= 2:
                parentWorldMatrix = getDagPath(self).inclusiveMatrix()
                childWorldMatrix = getDagPath(driven).inclusiveMatrix()

                result_matrix = childWorldMatrix * parentWorldMatrix.inverse()
                if not result_matrix.isEquivalent(om.MMatrix.identity, 10e-5):
                    offset_matrix = [result_matrix(i, j) for i in range(4) for j in range(4)]

                    # Zero the translation part on the offset matrix, compute the post translation
                    # offset and add it to the matrices list
                    #
                    if mo == 2:
                        # Zero the translation part on the offset matrix,
                        # this will keep the rotation
                        #
                        offset_matrix[12] = 0
                        offset_matrix[13] = 0
                        offset_matrix[14] = 0

                        # Compute the offset from the driven to the driver in the
                        # local space of the driven
                        #
                        local_offset = parentWorldMatrix * childWorldMatrix.inverse()
                        loc_off_m = [local_offset(i, j) for i in range(4) for j in range(4)]

                        # Keep only the translation information and set to the node
                        #
                        trans_offset_matrix = [1, 0, 0, 0,
                                               0, 1, 0, 0,
                                               0, 0, 1, 0,
                                               -loc_off_m[12], -loc_off_m[13], -loc_off_m[14], 1]
                        matrices_order.append(trans_offset_matrix)

                    matrices_order.insert(0, offset_matrix)
            else:
                raise TransformError('Invalid offset value {}.'.format(mo))

        # Set or connect the matrices
        for x, matrix_out in enumerate(matrices_order):
            if isinstance(matrix_out, list):
                mc.setAttr('{}.matrixIn[{}]'.format(constrain_matrix, x), matrix_out, type='matrix')
            else:
                mc.connectAttr(matrix_out, '{}.matrixIn[{}]'.format(constrain_matrix, x))

        # Connect the resulting matrix to the decompose matrix, then connect only
        # the specified channels to the driven object
        constrain_matrix.connect('matrixSum', decompose, 'inputMatrix')
        for channel in channels:
            if channel == 't':
                decompose.connect('outputTranslate', driven, 'translate')
            if channel == 'r':
                decompose.connect('outputRotate', driven, 'rotate')
                driven.connect('rotateOrder', decompose, 'inputRotateOrder')
            if channel == 's':
                decompose.connect('outputScale', driven, 'scale')
            if channel == 'h':
                decompose.connect('outputShear', driven, 'shear')

        # If the driven is a joint, make sure to handle the joint orient
        # as well as scale inverse. this is apparently slower than using a
        # constraint though...
        if driven.mayaType == 'joint' and {'r', 's', 'h'}.intersection(set(channels)):
            joint_matrix_order = ['{}.matrixSum'.format(constrain_matrix)]

            is_value = driven.getAttr('inverseScale')[0]
            jo_value = driven.getAttr('jointOrient')[0]

            # Connect inverse scale ...
            if scale_compensate:
                inv_scale_bc = DGComponent(mc.createNode('blendColors'))
                driven.connect('inverseScale', inv_scale_bc, 'color1')
                inv_scale_bc.setAttr('color2', [1, 1, 1])
                driven.connect('segmentScaleCompensate', inv_scale_bc, 'blender')

                inv_scale_cm = DGComponent(mc.createNode('composeMatrix'))
                inv_scale_bc.connect('output', inv_scale_cm, 'inputScale')
                joint_matrix_order.append(inv_scale_cm.attr('outputMatrix'))

            # ... or set a fixed value
            elif (om.MVector(*is_value) - om.MVector(1, 1, 1)).length() > 10e-4:
                if driven.getAttr('segmentScaleCompensate'):
                    is_matrix = [is_value[0], 0, 0, 0,
                                 0, is_value[1], 0, 0,
                                 0, 0, is_value[2], 0,
                                 0, 0, 0, 1]
                    joint_matrix_order.append(is_matrix)

            # Connect joint orient ...
            if joint_orient:
                jo_cm = DGComponent(mc.createNode('composeMatrix'))
                driven.connect('jointOrient', jo_cm, 'inputRotate')

                jo_im = DGComponent(mc.createNode('inverseMatrix'))
                jo_cm.connect('outputMatrix', jo_im, 'inputMatrix')
                joint_matrix_order.append(jo_im.attr('outputMatrix'))

            # ... or set a fixed value
            elif om.MVector(*jo_value).length() > 10e-4:
                jo_euler = om.MEulerRotation(*[math.radians(value) for value in jo_value])
                jo_inv_mtx = jo_euler.asMatrix().inverse()
                jo_inv_mtx = [jo_inv_mtx(i, j) for i in range(4) for j in range(4)]
                joint_matrix_order.append(jo_inv_mtx)

            # Reconnect the matrix decompose if we need to adjust for joint
            # orient or inverse scale
            if len(joint_matrix_order) > 1:
                joint_mm = DGComponent(mc.createNode('multMatrix'))
                for x, matrix_out in enumerate(joint_matrix_order):
                    if isinstance(matrix_out, list):
                        mc.setAttr('{}.matrixIn[{}]'.format(joint_mm, x), matrix_out, type='matrix')
                    else:
                        mc.connectAttr(matrix_out, '{}.matrixIn[{}]'.format(joint_mm, x))
                joint_mm.connect('matrixSum', decompose, 'inputMatrix')

                # But keep calculating translation in parent space
                if 't' in channels:
                    t_vp = DGComponent(mc.createNode('vectorProduct'))
                    t_vp.setAttr('operation', 4)
                    constrain_matrix.connect('matrixSum', t_vp, 'matrix')
                    t_vp.connect('output', driven, 'translate')

        return decompose

    def twistConstrain(self, driven, twist_axis):  # , mo=0):
        """
        Constrain the rotations of the driven object from the specified twist axis of
        the driver object. This is similar to using the ik or aim constraint and
        will flip at 180 degrees.

        :param Transform driven: the object that will be driven from the twist of this object
        :param str twist_axis: x, y or z. The axis to extract for the twist
        :return DGComponent : the quatToEuler node
        """
        # Make sure that the rotate order of the driven is xyz since other rotate orders do not work
        #
        if driven.rotate_order == 0:
            if twist_axis in 'xyzXYZ':
                # Get the difference matrix between this object and its parent
                # This will give us an relative matrix of this object regardless
                # of the orientation of the parent
                #
                diff_matrix = DGComponent(mc.createNode('multMatrix'))
                self.connect('worldMatrix[0]', diff_matrix, 'matrixIn[0]')
                self.connect('parentInverseMatrix[0]', diff_matrix, 'matrixIn[1]')

                # Now get the quaternion rotation of this matrix and use only
                # the specified axis to output the euler rotation
                #
                decompose = DGComponent(mc.createNode('decomposeMatrix'))
                quat_to_euler = DGComponent(mc.createNode('quatToEuler'))

                diff_matrix.connect('matrixSum', decompose, 'inputMatrix')
                self.connect('rotateOrder', decompose, 'inputRotateOrder')

                decompose.connect('outputQuatW', quat_to_euler, 'inputQuatW')
                self.connect('rotateOrder', quat_to_euler, 'inputRotateOrder')

                for ax in 'XYZ':
                    if ax == twist_axis.upper():
                        decompose.connect('outputQuat' + ax, quat_to_euler, 'inputQuat' + ax)

                # Connect the rotation to the driven object
                #
                quat_to_euler.connect('outputRotate', driven, 'rotate')

            else:
                raise TransformError('The specified axis {} is not valid.'.format(twist_axis))
        else:
            # its true for the matrix constraint... to check if is also for this...
            #
            raise TransformError('Unfortunately the twistConstrain works only if the driven has '
                                 'the default rotate order.')

    # -------------------------------------------------------------------------------------------- #
    def getFlipAxis(self, ref_matrix):
        """
        Get the mirror axis from an object flipped with the right orientation.
        We use this method when our guide controls are constrained and we need
        to know wich axis we have to flip in order to have a mirrored transform behavior
        along the world X axis.

        :param list ref_matrix: The object matrix from the opposite side used for the comparison.
        :return: the axis to flip to use once the points are mirrored
        """
        dot_list = []
        for x in range(0, 12, 4):
            # ref_vector = Vector(ref_pt.world_matrix[x:x + 3])
            ref_vector = Vector(ref_matrix[x:x + 3])
            ctrl_vector = Vector(self.world_matrix[x:x + 3])
            dot_p = ref_vector.dot(ctrl_vector)

            dot_list.append(dot_p)

        return 'xyz'[dot_list.index(min(dot_list))]

    def invert(self, axis='x'):
        if axis not in 'xyz':
            raise TransformError("Invert axis '{}' not recognized.".format(axis))

        if axis == 'x':
            self.scale.x *= -1
        elif axis == 'y':
            self.scale.y *= -1
        elif axis == 'z':
            self.scale.z *= -1

    def isInFront(self, plane_center, plane_normal):
        """
        Given a plane described by 2 vectors, return True if currently in front of the plane,
        False if behind.

        :param vector plane_center:
        :param vector plane_normal:

        :return bool
        """
        position = Vector(self.world_translate)
        offset = Vector(plane_center)
        normal = Vector(plane_normal)
        normal.normalize()

        vec = position - offset
        side = normal.dot(vec)

        if side >= 0:
            return True
        return False

    def scaleMirror(self, axis, world=True):
        """
        Create a temporary group flip and delete the group
        :param str axis: the axis to mirror
        :param bool world: If the mirror must be done across
                           the world center or not.
        """
        if axis not in 'xyz':
            raise TransformError("Scale axis '{}' not recognized.".format(axis))

        tmp_grp = mc.group(self.name)

        if world:
            mc.move(0, 0, 0, '{}.scalePivot'.format(tmp_grp),
                    '{}.rotatePivot'.format(tmp_grp), rpr=True)

        mc.setAttr('{}.scale{}'.format(tmp_grp, axis.capitalize()), -1)

        mc.ungroup(tmp_grp)

    def mirrorInX(self, world=False):
        '''
        Reflects the transform across the X axis.

        :param bool world: if True, use world axis
        '''
        return self._mirrorInAxis((1, 0, 0), world)

    def mirrorInY(self, world=False):
        '''
        Reflects the transform across the Y axis.

        :param bool world: if True, use world axis
        '''
        return self._mirrorInAxis((0, 1, 0), world)

    def mirrorInZ(self, world=False):
        '''
        Reflects the transform across the Z axis.

        :param bool world: if True, use world axis
        '''
        return self._mirrorInAxis((0, 0, 1), world)

    def _mirrorInAxis(self, plane_normal, world):
        plane_center = (0, 0, 0)
        if world:
            return self.mirrorAcrossPlane(plane_center, plane_normal)

        parent = self.parent
        if parent:
            parent = Transform(parent)
            plane_center = parent.world_translate
            plane_normal = Vector(plane_normal) * Matrix(parent.world_matrix)
            plane_normal = (plane_normal[0], plane_normal[1], plane_normal[2])

        return self.mirrorAcrossPlane(plane_center, plane_normal)

    def mirrorAcrossPlane(self, plane_center, plane_normal):
        """
        Reflect the transformations of the current object by providing a reflection
        plane described as 2 vectors and the center of reflection as a vector.

        :param center_point:
        :param reflection_plane:
        :return:
        """

        position = Vector(self.world_translate)
        offset = Vector(plane_center)
        normal = Vector(plane_normal)
        normal.normalize()

        vec = position - offset
        proj = normal.dot(vec) * normal
        mirror = -proj + (vec - proj) + offset

        self.world_translate = mirror[0], mirror[1], mirror[2]

    # -------------------------------------------------------------------------------------------- #

    def lookAt(self, node, aim_vector=(1, 0, 0), up_vector=(0, 1, 0)):  # NEEDS TO BE FINISHED
        """
        Orient a transform by making it point to another transform

        :param node:         A transform node to aim at.
        :param aim_vector:    The aim vector
        :param up_vector:    The Up vector

        :return None
        """

        if not isinstance(node, Transform):
            node = Transform(node)

        pivot = Vector(*self.world_translate)
        point = Vector(*node.world_translate)

        x = point - pivot
        x.normalize()

        y = Vector(up_vector)
        y.normalize()

        z = x ^ y
        z.normalize()

        y = z ^ x
        y.normalize()

        atan2 = math.atan2
        power = math.pow
        degrees = math.degrees
        sqrt = math.sqrt

        rot_x = degrees(atan2(y[2], z[2]))
        rot_y = degrees(atan2(-x[2], sqrt(power(y[2], 2) + power(z[2], 2))))
        rot_z = degrees(atan2(x[1], x[0]))

        self.world_rotate = rot_x, rot_y, rot_z
        #
        aim = Vector(aim_vector)
        aim.normalize()

        aim = aim ^ x
        aim.normalize()

        angle = math.acos(aim.dot(x))

        A = Matrix(0, -aim[2], aim[1], 0,
                   aim[2], 0, -aim[0], 0,
                   -aim[1], aim[0], 0, 0,
                   0, 0, 0, 1)

        I = Matrix()
        I.setToIdentity()

        R = (I + (angle * A) + ((1 - math.cos(angle)) * (A * A))) * Matrix(x, y, z)
        return R[0], R[1], R[2]

        x, y, z = R[0], R[1], R[2]
        x.normalize()
        y.normalize()
        z.normalize()

        rot_x = degrees(atan2(y[2], z[2]))
        rot_y = degrees(atan2(-x[2], sqrt(power(y[2], 2) + power(z[2], 2))))
        rot_z = degrees(atan2(x[1], x[0]))

        self.world_rotate = rot_x, rot_y, rot_z

        return (math.sin(angle) * A) + ((1 - math.cos(angle)) * (A * A))

    # ---------------------------------------------------------------------------------------- #

    def snap(self, snap_items):
        '''
        Snap the transform to an average position of the given snap items.
        Dag objects only. Transforms, Joints or shape components.

        :param list snap_items: the list of items to create an average position from
        '''
        if not snap_items:
            return

        if isinstance(snap_items, (str, unicode)):
            snap_items = [snap_items]

        allowed_items = ['transform', 'joint', 'mesh', 'nurbsCurve', 'nurbsSurface']

        center = Vector(0, 0, 0)
        filtered_snap_items = []
        for snap_item in snap_items:
            if not mc.objExists(snap_item):
                continue

            item_type = mc.nodeType(snap_item)
            if item_type not in allowed_items:
                continue

            check_data = ()

            if item_type == 'mesh':
                num_verts = mc.polyEvaluate(snap_item, v=True)
                num_faces = mc.polyEvaluate(snap_item, f=True)
                check_data = (num_verts, num_faces)

            elif item_type == 'nurbsCurve':
                check_data = mc.getAttr('{}.cp'.format(snap_item), size=True)

            elif item_type == 'nurbsSurface':
                check_data = len(mc.getAttr('{}.cv[*]'.format(snap_item)))

            center += Vector(mc.xform(snap_item, q=True, ws=True, t=True))
            filtered_snap_items.append((str(snap_item), check_data))

        center /= len(filtered_snap_items)

        self.world_translate = (center.x, center.y, center.z)

        self._setSnapItems(filtered_snap_items)

    @property
    def snap_items(self):
        if self._snap_items:
            return self._snap_items

        snap_items = self._getSnapItems()
        self._snap_items = [snap_item for snap_item, _ in snap_items]
        return self._snap_items

    def _getSnapItems(self):
        if not self.hasTag(CTRL_SNAP):
            snap_items = []
        else:
            snap_items = eval(self.getTagValue(CTRL_SNAP))
        return snap_items

    def _setSnapItems(self, snap_items_data):
        if not self.hasTag(CTRL_SNAP):
            self.addTagAttribute(CTRL_SNAP, repr(snap_items_data))
        else:
            self.setTagValue(CTRL_SNAP, repr(snap_items_data))

    # ---------------------------------------------------------------------------------------- #

    def saveData(self, parent=None):
        root = ET.Element('Transform', attrib={'name': repr(self.node)})
        if parent == None:
            xml_tree = ET.ElementTree(root)
        else:
            parent.append(root)

        root.attrib['visibility'] = repr(self.visibility)
        root.attrib['rotate_order'] = repr(self.rotate_order)

        parent_transform = self.parent
        if parent_transform:
            parent_transform = parent_transform.name
        root.attrib['parent'] = repr(parent_transform)

        local_element = ET.Element('local')
        local_element.attrib['t'] = repr(self.translate)
        local_element.attrib['r'] = repr(self.rotate)
        local_element.attrib['s'] = repr(self.scale)
        root.append(local_element)

        world_element = ET.Element('world')
        world_element.attrib['t'] = repr(self.world_translate)
        world_element.attrib['r'] = repr(self.world_rotate)
        world_element.attrib['s'] = repr(self.world_scale)
        root.append(world_element)

        limit_element = ET.Element('limit')
        limit_element.attrib['t'] = repr(self.translate.limits)
        limit_element.attrib['r'] = repr(self.rotate.limits)
        limit_element.attrib['s'] = repr(self.scale.limits)
        root.append(limit_element)

        snap_items = self._getSnapItems()
        if snap_items:
            snap_element = ET.Element('snap')
            snap_element.attrib['items'] = repr(snap_items)
            root.append(snap_element)

        if parent is None:
            xml_utils.write(xml_tree, self.name, self.FOLDERS)

    def loadData(self, root=None, filename=None, inherit=True, parent=True, world=False):
        root = xml_utils.getRoot(self.node, root, filename, self.FOLDERS, inherit)

        self.visibility = eval(root.attrib['visibility'])
        self.rotate_order = eval(root.attrib['rotate_order'])

        # attempt to parent transform under stored parent transform
        #
        parent_transform = eval(root.attrib['parent'])
        parent_space = not world and parent and parent_transform and mc.objExists(parent_transform)

        if parent_space and (not self.parent or self.parent.name != parent_transform):
            self.parent = parent_transform

        local_element = world_element = limit_element = snap_element = None
        for child in root:
            if child.tag == 'local':
                local_element = child
            elif child.tag == 'world':
                world_element = child
            elif child.tag == 'limit':
                limit_element = child
            elif child.tag == 'snap':
                snap_element = child

        if limit_element is not None:
            self.translate.limits = eval(limit_element.attrib['t'])
            self.rotate.limits = eval(limit_element.attrib['r'])
            self.scale.limits = eval(limit_element.attrib['s'])

        # if snap items stored, attempt to snap transform if they exist
        #
        if snap_element is not None and not world:
            snap_items = eval(snap_element.attrib['items'])

            filtered_snap_items = []
            for snap_item, check_data in snap_items:
                if not mc.objExists(snap_item):
                    continue

                item_type = mc.nodeType(snap_item)
                if item_type == 'mesh':
                    num_verts = mc.polyEvaluate(snap_item, v=True)
                    num_faces = mc.polyEvaluate(snap_item, f=True)
                    if (num_verts, num_faces) != check_data:
                        continue
                elif item_type == 'nurbsCurve':
                    if check_data != mc.getAttr('{}.cp'.format(snap_item), size=True):
                        continue
                elif item_type == 'nurbsSurface':
                    if check_data != len(mc.getAttr('{}.cv[*]'.format(snap_item))):
                        continue

                filtered_snap_items.append(snap_item)

            if filtered_snap_items:
                self.snap(filtered_snap_items)
                self.rotate = eval(local_element.attrib['r'])
                self.scale = eval(local_element.attrib['s'])
                return

        # if no snap items, set to parent space or world space
        #
        if parent_space:
            self.translate = eval(local_element.attrib['t'])
            self.rotate = eval(local_element.attrib['r'])
            self.scale = eval(local_element.attrib['s'])
        else:
            self.world_translate = eval(world_element.attrib['t'])
            self.world_rotate = eval(world_element.attrib['r'])
            self.world_scale = eval(world_element.attrib['s'])


# ------------------------------------------------------------------------------------------------ #


class Double3Attribute(list):
    AXES = ('X', 'Y', 'Z')
    TOL = 10e-7

    def __init__(self, node, attr):
        self.attr = '{}.{}'.format(node, attr)

    @property
    def lock(self):
        for axis in self.AXES:
            if mc.getAttr('{}{}'.format(self.attr, axis), lock=True):
                return True
        return False

    @lock.setter
    def lock(self, value):
        value = bool(value)
        for axis in self.AXES:
            mc.setAttr('{}{}'.format(self.attr, axis), lock=value)

    @property
    def hide(self):
        for axis in self.AXES:
            if not mc.getAttr('{}{}'.format(self.attr, axis), keyable=True):
                return True
        return False

    @hide.setter
    def hide(self, value):
        for axis in self.AXES:
            mc.setAttr('{}{}'.format(self.attr, axis), keyable=(not value))

    def __len__(self):
        return 3

    def __getitem__(self, index):
        attribute = '{}{}'.format(self.attr, self.AXES[index])
        value = FloatAttribute(mc.getAttr(attribute))
        value.attribute = attribute
        return value

    def __setitem__(self, index, value):
        mc.setAttr('{}{}'.format(self.attr, self.AXES[index]), value)

    def __iter__(self, *args, **kwargs):
        for index in range(3):
            yield self.__getitem__(index)

    def __eq__(self, cmp):
        for value, cmp_value in zip(self, cmp):
            if abs(value - cmp_value) > self.TOL:
                return False
        return True

    def __repr__(self, *args, **kwargs):
        return '[{}, {}, {}]'.format(*[self.__getitem__(index) for index in range(3)])


class TransformAttribute(Double3Attribute):
    limit_attrs = {'translate': 'Trans', 'rotate': 'Rot', 'scale': 'Scale'}

    @property
    def x(self):
        return self.__getitem__(0)

    @x.setter
    def x(self, value):
        self.__setitem__(0, value)

    @property
    def y(self):
        return self.__getitem__(1)

    @y.setter
    def y(self, value):
        self.__setitem__(1, value)

    @property
    def z(self):
        return self.__getitem__(2)

    @z.setter
    def z(self, value):
        self.__setitem__(2, value)

    @property
    def __and__(self, rhs):
        return (self.x, self.y, self.z) & rhs

    @property
    def limits(self):
        ''' Returns a list of 3 tuples representing translate, rotate, scale, each containing a
            pair of tuples ((min_enabled, min_value), (max_enabled, max_value)).

        :return list of enabled/value pairs
        '''
        node, transform = self.attr.split('.')
        limit_attr = TransformAttribute.limit_attrs[transform]

        limits = []
        for axis in 'XYZ':
            limit_axis = limit_attr + axis
            min_enabled = mc.getAttr('{}.min{}LimitEnable'.format(node, limit_axis))
            min_value = mc.getAttr('{}.min{}Limit'.format(node, limit_axis))
            max_enabled = mc.getAttr('{}.max{}LimitEnable'.format(node, limit_axis))
            max_value = mc.getAttr('{}.max{}Limit'.format(node, limit_axis))
            limits.append(((min_enabled, min_value), (max_enabled, max_value)))

        return limits

    @limits.setter
    def limits(self, limits):
        ''' Requires a list of 3 tuples (translate, rotate, scale), each containing a
            pair of tuples ((min_enabled, min_value), (max_enabled, max_value)).

        :param list/tuple limits : list of enabled/value pairs. See description.
        '''
        node, transform = self.attr.split('.')
        limit_attr = TransformAttribute.limit_attrs[transform]

        for i, axis in enumerate('XYZ'):
            limit_axis = limit_attr + axis
            mc.setAttr('{}.min{}LimitEnable'.format(node, limit_axis), limits[i][0][0])
            mc.setAttr('{}.min{}Limit'.format(node, limit_axis), limits[i][0][1])
            mc.setAttr('{}.max{}LimitEnable'.format(node, limit_axis), limits[i][1][0])
            mc.setAttr('{}.max{}Limit'.format(node, limit_axis), limits[i][1][1])

    def __getitem__(self, index):
        axis = self.AXES[index]
        attribute = '{}{}'.format(self.attr, axis)
        node, transformation = self.attr.split('.')

        if transformation in TransformAttribute.limit_attrs.keys():
            value = TransformFloatAttribute(mc.getAttr(attribute))
            value.attribute = attribute
            value._node = node
            value._limit_attr = TransformAttribute.limit_attrs.get(transformation, None)
            value._limit_attr = value._limit_attr + axis if value._limit_attr else None

        else:
            value = FloatAttribute(mc.getAttr(attribute))
            value.attribute = attribute

        return value


class ShearAttribute(Double3Attribute):
    AXES = ('XY', 'XZ', 'YZ')

    @property
    def xy(self):
        return self.__getitem__(0)

    @xy.setter
    def xy(self, value):
        self.__setitem__(0, value)

    @property
    def xz(self):
        return self.__getitem__(1)

    @xz.setter
    def xz(self, value):
        self.__setitem__(1, value)

    @property
    def yz(self):
        return self.__getitem__(2)

    @yz.setter
    def yz(self, value):
        self.__setitem__(2, value)


class Attribute(object):
    def __init__(self):
        self.attribute = None

    @property
    def lock(self):
        return mc.getAttr(self.attribute, l=True)

    @lock.setter
    def lock(self, value):
        mc.setAttr(self.attribute, l=bool(value))

    @property
    def hide(self):
        return not (mc.getAttr(self.attribute, k=True))

    @hide.setter
    def hide(self, value):
        mc.setAttr(self.attribute, k=not (bool(value)))


class FloatAttribute(float, Attribute):
    def __init__(self, *args, **kwargs):
        float.__init__(self, *args, **kwargs)
        Attribute.__init__(self)


class IntAttribute(int, Attribute):
    def __init__(self, *args, **kwargs):
        int.__init__(self, *args, **kwargs)
        Attribute.__init__(self)


class BoolAttribute(Attribute):
    def __init__(self, value):
        Attribute.__init__(self)
        self.value = bool(value)

        func_names = set(dir(bool)) - set(['__init__', '__doc__', '__class__'])
        for func_name in list(func_names):
            setattr(self, func_name, getattr(self.value, func_name))

    def __eq__(self, rhs):
        return self.value == rhs

    def __nonzero__(self):
        return self.value

    def __str__(self):
        return self.value.__str__()

    __repr__ = __str__


# ------------------------------------------------------------------------------------------------ #

class WorldAttribute(TransformAttribute):
    def __init__(self, node, attr):
        super(WorldAttribute, self).__init__(node, attr)
        self.node = node
        self._get_kwargs = {'q': True, attr: True, 'ws': True}
        self._set_kwargs = {attr: 0, 'a': True, 'ws': True}

    def __getitem__(self, index):
        return mc.xform(self.node, **self._get_kwargs)[index]

    def __setitem__(self, index, value):
        values = mc.xform(self.node, **self._get_kwargs)
        values[index] = value
        self._set_kwargs[self.attr] = values
        mc.xform(self.node, **self._set_kwargs)

    def __iter__(self, *args, **kwargs):
        for value in mc.xform(self.node, **self._get_kwargs):
            yield value

    def __repr__(self, *args, **kwargs):
        return '[{}, {}, {}]'.format(*[value for value in self.__iter__()])


# ------------------------------------------------------------------------------------------------ #

class TransformFloatAttribute(FloatAttribute):
    def __init__(self, *args, **kwargs):
        FloatAttribute.__init__(self, *args, **kwargs)
        self._node = None
        self._limit_attr = None
        self._axis = None

    @property
    def minLimit(self):
        return mc.getAttr('{}.min{}Limit'.format(self._node, self._limit_attr))

    @minLimit.setter
    def minLimit(self, value):
        mc.setAttr('{}.min{}Limit'.format(self._node, self._limit_attr), value)

    @property
    def minLimitEnable(self):
        return mc.getAttr('{}.min{}LimitEnable'.format(self._node, self._limit_attr))

    @minLimitEnable.setter
    def minLimitEnable(self, value):
        mc.setAttr('{}.min{}LimitEnable'.format(self._node, self._limit_attr), bool(value))

    @property
    def maxLimit(self):
        return mc.getAttr('{}.max{}Limit'.format(self._node, self._limit_attr, self._axis))

    @maxLimit.setter
    def maxLimit(self, value):
        mc.setAttr('{}.max{}Limit'.format(self._node, self._limit_attr), value)

    @property
    def maxLimitEnable(self):
        return mc.getAttr('{}.max{}LimitEnable'.format(self._node, self._limit_attr))

    @maxLimitEnable.setter
    def maxLimitEnable(self, value):
        mc.setAttr('{}.max{}LimitEnable'.format(self._node, self._limit_attr), bool(value))


