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
from . import NodeGroupComputer

def checkVersion():
    numero = bpy.app.version
    tulos = int(eval(f"{numero[0]}{numero[1]}"))
    return tulos

def writeGroupExtraSettings(node):

    settings = []

    if(len(node.inputs) > 0):

        for index, input in enumerate(node.inputs):
            print('input', input)
            if input.type == 'VALUE':
                settings.append([11, index, node.inputs[index].default_value, node.node_tree.inputs[index].min_value, node.node_tree.inputs[index].max_value])

            elif input.type == 'RGBA':
                settings.append([10, index,
                                 [node.inputs[index].default_value[0],
                                  node.inputs[index].default_value[1],
                                  node.inputs[index].default_value[2],
                                  node.inputs[index].default_value[3]]])

            elif input.type == 'VECTOR':
                settings.append([10, index,
                                 [node.inputs[index].default_value[0],
                                  node.inputs[index].default_value[1],
                                  node.inputs[index].default_value[2]]])

    else:

        settings.append([-1,-1,-1])

    return settings

def writeExtraSettings(dict, node, type, nimi, main_mode):

    settings = []
    hidden_outputs = []
    script = []
    color_ramp_data = []

    # OUTPUTS
    for output in node.outputs:
        settings.append([-2, output.type, output.name, output.hide])    

    #  SETTINGS
    settings = node_attributes(node, settings)

    # INPUTS
    socket_number = 0
    for Ninput in node.inputs:

        if (Ninput.type == 'VALUE' or Ninput.type == 'BOOLEAN' or Ninput.type == 'STRING' or Ninput.type == 'INT'):
            settings.append([1, socket_number, Ninput.default_value, Ninput.hide])

        elif Ninput.type == 'RGBA':
            settings.append([1, Ninput.name,
                        [Ninput.default_value[0],
                        Ninput.default_value[1],
                        Ninput.default_value[2],
                        Ninput.default_value[3]], Ninput.hide])

        elif Ninput.type == 'VECTOR':
            settings.append([1, socket_number,
                    [Ninput.default_value[0],
                    Ninput.default_value[1],
                    Ninput.default_value[2]], Ninput.hide])

        elif Ninput.type == 'SHADER':
            settings.append([5, Ninput.name, Ninput.type, Ninput.hide])

        elif Ninput.type == 'OBJECT' and Ninput.default_value != None:
            settings.append([3, socket_number, Ninput.default_value.name, Ninput.hide])

        elif Ninput.type == 'COLLECTION' and Ninput.default_value != None:
            settings.append([13, socket_number, Ninput.default_value.name, Ninput.hide])

        socket_number += 1


    if(len(node.outputs) > 0):
        for output in node.outputs:
            if output.hide == True:
                hidden_outputs.append([output.name])

    if main_mode == 'SUB_TREE':

        dict['node'].append({
            'node': node.bl_idname,
            'name': node.name,
            'label': node.label,
            'location': [node.location[0], node.location[1]],
            'hide': node.hide,
            'main_socket_type': type,
            'parent': nimi,
            'hidden_outputs': hidden_outputs,
            'height': node.height,
            'width': node.width,
            'extra_settings': settings
        })

    elif main_mode == 'MAIN_TREE':

        dict['nodes'].append({
            'node': node.bl_idname,
            'name': node.name,
            'label': node.label,
            'location': [node.location[0], node.location[1]],
            'hide': node.hide,
            'main_socket_type': "",
            'parent': nimi,
            'hidden_outputs': hidden_outputs,
            'height': node.height,
            'width': node.width,
            'extra_settings': settings
        })
    


    return dict

