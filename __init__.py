# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

''' Code is written by Samuli Riihikoski (haikalle) haikalle@gmail.com '''

bl_info = {
    "name": "NodeCustomBuilder",
    "author": "Kalle-Samuli Riihikoski (haikalle)",
    "version": (0, 0, 70),
    "blender": (2, 80, 0),
    "description": "Save/Load your custom node trees.",
    "warning": "",
    "category": "3D View",
}

import bpy
import os
import json
from bpy.utils import register_class, unregister_class
from bpy.props import IntProperty, CollectionProperty, StringProperty
from bpy.app.handlers import persistent
from bpy.types import Panel, UIList

from . import write_json
from . import read_json

class NodeCustomBuilderPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    
    library_dir = os.path.expanduser("~")	         
    library_dir = os.path.join(library_dir, "Documents", "NodeCustomBuilder")

    user_lib_path: StringProperty(name="Library Path",
                                  default=library_dir,
                                  subtype='DIR_PATH')

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, "user_lib_path", expand=True)

def get_library_path():
    library_dir = os.path.expanduser("~")
    library_dir = os.path.join(library_dir, "Documents", "NodeCustomBuilder")
    library_dir = bpy.context.preferences.addons["NodeCustomBuilder"].preferences.user_lib_path
    return library_dir


def get_items(self, context):
    library_dir = get_library_path() 
    folder_file = library_dir + os.sep + 'folders.txt'
    l = [];

    if(os.path.isdir(library_dir) == False):
        os.mkdir(library_dir)

    if(os.path.isfile(folder_file) == False):
        file = open(folder_file, "w")
        file.write('ALL,Default,Default,')
        file.close()

    with open(folder_file, 'r') as f:
        for line in f:
            s = line.split(',')
            l.append((s[1], s[1], s[2]))
    return l;

@persistent
def handler(scene):

    if(bpy.types.Scene.custom_string != bpy.context.scene.custom_folders):
        bpy.types.Scene.custom_string = bpy.context.scene.custom_folders
        bpy.ops.custom.blend_select()

@persistent
def init_handler(scene):
    bpy.app.handlers.depsgraph_update_pre.remove(init_handler)
    bpy.ops.custom.blend_select()


class DeleteFolder(bpy.types.Operator):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "custom.delete_folder"
    bl_label = "Delete selected"
    bl_options = {'PRESET'}

    def execute(self, context):
        scn = context.scene

        if (bpy.context.area.ui_type == 'CompositorNodeTree'):
            type_mode = 'CM'
        elif (bpy.context.area.ui_type == 'GeometryNodeTree'):
            type_mode = 'GM'

        else:
            if (bpy.context.space_data.shader_type == 'OBJECT'):
                type_mode = 'OB'
            elif (bpy.context.space_data.shader_type == 'WORLD'):
                type_mode = 'WL'

        library_dir = get_library_path() 
        folder_file = library_dir + os.sep + 'folders.txt'

        if(bpy.context.scene.custom_folders == 'Default'):
            return {'FINISHED'}

        if (bpy.context.area.ui_type == 'CompositorNodeTree'):
            name_begin = 'CM__' + bpy.context.scene.custom_folders + '__'
            for file in os.listdir(library_dir):
                if (file.startswith(name_begin)):
                    osoite = library_dir + os.sep + file
                    os.remove(osoite)
                    if (scn.custom_comp_index > 0):
                        scn.custom_comp_index -= 1
        
        elif (bpy.context.area.ui_type == 'GeometryNodeTree'):
            name_begin = 'GM__' + bpy.context.scene.custom_folders + '__'
            for file in os.listdir(library_dir):
                if (file.startswith(name_begin)):
                    osoite = library_dir + os.sep + file
                    os.remove(osoite)
                    if (scn.custom_geo_index > 0):
                        scn.custom_geo_index -= 1

        else:

            if (bpy.context.space_data.shader_type == 'OBJECT'):
                name_begin = 'OB__' + bpy.context.scene.custom_folders + '__'
                for file in os.listdir(library_dir):
                    if(file.startswith(name_begin)):
                        osoite = library_dir + os.sep + file
                        os.remove(osoite)
                        if (scn.custom_index > 0):
                            scn.custom_index -= 1


            elif (bpy.context.space_data.shader_type == 'WORLD'):
                name_begin = 'WL__' + bpy.context.scene.custom_folders + '__'
                for file in os.listdir(library_dir):
                    if (file.startswith(name_begin)):
                        osoite = library_dir + os.sep + file
                        os.remove(osoite)
                        if (scn.custom_world_index > 0):
                            scn.custom_world_index -= 1


        with open(folder_file, "r+") as f:
            d = f.readlines()
            f.seek(0)
            for i in d:
                if i.startswith(type_mode + ',' + bpy.context.scene.custom_folders) == False:
                    f.write(i)
            f.truncate()

        bpy.context.scene.custom_folders = 'Default'
        bpy.ops.custom.blend_select()

        return {'FINISHED'}

