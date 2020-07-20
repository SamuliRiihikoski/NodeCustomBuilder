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
    for Ninput in node.inputs:
        if Ninput.type == 'VALUE':
            settings.append([1, Ninput.name, Ninput.default_value, Ninput.hide])
        elif Ninput.type == 'RGBA':
            settings.append([1, Ninput.name,
                        [Ninput.default_value[0],
                        Ninput.default_value[1],
                        Ninput.default_value[2],
                        Ninput.default_value[3]], Ninput.hide])
        elif Ninput.type == 'VECTOR':
            settings.append([1, Ninput.name,
                    [Ninput.default_value[0],
                    Ninput.default_value[1],
                    Ninput.default_value[2]], Ninput.hide])
        elif Ninput.type == 'SHADER':
            settings.append([5, Ninput.name, Ninput.type, Ninput.hide])


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

    if node.type == 'AMBIENT_OCCLUSION':

        settings.append([0, 'samples', node.samples])
        settings.append([0, 'inside', node.inside])
        settings.append([0, 'only_local', node.only_local])

    elif node.type == 'ATTRIBUTE':

        settings.append([0, 'attribute_name', node.attribute_name])

    elif node.type == 'BEVEL':

        settings.append([0, 'samples', node.samples])

    elif node.type == 'RGB':

        settings.append([2, 'Color',
                         [node.outputs['Color'].default_value[0],
                          node.outputs['Color'].default_value[1],
                          node.outputs['Color'].default_value[2],
                          node.outputs['Color'].default_value[3]]])

    elif node.type == 'TANGENT':

        settings.append([0, 'direction_type', node.direction_type])
        settings.append([0, 'axis', node.axis])

    elif node.type == 'TEX_COORD':

        #settings.append([0, 'object', node.object.name])  TODO
        settings.append([0, 'from_instancer', node.from_instancer])

    elif node.type == 'UVMAP':

        settings.append([0, 'uv_map', node.uv_map])
        settings.append([0, 'from_instancer', node.from_instancer])

    elif node.type == 'VALUE':

        settings.append([2, 'Value', node.outputs['Value'].default_value])

    elif node.type == 'WIREFRAME':

        settings.append([0, 'use_pixel_size', node.use_pizel_size])



    # OUTPUT

    elif node.type == 'OUTPUT_LIGHT':

        settings.append([0, 'target', node.target])

    elif node.type == 'OUTPUT_MATERIAL':

        settings.append([0, 'target', node.target])



    # SHADER

    elif node.type == 'BSDF_ANISOTROPIC':

        settings.append([0, 'distribution', node.distribution])

    elif node.type == 'BSDF_GLASS':

        settings.append([0, 'distribution', node.distribution])

    elif node.type == 'BSDF_GLOSSY':

        settings.append([0, 'distribution', node.distribution])

    elif node.type == 'BSDF_HAIR':

        settings.append([0, 'component', node.component])

    elif node.type == 'BSDF_HAIR':

        settings.append([0, 'component', node.component])

    elif node.type == 'BSDF_PRINCIPLED':

        settings.append([0, 'distribution', node.distribution])
        settings.append([0, 'subsurface_method', node.subsurface_method])

    elif node.type == 'BSDF_HAIR_PRINCINPLED':

        settings.append([0, 'distribution', node.distribution])

    elif node.type == 'BSDF_REFRACTION':

        settings.append([0, 'distribution', node.distribution])

    elif node.type == 'SUBSURFACE_SCATTERING':

        settings.append([0, 'falloff', node.falloff])

    elif node.type == 'BSDF_TOON':

        settings.append([0, 'component', node.component])



    # TEXTURE

    elif node.type == 'TEX_BRICK':

        settings.append([0, 'offset', node.offset])
        settings.append([0, 'offset_frequency', node.offset_frequency])
        settings.append([0, 'squash', node.squash])
        settings.append([0, 'squash_frequency', node.squash_frequency])

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
        settings.append([0, 'interpolation', node.interpolation])
        settings.append([0, 'projection', node.projection])


    elif node.type == 'TEX_GRADIENT':

        settings.append([0, 'gradient_type', node.gradient_type])

    elif node.type == 'TEX_IES':

        settings.append([0, 'mode', node.mode])
        settings.append([0, 'ies', node.ies])
        settings.append([0, 'filepath', node.filepath])

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
        settings.append([0, 'interpolation', node.interpolation])
        settings.append([0, 'projection', node.projection])
        settings.append([0, 'extension', node.extension])


        #TODO
        pass

    elif node.type == 'TEX_MAGIC':

        settings.append([0, 'turbulence_depth', node.turbulence_depth])

    elif node.type == 'TEX_MUSGRAVE':

        settings.append([0, 'musgrave_type', node.musgrave_type])

    elif node.type == 'TEX_POINTDENSITY':

        settings.append([0, 'point_source', node.point_source])
        #settings.append([0, 'object', node.object.name])  TODO
        settings.append([0, 'space', node.space])
        settings.append([0, 'radius', node.radius])
        settings.append([0, 'interpolation', node.interpolation])
        settings.append([0, 'resolution', node.resolution])
        settings.append([0, 'particle_color_source', node.particle_color_source])

    elif node.type == 'TEX_SKY':

        settings.append([0, 'sky_type', node.sky_type])
        settings.append([0, 'sun_direction', node.sun_direction])
        settings.append([0, 'grounf_albedo', node.ground_albedo])
        settings.append([0, 'turbidity', node.turbidity])

    elif node.type == 'TEX_VORONOI':

        version = checkVersion()
        if version >= 281:


            settings.append([0, 'distance', node.distance])
            settings.append([0, 'feature', node.feature])
            settings.append([0, 'voronoi_dimensions', node.voronoi_dimensions])

        else:

            settings.append([0, 'coloring', node.coloring])
            settings.append([0, 'distance', node.distance])
            settings.append([0, 'feature', node.feature])


    elif node.type == 'TEX_WAVE':

        settings.append([0, 'wave_type', node.wave_type])
        settings.append([0, 'wave_profile', node.wave_profile])


    # COLOR

    elif node.type == 'MIX_RGB':

        settings.append([0, 'blend_type', node.blend_type])
        settings.append([0, 'use_clamp', node.use_clamp])

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

        settings.append([0, 'invert', node.invert])

    elif node.type == 'DISPLACEMENT':

        settings.append([0, 'space', node.space])

    elif node.type == 'MAPPING':
        version = checkVersion()
        if version >= 281:
            settings.append([0, 'vector_type', node.vector_type])

        else:
            settings.append([0, 'vector_type', node.vector_type])

            settings.append([0, 'translation', [node.translation[0], node.translation[1], node.translation[2]]])
            settings.append([0, 'rotation', [node.rotation[0], node.rotation[1], node.rotation[2]]])
            settings.append([0, 'scale', [node.scale[0], node.scale[1], node.scale[2]]])

            settings.append([0, 'use_min', node.use_min])
            settings.append([0, 'use_max', node.use_max])

            settings.append([0, 'min', [node.min[0], node.min[1], node.min[2]]])
            settings.append([0, 'max', [node.max[0], node.max[1], node.max[2]]])

    elif node.type == 'NORMAL':

        settings.append([2, 'Normal', [node.outputs['Normal'].default_value[0],
                                       node.outputs['Normal'].default_value[1],
                                       node.outputs['Normal'].default_value[2]]])

    elif node.type == 'NORMAL_MAP':

        settings.append([0, 'space', node.space])
        settings.append([0, 'uv_map', node.uv_map])

    elif node.type == 'CURVE_VEC':

        settings.append([1, 'Fac', node.inputs['Fac'].default_value])

        #TODO

    elif node.type == 'VECTOR_DISPLACEMENT':

        settings.append([0, 'space', node.space])

    elif node.type == 'VECT_TRANSFORM':

        settings.append([0, 'vector_type', node.vector_type])
        settings.append([0, 'convert_from', node.convert_from])
        settings.append([0, 'convert_to', node.convert_to])


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

        settings.append([0, 'clamp', node.clamp])

    elif node.type == 'MATH':

        settings.append([0, 'operation', node.operation])
        settings.append([0, 'use_clamp', node.use_clamp])

        settings.append([10, 0, node.inputs[0].default_value])
        settings.append([10, 1, node.inputs[1].default_value])

        # TODO need some work because there is no value1 and value2, only value

    elif node.type == 'VECT_MATH':

        settings.append([0, 'operation', node.operation])

        settings.append([10, 0,
                         [node.inputs[0].default_value[0],
                          node.inputs[0].default_value[1],
                          node.inputs[0].default_value[2]]])

        settings.append([10, 1,
                         [node.inputs[1].default_value[0],
                          node.inputs[1].default_value[1],
                          node.inputs[1].default_value[2]]])

    elif node.type == 'TEX_WHITE_NOISE':

        settings.append([0, 'noise_dimensions', node.noise_dimensions])

    elif node.type == 'WAVELENGTH':

        settings.append([1, 'Wavelength', node.inputs['Wavelength'].default_value])

    elif node.type == 'SCRIPT':

        settings.append([0, 'mode', node.mode])
        if (node.mode == 'EXTERNAL'):
            settings.append([0, 'filepath', node.filepath])
        elif (node.mode == 'INTERNAL'):

            if node.script != '':
                for line in node.script.lines:
                    script.append(line.body)

            settings.append(['script',node.script.name, script])

    else:
        settings.append([-1,-1,-1]) #  -1 Means that it dosen't have any extra settings

    return settings

def readExtraSettings(extra_settings, node):
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
