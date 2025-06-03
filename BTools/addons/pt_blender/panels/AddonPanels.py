import bpy

from ..config import __addon_name__
from ..operators.AddonOperators import ExampleOperator
from ....common.i18n.i18n import i18n
from ....common.types.framework import reg_order


class BasePanel(object):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ExampleAddon"

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return True


# 注册属性（放在 register 之前）
bpy.types.Scene.wrapper_object = bpy.props.PointerProperty(
    name="包裹器",
    type=bpy.types.Object,
    description="点击选择一个物体作为包裹器"
)

@reg_order(0)
class ExampleAddonPanel(BasePanel, bpy.types.Panel):
    bl_label = "Blender&PT&UE全流程工具"
    bl_idname = "B_P_U"


    def draw(self, context: bpy.types.Context):
        addon_prefs = context.preferences.addons[__addon_name__].preferences

        layout = self.layout

        layout.separator()
        # layout.label(text=i18n("Example Functions") + ": " + str(addon_prefs.number))
        layout.prop(addon_prefs, "filepath")
        layout.operator(ExampleOperator.bl_idname, text="清理").action = "clear"
        layout.separator()
        layout.label(text="模型优化")
        layout.operator(ExampleOperator.bl_idname, text="重拓扑&材质").action = "debuff1"
        row0 = layout.row()
        row0.operator(ExampleOperator.bl_idname, text="重拓扑").action = "debuff2"
        row0.operator(ExampleOperator.bl_idname, text="烘焙(auto E)").action = "debuff3"

        row1 = layout.row()
        row1.prop(context.scene, "wrapper_object", text="包裹器")
        row1.operator(ExampleOperator.bl_idname, text="烘焙(cage E)").action = "debuff4"
        layout.separator()
        # row = layout.row()
        # row.prop(addon_prefs, "number")
        layout.label(text="贴图优化")
        layout.operator(ExampleOperator.bl_idname, text="材质导出到pt").action = "export"
        row2 = layout.row()
        row2.operator(ExampleOperator.bl_idname, text="cm->m").action = "exportup"
        row2.operator(ExampleOperator.bl_idname, text="m->cm").action = "exportdown"
        layout.operator(ExampleOperator.bl_idname, text="材质导入回blender").action = "import"
        layout.separator()
        layout.label(text="导入优化")
        row = layout.row()
        row.prop(addon_prefs, "mystring")
        row.prop(addon_prefs, "boolean")

        layout.operator(ExampleOperator.bl_idname, text="导出模型到UE").action = "exportfbx"

        box = layout.box()

        box.label(text="使用说明", icon='MODIFIER')
        box.label(text="一定要先选择资源位置")
        box.label(text="高模拖入h集合重拓扑")
        box.label(text="按住CTRL select高模active低模烘焙")
        box.label(text="选择物体导出到pt")
        box.label(text="选择物体导入pt材质")
        box.label(text="模型拖入Mesh集合")
        box.label(text="骨骼拖入Rig集合")

        box.label(text="ue-tga材质", icon='MODIFIER')
        box.label(text="rgba RGB-BASE COLOR(rgb) A-Opacity(灰度)")
        box.label(text="CucaoJinshuYinying R-Roughness(灰度) G-Metallic(灰度) B-Ambient occlusion(灰度)")
        box.label(text="faxianDirectX RGB-Normal DirectX(rgb)")
        box.label(text="faxianOpenGL RGB-Normal(rgb)")
        box.label(text="zifaguang RGB-Emissive(rgb)")
    @classmethod
    def poll(cls, context: bpy.types.Context):
        return True


# This panel will be drawn after ExampleAddonPanel since it has a higher order value
# @reg_order(1)
# class ExampleAddonPanel2(BasePanel, bpy.types.Panel):
#     bl_label = "导出blender模型"
#     bl_idname = "B_P_U_out"
#
#     def draw(self, context: bpy.types.Context):
#         layout = self.layout
#         layout.label(text="导出blender模型到pt中")
#         layout.operator(ExampleOperator.bl_idname)