class DeleteSelected(bpy.types.Operator):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "custom.delete_selected"
    bl_label = "Delete selected"
    bl_options = {'PRESET'}


    def execute(self, context):
        scn = context.scene
        library_dir = get_library_path() 

        if (bpy.context.area.ui_type == 'CompositorNodeTree'):

            presets = scn.custom_comp.items()

            if (presets != []):
                presets = scn.custom_comp.items()
                preset_name = 'CM__' + bpy.context.scene.custom_folders + '__' + presets[scn.custom_comp_index][0] + '.json'
                scn.custom_comp.remove(scn.custom_comp_index)

                full_path = library_dir + os.sep + preset_name
                if (os.path.isfile(full_path)):
                    os.remove(full_path)
                if (scn.custom_comp_index > 0):
                    scn.custom_comp_index -= 1

        elif (bpy.context.area.ui_type == 'GeometryNodeTree'):

            presets = scn.custom_geo.items()

            if (presets != []):
                presets = scn.custom_geo.items()
                preset_name = 'GM__' + bpy.context.scene.custom_folders + '__' + presets[scn.custom_geo_index][0] + '.json'
                scn.custom_geo.remove(scn.custom_geo_index)

                full_path = library_dir + os.sep + preset_name
                if (os.path.isfile(full_path)):
                    os.remove(full_path)
                if (scn.custom_geo_index > 0):
                    scn.custom_gep_index -= 1

        else:

            if (bpy.context.space_data.shader_type == 'OBJECT'):

                presets = scn.custom.items()

                if(presets != []):
                    presets = scn.custom.items()
                    preset_name = 'OB__' + bpy.context.scene.custom_folders + '__' + presets[scn.custom_index][0] + '.json'
                    scn.custom.remove(scn.custom_index)

                    full_path = library_dir + os.sep + preset_name
                    if(os.path.isfile(full_path)):
                        os.remove(full_path)
                    if(scn.custom_index > 0):
                        scn.custom_index -= 1

            elif (bpy.context.space_data.shader_type == 'WORLD'):

                presets = scn.custom_world.items()

                if (presets != []):
                    presets = scn.custom_world.items()
                    preset_name = 'WL__' + bpy.context.scene.custom_folders + '__' + presets[scn.custom_world_index][0] + '.json'
                    scn.custom_world.remove(scn.custom_world_index)

                    full_path = library_dir + os.sep + preset_name
                    if (os.path.isfile(full_path)):
                        os.remove(full_path)
                    if (scn.custom_world_index > 0):
                        scn.custom_world_index -= 1


        return {'FINISHED'}

class BlendSelectOperator(bpy.types.Operator):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "custom.blend_select"
    bl_label = "Blend Selector"
    bl_options = {'PRESET', 'UNDO'}

    def execute(self, context):
        main_list = []

        scn = context.scene
        if(scn != None):
            library_dir = get_library_path() 

            if(os.path.isdir(library_dir)):

                for one in scn.custom:
                    scn.custom.remove(0)
                for one in scn.custom_world:
                    scn.custom_world.remove(0)
                for one in scn.custom_comp:
                    scn.custom_comp.remove(0)
                for one in scn.custom_geo:
                    scn.custom_geo.remove(0)

                # iterate through the selected files
                for file in os.listdir(library_dir):
                    # generate full path to file
                    if(file.startswith('OB__' + bpy.context.scene.custom_folders + '__')):
                        item = scn.custom.add()
                        item.id = len(scn.custom)
                        item.name = file[:-5]
                        test_name = item.name.split('__')
                        item.name = test_name[2]
                    elif (file.startswith('WL__' + bpy.context.scene.custom_folders + '__')):
                        item = scn.custom_world.add()
                        item.id = len(scn.custom_world)
                        item.name = file[:-5]
                        test_name = item.name.split('__')
                        item.name = test_name[2]
                    elif (file.startswith('CM__' + bpy.context.scene.custom_folders + '__')):
                        item = scn.custom_comp.add()
                        item.id = len(scn.custom_comp)
                        item.name = file[:-5]
                        test_name = item.name.split('__')
                        item.name = test_name[2]
                    elif (file.startswith('GM__' + bpy.context.scene.custom_folders + '__')):
                        item = scn.custom_geo.add()
                        item.id = len(scn.custom_geo)
                        item.name = file[:-5]
                        test_name = item.name.split('__')
                        item.name = test_name[2]
            else:
                for one in scn.custom:
                    scn.custom.remove(0)
                for one in scn.custom_world:
                    scn.custom_world.remove(0)
                for one in scn.custom_comp:
                    scn.custom_comp.remove(0)
                for one in scn.custom_geo:
                    scn.custom_geo.remove(0)


            material = bpy.context.object.active_material
            if(material != None):
                for node in material.node_tree.nodes:
                    material.node_tree.nodes.active = node

        return {'FINISHED'}

