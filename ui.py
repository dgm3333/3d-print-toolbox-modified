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

# <pep8-80 compliant>

# Interface for this addon.


from bpy.types import Panel
import bmesh

from . import report

#Misc notes:
#row = layout.row() - creates a new line in the interface
#row = col.row(align=True)


'''
def print3d_show_check_clean_help(bpy.types.Operator):
    bl_idname = "message.print3d_show_check_clean_help"
    bl_label = ""
 
    message = bpy.props.StringProperty(
        name = "message",
        description = "message",
        default = ''
    )
 
    def execute(self, context):
        self.report({'INFO'}, self.message)
        print(self.message)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 400)
 
    def draw(self, context):
        self.layout.label(self.message)
        self.layout.label("")
'''


class View3DPrintPanel:
    bl_category = "3D-Print"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == 'MESH' and obj.mode in {'OBJECT', 'EDIT'}


class VIEW3D_PT_print3d_analyze(View3DPrintPanel, Panel):
    bl_label = "Analyze"

    _type_to_icon = {
        bmesh.types.BMVert: 'VERTEXSEL',
        bmesh.types.BMEdge: 'EDGESEL',
        bmesh.types.BMFace: 'FACESEL',
    }

    def draw_report(self, context):
        layout = self.layout
        info = report.info()

        if info:
            is_edit = context.edit_object is not None

            layout.label(text="Result")
            box = layout.box()
            col = box.column()

            for i, (text, data, cls) in enumerate(info):
                if is_edit and data and data[1]:
                    bm_type, _bm_array = data
                    row = col.row(align=True)
                    row.operator("mesh.print3d_select_report", text=text, icon=self._type_to_icon[bm_type],).index = i
                    row.operator("mesh.print3d_trigger_clean", text="", icon="SHADERFX",).index = i
                    #col.operator("mesh.print3d_clean_non_manifold", text="", icon="SHADERFX",)
                    #TODO: insert Blender icon SHADERFX for the cleanup
                else:
                    col.label(text=text)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        unit = scene.unit_settings
        print_3d = scene.print_3d

        #row = col.row(align="Right")
        #row.operator("mesh.print3d_trigger_clean", text="", icon="QUESTION",).index = i
        # NB Icon Viewer is a plugin which adds an button to top of the python console showing the Blender Icons


        layout.label(text="Statistics")
        row = layout.row(align=True)
        #row = col.row(align="Right")
        #row.operator("mesh.print3d_show_hide_beta_items", text="", icon="LIGHT_DATA",).index = i



        col = layout.column(align=True)
        row = col.row(align=True)
        row.label(text="Checks")
#        row.operator("message.print3d_show_check_clean_help", text="", icon="QUESTION",)   # placeholder 
#        row.operator("ui.print3d_show_check_clean_help", text="", icon="QUESTION",)
        
        row = col.row(align=True)
        layout.operator("mesh.print3d_check_all", text="Check All")

      # layout.column starts a new block
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("mesh.print3d_check_solid", text="Solid / Manifold")
        row.operator("mesh.print3d_clean_non_manifold", text="", icon="SHADERFX",)
#        layout.operator("mesh.print3d_clean_non_manifold", text="Make Manifold")
        row = col.row(align=True)
        row.label(text="")
        row.operator("mesh.print3d_info_volume", text="Volume=")
        row.label(text=str(float(int(print_3d.object_volume*1000)/1000)))
        #row.prop(print_3d, "object_volume", text="")
        if unit.system == 'IMPERIAL':
            row.label(text='"³')
        else:
            row.label(text="cm³")
        row = col.row(align=True)
        row.label(text="")
        row.operator("mesh.print3d_info_area", text="Area=")
        #to make non-editible:
        row.label(text=str(print_3d.object_area))
        #row.prop(print_3d, "object_area", text="")
        if unit.system == 'IMPERIAL':
            row.label(text='"²')
        else:
            row.label(text="cm²")
            
        row = col.row(align=True)
        row.operator("mesh.print3d_check_intersect", text="Intersections")
        row.operator("mesh.print3d_class_notdefined", text="", icon="UNLINKED",)

        row = col.row(align=True)
        row.operator("mesh.print3d_check_degenerate", text="v. Small Edge or Face")
        row.prop(print_3d, "threshold_zero", text="")
        row.operator("mesh.print3d_clean_degenerate", text="", icon="SHADERFX",)
