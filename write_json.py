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
    dict['nodes'] = []
    dict['links'] = []
    dict['keyframes'] = []
    groups = []
    final_groups_list = {}
    final_groups_list['groups'] = []

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
        if not node.select:
            continue

        if(node.name.startswith('__node__') == False):
            node.name = '__node__' + node.name

        area = bpy.context.area.ui_type
        settings = ExtraSetting.writeExtraSettings(area, node)

        dict['nodes'].append({
            'node': node.bl_idname,
            'name': node.name,
            'label': node.label,
            'hide': node.hide,
            'height': node.height,
            'width': node.width,
            'extra_settings': settings
        })

        if (node.parent != None):
            if nodes[node.parent.name].select:
                dict['nodes'][-1].update({
                    'parent': node.parent.name,
                    'location': [node.location[0], node.location[1]],
                })
            else:
                x_loc = nodes[node.parent.name].location[0] + node.location[0]
                y_loc = nodes[node.parent.name].location[1] + node.location[1]

                dict['nodes'][-1].update({
                    'location': [x_loc, y_loc],
                })

        else:
            dict['nodes'][-1].update({
                'location': [node.location[0], node.location[1]],
            })

        if (node.type == 'GROUP'):
            if(node.node_tree != None):

                if node.node_tree.name not in groups:
                    dict['nodes'][-1].update({
                        'node_tree': '__node__' + node.node_tree.name
                    })

                    groups.append(node.node_tree)
                    new_group, groups = NodeGroupComputer.collectGroupTree(node.node_tree.name, final_groups_list, groups)
                    final_groups_list['groups'].append(new_group)

    for node in nodes:
        if(len(node.inputs) == 0):
            continue

        for index, input in enumerate(node.inputs):
            if(input.is_linked):
                from_node = input.links[0].from_node

                if not from_node.select:
                    continue

                temp_socket = str(input.links[0].from_socket.path_from_id()).split('outputs[')[-1]
                temp_socket = temp_socket.split(']')[0]

                dict['links'].append([
                        input.links[0].from_node.name,
                        int(temp_socket),
                        node.name,
                        index,
                    ])

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

    return dict, final_groups_list