class BlendSelectButtonOperator(bpy.types.Operator):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "custom.refresh_list"
    bl_label = "Blend Selector"
    bl_options = {'PRESET', 'UNDO'}

    def execute(self, context):

        if (bpy.context.scene.custom_folders == ''):
            bpy.context.scene.custom_folders = 'Default'

        if (bpy.context.area.ui_type == 'CompositorNodeTree'):
            type = 'CM__'
            type_mode ='CM'
        elif (bpy.context.area.ui_type == 'GeometryNodeTree'):
            type = 'GM__'
            type_mode ='GM'
        else:
            if (bpy.context.space_data.shader_type == 'OBJECT'):
                type = 'OB__'
                type_mode = 'OB'
            elif (bpy.context.space_data.shader_type == 'WORLD'):
                type = 'WL__'
                type_mode = 'WL'

        library_dir = get_library_path() 
        folder_file = library_dir + os.sep + 'folders.txt'
        folder_index = []

        if (os.path.isfile(folder_file) == False):
            file = open(folder_file, "w")
            file.write('ALL,Default,Default,')
            file.close()

        with open(folder_file, 'r') as f:
            for line in f:
                split = line.split(',')
                if(split[0] == type_mode or split[0] == 'ALL'):
                    folder_index.append(split[1])


        # iterate through the selected files
        for file in os.listdir(library_dir):
            if (file.startswith(type)):
                split_filename = file.split('__')
                if (split_filename[1] not in folder_index):
                    folder_index.append(split_filename[1])
        file = open(folder_file, "w")

        for index in folder_index:
            if(index == 'Default'):
                file.write('ALL,' + index + ',' + index + ',\n')
            else:
                file.write(type_mode + ',' + index + ',' + index + ',\n')

        file.close()

        material = bpy.context.object.active_material

        if (material != None):
            for node in material.node_tree.nodes:
                material.node_tree.nodes.active = node
                #node.select = True
                bpy.ops.custom.blend_select()
        bpy.ops.custom.blend_select()

        return {'FINISHED'}


class PresetLoad(bpy.types.Operator):
    bl_idname = "node.preset_load"
    bl_label = "Index Node"

    filename : StringProperty(default='')

    def execute(self, context):

        if(bpy.context.active_object != None):
            if(bpy.context.active_object.type == 'MESH' or bpy.context.active_object.type == 'CURVE'):
                read_json.read(self.filename)

        return {'FINISHED'}

class LIBRARY_MT_node(bpy.types.Menu):
    bl_idname = "LIBRARY_MT_node"
    bl_label = "NodeCustomBuilder"


    def draw(self, context):
        active_node = bpy.context.active_object.active_material.node_tree.nodes.active

        library_dir = get_library_path() 

        for index, file in enumerate(os.listdir(library_dir)):

            self.layout.operator("node.preset_load", text=file[:-5]).filename = library_dir + os.sep + file
        pass

class ITEM_UL_items(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)