#        row.operator("mesh.print3d_clean_degenerate", text="Dissolve Smalls")

        row = col.row(align=True)
        row.operator("mesh.print3d_check_doubles", text="v. Close Vertices")
        row.prop(print_3d, "threshold_double", text="")
        row.operator("mesh.print3d_clean_doubles", text="", icon="SHADERFX",)
#        row.operator("mesh.print3d_clean_doubles", text="Merge very close Doubles")

        row = col.row(align=True)
        row.operator("mesh.print3d_check_distort", text="Distorted")
        row.prop(print_3d, "angle_distort", text="")
        row.operator("mesh.print3d_clean_distorted", text="", icon="SHADERFX",)
#        row.operator("mesh.print3d_clean_distorted", text="Distorted")

        row = col.row(align=True)
        row.operator("mesh.print3d_check_thick", text="Thickness")
        row.prop(print_3d, "thickness_min", text="")
        row.operator("mesh.print3d_class_notdefined", text="", icon="UNLINKED",)
#        row.operator("mesh.print3d_clean_thin", text="Wall Thickness")

        row = col.row(align=True)
        row.operator("mesh.print3d_check_sharp", text="Edge Sharp")
        row.prop(print_3d, "angle_sharp", text="")
        row.operator("mesh.print3d_class_notdefined", text="", icon="UNLINKED",)

#        row = col.row(align=True)
#        row.operator("mesh.print3d_check_disconnected", text="Disconnected")
#        row.prop(print_3d, "proportion_disconnected", text="")

        row = col.row(align=True)
        row.operator("mesh.print3d_check_overhang", text="Overhang")
        row.prop(print_3d, "angle_overhang", text="")
        row.operator("mesh.print3d_class_notdefined", text="", icon="UNLINKED",)

        row = col.row(align=True)
#        row.label(text="Resin Traps:")
#        row.operator("mesh.print3d_check_unfilled_islands", text="Resin Traps")
        row.label(text="Resin Traps:"+str(float(int(print_3d.volume_uncured*1000)/1000)))
        if unit.system == 'IMPERIAL':
            row.label(text='"³')
        else:
            row.label(text="cm³")
        row.operator("mesh.print3d_class_notdefined", text="", icon="UNLINKED",)

#        row = col.row(align=True)
#        layout.label(text="print3d_check_touching_boundaries")  # can't remember why I wanted to do this - probably just delete it


        row = col.row(align=True)
        row.label(text="Delete Loose:")
        row.operator("mesh.print3d_clean_loose", text="", icon="SHADERFX",)

        row = col.row(align=True)
        row.label(text="Split Non Planar Faces:")
        row.operator("mesh.print3d_clean_non_planars", text="", icon="SHADERFX",)

        row = col.row(align=True)
        row.label(text="Split Concave Faces:")
        row.operator("mesh.print3d_clean_concaves", text="", icon="SHADERFX",)

        row = col.row(align=True)
        row.label(text="Triangulate Faces:")
        row.operator("mesh.print3d_clean_triangulates", text="", icon="SHADERFX",)

        row = col.row(align=True)
        row.label(text="Fill Holes:")
        row.operator("mesh.print3d_clean_holes", text="", icon="SHADERFX",)

        row = col.row(align=True)
        row.label(text="Highlight Printing Risk:")
        row.operator("mesh.print3d_class_notdefined", text="", icon="UNLINKED",)




        self.draw_report(context)


