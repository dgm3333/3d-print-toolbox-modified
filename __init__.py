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


# 2019 - forked by Agnieszka Pas to: https://github.com/agapas/3d-print-toolbox-modified
#      - added various repair tools (but not merged with main branch)
# 2020 - Blender official version updated
# 2021 - forked 2020 official version and merged Agnieszka updates



#Misc addon dev Notes:
# when editing an addon you can more quickly have it updated by Blender using the following
# you can symlink the installed Blender directory to target your editing directory.
# Then whenever you save the __init__.py file, Blender will know it needs to be reloaded 
#   when you untick/retick to activate addon (in the Blender Preferences/Addons/section). See:
#https://www.matthewsessions.com/blog/developing-blender-addon-tips/
#in windows from an admin level command prompt (not a powershell)
#mklink /J "C:\Users\dgm55\AppData\Roaming\Blender Foundation\Blender\2.92\scripts\addons\3d-print-toolbox-test" "C:\Users\dgm55\source\repos\StressTestAndSupportsVisualisation\3d-print-toolbox-test"
# BUT don't forget to keep incremental backups...

bl_info = {
    "name": "3D Print Toolbox",
    "description": "Utilities for 3D printing",
    "author": "Campbell Barton, Agnieszka Pas, David Mckenzie",
    "version": (2, 1, 410),
    "blender": (2, 80, 0),
    "location": "3D View > Sidebar",
    "warning": "",
    'wiki_url': '{BLENDER_MANUAL_URL}/addons/mesh/3d_print_toolbox.html',
    "category": "Mesh"
}



if "bpy" in locals():
    import importlib
    importlib.reload(ui)
    importlib.reload(operators)
    importlib.reload(mesh_helpers)
    importlib.reload(meshlab_integration)
    importlib.reload(meshlab_filter_panel)
    importlib.reload(slicer)
    importlib.reload(supports)
    if "export" in locals():
        importlib.reload(export)
else:
    import math

    import bpy
    from bpy.types import PropertyGroup
    from bpy.props import (
        StringProperty,
        IntProperty,
        BoolProperty,
        FloatProperty,
        EnumProperty,
        PointerProperty,
    )
    # normal convention is "from . file_name import CLASS_NAME"
    from . import (
        ui,
        operators,
        mesh_helpers,
        meshlab_integration,
        meshlab_filter_panel,
        slicer,
        supports,
    )


# subtype dependent on type. See: https://docs.blender.org/api/2.92/bpy.props.html#module-bpy.props
# if adding new property types (eg BoolProperty) they have to be imported from bpy.props (above)
class SceneProperties(PropertyGroup):
    export_format: EnumProperty(
        name="Format",
        description="Format type to export to",
        items=(
            ('STL', "STL", ""),
            ('PLY', "PLY", ""),
            ('X3D', "X3D", ""),
            ('OBJ', "OBJ", ""),
        ),
        default='STL',
    )
    use_export_texture: BoolProperty(
        name="Copy Textures",
        description="Copy textures on export to the output path",
        default=False,
    )
    use_apply_scale: BoolProperty(
        name="Apply Scale",
        description="Apply scene scale setting on export",
        default=False,
    )
    export_path: StringProperty(
        name="Export Directory",
        description="Path to directory where the files are created",
        default="//",
        maxlen=1024,
        subtype="DIR_PATH",
    )
    object_volume: FloatProperty(
        name="Volume",
        description="Volume of Selected Object",
        unit="VOLUME",
        default=0.0,
        precision=3,
        min=0.0,
        max=999999,
    )
    object_area: FloatProperty(
        name="Area",
        description="Surface Area of Selected Object",
        unit="AREA",
        default=0.0,
        precision=3,
        min=0.0,
        max=999999,
    )
    thickness_min: FloatProperty(
        name="Thickness",
        description="Minimum thickness",
        unit="LENGTH",
        subtype='DISTANCE',
        default=0.01,  # 0.01mm
        min=0.0,
        max=100.0,
    )
    threshold_zero: FloatProperty(
        name="Threshold",
        description="Limit for minimum face area and edge length",
        subtype='DISTANCE',
        default=0.01,
        precision=3,
        min=0.0,
        max=0.2,
    )
    threshold_double: FloatProperty(
        name="Threshold",
        description="Limit for minimum vertex proximity",
        unit="LENGTH",
        subtype='DISTANCE',
        default=0.01,
        precision=3,
        min=0.0,
        max=0.2,
    )
    angle_distort: FloatProperty(
        name="Angle",
        description="Limit for checking distorted faces",
        subtype='ANGLE',
        default=math.radians(45.0),
        min=0.0,
        max=math.radians(180.0),
    )
    angle_sharp: FloatProperty(
        name="Angle",
        subtype='ANGLE',
        default=math.radians(160.0),
        min=0.0,
        max=math.radians(180.0),
    )
    angle_overhang: FloatProperty(
        name="Angle",
        subtype='ANGLE',
        default=math.radians(45.0),
        min=0.0,
        max=math.radians(90.0),
    )
    proportion_disconnected: FloatProperty(
        name="Proportion",
        subtype='PERCENTAGE',
        default=10,
        min=0.0,
        max=100.0,
    )
    volume_uncured: FloatProperty(
        name="Volume of Uncured Resin left within model",
        unit="VOLUME",
        default=0.0,
        min=0.0,
        max=99999.0,
    )
    pymeshlabAvailable: IntProperty(
        name="Has pymeshlab been installed",
        description="0 if untested, -1 if unavailable, 1 if pymeshlab has been imported",
        default=0,
    )
    pymeshlabfilters: EnumProperty(
        name="MeshLab Filters",
        default="select_none",
        description="List of all MeshLab Filters accessible via pymeshlab",
        items=(
            ("select_none","select_none","select_none"),
            ("-","--------","Favorites are listed above"),       
        ),
    )



    