class CUSTOM_OT_actions(bpy.types.Operator):
    """Move items up and down, add and remove"""
    bl_idname = "custom.list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}

    action: bpy.props.EnumProperty(
        items=(
            ('FILE_REFRESH', "Refresh", ""),
            ('RENAME', "Rename", ""),
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('REMOVE_FOLDER', "Remove", ""),
            ('ADD_FOLDER', "Add", ""),
            ('ADD', "Add", "")))

    def invoke(self, context, event):

        if self.action == 'ADD':
            bpy.ops.custom.save_selected('INVOKE_DEFAULT')

        elif self.action == 'REMOVE_FOLDER':
            bpy.ops.custom.delete_folder('INVOKE_DEFAULT')
        elif self.action == 'ADD_FOLDER':
            bpy.ops.custom.create_new_folder('INVOKE_DEFAULT')

        elif self.action == 'RENAME':
            bpy.ops.custom.rename_item('INVOKE_DEFAULT')

        elif self.action == 'REMOVE':
            scn = context.scene
            library_dir = get_library_path() 

            if (bpy.context.area.ui_type == 'CompositorNodeTree'):

                presets = scn.custom_comp.items()

                if (presets != []):
                    presets = scn.custom_comp.items()
                    preset_name = 'CM__' + bpy.context.scene.custom_folders + '__' + presets[scn.custom_comp_index][
                        0] + '.json'
                    scn.custom_comp.remove(scn.custom_comp_index)

                    full_path = library_dir + os.sep + preset_name
                    if (os.path.isfile(full_path)):
                        os.remove(full_path)
                    if (scn.custom_comp_index > 0):
                        scn.custom_comp_index -= 1

            elif (bpy.context.area.ui_type == 'GeometryNodeTree'):

                presets = scn.custom_geo.items()

                if (presets != []):
                    presets = scn.custom_geo.items()
                    preset_name = 'GM__' + bpy.context.scene.custom_folders + '__' + presets[scn.custom_geo_index][
                        0] + '.json'
                    scn.custom_geo.remove(scn.custom_geo_index)

                    full_path = library_dir + os.sep + preset_name
                    if (os.path.isfile(full_path)):
                        os.remove(full_path)
                    if (scn.custom_geo_index > 0):
                        scn.custom_geo_index -= 1

            else:

                if (bpy.context.space_data.shader_type == 'OBJECT'):

                    presets = scn.custom.items()

                    if (presets != []):
                        presets = scn.custom.items()
                        preset_name = 'OB__' + bpy.context.scene.custom_folders + '__' + presets[scn.custom_index][
                            0] + '.json'
                        scn.custom.remove(scn.custom_index)

                        full_path = library_dir + os.sep + preset_name
                        if (os.path.isfile(full_path)):
                            os.remove(full_path)
                        if (scn.custom_index > 0):
                            scn.custom_index -= 1

                elif (bpy.context.space_data.shader_type == 'WORLD'):

                    presets = scn.custom_world.items()

                    if (presets != []):
                        presets = scn.custom_world.items()
                        preset_name = 'WL__' + bpy.context.scene.custom_folders + '__' + \
                                      presets[scn.custom_world_index][0] + '.json'
                        scn.custom_world.remove(scn.custom_world_index)

                        full_path = library_dir + os.sep + preset_name
                        if (os.path.isfile(full_path)):
                            os.remove(full_path)
                        if (scn.custom_world_index > 0):
                            scn.custom_world_index -= 1

        elif self.action == 'FILE_REFRESH':
            if (bpy.context.scene.custom_folders == ''):
                bpy.context.scene.custom_folders = 'Default'

            if (bpy.context.area.ui_type == 'CompositorNodeTree'):
                type = 'CM__'
                type_mode = 'CM'

            elif (bpy.context.area.ui_type == 'GeometryNodeTree'):
                type = 'GM__'
                type_mode = 'GM'

            else:
                if (bpy.context.space_data.shader_type == 'OBJECT'):
                    type = 'OB__'
                    type_mode = 'OB'

                elif (bpy.context.space_data.shader_type == 'WORLD'):
                    type = 'WL__'
                    type_mode = 'WL'

            library_dir = get_library_path() 
            folder_file = library_dir + os.sep + 'folders.txt'
            folder_index = []

            if (os.path.isfile(folder_file) == False):
                file = open(folder_file, "w")
                file.write('ALL,Default,Default,')
                file.close()

            with open(folder_file, 'r') as f:
                for line in f:
                    split = line.split(',')
                    if (split[0] == type_mode or split[0] == 'ALL'):
                        folder_index.append(split[1])

            # iterate through the selected files
            for file in os.listdir(library_dir):
                if (file.startswith(type)):
                    split_filename = file.split('__')
                    if (split_filename[1] not in folder_index):
                        folder_index.append(split_filename[1])
            file = open(folder_file, "w")

            for index in folder_index:
                if (index == 'Default'):
                    file.write('ALL,' + index + ',' + index + ',\n')
                else:
                    file.write(type_mode + ',' + index + ',' + index + ',\n')

            file.close()

            material = bpy.context.object.active_material

            if (material != None):
                for node in material.node_tree.nodes:
                    material.node_tree.nodes.active = node
                    # node.select = True
                    bpy.ops.custom.blend_select()
            bpy.ops.custom.blend_select()
        return {"FINISHED"}



