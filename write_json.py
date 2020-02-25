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
from . import NodeGroupComputer
from . import ExtraSetting
from . import ExtraSettingComp

def newname_to_node(nodes):
    for node in nodes:
        if(node.type == 'FRAME'):
            node.name = '__node__' + node.name

def oldname_to_node(nodes):
    for node in nodes:
        if(node.name.startswith('__node__')):
            node.name = node.name[8:]

def write(dict, nodes):


    dict['material'] = []
    dict['frames'] = []
    dict['nodes'] = []
    dict['links'] = []
    dict['keyframes'] = []
    group_nodes =[]
    frames = []
    temp_frames =[]
    all_nodes = [] # pitaa lukua kaikista nodeista. Jos loytyy link haaroista sama node kahteen kertaan niin ei kuitenkaan kirjoita sita

    newname_to_node(nodes)
    material = bpy.context.object.active_material


    ''' Keyframes '''
    '''
    for fcurve in material.node_tree.animation_data.action.fcurves:
        points_T = []
        if(len(fcurve.keyframe_points) >= 2):
            for points in fcurve.keyframe_points:
                print('aaa' + str(points.co[0]))
                points_T.append([points.co[0], points.co[1]])
            
            dict['keyframes'].append({
                'name': 'testi',
                'points': points_T
            })

    '''


    ''' Material Settings '''
    if (bpy.context.space_data.shader_type == 'OBJECT' and bpy.context.area.ui_type != 'CompositorNodeTree'):
        dict['material'].append({
            'use_backface_culling': material.use_backface_culling,
            'blend_method': material.blend_method,
            'shadow_method': material.shadow_method,
            'alpha_threshold': material.alpha_threshold,
            'use_screen_refraction': material.use_screen_refraction,
            'refraction_depth': material.refraction_depth,
            'use_sss_translucency': material.use_sss_translucency,
            'pass_index': material.pass_index
        })

    ''' Node Settings '''

    for node in nodes:
        print('node name:', node)
        if(node.type == 'FRAME' and node.select == True):
            if node.name not in frames:
                frames.append(node.name)
                for frame_node in nodes:
                    if(frame_node.type == 'FRAME'):
                        if(frame_node.parent == node):
                            frames.append(frame_node.name)

        if node not in all_nodes:
            frame_linked_and_selected = False
            frame_node = node.parent
            bank_frames = False
            while(frame_node != None):
                temp_frames.append(frame_node.name)
                if frame_node.select:
                    frame_linked_and_selected = True
                    bank_frames = True
                    break
                frame_node = frame_node.parent

            if(temp_frames != [] and bank_frames):
                for frame in temp_frames:
                    if frame not in frames:

                        frames.append(frame)

            temp_frames = []

            if node.parent != None:
                nimi = node.parent.name
            else:
                nimi = ''


            if node.select or frame_linked_and_selected:
                all_nodes.append(node)
                if(node.name.startswith('__node__') == False):
                    node.name = '__node__' + node.name

                if (node.type == 'GROUP'):

                    group_settings = ExtraSetting.writeGroupExtraSettings(node)
                    if(node.node_tree != None):
                        name_node_tree = node.node_tree.name
                    else:
                        name_node_tree = ''

                    dict['nodes'].append({
                        'node': node.bl_idname,
                        'name': node.name,
                        'label': node.label,
                        'location': [node.location[0], node.location[1]],
                        'node_tree': '__node__' + name_node_tree,
                        'main_socket_type': "",
                        'parent': nimi,
                        'hide': node.hide,
                        'hidden_outputs': [],
                        'height': node.height,
                        'width': node.width,
                        'extra_settings': group_settings
                    })
                    if node.node_tree not in group_nodes:
                        if node.node_tree != None:
                            group_nodes.append(node.node_tree)
                elif (node.type != 'FRAME'):
                    if(bpy.context.area.ui_type == 'CompositorNodeTree'):
                        dict = ExtraSettingComp.writeExtraSettings(dict, node, '', nimi, 'MAIN_TREE')
                    else:
                        dict = ExtraSetting.writeExtraSettings(dict, node, '', nimi, 'MAIN_TREE')
    for select_node in all_nodes:

        if(len(select_node.inputs) > 0):
            for index, input in enumerate(select_node.inputs):
                if(input.is_linked):
                    find_name = input.links[0].from_node
                    for find_from in all_nodes:
                        if find_name == find_from:
                            temp_socket = str(input.links[0].from_socket.path_from_id()).split('outputs[')[-1]
                            temp_socket = temp_socket.split(']')[0]
                            dict['links'].append({
                                'output_node': input.links[0].from_node.name,
                                'output_socket': int(temp_socket),
                                'input_node': select_node.name,
                                'input_socket': index,
                                'main_socket_type': ""
                            })
                            break

    if(frames != []):
        for frame in frames:
            if(nodes[frame].parent == None):
                nimi = ''
            else:
                nimi = nodes[frame].parent.name

            dict['frames'].append({
                'node': nodes[frame].bl_idname,
                'name': nodes[frame].name,
                'label': nodes[frame].label,
                'label_size': nodes[frame].label_size,
                'use_color': nodes[frame].use_custom_color,
                'color': [nodes[frame].color[0], nodes[frame].color[1], nodes[frame].color[2]],
                'height': nodes[frame].height,
                'width': nodes[frame].width,
                'location': [nodes[frame].location[0], nodes[frame].location[1]],
                'parent': nimi
            })

    allgroupnodes = NodeGroupComputer.find_all_groupnodes(group_nodes)
    dict_groups = NodeGroupComputer.write_groupnodetrees(allgroupnodes)

    # Renaming names for their initial states.

    for node in bpy.data.node_groups:
        if (node.name.startswith('__node__')):
            node.name = node.name[8:]
        for nod in node.nodes:
            if (nod.name.startswith('__node__')):
                nod.name = nod.name[8:]


    for node in nodes:
        if(node.type == 'GROUP'):
            if(node.node_tree != None):
                if(node.node_tree.name.startswith('__node__')):
                    node.node_tree.name = node.node_tree.name[8:]

    oldname_to_node(nodes)

    return dict, dict_groups