class VIEW3D_PT_print3d_meshlab(View3DPrintPanel, Panel):
    bl_label = "Use MeshLab Tools"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        print_3d = context.scene.print_3d

        layout = self.layout

        col = layout.column(align=True)
        row = col.row(align=True)

        if not print_3d.pymeshlabAvailable:
            row.label(text="You Need To Install Meshlab: ")
    #        row.operator("message.print3d_show_meshlab_install_help", text="", icon="QUESTION",)
            row.operator("mesh.print3d_class_notdefined", text="", icon="UNLINKED",)

            #To use meshlab filters on Blender meshes
            #Details are at:
            #https://pypi.org/project/pymeshlab/

            # You first need to install pymeshlab
            #You can do this from the Blender scripting workspace in Blender 2.92
            # BUT you have to have admininistor priviledges so for Windows users
            #JUST THIS ONCE open Blender by R-clicking on it in the start menu and select"Run as Administrator"

            #Open up the System Console (under the Window menu)
            #Then paste the following into the scripting workspace and run it

            #--- FROM HERE ---#
            '''
            import subprocess
            import sys
            import os
 
            # path to python.exe
            python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
 
            # upgrade pip
            subprocess.call([python_exe, "-m", "ensurepip"])
            subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
 
            # install required packages
            subprocess.call([python_exe, "-m", "pip", "install", "pymeshlab"])

            print("DONE")
            '''
            #--- TO HERE ---#


            #Now exit Blender and restart it normally



        else:

            row = col.row(align=True)
            row.operator("mesh.print3d_clean_triangulates", text="Triangulate Faces")




class VIEW3D_PT_print3d_transform(View3DPrintPanel, Panel):
    bl_label = "Transform"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.label(text="Align With Baseplate:")
        row.operator("mesh.print3d_class_notdefined", text="", icon="UNLINKED",)

        row = col.row(align=True)
        row.label(text="Simplify Mesh (=Limited Dissolve):")
        row.operator("mesh.print3d_clean_limited", text="", icon="SHADERFX",)

        row = col.row(align=True)
        row.label(text="print3d_merge_selected_into_single_solid:")
        row.operator("mesh.print3d_class_notdefined", text="", icon="UNLINKED",)
#        row.operator("mesh.print3d_merge_selected_into_single_solid", text="", icon="SHADERFX",)

        row = col.row(align=True)
        row.label(text="Hollow Out Object:")
        row.operator("mesh.print3d_class_notdefined", text="", icon="UNLINKED",)

        row = col.row(align=True)
        row.label(text="Scale to Volume:")
        row.operator("mesh.print3d_scale_to_volume", text="", icon="SHADERFX",)
        row = col.row(align=True)
        row.label(text="Scale to Bounds:")
        row.operator("mesh.print3d_scale_to_bounds", text="", icon="SHADERFX",)

        
        row = col.row(align=True)
        row.label(text="Auto Support Selected Faces:")
        row.operator("mesh.print3d_create_supports", text="", icon="SHADERFX",)

        row = col.row(align=True)
        row.label(text="Slice Object:")
        row.operator("mesh.print3d_slicer", text="", icon="SHADERFX",)






#        row.operator("mesh.print3d_merge_selected_into_single_solid", text="Merge To Solid")



class VIEW3D_PT_print3d_export(View3DPrintPanel, Panel):
    bl_label = "Export"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        print_3d = context.scene.print_3d

        layout.prop(print_3d, "export_path", text="")

        col = layout.column()
        col.prop(print_3d, "use_apply_scale")
        col.prop(print_3d, "use_export_texture")

        layout.prop(print_3d, "export_format")
        layout.operator("mesh.print3d_export", text="Export", icon='EXPORT')

        layout.label(text="TODO: export direct to SLA voxel format - possibly use UVTools.core.dll")


class VIEW3D_PT_print3d_workarea(View3DPrintPanel, Panel):
    bl_label = "Settings"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        print_3d = context.scene.print_3d

        col = layout.column(align=True)
        layout.label(text="TODO:")
        layout.label(text="print3d_setup_illuminate")
        layout.label(text="print3d_setup_printer_bed")
        layout.label(text="print3d_setup_printer_volume")
        layout.label(text="print3d_setup_printer_resolution")

        layout.label(text="Printer Presets - including creating printer workspace")
        layout.label(text="Generate Printer Calibration Test Pieces")
        # Calibration pieces are required to support slicing checks



#        layout.operator("mesh.print3d_setup_illuminate", text="Illuminate Visible")
#        layout.operator("mesh.print3d_setup_printer_bed", text="Add Printer Bed")
#        layout.operator("mesh.print3d_setup_printer_volume", text="Add Printer Volume")
#        layout.operator("mesh.print3d_setup_printer_resolution", text="Set Printer Resolution")


