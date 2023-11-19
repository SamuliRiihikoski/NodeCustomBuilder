# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

import bpy
import os
from enum import Enum
import numpy


class settingType(int, Enum):
    OUTPUT: int = -2
    PARAM: int = 0
    INPUT: int = 1
    OBJECT: int = 3
    IMAGE: int = 4
    COLOR_RAMP1: int = 7
    CoLOR_RAMP2: int = 8
    CURVE: int = 9
    COLLECTION: int = 13
    SELECT_IMAGE: int = 14
    SELECT_TEXTURE: int = 15
    SELECT_MATERIAL: int = 16
    MULTI_OPTION: int = 17
    SELECT_FONT: int = 18


def checkVersion():
    numero = bpy.app.version
    tulos = int(eval(f"{numero[0]}{numero[1]}"))
    return tulos


def node_specific_attributes(node, settings):

    # ATTRIBUTE

    if node.type == 'ATTRIBUTE_STATISTIC':
        settings.append([settingType.PARAM, 'data_type', node.data_type])
        settings.append([settingType.PARAM, 'domain', node.domain])
    
    elif node.type == 'ATTRIBUTE_DOMAIN_SIZE':
        settings.append([settingType.PARAM, 'component', node.component])

    elif node.type == 'BLUR_ATTRIBUTE':
        settings.append([settingType.PARAM, 'data_type', node.data_type])

    elif node.type == 'CAPTURE_ATTRIBUTE':
        settings.append([settingType.PARAM, 'data_type', node.data_type])
        settings.append([settingType.PARAM, 'domain', node.domain])

    elif node.type == 'STORE_NAMED_ATTRIBUTE':
        settings.append([settingType.PARAM, 'data_type', node.data_type])
        settings.append([settingType.PARAM, 'domain', node.domain])

    # INPUT / CONSTANT

    elif node.type == 'INPUT_BOOL':
        settings.append([settingType.PARAM, 'boolean', node.boolean])

    elif node.type == 'INPUT_COLOR':
        array = numpy.array(node.color).tolist()
        settings.append([settingType.PARAM, 'color', array])

    elif node.type == 'INPUT_INT':
        settings.append([settingType.PARAM, 'integer', node.integer])

    elif node.type == 'INPUT_VECTOR':
        array = numpy.array(node.vector).tolist()
        settings.append([settingType.PARAM, 'vector', array])

    elif node.type == 'INPUT_MATERIAL':
        settings.append([settingType.SELECT_MATERIAL, node.material.name])

    elif node.type == 'INPUT_STRING':
        settings.append([settingType.PARAM, 'string', node.string])


    # INPUT / GROUP

    elif node.type == 'COLLECTION_INFO':
        settings.append([settingType.PARAM, 'transform_space', node.transform_space])

    elif node.type == 'OBJECT_INFO':
        settings.append([settingType.PARAM, 'transform_space', node.transform_space])

    # INPUT / SCENE


    # OUTPUT

    elif node.type == 'VIEWER':
        settings.append([settingType.PARAM, 'domain', node.domain])

    # GEOMETRY / SAMPLE

    elif node.type == 'PROXIMITY':
        settings.append([settingType.PARAM, 'target_element', node.target_element])

    elif node.type == 'RAYCAST':
        settings.append([settingType.PARAM, 'data_type', node.data_type])
        settings.append([settingType.PARAM, 'mapping', node.mapping])

    elif node.type == 'SAMPLE_INDEX':
        settings.append([settingType.PARAM, 'data_type', node.data_type])
        settings.append([settingType.PARAM, 'domain', node.domain])
        settings.append([settingType.PARAM, 'clamp', node.clamp])

    elif node.type == 'SAMPLE_INDEX':
        settings.append([settingType.PARAM, 'domain', node.domain])

    # GEOMETRY / OPERATIONS

    elif node.type == 'DELETE_GEOMETRY':
        settings.append([settingType.PARAM, 'domain', node.domain])
        settings.append([settingType.PARAM, 'mode', node.mode])

    elif node.type == 'DUPLICATE_ELEMENTS':
        settings.append([settingType.PARAM, 'domain', node.domain])

    elif node.type == 'MERGE_BY_DISTANCE':
        settings.append([settingType.PARAM, 'mode', node.mode])

    elif node.type == 'SEPARATE_GEOMETRY':
        settings.append([settingType.PARAM, 'domain', node.domain])

    # CURVE / READ

    elif node.type == 'CURVE_HANDLE_TYPE_SELECTION':
        settings.append([settingType.PARAM, 'handle_type', node.handle_type])
        settings.append([settingType.MULTI_OPTION, 'mode', list(node.mode)])


    # CURVE / SAMPLE

    elif node.type == 'SAMPLE_CURVE':
        settings.append([settingType.PARAM, 'data_type', node.data_type])
        settings.append([settingType.PARAM, 'mode', node.mode])
        settings.append([settingType.PARAM, 'use_all_curves', node.use_all_curves])


    # CURVE / WRITE

    elif node.type == 'SET_CURVE_NORMAL':
        settings.append([settingType.PARAM, 'mode', node.mode])

    elif node.type == 'SET_CURVE_HANDLES':
        settings.append([settingType.PARAM, 'mode', node.mode])

    elif node.type == 'CURVE_SET_HANDLES':
        settings.append([settingType.PARAM, 'handle_type', node.handle_type])
        settings.append([settingType.MULTI_OPTION, 'mode', list(node.mode)])

    elif node.type == 'CURVE_SPLINE_TYPE':
        settings.append([settingType.PARAM, 'spline_type', node.spline_type])

    # CURVE / OPERATIONS

    elif node.type == 'CURVE_TO_POINTS':
        settings.append([settingType.PARAM, 'mode', node.mode])

    elif node.type == 'FILL_CURVE':
        settings.append([settingType.PARAM, 'mode', node.mode])

    elif node.type == 'FILLET_CURVE':
        settings.append([settingType.PARAM, 'mode', node.mode])

    elif node.type == 'RESAMPLE_CURVE':
        settings.append([settingType.PARAM, 'mode', node.mode])

    elif node.type == 'TRIM_CURVE':
        settings.append([settingType.PARAM, 'mode', node.mode])

    # CURVE / PRIMITIVES

    elif node.type == 'CURVE_PRIMITIVE_ARC':
        settings.append([settingType.PARAM, 'mode', node.mode])

    elif node.type == 'CURVE_PRIMITIVE_BEZIER_SEGMENT':
        settings.append([settingType.PARAM, 'mode', node.mode])

    elif node.type == 'CURVE_PRIMITIVE_CIRCLE':
        settings.append([settingType.PARAM, 'mode', node.mode])

    elif node.type == 'CURVE_PRIMITIVE_LINE':
        settings.append([settingType.PARAM, 'mode', node.mode])

    elif node.type == 'CURVE_PRIMITIVE_QUADRILATERAL':
        settings.append([settingType.PARAM, 'mode', node.mode])

    # CURVE / TOPOLOGY

    # UTILITIES / COLOR

    # UTILITIES / TEXT

    elif node.type == 'STRING_TO_CURVES':
        settings.append([settingType.PARAM, 'overflow', node.overflow])
        settings.append([settingType.PARAM, 'align_x', node.align_x])
        settings.append([settingType.PARAM, 'align_y', node.align_y])
        settings.append([settingType.PARAM, 'pivot_mode', node.pivot_mode])
        settings.append([settingType.SELECT_FONT, node.font.name])


    # UTILITIES / VECTOR

    elif node.type == 'CURVE_VEC':

        curve_0 = []
        curve_1 = []
        curve_2 = []

        for point in node.mapping.curves[0].points:
            curve_0.append([point.location[0], point.location[1], point.handle_type])

        for point in node.mapping.curves[1].points:
            curve_1.append([point.location[0], point.location[1], point.handle_type])

        for point in node.mapping.curves[2].points:
            curve_2.append([point.location[0], point.location[1], point.handle_type])


        settings.append([settingType.CURVE, 0, curve_0])
        settings.append([settingType.CURVE, 1, curve_1])
        settings.append([settingType.CURVE, 2, curve_2])

    elif node.type == 'VECT_MATH':
        settings.append([settingType.PARAM, 'operation', node.operation])

    elif node.type == 'VECTOR_ROTATE':
        settings.append([settingType.PARAM, 'rotation_type', node.rotation_type])
        settings.append([settingType.PARAM, 'invert', node.invert])

    elif node.type == 'MIX':
        settings.append([settingType.PARAM, 'data_type', node.data_type])
        settings.append([settingType.PARAM, 'clamp_factor', node.clamp_factor])
        settings.append([settingType.PARAM, 'clamp_result', node.clamp_result])
        settings.append([settingType.PARAM, 'factor_mode', node.factor_mode])
        settings.append([settingType.PARAM, 'blend_type', node.blend_type])

    # UTILITIES / FIELD

    elif node.type == 'ACCUMULATE_FIELD':
        settings.append([settingType.PARAM, 'data_type', node.data_type])
        settings.append([settingType.PARAM, 'domain', node.domain])

    elif node.type == 'FIELD_AT_INDEX':
        settings.append([settingType.PARAM, 'data_type', node.data_type])
        settings.append([settingType.PARAM, 'domain', node.domain])

    elif node.type == 'FIELD_ON_DOMAIN':
        settings.append([settingType.PARAM, 'data_type', node.data_type])
        settings.append([settingType.PARAM, 'domain', node.domain])

    # UTILITIES / MATH

    elif node.type == 'BOOLEAN_MATH':
        settings.append([settingType.PARAM, 'operation', node.operation])

    elif node.type == 'CLAMP':
        settings.append([settingType.PARAM, 'clamp_type', node.clamp_type])
    
    elif node.type == 'COMPARE':
        settings.append([settingType.PARAM, 'data_type', node.data_type])
        settings.append([settingType.PARAM, 'operation', node.operation])

    elif node.type == 'CURVE_FLOAT':
        curve_0 = []

        for point in node.mapping.curves[0].points:
            curve_0.append([point.location[0], point.location[1], point.handle_type])

        settings.append([settingType.CURVE, 0, curve_0])   

    elif node.type == 'FLOAT_TO_INT':
        settings.append([settingType.PARAM, 'rounding_mode', node.rounding_mode])

    elif node.type == 'ACCUMULATE_FIELD':
        settings.append([settingType.PARAM, 'data_type', node.data_type])
        settings.append([settingType.PARAM, 'interpolation_type', node.interpolation_type])
        settings.append([settingType.PARAM, 'clamp', node.clamp])

    elif node.type == 'MATH':
        settings.append([settingType.PARAM, 'operation', node.operation])
        settings.append([settingType.PARAM, 'use_clamp', node.use_clamp])


    # UTILITIES / ROTATION

    elif (node.type == 'ALIGN_EULER_TO_VECTOR'):
        settings.append([settingType.PARAM, 'axis', node.axis])
        settings.append([settingType.PARAM, 'pivot_axis', node.pivot_axis])

    elif (node.type == 'EULER'):
        settings.append([settingType.PARAM, 'space', node.space])
        settings.append([settingType.PARAM, 'type', node.type])

    elif (node.type == 'RANDOM_VALUE'):
        settings.append([settingType.PARAM, 'data_type', node.data_type])

    elif (node.type == 'SWITCH'):
        settings.append([settingType.PARAM, 'input_type', node.input_type])