class MAINPANEL_PT_nodecustombuilder(Panel):
    bd_idname = 'OBJECT_PT_my_panel'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_label = "NodeCustomBuilder"
    bl_category = 'Node'

    def draw(self, context):

        if (bpy.context.area.ui_type == 'CompositorNodeTree'):
            layout = self.layout
            scn = bpy.context.scene

            if (scn != None):
                presets = scn.custom_comp.items()

                if (presets != []):
                    try:
                        active_item = presets[scn.custom_comp_index][0] + '.json'
                    except:
                        pass

                library_dir = get_library_path() 

                rows = 6

                row = layout.row(align=True)
                row.prop(bpy.context.scene, "custom_folders", text="")
                row.separator()
                row.operator("custom.list_action", icon='NEWFOLDER', text="").action = 'ADD_FOLDER'
                row.operator("custom.list_action", icon='TRASH', text="").action = 'REMOVE_FOLDER'

                row = layout.row()
                row.template_list("ITEM_UL_items", "", scn, "custom_comp", scn, "custom_comp_index", rows=rows)

                col = row.column(align=True)
                col.operator("custom.list_action", icon='ADD', text="").action = 'ADD'
                col.operator("custom.list_action", icon='REMOVE', text="").action = 'REMOVE'
                col.separator()
                col.operator("custom.list_action", icon='SORTALPHA', text="").action = 'RENAME'
                col.separator()
                col.operator("custom.list_action", icon='FILE_REFRESH', text="").action = 'FILE_REFRESH'

                row = layout.row()

                if (presets != []):
                    row.operator('node.preset_load', text="Load").filename = library_dir + os.sep + 'CM__' + bpy.context.scene.custom_folders + '__'+ active_item
    
        elif (bpy.context.area.ui_type == 'GeometryNodeTree'):
            layout = self.layout
            scn = bpy.context.scene

            if (scn != None):
                presets = scn.custom_geo.items()

                if (presets != []):
                    try:
                        active_item = presets[scn.custom_geo_index][0] + '.json'
                    except:
                        pass

                library_dir = get_library_path() 

                rows = 6

                row = layout.row(align=True)
                row.prop(bpy.context.scene, "custom_folders", text="")
                row.separator()
                row.operator("custom.list_action", icon='NEWFOLDER', text="").action = 'ADD_FOLDER'
                row.operator("custom.list_action", icon='TRASH', text="").action = 'REMOVE_FOLDER'

                row = layout.row()
                row.template_list("ITEM_UL_items", "", scn, "custom_geo", scn, "custom_geo_index", rows=rows)

                col = row.column(align=True)
                col.operator("custom.list_action", icon='ADD', text="").action = 'ADD'
                col.operator("custom.list_action", icon='REMOVE', text="").action = 'REMOVE'
                col.separator()
                col.operator("custom.list_action", icon='SORTALPHA', text="").action = 'RENAME'
                col.separator()
                col.operator("custom.list_action", icon='FILE_REFRESH', text="").action = 'FILE_REFRESH'

                row = layout.row()

                if (presets != []):
                    row.operator('node.preset_load', text="Load").filename = library_dir + os.sep + 'GM__' + bpy.context.scene.custom_folders + '__'+ active_item

        else:

            if(bpy.context.space_data.shader_type == 'OBJECT'):
                layout = self.layout
                scn = bpy.context.scene
                active_item = ""
                if(scn != None):
                    presets = scn.custom.items()
                    if(presets != []):
                        try:
                            active_item = presets[scn.custom_index][0] + '.json'
                        except:
                            pass

                    library_dir = get_library_path() 

                    rows = 6

                    row = layout.row(align=True)
                    row.prop(bpy.context.scene, "custom_folders", text="")
                    row.separator()
                    row.operator("custom.list_action", icon='NEWFOLDER', text="").action = 'ADD_FOLDER'
                    row.operator("custom.list_action", icon='TRASH', text="").action = 'REMOVE_FOLDER'

                    row = layout.row()
                    row.template_list("ITEM_UL_items", "", scn, "custom", scn, "custom_index", rows=rows)
                    col = row.column(align=True)
                    col.operator("custom.list_action", icon='ADD', text="").action = 'ADD'
                    col.operator("custom.list_action", icon='REMOVE', text="").action = 'REMOVE'
                    col.separator()
                    col.operator("custom.list_action", icon='SORTALPHA', text="").action = 'RENAME'
                    col.separator()
                    col.operator("custom.list_action", icon='FILE_REFRESH', text="").action = 'FILE_REFRESH'


                    row = layout.row()

                    if(presets != []):
                        row.operator('node.preset_load', text="Load Preset").filename = library_dir + os.sep + 'OB__' + bpy.context.scene.custom_folders + '__'+ active_item

            elif (bpy.context.space_data.shader_type == 'WORLD'):
                layout = self.layout
                scn = bpy.context.scene

                if (scn != None):
                    presets = scn.custom_world.items()
                    
                    if (presets != []):
                        try:
                            active_item = presets[scn.custom_world_index][0] + '.json'
                        except:
                            pass

                    library_dir = get_library_path() 

                    rows = 6

                    row = layout.row(align=True)
                    row.prop(bpy.context.scene, "custom_folders", text="")
                    row.separator()
                    row.operator("custom.list_action", icon='NEWFOLDER', text="").action = 'ADD_FOLDER'
                    row.operator("custom.list_action", icon='TRASH', text="").action = 'REMOVE_FOLDER'

                    row = layout.row()
                    row.template_list("ITEM_UL_items", "", scn, "custom_world", scn, "custom_world_index", rows=rows)

                    col = row.column(align=True)
                    col.operator("custom.list_action", icon='ADD', text="").action = 'ADD'
                    col.operator("custom.list_action", icon='REMOVE', text="").action = 'REMOVE'
                    col.separator()
                    col.operator("custom.list_action", icon='SORTALPHA', text="").action = 'RENAME'
                    col.separator()
                    col.operator("custom.list_action", icon='FILE_REFRESH', text="").action = 'FILE_REFRESH'

                    row = layout.row()

                    if (presets != []):
                        try:
                            row.operator('node.preset_load', text="Load").filename = library_dir + os.sep + 'WL__' + bpy.context.scene.custom_folders + '__'+ active_item
                        except:
                            pass