# Notes on class naming conventions (since Blender 2.8)
# see: https://wiki.blender.org/wiki/Reference/Release_Notes/2.80/Python_API/Addons for the naming convention

#Classes that contain properties from bpy.props use Python's type annotations and should be assigned with a colon, not an =
#class MyOperator(Operator):
#    value: IntProperty()

# Add-on's should assign their classes to a tuple or list and register/unregister them directly (see functions below).
#Module names are the name of the file (as per normal Python)
#Class names within each module *MUST* be: UPPER_CASE_{SEPARATOR}_mixed_case
#where separator is one of:-
#Header -> _HT_
#Menu -> _MT_
#Operator -> _OT_
#Panel -> _PT_
#UIList -> _UL_

classes = (
    SceneProperties,

    ui.VIEW3D_PT_print3d_analyze,
    ui.VIEW3D_PT_print3d_meshlab,
    ui.VIEW3D_PT_print3d_transform,
    ui.VIEW3D_PT_print3d_export,
    ui.VIEW3D_PT_print3d_workarea,

    operators.MESH_OT_print3d_info_volume,
    operators.MESH_OT_print3d_info_area,
    operators.MESH_OT_print3d_check_degenerate,
    operators.MESH_OT_print3d_check_doubles,
    operators.MESH_OT_print3d_check_disconnected,
#    operators.MESH_OT_print3d_check_unfilled_islands,
    operators.MESH_OT_print3d_check_distorted,
#    operators.MESH_OT_print3d_check_triangulates,    # not required check_distorted does the job fine
    operators.MESH_OT_print3d_check_solid,
    operators.MESH_OT_print3d_check_intersections,
    operators.MESH_OT_print3d_check_thick,
    operators.MESH_OT_print3d_check_sharp,
    operators.MESH_OT_print3d_check_overhang,
    operators.MESH_OT_print3d_check_all,

    operators.MESH_OT_print3d_class_notdefined,

    operators.MESH_OT_print3d_clean_distorted,
    operators.MESH_OT_print3d_clean_triangulates,   # basically a duplicated of clean_distorted
    operators.MESH_OT_print3d_clean_non_manifold,

    operators.MESH_OT_print3d_clean_degenerate,
    operators.MESH_OT_print3d_clean_doubles,

    operators.MESH_OT_print3d_clean_loose,
    operators.MESH_OT_print3d_clean_non_planars,
    operators.MESH_OT_print3d_clean_concaves,
    operators.MESH_OT_print3d_clean_holes,
    operators.MESH_OT_print3d_clean_limited,

    operators.MESH_OT_print3d_trigger_clean,

    operators.MESH_OT_print3d_select_report,
    operators.MESH_OT_print3d_scale_to_volume,
    operators.MESH_OT_print3d_scale_to_bounds,

    operators.MESH_OT_print3d_export,
    
#    meshlab_integration.VIEW3D_OT_print3d_install_pymeshlab,
#    meshlab_integration.MESH_OT_print3d_process_mesh_in_meshlab,

#    meshlab_filter_panel.VIEW3D_OT_print3d_actions,
#    meshlab_filter_panel.VIEW3D_OT_print3d_printItems,
#    meshlab_filter_panel.VIEW3D_OT_print3d_clearList,
#    meshlab_filter_panel.VIEW3D_OT_print3d_removeDuplicates,
#    meshlab_filter_panel.VIEW3D_OT_print3d_selectItems,
#    meshlab_filter_panel.VIEW3D_UL_print3d_items,
#    meshlab_filter_panel.VIEW3D_PT_print3d_objectList,
#    meshlab_filter_panel.VIEW3D_print3d_objectCollection,


    slicer.MESH_OT_print3d_slicer,

    supports.MESH_OT_print3d_create_supports,



)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.print_3d = PointerProperty(type=SceneProperties)



def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.print_3d
