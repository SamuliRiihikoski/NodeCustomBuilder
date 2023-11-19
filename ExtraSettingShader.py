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
    tulos = int(eval(f"{numero[0]}{numero[1]}{numero[2]}"))
    return tulos

def writeGroupExtraSettings(node):

    settings = []

    if(len(node.inputs) > 0):

        for index, input in enumerate(node.inputs):
            if input.type == 'INPUT':
                settings.append([11, index, node.inputs[index].default_value])

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

    return settings


def node_specific_attributes(node, settings):

    if node.type == 'AMBIENT_OCCLUSION':

        settings.append([settingType.PARAM, 'samples', node.samples])
        settings.append([settingType.PARAM, 'inside', node.inside])
        settings.append([settingType.PARAM, 'only_local', node.only_local])

    elif node.type == 'ATTRIBUTE':

        settings.append([settingType.PARAM, 'attribute_name', node.attribute_name])

    elif node.type == 'BEVEL':

        settings.append([settingType.PARAM, 'samples', node.samples])

    elif node.type == 'TANGENT':

        settings.append([settingType.PARAM, 'direction_type', node.direction_type])
        settings.append([settingType.PARAM, 'axis', node.axis])

    elif node.type == 'TEX_COORD':

        #settings.append([0, 'object', node.object.name])  TODO
        settings.append([settingType.PARAM, 'from_instancer', node.from_instancer])

    elif node.type == 'UVMAP':

        settings.append([settingType.PARAM, 'uv_map', node.uv_map])
        settings.append([settingType.PARAM, 'from_instancer', node.from_instancer])

    elif node.type == 'WIREFRAME':

        settings.append([settingType.PARAM, 'use_pixel_size', node.use_pizel_size])



    # OUTPUT

    elif node.type == 'OUTPUT_LIGHT':

        settings.append([settingType.PARAM, 'target', node.target])

    elif node.type == 'OUTPUT_MATERIAL':

        settings.append([settingType.PARAM, 'target', node.target])



    # SHADER

    elif node.type == 'BSDF_ANISOTROPIC':

        settings.append([settingType.PARAM, 'distribution', node.distribution])

    elif node.type == 'BSDF_GLASS':

        settings.append([settingType.PARAM, 'distribution', node.distribution])

    elif node.type == 'BSDF_GLOSSY':

        settings.append([settingType.PARAM, 'distribution', node.distribution])

    elif node.type == 'BSDF_HAIR':

        settings.append([settingType.PARAM, 'component', node.component])

    elif node.type == 'BSDF_HAIR':

        settings.append([settingType.PARAM, 'component', node.component])

    elif node.type == 'BSDF_PRINCIPLED':

        settings.append([settingType.PARAM, 'distribution', node.distribution])
        settings.append([settingType.PARAM, 'subsurface_method', node.subsurface_method])

    elif node.type == 'BSDF_HAIR_PRINCINPLED':

        settings.append([settingType.PARAM, 'distribution', node.distribution])

    elif node.type == 'BSDF_REFRACTION':

        settings.append([settingType.PARAM, 'distribution', node.distribution])

    elif node.type == 'SUBSURFACE_SCATTERING':

        settings.append([settingType.PARAM, 'falloff', node.falloff])

    elif node.type == 'BSDF_TOON':

        settings.append([settingType.PARAM, 'component', node.component])



    # TEXTURE

    elif node.type == 'TEX_BRICK':

        settings.append([settingType.PARAM, 'offset', node.offset])
        settings.append([settingType.PARAM, 'offset_frequency', node.offset_frequency])
        settings.append([settingType.PARAM, 'squash', node.squash])
        settings.append([settingType.PARAM, 'squash_frequency', node.squash_frequency])

    elif node.type == 'TEX_ENVIRONMENT':

        if(node.image == None):
            filepath = ''
        else:
            filepath = node.image.filepath
            settings.append([5, 'source', node.image.source])
            settings.append([14, 'image', node.image.name])

        settings.append([4, 'filepath', filepath])
        if(node.image != None):
            settings.append([12, 'name', node.image.colorspace_settings.name])
        settings.append([settingType.PARAM, 'interpolation', node.interpolation])
        settings.append([settingType.PARAM, 'projection', node.projection])


    elif node.type == 'TEX_GRADIENT':

        settings.append([settingType.PARAM, 'gradient_type', node.gradient_type])

    elif node.type == 'TEX_IES':

        settings.append([settingType.PARAM, 'mode', node.mode])
        settings.append([settingType.PARAM, 'ies', node.ies])
        settings.append([settingType.PARAM, 'filepath', node.filepath])

    elif node.type == 'TEX_IMAGE':

        if(node.image == None):
            filepath = ''
        else:
            filepath = node.image.filepath
            settings.append([5, 'source', node.image.source])
            settings.append([14, 'image', node.image.name])

        settings.append([4, 'filepath', filepath])
        if(node.image != None):
            settings.append([12, 'name', node.image.colorspace_settings.name])
        settings.append([settingType.PARAM, 'interpolation', node.interpolation])
        settings.append([settingType.PARAM, 'projection', node.projection])
        settings.append([settingType.PARAM, 'extension', node.extension])


        #TODO
        pass

    elif node.type == 'TEX_MAGIC':

        settings.append([settingType.PARAM, 'turbulence_depth', node.turbulence_depth])

    elif node.type == 'TEX_MUSGRAVE':

        settings.append([settingType.PARAM, 'musgrave_type', node.musgrave_type])

    elif node.type == 'TEX_POINTDENSITY':

        settings.append([settingType.PARAM, 'point_source', node.point_source])
        #settings.append([0, 'object', node.object.name])  TODO
        settings.append([settingType.PARAM, 'space', node.space])
        settings.append([settingType.PARAM, 'radius', node.radius])
        settings.append([settingType.PARAM, 'interpolation', node.interpolation])
        settings.append([settingType.PARAM, 'resolution', node.resolution])
        settings.append([settingType.PARAM, 'particle_color_source', node.particle_color_source])

    elif node.type == 'TEX_SKY':

        settings.append([settingType.PARAM, 'sky_type', node.sky_type])
        settings.append([settingType.PARAM, 'sun_direction', node.sun_direction])
        settings.append([settingType.PARAM, 'grounf_albedo', node.ground_albedo])
        settings.append([settingType.PARAM, 'turbidity', node.turbidity])

    elif node.type == 'TEX_VORONOI':

        version = checkVersion()
        if version >= 281:


            settings.append([settingType.PARAM, 'distance', node.distance])
            settings.append([settingType.PARAM, 'feature', node.feature])
            settings.append([settingType.PARAM, 'voronoi_dimensions', node.voronoi_dimensions])

        else:

            settings.append([settingType.PARAM, 'coloring', node.coloring])
            settings.append([settingType.PARAM, 'distance', node.distance])
            settings.append([settingType.PARAM, 'feature', node.feature])


    elif node.type == 'TEX_WAVE':

        settings.append([settingType.PARAM, 'wave_type', node.wave_type])
        settings.append([settingType.PARAM, 'wave_profile', node.wave_profile])


    # COLOR

    elif node.type == 'MIX_RGB':

        settings.append([settingType.PARAM, 'blend_type', node.blend_type])
        settings.append([settingType.PARAM, 'use_clamp', node.use_clamp])

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


        settings.append([9, 0, curve_0])
        settings.append([9, 1, curve_1])
        settings.append([9, 2, curve_2])

        settings.append([1, 'Fac', node.inputs['Fac'].default_value])

    elif node.type == 'CURVE_RGB':

        curve_0 = []
        curve_1 = []
        curve_2 = []
        curve_3 = []

        for point in node.mapping.curves[0].points:
            curve_0.append([point.location[0], point.location[1], point.handle_type])

        for point in node.mapping.curves[1].points:
            curve_1.append([point.location[0], point.location[1], point.handle_type])

        for point in node.mapping.curves[2].points:
            curve_2.append([point.location[0], point.location[1], point.handle_type])

        for point in node.mapping.curves[3].points:
            curve_3.append([point.location[0], point.location[1], point.handle_type])

        settings.append([9, 0, curve_0])
        settings.append([9, 1, curve_1])
        settings.append([9, 2, curve_2])
        settings.append([9, 3, curve_3])


    # VECTOR

    elif node.type == 'BUMP':

        settings.append([settingType.PARAM, 'invert', node.invert])

    elif node.type == 'DISPLACEMENT':

        settings.append([settingType.PARAM, 'space', node.space])

    elif node.type == 'MAPPING':
        version = checkVersion()
        if version >= 281:
            settings.append([settingType.PARAM, 'vector_type', node.vector_type])

        else:
            settings.append([settingType.PARAM, 'vector_type', node.vector_type])

            settings.append([settingType.PARAM, 'translation', [node.translation[0], node.translation[1], node.translation[2]]])
            settings.append([settingType.PARAM, 'rotation', [node.rotation[0], node.rotation[1], node.rotation[2]]])
            settings.append([settingType.PARAM, 'scale', [node.scale[0], node.scale[1], node.scale[2]]])

            settings.append([settingType.PARAM, 'use_min', node.use_min])
            settings.append([settingType.PARAM, 'use_max', node.use_max])

            settings.append([settingType.PARAM, 'min', [node.min[0], node.min[1], node.min[2]]])
            settings.append([settingType.PARAM, 'max', [node.max[0], node.max[1], node.max[2]]])


    elif node.type == 'NORMAL_MAP':

        settings.append([settingType.PARAM, 'space', node.space])
        settings.append([settingType.PARAM, 'uv_map', node.uv_map])

    elif node.type == 'CURVE_VEC':

        settings.append([1, 'Fac', node.inputs['Fac'].default_value])

        #TODO

    elif node.type == 'VECTOR_DISPLACEMENT':

        settings.append([settingType.PARAM, 'space', node.space])

    elif node.type == 'VECT_TRANSFORM':

        settings.append([settingType.PARAM, 'vector_type', node.vector_type])
        settings.append([settingType.PARAM, 'convert_from', node.convert_from])
        settings.append([settingType.PARAM, 'convert_to', node.convert_to])


    # CONVERTER

    elif node.type == 'VALTORGB':

        settings.append([7, 'color_mode', node.color_ramp.color_mode])
        settings.append([7, 'interpolation', node.color_ramp.interpolation])
        settings.append([7, 'hue_interpolation', node.color_ramp.hue_interpolation])

        ramp_data = node.color_ramp.elements.values()
        color_ramp_data = []

        for data in ramp_data:
            color_ramp_data.append([data.position,[data.color[0], data.color[1], data.color[2], data.color[3]]])

        settings.append([8, 'color_ramp', color_ramp_data])

    elif node.type == 'MAP_RANGE':

        settings.append([settingType.PARAM, 'clamp', node.clamp])

    elif node.type == 'MATH':

        settings.append([settingType.PARAM, 'operation', node.operation])
        settings.append([settingType.PARAM, 'use_clamp', node.use_clamp])

        settings.append([10, 0, node.inputs[0].default_value])
        settings.append([10, 1, node.inputs[1].default_value])

        # TODO need some work because there is no value1 and value2, only value

    elif node.type == 'VECT_MATH':

        settings.append([settingType.PARAM, 'operation', node.operation])

        settings.append([10, 0,
                         [node.inputs[0].default_value[0],
                          node.inputs[0].default_value[1],
                          node.inputs[0].default_value[2]]])

        settings.append([10, 1,
                         [node.inputs[1].default_value[0],
                          node.inputs[1].default_value[1],
                          node.inputs[1].default_value[2]]])

    elif node.type == 'TEX_WHITE_NOISE':

        settings.append([settingType.PARAM, 'noise_dimensions', node.noise_dimensions])

    elif node.type == 'WAVELENGTH':

        settings.append([1, 'Wavelength', node.inputs['Wavelength'].default_value])

    elif node.type == 'SCRIPT':

        settings.append([settingType.PARAM, 'mode', node.mode])
        if (node.mode == 'EXTERNAL'):
            settings.append([settingType.PARAM, 'filepath', node.filepath])
        elif (node.mode == 'INTERNAL'):

            if node.script != '':
                for line in node.script.lines:
                    script.append(line.body)

            settings.append(['script',node.script.name, script])

    return settings

def readExtraSttings(extra_settings, node):
    for setting in extra_settings:

        if setting[0] == 0:
            setattr(node, setting[1], setting[2])

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

        elif setting[0] == 'script':
            textFile = bpy.data.texts.new(setting[1])

            for line in setting[2]:
                textFile.write(line + '\n')

            node.script = textFile