class OFPropConfirmOperator(bpy.types.Operator):
    """Generate Custom Output Folders"""
    bl_idname = "custom.save_selected"
    bl_label = "Save Node Preset"

    type : bpy.props.StringProperty(
        default="",
        #options={'SKIP_SAVE'}
        )

    @classmethod
    def poll(cls, context):
        space = context.space_data

        return space.type == 'NODE_EDITOR'


    def execute(self, context):

        if self.type != '':

            scn = context.scene
            dict = {}

            if(bpy.context.area.ui_type == 'CompositorNodeTree'):
                nodes = bpy.context.scene.node_tree.nodes
            elif(bpy.context.area.ui_type == 'GeometryNodeTree'):
                nodes = bpy.context.active_object.modifiers['GeometryNodes'].node_group.nodes

            else:
                if (bpy.context.space_data.shader_type == 'OBJECT'):
                    nodes = bpy.context.active_object.active_material.node_tree.nodes
                if (bpy.context.space_data.shader_type == 'WORLD'):
                    nodes = bpy.data.worlds[0].node_tree.nodes

            dict, dict_groups = write_json.write(dict, nodes)

            total_dict = {**dict, **dict_groups}

            library_dir = get_library_path() 
            print('osoite: ', library_dir)
            if (not (os.path.isdir(library_dir))):
                os.makedirs(library_dir)

            if (bpy.context.area.ui_type == 'CompositorNodeTree'):
                type = 'CM__'
                file = library_dir + os.sep + type + bpy.context.scene.custom_folders + '__' + self.type + '.json'

            elif (bpy.context.area.ui_type == 'GeometryNodeTree'):
                type = 'GM__'
                file = library_dir + os.sep + type + bpy.context.scene.custom_folders + '__' + self.type + '.json'

            else:
                if (bpy.context.space_data.shader_type == 'OBJECT'):
                    type = 'OB__'
                    file = library_dir + os.sep + type + bpy.context.scene.custom_folders + '__' + self.type + '.json'
                elif (bpy.context.space_data.shader_type == 'WORLD'):
                    type = 'WL__'
                    file = library_dir + os.sep + type + bpy.context.scene.custom_folders + '__' + self.type + '.json'
            name_temp = type + bpy.context.scene.custom_folders + '__' + self.type
            looking = True
            name_index = 0
            while (looking == True):
                if (os.path.isfile(file)):
                    if (self.type[-1].isdigit()):
                        fi = library_dir + os.sep
                        last_digit = int(self.type[-1])
                        last_digit += 1
                        pituus = len(self.type) - 1
                        self.type = self.type[:pituus] + str(last_digit)
                        testing = bpy.context.scene.custom_folders + '__'
                        file = ("%s%s%s%s.json" % (fi, type, testing, self.type))
                    else:
                        fi = library_dir + os.sep + name_temp
                        file = ("%s%.2d.json" % (fi, name_index))
                        self.type = ("%s%.2d" % (self.type, name_index))
                else:
                    looking = False
            print('total_dict', total_dict)
            with open(file, 'w') as outfile:
                json.dump(total_dict, outfile, indent='    ')

            if(bpy.context.area.ui_type == 'CompositorNodeTree'):
                item = scn.custom_comp.add()
                item.id = len(scn.custom_comp)
                item.name = self.type
                self.type = ""
            
            elif(bpy.context.area.ui_type == 'GeometryNodeTree'):
                item = scn.custom_geo.add()
                item.id = len(scn.custom_geo)
                item.name = self.type
                self.type = ""

            else:

                if (bpy.context.space_data.shader_type == 'OBJECT'):
                    item = scn.custom.add()
                    item.id = len(scn.custom)
                    item.name = self.type
                    self.type = ""

                elif (bpy.context.space_data.shader_type == 'WORLD'):
                    item = scn.custom_world.add()
                    item.id = len(scn.custom_world)
                    item.name = self.type
                    self.type = ""

        bpy.ops.custom.refresh_list()
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=200)

    def draw(self, context):
        row = self.layout
        row.prop(self, "type", text="Name")
        row.separator()