def node_attributes(node, settings):

    # ATTRIBUTE
    
    if node.type == 'ATTRIBUTE_COLOR_RAMP':

        settings.append([7, 'color_mode', node.color_ramp.color_mode])
        settings.append([7, 'interpolation', node.color_ramp.interpolation])
        settings.append([7, 'hue_interpolation', node.color_ramp.hue_interpolation])

        ramp_data = node.color_ramp.elements.values()
        color_ramp_data = []

        for data in ramp_data:
            color_ramp_data.append([data.position,[data.color[0], data.color[1], data.color[2], data.color[3]]])

        settings.append([8, 'color_ramp', color_ramp_data])

    elif node.type == 'ATTRIBUTE_COMBINE_XYZ':

        settings.append([0, 'input_type_x', node.input_type_x])
        settings.append([0, 'input_type_y', node.input_type_y])
        settings.append([0, 'input_type_z', node.input_type_z])

    elif node.type == 'ATTRIBUTE_COMPARE':

        settings.append([0, 'operation', node.operation])
        settings.append([0, 'input_type_a', node.input_type_a])
        settings.append([0, 'input_type_b', node.input_type_b])

    elif node.type == 'ATTRIBUTE_FILL':

        settings.append([0, 'data_type', node.data_type])

    elif node.type == 'ATTRIBUTE_MATH':

        settings.append([0, 'operation', node.operation])
        settings.append([0, 'input_type_a', node.input_type_a])
        settings.append([0, 'input_type_b', node.input_type_b])

    elif node.type == 'ATTRIBUTE_MIX':

        settings.append([0, 'blend_type', node.blend_type])
        settings.append([0, 'input_type_factor', node.input_type_factor])
        settings.append([0, 'input_type_a', node.input_type_a])
        settings.append([0, 'input_type_b', node.input_type_b])

    elif node.type == 'ATTRIBUTE_PROXIMITY':

        settings.append([0, 'target_geometry_element', node.target_geometry_element])

    elif node.type == 'ATTRIBUTE_RANDOMIZE':

        settings.append([0, 'operation', node.operation])
        settings.append([0, 'data_type', node.data_type])

    elif node.type == 'ATTRIBUTE_SAMPLE_TEXTURE':

        if (node.texture != None):
            settings.append([15, node.texture.name])

    elif node.type == 'ATTRIBUTE_SEPARATE_XYZ':

        settings.append([0, 'input_type', node.input_type])

    elif node.type == 'ATTRIBUTE_VECTOR_MATH':

        settings.append([0, 'operation', node.operation])
        settings.append([0, 'input_type_a', node.input_type_a])
        settings.append([0, 'input_type_b', node.input_type_b])
    



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

        settings.append([0, 'transform_space', node.transform_space])

    elif node.type == 'OBJECT_INFO':

        settings.append([0, 'transform_space', node.transform_space])

    elif node.type == 'INPUT_VECTOR':

            settings.append([0, 'vector',
            [node.vector[0],
            node.vector[1],
            node.vector[2]]])

    # MESH

    elif node.type == 'BOOLEAN':

        settings.append([0, 'operation', node.operation])

    elif node.type == 'TRIANGULATE':

        settings.append([0, 'quad_method', node.quad_method])
        settings.append([0, 'ngon_method', node.ngon_method])



    # POINT

    elif node.type == 'ALIGN_ROTATION_TO_VECTOR':

        settings.append([0, 'pivot_axis', node.pivot_axis])
        settings.append([0, 'input_type_factor', node.input_type_factor])
        settings.append([0, 'input_type_vector', node.input_type_vector])
        settings.append([0, 'axis', node.axis])

    elif node.type == 'POINT_DISTRIBUTE':

        settings.append([0, 'distribute_method', node.distribute_method])

    elif node.type == 'POINT_INSTANCE':

        settings.append([0, 'instance_type', node.instance_type])
        settings.append([0, 'use_whole_collection', node.use_whole_collection])

    elif (node.type == 'EULER' or node.type == 'AXIS_ANGLE'):

        settings.append([0, 'input_type_rotation', node.input_type_rotation])
        settings.append([0, 'input_type_axis', node.input_type_axis])
        settings.append([0, 'input_type_angle', node.input_type_angle])
        settings.append([0, 'space', node.space])
        settings.append([0, 'type', node.type])

    elif node.type == 'POINT_SCALE':

        settings.append([0, 'input_type', node.input_type])

    elif node.type == 'POINT_TRANSLATE':

        settings.append([0, 'input_type', node.input_type])

    

    # VOLUME

    elif node.type == 'POINTS_TO_VOLUME':

        settings.append([0, 'resolution_mode', node.resolution_mode])

    elif node.type == 'VOLUME_TO_MESH':

        settings.append([0, 'resolution_mode', node.resolution_mode])

    # UTILIES

    elif node.type == 'FLOAT_COMPARE':

        settings.append([0, 'operation', node.operation])

    elif node.type == 'MAP_RANGE':

        settings.append([0, 'interpolation_type', node.interpolation_type]) 
        settings.append([0, 'clamp', node.clamp])

    elif node.type == 'BOOLEAN_MATH':

        settings.append([0, 'operation', node.operation])
    
    else:
        settings.append([-1,-1,-1]) #  -1 Means that it dosen't have any extra settings

    # VECTOR

    return settings

