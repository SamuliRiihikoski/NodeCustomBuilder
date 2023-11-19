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
import json
from . import ExtraSetting

def read(filename):


    if (bpy.context.active_object.material_slots.keys() == [] and bpy.context.area.ui_type != 'CompositorNodeTree'):
        newmat = bpy.data.materials.new('Material')
        newmat.use_nodes = True
        bpy.context.active_object.data.materials.append(newmat)

    if(bpy.context.area.ui_type == 'CompositorNodeTree'):
        if bpy.context.scene.use_nodes == False:
            bpy.context.scene.use_nodes = True

        active_nodetree = bpy.context.scene.node_tree

    elif(bpy.context.area.ui_type == 'GeometryNodeTree'):
        active_nodetree = bpy.context.active_object.modifiers['GeometryNodes'].node_group

    else:
        if (bpy.context.space_data.shader_type == 'OBJECT'):
            active_nodetree = bpy.context.active_object.active_material.node_tree
        elif (bpy.context.space_data.shader_type == 'WORLD'):
            active_nodetree = bpy.data.worlds[0].node_tree


    if(len(active_nodetree.nodes) > 0):
        for node in active_nodetree.nodes:
            node.select = False

    type_not = []
    used_frames = []
    new_nodes = []
    frame_and_location = []

    with open(filename) as json_file:
        data = json.load(json_file)

        # MATERIAL SETTINGS

        active_material = bpy.context.object.active_material
        if (bpy.context.space_data.shader_type == 'OBJECT'):
            if data.get('material'):
                for material in data['material']:

                    active_material.use_backface_culling = material['use_backface_culling']
                    active_material.blend_method = material['blend_method']
                    active_material.shadow_method = material['shadow_method']
                    active_material.alpha_threshold = material['alpha_threshold']
                    active_material.use_screen_refraction = material['use_screen_refraction']
                    active_material.refraction_depth = material['refraction_depth']
                    active_material.use_sss_translucency = material['use_sss_translucency']
                    active_material.pass_index = material['pass_index']


        # CREATE GROUP NODE TREES 

        for group in data['groups']:
            if (bpy.context.area.ui_type == 'CompositorNodeTree'):
                group_nodetree = bpy.data.node_groups.new(type="CompositorNodeTree", name=group['name'])
            elif (bpy.context.area.ui_type == 'GeometryNodeTree'):
                group_nodetree = bpy.data.node_groups.new(type="GeometryNodeTree", name=group['name'])
            else:
                group_nodetree = bpy.data.node_groups.new(type="ShaderNodeTree", name=group['name'])

            for node in group['nodes']:
                new_node = group_nodetree.nodes.new(node['node'])
                new_node.name = node['name']
                try:
                    new_node.label = node['label']
                except:
                    pass

                new_node.hide = node['hide']
                new_node.height = node['height']
                new_node.width = node['width']
                if (new_node.type != 'FRAME'):
                    new_node.location = node['location']
                if node['parent'] != '':
                    new_node.parent = group_nodetree.nodes[node['parent']]

                # Group interface is build later (when selecting nodetrees)
                if (len(node['extra_settings']) != 0 and new_node.type != 'GROUP'):
                    ExtraSetting.readExtraSettings(node['extra_settings'], new_node)
           

                if(new_node.type == 'FRAME'):
                    new_node.use_custom_color = node['use_color']
                    new_node.color[0] = node['color'][0]
                    new_node.color[1] = node['color'][1]
                    new_node.color[2] = node['color'][2]
                    #new_node.location = node['location']
                    new_node.height = node['height']
                    new_node.width = node['width']
                    new_node.label = node['label']
                    #if node.get('label_size'):
                    #    new_node.label_size = node['label_size']
                    frame_and_location.append([node['name'],node['location']])
                    if node['parent'] != '':
                        new_node.parent = group_nodetree.nodes[node['parent']]

        

        # CREATE BASE TREE NODES

        # FIRST PASS CREATES NODES
        for p in data['nodes']:
            node_new = active_nodetree.nodes.new(p['node'])
             
            active_nodetree.nodes[-1].name = p['name']
            active_nodetree.nodes[-1].label = p['label']
            active_nodetree.nodes[-1].height = p['height']
            active_nodetree.nodes[-1].width = p['width']

            if(active_nodetree.nodes[-1].type == 'GROUP'):
                if p['node_tree'] != '':
                    active_nodetree.nodes[-1].node_tree = bpy.data.node_groups[p['node_tree']]
            
            active_nodetree.nodes[-1].location = p['location']
            new_nodes.append(node_new.name)

            if(len(p['extra_settings']) != 0):
                ExtraSetting.readExtraSettings(p['extra_settings'], node_new)

        # SECOND PASS CONNECTS PARENTS
        for p in data['nodes']:
            if 'parent' in p.keys():
                active_nodetree.nodes[p['name']].parent = active_nodetree.nodes[p['parent']]
             
        # CONNECT FRAMES WITH NODES IN BASE TREE

        for new_node_name in new_nodes:
            node = active_nodetree.nodes[new_node_name]
            if(node.parent != None):
                temp = node.parent
                while (temp != None):

                    if temp.name not in used_frames:
                        used_frames.append(temp.name)
                    if(temp.parent != None):
                        temp = temp.parent
                    else:
                        temp = None

        # SOCKET CONNECTIONS IN BASE TREE

        for link in data['links']:
          
            try:
                active_nodetree.nodes[link['output_node']]
                active_nodetree.nodes[link['input_node']]
        
                active_nodetree.links.new(active_nodetree.nodes[link['output_node']].outputs[link['output_socket']],
                                        active_nodetree.nodes[link['input_node']].inputs[link['input_socket']])
            except:
                print('ERROR: link problem')
                pass

    # NODE TREES INTO GROUP NODES (Creating group interface here)

    for group in data['groups']:
        group_tree = bpy.data.node_groups[group['name']]

        for node in group['nodes']:
            if (node['node'].endswith('NodeGroup')):
                nd = group_tree.nodes[node['name']]
                nd.node_tree = bpy.data.node_groups[node['node_tree']]
                ExtraSetting.readExtraSettings(node['extra_settings'], nd)

    
    # SOCKET CONNECTIONS FOR GROUP NODE TREES

    for group in bpy.data.node_groups:
        name = group.name
        print(name)

    for group in data['groups']:
        group_tree = bpy.data.node_groups[group['name']]
        print(group_tree.name)

        for link in group['links']:
            print(link)
            try:
                group_tree.links.new(group_tree.nodes[link[0]].outputs[link[1]], group_tree.nodes[link[2]].inputs[link[3]])
            except:
                print('soxket error')
                pass

    # FRAMES RE-LOCATION

    for group in bpy.data.node_groups:
        for node in group.nodes:
            if(node.name.startswith('__node__')):
                if node.type == 'FRAME':
                    for seek in frame_and_location:
                        if seek[0] == node.name:
                            node.location = seek[1]
                            break

    ''' We skipped to set GROUP param in first loop. Now we need other loop to do this '''

    for group in data['groups']:
        g_name = group['name']
        for group_node in group['nodes']:
            n_name = group_node['name']
            node = bpy.data.node_groups[g_name].nodes[n_name]
            if group_node['node'] == 'ShaderNodeGroup' and len(group_node['extra_settings'])>0:
                if (len(group_node['extra_settings']) != 0):
                    ExtraSetting.readExtraSettings(group_node['extra_settings'], bpy.data.node_groups[g_name].nodes[n_name])
            
            if node.type == 'GROUP_INPUT':
                for link in node.outputs:
                    link.hide = True

            if node.type == 'GROUP_OUTPUT':
                for link in node.inputs:
                    link.hide = True
               

    ''' Remove __node__ tag from nodes and groups name '''

    for node in active_nodetree.nodes:
        if node.name.startswith('__node__'):
            node.name = node.name[8:]

    for node in bpy.data.node_groups:
        if node.name.startswith('__node__'):
            node.name = node.name[8:]

    ''' Next calculate average center point and move selected nodes into center '''
    
    average_x = 0
    average_y = 0
    average_index = 0

    for node in active_nodetree.nodes:
        has_parent = True
        if node.select == True:
            try:
                node.parent.name
            except:
                has_parent = False

            if(has_parent == False):
                average_x += node.location[0]
                average_y += node.location[1]
                average_index += 1

    if average_index == 0:
        average_x = 0
        average_y = 0
    else:
        average_x = average_x / average_index
        average_y = average_y / average_index
    
    for node in active_nodetree.nodes:
        has_parent = True
        if node.select == True:
            try:
                node.parent.name
            except:
                has_parent = False

            if(has_parent == False):
                node.location[0] = node.location[0] - average_x
                node.location[1] = node.location[1] - average_y
    