class FolderConfirmOperator(bpy.types.Operator):
    """Generate Custom Output Folders"""
    bl_idname = "custom.create_new_folder"
    bl_label = "Create New Folder"

    type : bpy.props.StringProperty(
        default="",
        #options={'SKIP_SAVE'}
        )

    @classmethod
    def poll(cls, context):
        space = context.space_data

        return space.type == 'NODE_EDITOR'


    def execute(self, context):

        bpy.ops.custom.refresh_list()

        if (bpy.context.area.ui_type == 'CompositorNodeTree'):
            type_mode = 'CM'
        elif (bpy.context.area.ui_type == 'GeometryNodeTree'):
            type_mode = 'GM'
            
        else:
            if (bpy.context.space_data.shader_type == 'OBJECT'):
                type_mode = 'OB'
            elif (bpy.context.space_data.shader_type == 'WORLD'):
                type_mode = 'WL'

        if self.type != '':
            library_dir = get_library_path() 
            folder_file = library_dir + os.sep + 'folders.txt'
            '''
            with open(folder_file, "r+") as f:
                d = f.readlines()
                f.seek(0)
                for i in d:
                    if i == "":
                        f.write(i)
                f.truncate()
            '''
            if (os.path.isfile(folder_file) == True):
                file = open(folder_file, "a")
                file.write(type_mode + ',' + self.type + ',' + self.type + ',' + '\n')
                file.close()


        bpy.ops.custom.refresh_list()
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=200)

    def draw(self, context):
        row = self.layout
        row.prop(self, "type", text="Name")
        row.separator()


class RenameConfirmOperator(bpy.types.Operator):
    """Generate Custom Output Folders"""
    bl_idname = "custom.rename_item"
    bl_label = "Rename Item"

    type : bpy.props.StringProperty(default='')
    filename: StringProperty(default='')

    @classmethod
    def poll(cls, context):
        space = context.space_data

        return space.type == 'NODE_EDITOR'

    def execute(self, context):

        print('CustomFolder1: ', bpy.context.scene.custom_folders)
        current_folder = bpy.context.scene.custom_folders

        if (bpy.context.area.ui_type == 'CompositorNodeTree'):
            scn = bpy.context.scene
            presets = scn.custom_comp.items()

            if (presets != []):
                try:
                    active_item = presets[scn.custom_comp_index][0] + '.json'
                except:
                    pass

            self.filename = 'CM__'+ bpy.context.scene.custom_folders + '__' + active_item

        elif (bpy.context.area.ui_type == 'GeometryNodeTree'):
            scn = bpy.context.scene
            presets = scn.custom_geo.items()

            if (presets != []):
                try:
                    active_item = presets[scn.custom_geo_index][0] + '.json'
                except:
                    pass

            self.filename = 'GM__'+ bpy.context.scene.custom_folders + '__' + active_item

        else:
            if (bpy.context.space_data.shader_type == 'OBJECT'):
                scn = bpy.context.scene
                presets = scn.custom.items()
                if (presets != []):
                    try:
                        active_item = presets[scn.custom_index][0] + '.json'
                    except:
                        pass

                self.filename = 'OB__' + bpy.context.scene.custom_folders + '__' + active_item

            elif (bpy.context.space_data.shader_type == 'WORLD'):
                scn = bpy.context.scene
                presets = scn.custom_world.items()

                if (presets != []):
                    try:
                        active_item = presets[scn.custom_world_index][0] + '.json'
                    except:
                        pass

                self.filename = 'WL__' + bpy.context.scene.custom_folders + '__' + active_item

        if (bpy.context.area.ui_type == 'CompositorNodeTree'):
            item_count = len(scn.custom_comp)
        elif (bpy.context.area.ui_type == 'GeometryNodeTree'):
            item_count = len(scn.custom_geo)

        else:
            if (bpy.context.space_data.shader_type == 'OBJECT'):
                item_count = len(scn.custom)
            elif (bpy.context.space_data.shader_type == 'WORLD'):
                item_count = len(scn.custom_world)

        if self.type != '' and self.filename != '':
            library_dir = get_library_path() 
            folder_file = library_dir + os.sep + 'folders.txt'

            if (bpy.context.area.ui_type == 'CompositorNodeTree'):
                type = 'CM__'
                type_i = 'CM'
                active_item = scn.custom_comp[scn.custom_comp_index].name + '.json'
                file = library_dir + os.sep + type + bpy.context.scene.custom_folders + '__' + active_item

            elif (bpy.context.area.ui_type == 'GeometryNodeTree'):
                type = 'GM__'
                type_i = 'GM'
                active_item = scn.custom_geo[scn.custom_geo_index].name + '.json'
                file = library_dir + os.sep + type + bpy.context.scene.custom_folders + '__' + active_item

            else:
                if (bpy.context.space_data.shader_type == 'OBJECT'):
                    type = 'OB__'
                    type_i = 'OB'
                    active_item = scn.custom[scn.custom_index].name + '.json'
                    file = library_dir + os.sep + type + bpy.context.scene.custom_folders + '__' + active_item
                elif (bpy.context.space_data.shader_type == 'WORLD'):
                    type = 'WL__'
                    type_i = 'WL'
                    active_item = scn.custom_world[scn.custom_world_index].name + '.json'
                    file = library_dir + os.sep + type + bpy.context.scene.custom_folders + '__' + active_item

            old_name_split = self.filename.split('__')
            new_name = self.type.split('__')
            if(len(new_name) > 1):
                new_name_label = new_name[0]
                new_folder = new_name[1]
            else:
                new_folder = bpy.context.scene.custom_folders
                new_name_label = new_name[0]

            new_new = old_name_split[0] + '__' + new_folder + '__' + new_name_label + '.json'
            new = os.path.join(library_dir, new_new)

            if(os.path.isfile(file)):
                os.replace(file, new)
                delete_folder = True
                print('CustomFolder2: ', bpy.context.scene.custom_folders)
                if(item_count == 1):
                    with open(folder_file, "r+") as f:
                        d = f.readlines()
                        f.seek(0)
                        for i in d:
                            if i.startswith(type_i + ',' + bpy.context.scene.custom_folders) == False:
                                f.write(i)
                        f.truncate()

                    #bpy.context.scene.custom_folders = 'Default'



            else:
                bpy.ops.custom.refresh_list()

        bpy.ops.custom.refresh_list()
        try:
            bpy.context.scene.custom_folders = current_folder
        except:
            bpy.context.scene.custom_folders = 'Default'
        bpy.ops.custom.refresh_list()
        return {'FINISHED'}

    def invoke(self, context, event):
        scn = bpy.context.scene
        if (bpy.context.area.ui_type == 'CompositorNodeTree'):
            active_item = scn.custom_comp[scn.custom_comp_index].name
        elif (bpy.context.area.ui_type == 'GeometryNodeTree'):
            active_item = scn.custom_geo[scn.custom_geo_index].name
        else:
            if (bpy.context.space_data.shader_type == 'OBJECT'):
                active_item = scn.custom[scn.custom_index].name
            elif (bpy.context.space_data.shader_type == 'WORLD'):
                active_item = scn.custom_world[scn.custom_world_index].name
        self.type = active_item
        return context.window_manager.invoke_props_dialog(self, width=200)


    def draw(self, context):
        row = self.layout
        row.prop(self, "type", text="Name")
        row.separator()