def readExtraSettings(extra_settings, node):
    for setting in extra_settings:

        # DOWNLIST

        if setting[0] == 0: 
            setattr(node, setting[1], setting[2])

        # INPUT SOCKET: VALUE, BOOLEAN, STRING and INT

        elif setting[0] == 1:
            try:
                node.inputs[setting[1]].default_value = setting[2]
            except:
                pass

        elif setting[0] == 2:
            node.outputs[setting[1]].default_value = setting[2]

        # INPUT SOCKET: OBJECT
        
        elif setting[0] == 3:
            try:
                node.inputs[setting[1]].default_value = bpy.data.objects[setting[2]]
            except:
                pass
       
        # Image loading for image texture node

        elif setting[0] == 4:
            if(setting[2] != '' and node.image == None):

                use_this_path = ''
                for image in bpy.data.images:
                    if(image.filepath == setting[2]):
                        use_this_path = image
                        break
                if(use_this_path == ''):
                    if(os.path.isfile(setting[2])):
                        node.image = bpy.data.images.load(setting[2])
                else:
                    node.image = use_this_path

        # INPUT SOCKET: COLLECTION
        
        elif setting[0] == 13:
            try:
                node.inputs[setting[1]].default_value = bpy.data.collections[setting[2]]
            except:
                pass


        elif setting[0] == 14:
            if(setting[2] != ''):
                for image in bpy.data.images:
                    if image.name == setting[2]:
                        node.image = image
        # COLOR RAMP


        elif setting[0] == 7:
            setattr(node.color_ramp, setting[1], setting[2])

        elif setting[0] == 8:
            data = setting[2]
            if(len(data) > 2):
                while(len(node.color_ramp.elements) < len(data)):
                    node.color_ramp.elements.new(0)

            for index, element in enumerate(setting[2]):
                node.color_ramp.elements[index].position = element[0]
                node.color_ramp.elements[index].color = element[1]

        # CURVE NODE

        elif setting[0] == 9:
            data = setting[2]
            curve = node.mapping.curves[setting[1]]

            if (len(data) > 2):
                while (len(curve.points) < len(data)):
                    curve.points.new(0, 0)
            elif (len(data) < 2):
                while (len(curve.points) > len(data)):
                    curve.points.remove(curve.points[0])

            for index, loc in enumerate(setting[2]):
                curve.points[index].location = (loc[0], loc[1])
                curve.points[index].handle_type = loc[2]

        # Image1 ja Image2 kasittely taalla // 10

        elif setting[0] == 10:
            print(setting)
            node.inputs[setting[1]].default_value = setting[2]

        # Group Node

        elif setting[0] == 11:
            node.inputs[setting[1]].default_value = setting[2]
            node.node_tree.inputs[setting[1]].min_value = setting[3]
            node.node_tree.inputs[setting[1]].max_value = setting[4]

        elif setting[0] == 12:
            if node.image != None:
                node.image.colorspace_settings.name = setting[2]

        elif setting[0] == 'script':
            textFile = bpy.data.texts.new(setting[1])

            for line in setting[2]:
                textFile.write(line + '\n')

            node.script = textFile

        elif setting[0] == 15:
            try:
                node.texture = bpy.data.textures[setting[1]]
            except:
                pass
