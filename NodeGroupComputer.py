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
from . import ExtraSetting

def collectGroupTree(current_group, final_groups_list, groups):

    nodes = {}
    nodes['node'] = []
    links = {}
    links['links'] = []
    inputs = {}
    outputs = {}
    settings = []

    if current_group in groups:
        return

    for node in bpy.data.node_groups[current_group].nodes:

        if (node.parent != None):
            parent = node.parent.name
        else:
            parent = ''

        nodes['node'].append({
            'node': node.bl_idname,
            'name': node.name,
            'label': node.label,
            'location': [node.location[0], node.location[1]],
            'parent': parent,
            'hide': node.hide,
            'height': node.height,
            'width': node.width,
        })

        if(node.type == 'GROUP'):
            if (node.node_tree == None):
                continue

            name_node_tree = node.node_tree.name

            if(name_node_tree.startswith('__node__') == False):
                name_node_tree = '__node__' + name_node_tree

            area = bpy.context.area.ui_type
            settings = ExtraSetting.writeExtraSettings(area, node)

            nodes['node'][-1].update({
                'node_tree': name_node_tree,
                'extra_settings': settings
            })

            groups.append(node.node_tree)
            new_group, groups = collectGroupTree(node.node_tree.name, final_groups_list, groups)
            final_groups_list['groups'].append(new_group)

        elif(node.type == 'GROUP_INPUT'):

            outputs['outputs'] = []

            for input in node.outputs:
                if(input.name != ''):
                    outputs['outputs'].append([input.bl_idname, input.name])

            nodes['node'][-1].update({
                'outputs': outputs['outputs'],
                'extra_settings': []
            })

        elif(node.type == 'GROUP_OUTPUT'):

            inputs['inputs'] = []

            for input in node.inputs:
                if(input.name != ''):
                    inputs['inputs'].append([input.bl_idname, input.name])

            nodes['node'][-1].update({
        
                'inputs': inputs['inputs'],
                'location': [node.location[0], node.location[1]],
        
                'extra_settings': []
            })

        elif (node.type == 'FRAME'):

            if (node.name.startswith('__node__') == False):
                node.name = '__node__' + node.name

            nodes['node'][-1].update({
                'name': node.name,
                'color': [node.color[0], node.color[1], node.color[2]],
                'use_color': node.use_custom_color,
                'extra_settings': []
            })

        else:

            if node.parent != None:
                nimi = node.parent.name
            else:
                nimi = ''
            area = bpy.context.area.ui_type
            settings = ExtraSetting.writeExtraSettings(area, node)

            nodes['node'][-1].update({
                'extra_settings': settings
            })

        # Write connections

        if(len(node.inputs) == 0):
            continue

        for index, input in enumerate(node.inputs):
            if(input.is_linked):

                temp_socket = str(input.links[0].from_socket.path_from_id()).split('outputs[')[-1]
                temp_socket = temp_socket.split(']')[0]

                links['links'].append([
                        input.links[0].from_node.name,
                        int(temp_socket),
                        node.name,
                        index,
                    ])

    return {
        'name': '__node__' + current_group,
        'nodes': nodes['node'],
        'links': links['links']
    }, groups