#######
    
    elif node.type == 'ATTRIBUTE_COLOR_RAMP':

        settings.append([7, 'color_mode', node.color_ramp.color_mode])
        settings.append([7, 'interpolation', node.color_ramp.interpolation])
        settings.append([7, 'hue_interpolation', node.color_ramp.hue_interpolation])

        ramp_data = node.color_ramp.elements.values()
        color_ramp_data = []

        for data in ramp_data:
            color_ramp_data.append([data.position,[data.color[0], data.color[1], data.color[2], data.color[3]]])

        settings.append([8, 'color_ramp', color_ramp_data])

    elif node.type == 'ATTRIBUTE_COMBINE_XYZ':

        settings.append([settingType.PARAM, 'input_type_x', node.input_type_x])
        settings.append([settingType.PARAM, 'input_type_y', node.input_type_y])
        settings.append([settingType.PARAM, 'input_type_z', node.input_type_z])

    elif node.type == 'ATTRIBUTE_COMPARE':

        settings.append([settingType.PARAM, 'operation', node.operation])
        settings.append([settingType.PARAM, 'input_type_a', node.input_type_a])
        settings.append([settingType.PARAM, 'input_type_b', node.input_type_b])

    elif node.type == 'ATTRIBUTE_FILL':

        settings.append([settingType.PARAM, 'data_type', node.data_type])

    elif node.type == 'ATTRIBUTE_MATH':

        settings.append([settingType.PARAM, 'operation', node.operation])
        settings.append([settingType.PARAM, 'input_type_a', node.input_type_a])
        settings.append([settingType.PARAM, 'input_type_b', node.input_type_b])

    elif node.type == 'ATTRIBUTE_MIX':

        settings.append([settingType.PARAM, 'blend_type', node.blend_type])
        settings.append([settingType.PARAM, 'input_type_factor', node.input_type_factor])
        settings.append([settingType.PARAM, 'input_type_a', node.input_type_a])
        settings.append([settingType.PARAM, 'input_type_b', node.input_type_b])

    elif node.type == 'ATTRIBUTE_PROXIMITY':

        settings.append([settingType.PARAM, 'target_geometry_element', node.target_geometry_element])

    elif node.type == 'ATTRIBUTE_RANDOMIZE':

        settings.append([settingType.PARAM, 'operation', node.operation])
        settings.append([settingType.PARAM, 'data_type', node.data_type])

    elif node.type == 'ATTRIBUTE_SAMPLE_TEXTURE':

        if (node.texture != None):
            settings.append([15, node.texture.name])

    elif node.type == 'ATTRIBUTE_SEPARATE_XYZ':

        settings.append([settingType.PARAM, 'input_type', node.input_type])

    elif node.type == 'ATTRIBUTE_VECTOR_MATH':

        settings.append([settingType.PARAM, 'operation', node.operation])
        settings.append([settingType.PARAM, 'input_type_a', node.input_type_a])
        settings.append([settingType.PARAM, 'input_type_b', node.input_type_b])
    



    # COLOR

    elif node.type == 'VALTORGB':

        settings.append([7, 'color_mode', node.color_ramp.color_mode])
        settings.append([7, 'interpolation', node.color_ramp.interpolation])
        settings.append([7, 'hue_interpolation', node.color_ramp.hue_interpolation])

        ramp_data = node.color_ramp.elements.values()
        color_ramp_data = []

        for data in ramp_data:
            color_ramp_data.append([data.position,[data.color[0], data.color[1], data.color[2], data.color[3]]])

        settings.append([8, 'color_ramp', color_ramp_data])



    # GEOMETRY


    # INPUT

    elif node.type == 'COLLECTION_INFO':

        settings.append([settingType.PARAM, 'transform_space', node.transform_space])

    elif node.type == 'OBJECT_INFO':

        settings.append([settingType.PARAM, 'transform_space', node.transform_space])

    elif node.type == 'INPUT_VECTOR':

            settings.append([settingType.PARAM, 'vector',
            [node.vector[0],
            node.vector[1],
            node.vector[2]]])

    # MESH

    elif node.type == 'BOOLEAN':

        settings.append([settingType.PARAM, 'operation', node.operation])

    elif node.type == 'TRIANGULATE':

        settings.append([settingType.PARAM, 'quad_method', node.quad_method])
        settings.append([settingType.PARAM, 'ngon_method', node.ngon_method])



    # POINT

    elif node.type == 'ALIGN_ROTATION_TO_VECTOR':

        settings.append([settingType.PARAM, 'pivot_axis', node.pivot_axis])
        settings.append([settingType.PARAM, 'input_type_factor', node.input_type_factor])
        settings.append([settingType.PARAM, 'input_type_vector', node.input_type_vector])
        settings.append([settingType.PARAM, 'axis', node.axis])

    elif node.type == 'POINT_DISTRIBUTE':

        settings.append([settingType.PARAM, 'distribute_method', node.distribute_method])

    elif node.type == 'POINT_INSTANCE':

        settings.append([settingType.PARAM, 'instance_type', node.instance_type])
        settings.append([settingType.PARAM, 'use_whole_collection', node.use_whole_collection])



    elif node.type == 'POINT_SCALE':

        settings.append([settingType.PARAM, 'input_type', node.input_type])

    elif node.type == 'POINT_TRANSLATE':

        settings.append([settingType.PARAM, 'input_type', node.input_type])

    

    # VOLUME

    elif node.type == 'POINTS_TO_VOLUME':

        settings.append([settingType.PARAM, 'resolution_mode', node.resolution_mode])

    elif node.type == 'VOLUME_TO_MESH':

        settings.append([settingType.PARAM, 'resolution_mode', node.resolution_mode])

    # UTILIES

    elif node.type == 'FLOAT_COMPARE':

        settings.append([settingType.PARAM, 'operation', node.operation])

    elif node.type == 'MAP_RANGE':

        settings.append([settingType.PARAM, 'interpolation_type', node.interpolation_type]) 
        settings.append([settingType.PARAM, 'clamp', node.clamp])

    elif node.type == 'BOOLEAN_MATH':

        settings.append([settingType.PARAM, 'operation', node.operation])

    # VECTOR

    return settings