class CustomProps(bpy.types.PropertyGroup):
    id : IntProperty()
    name : StringProperty()
    path : StringProperty()


classes = (
    NodeCustomBuilderPreferences,
    CUSTOM_OT_actions,
    DeleteFolder,
    DeleteSelected,
    BlendSelectOperator,
    BlendSelectButtonOperator,
    MAINPANEL_PT_nodecustombuilder,
    ITEM_UL_items,
    OFPropConfirmOperator,
    FolderConfirmOperator,
    PresetLoad,
    LIBRARY_MT_node,
    CustomProps,
    RenameConfirmOperator,
)


def register():
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.custom = CollectionProperty(type=CustomProps)
    bpy.types.Scene.custom_index = IntProperty(default = 0)
    
    bpy.types.Scene.custom_world = CollectionProperty(type=CustomProps)
    bpy.types.Scene.custom_world_index = IntProperty(default=0)
    
    bpy.types.Scene.custom_comp = CollectionProperty(type=CustomProps)
    bpy.types.Scene.custom_comp_index = IntProperty(default=0)
    
    bpy.types.Scene.custom_geo = CollectionProperty(type=CustomProps)
    bpy.types.Scene.custom_geo_index = IntProperty(default=0)
    
    bpy.types.Scene.custom_string = StringProperty(default="")

    bpy.types.Scene.custom_folders = bpy.props.EnumProperty(items=get_items)
    bpy.app.handlers.depsgraph_update_pre.append(init_handler)
    bpy.app.handlers.depsgraph_update_post.append(handler)




def unregister():


    for cls in classes:
        unregister_class(cls)

    del bpy.types.Scene.custom
    del bpy.types.Scene.custom_index

    del bpy.types.Scene.custom_world
    del bpy.types.Scene.custom_world_index

    del bpy.types.Scene.custom_comp
    del bpy.types.Scene.custom_comp_index

    del bpy.types.Scene.custom_geo
    del bpy.types.Scene.custom_geo_index

    del bpy.types.Scene.custom_string


    