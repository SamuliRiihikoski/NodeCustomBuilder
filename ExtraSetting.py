import bpy
from . import ExtraSettingShader
from . import ExtraSettingComp
from . import ExtraSettingGeo
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

socketInputType = {
    'VALUE': 'NodeSocketFloat',
    'INT': 'NodeSocketInt',
    'BOOLEAN': 'NodeSocketBool',
    'VECTOR': 'NodeSocketVector',
    'ROTATION': 'NodeSocketRotation',
    'STRING': 'NodeSocketString',
    'RGBA': 'NodeSocketColor',
    'OBJECT': 'NodeSocketObject',
    'IMAGE': 'NodeSocketImage',
    'GEOMETRY': 'NodeSocketGeometry',
    'COLLECTION': 'NodeSocketCollection',
    'TEXTURE': 'NodeSocketTexture',
    'MATERIAL': 'NodeSocketMaterial',

}


def writeExtraSettings(area, node):
    settings = []

    socket_number = 0
    for output in node.outputs:
        if hasattr(output, 'default_value'):
            array = numpy.array(output.default_value).tolist()
            settings.append([-2, output.type, output.name, output.hide, socket_number,  array]) 
        else:
            settings.append([-2, output.type, output.name, output.hide, socket_number])  
        socket_number += 1
    
    if(area == 'CompositorNodeTree'):
        settings = ExtraSettingComp.node_specific_attributes(node, settings)
    elif(area == 'GeometryNodeTree'):
        settings = ExtraSettingGeo.node_specific_attributes(node, settings)
    elif(area == 'ShaderNodeTree'):
        settings = ExtraSettingShader.node_specific_attributes(node, settings)

    socket_number = 0
    for Ninput in node.inputs:
        if Ninput.type == 'OBJECT':
            if 'default_value' in Ninput.keys():
                settings.append([settingType.OBJECT, socket_number, Ninput.type, Ninput.name, Ninput.default_value.name])
            else:
                settings.append([settingType.OBJECT, socket_number, Ninput.type, Ninput.name])
        elif hasattr(Ninput, 'default_value'):
            array = numpy.array(Ninput.default_value).tolist()
            settings.append([settingType.INPUT, socket_number, Ninput.type, Ninput.name, Ninput.hide, array])
        else:
            settings.append([settingType.INPUT, socket_number, Ninput.type, Ninput.name, Ninput.hide])


        socket_number += 1

    return settings


def readExtraSettings(extra_settings, node):
    for setting in extra_settings:

        if setting[0] == settingType.OUTPUT:
            if node.type == 'GROUP':
                node.node_tree.interface.new_socket(setting[2], socket_type=socketInputType[setting[1]], in_out="OUTPUT")
            
            try:
                if len(setting) == 6:
                    node.outputs[setting[4]].default_value = setting[5]

            
                node.outputs[setting[4]].hide = setting[3]
            except:
                pass

        elif setting[0] == settingType.PARAM:
            setattr(node, setting[1], setting[2])

        elif setting[0] == settingType.INPUT:
            if node.type == 'GROUP':
                node.node_tree.interface.new_socket(setting[3], socket_type=socketInputType[setting[2]], in_out="INPUT")
            else:
                try:
                    node.inputs[setting[1]].default_value = setting[5]
                except:
                    pass

            if setting[4] == True:
                node.inputs[setting[1]].hide = True

        # INPUT SOCKET: OBJECT
        
        elif setting[0] == settingType.OBJECT:
            try:
                node.inputs[setting[1]].default_value = bpy.data.objects[setting[4]]
            except:
                pass

        # Image loading for image texture node

        elif setting[0] == settingType.IMAGE:
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


        # COLOR RAMP

        elif setting[0] == settingType.COLOR_RAMP1:
            setattr(node.color_ramp, setting[1], setting[2])

        elif setting[0] == settingType.CoLOR_RAMP2:
            data = setting[2]
            if(len(data) > 2):
                while(len(node.color_ramp.elements) < len(data)):
                    node.color_ramp.elements.new(0)

            for index, element in enumerate(setting[2]):
                node.color_ramp.elements[index].position = element[0]
                node.color_ramp.elements[index].color = element[1]

        # CURVE NODE

        elif setting[0] == settingType.CURVE:
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
            node.inputs[setting[1]].default_value = setting[2]

        # Group Node

        # Blender 3.6 
        #elif setting[0] == 11:
        #    node.inputs[setting[1]].default_value = setting[2]
        #    node.node_tree.inputs[setting[1]].min_value = setting[3]
        #    node.node_tree.inputs[setting[1]].max_value = setting[4]

        #elif setting[0] == 11:
        #    node.inputs[setting[1]].default_value = setting[2]

        elif setting[0] == 12:
            if node.image != None:
                node.image.colorspace_settings.name = setting[2]

        # INPUT SOCKET: COLLECTION
        
        elif setting[0] == 13:
            try:
                node.inputs[setting[1]].default_value = bpy.data.collections[setting[2]]
            except:
                pass


        elif setting[0] == settingType.SELECT_IMAGE:
            if(setting[2] != ''):
                for image in bpy.data.images:
                    if image.name == setting[2]:
                        node.image = image

        elif setting[0] == settingType.SELECT_TEXTURE:
            try:
                node.texture = bpy.data.textures[setting[1]]
            except:
                pass

        elif setting[0] == settingType.SELECT_MATERIAL:
            try:
                node.material = bpy.data.materials[setting[1]]
            except:
                pass

        elif setting[0] == settingType.MULTI_OPTION:
            setattr(node, setting[1], set(setting[2]))

        elif setting[0] == settingType.SELECT_FONT:
            try:
                node.font = bpy.data.fonts[setting[1]]
            except:
                pass


        elif setting[0] == 'script':
            textFile = bpy.data.texts.new(setting[1])

            for line in setting[2]:
                textFile.write(line + '\n')

            node.script = textFile

'''
def readExtraSttings(extra_settings, node):
    for setting in extra_settings:

        # DOWNLIST

        if setting[0] == 0: 
            setattr(node, setting[1], setting[2])

        # INPUT SOCKET: INPUT, BOOLEAN, STRING and INT

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

'''