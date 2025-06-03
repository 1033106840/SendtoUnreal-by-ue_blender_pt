import bpy
import os
import subprocess
from ..config import __addon_name__
from datetime import datetime


# This Example Operator will scale up the selected object
# ---- 创建纹理节点 ----
# def load_image_node(nodes,filepath,name, filename, location):
#     path = os.path.join(filepath, filename)
#     if not os.path.exists(path):
#         raise Exception(f"❌ 图片不存在: {path}")
#     node = nodes.new("ShaderNodeTexImage")
#     node.location = location
#     node.label = name
#     node.image = bpy.data.images.load(path)
#     node.image.colorspace_settings.name = 'sRGB'  # 默认sRGB, 根据需要调整
#     return node


class ExampleOperator(bpy.types.Operator):
    action: bpy.props.StringProperty()
    '''ExampleAddon'''
    bl_idname = "object.example_ops"
    bl_label = "ExampleOperator"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None

    def execute(self, context: bpy.types.Context):
        if self.action == "import":
            selected_objs = bpy.context.selected_objects
            if len(selected_objs) == 1:
                obj = bpy.context.active_object
                obj.data.materials.clear()
                material = bpy.data.materials.new(name="Alpha_Material_Advanced")
                material.use_nodes = True
                nodes = material.node_tree.nodes
                links = material.node_tree.links
                nodes.clear()
                blend_dir = os.path.dirname(bpy.data.filepath)
                # ---- 添加 Texture Coordinate 和 Mapping ----
                tex_coord = nodes.new("ShaderNodeTexCoord")
                tex_coord.location = (-1600, 0)
                mapping = nodes.new("ShaderNodeMapping")
                mapping.location = (-1400, 0)
                addon_prefs = context.preferences.addons[__addon_name__].preferences
                links.new(tex_coord.outputs["UV"], mapping.inputs["Vector"])  # 使用 UV 坐标
                # ---- 创建纹理节点函数 ----
                def load_image_node(name, filepath, location, non_color=False):
                    try:
                        path = os.path.join(addon_prefs.filepath, filepath)
                        if not os.path.exists(path):
                            print(f"⚠️ 图片未找到: {path}")
                            return None
                        node = nodes.new("ShaderNodeTexImage")
                        node.location = location
                        node.label = name
                        node.name = name
                        node.image = bpy.data.images.load(path)
                        node.image.colorspace_settings.name = 'Non-Color' if non_color else 'sRGB'
                        links.new(mapping.outputs["Vector"], node.inputs["Vector"])
                        return node
                    except Exception as e:
                        print(f"❌ 加载图片出错 [{name}]: {e}")
                        return None

                # ---- 加载图片 ----
                rgba_tex = load_image_node("RGBA", "rgba.tga", (-1000, 300), non_color=False)
                cucao_tex = load_image_node("CucaoJinshuYinying", "CucaoJinshuYinying.tga", (-1000, 0), non_color=True)
                zifaguang_tex = load_image_node("Zifaguang", "zifaguang.tga", (-1000, -300), non_color=False)
                faxian_tex = load_image_node("FaxianOpenGL", "faxianOpenGL.tga", (-1000, -600), non_color=True)

                # ---- 创建主材质节点 ----
                bsdf = nodes.new("ShaderNodeBsdfPrincipled")
                bsdf.location = (300, 0)

                output = nodes.new("ShaderNodeOutputMaterial")
                output.location = (600, 0)

                # ---- Alpha ----
                if rgba_tex:
                    links.new(rgba_tex.outputs["Alpha"], bsdf.inputs["Alpha"])

                # ---- Base Color (rgba RGB 和 cucao 的 B 通道混合) ----
                if rgba_tex and cucao_tex:
                    sep_cucao = nodes.new("ShaderNodeSeparateRGB")
                    sep_cucao.location = (-700, 50)
                    links.new(cucao_tex.outputs["Color"], sep_cucao.inputs["Image"])

                    mix_rgb = nodes.new("ShaderNodeMixRGB")
                    mix_rgb.location = (-300, 150)
                    mix_rgb.blend_type = 'MIX'
                    mix_rgb.inputs["Fac"].default_value = 0.01

                    links.new(rgba_tex.outputs["Color"], mix_rgb.inputs[1])      # Base Color
                    links.new(sep_cucao.outputs["B"], mix_rgb.inputs[2])         # Mask 灰度

                    links.new(mix_rgb.outputs["Color"], bsdf.inputs["Base Color"])

                    # Roughness / Metallic
                    links.new(sep_cucao.outputs["R"], bsdf.inputs["Roughness"])
                    links.new(sep_cucao.outputs["G"], bsdf.inputs["Metallic"])

                elif rgba_tex:
                    links.new(rgba_tex.outputs["Color"], bsdf.inputs["Base Color"])

                # ---- Emission Color ----
                if zifaguang_tex:
                    links.new(zifaguang_tex.outputs["Color"], bsdf.inputs["Emission Color"])
                    bsdf.inputs['Emission Strength'].default_value = 1.0
                else:
                    bsdf.inputs['Emission Strength'].default_value = 0.0

                # ---- Normal ----
                if faxian_tex:
                    normal_map = nodes.new("ShaderNodeNormalMap")
                    normal_map.location = (-400, -400)
                    links.new(faxian_tex.outputs["Color"], normal_map.inputs["Color"])
                    links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])

                # ---- Output ----
                links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

                # ---- 赋材质 ----
                obj.data.materials.append(material)
                print("✅ 材质创建完成。")

            # addon_prefs = bpy.context.preferences.addons[__addon_name__].preferences
            # assert isinstance(addon_prefs, ExampleAddonPreferences)
            # # use operator
            # # bpy.ops.transform.resize(value=(2, 2, 2))
            #
            # # manipulate the scale directly
            # context.active_object.location.x += addon_prefs.number
            #
        elif self.action == "export":
            selected_objs = bpy.context.selected_objects
            if len(selected_objs) == 1:
            # Substance Painter 可执行文件路径（确保路径正确）
            # sp_exe_path = r"C:\Program Files\Adobe\Adobe Substance 3D Painter\Adobe Substance 3D Painter.exe"
                paths = []
                if os.name == 'nt':
                    for letter in 'CDEFGHIJKLMNOPQRSTUVWXYZ':
                        paths.extend([
                            f'{letter}:\\Program Files\\Adobe\\Adobe Substance 3D Painter\\Adobe Substance 3D Painter.exe',
                            f'{letter}:\\Program Files (x86)\\Adobe\\Adobe Substance 3D Painter\\Adobe Substance 3D Painter.exe',
                            f'{letter}:\\Program Files\\Steam\\steamapps\\common\\Substance Painter\\Adobe Substance 3D Painter.exe'
                            f'{letter}:\\Program Files (x86)\\Steam\\steamapps\\common\\Substance Painter\\Adobe Substance 3D Painter.exe'
                            f'{letter}:\\Program Files\\Steam\\steamapps\\common\\Substance 3D Painter\\Adobe Substance 3D Painter.exe'
                            f'{letter}:\\Program Files (x86)\\Steam\\steamapps\\common\\Substance 3D Painter\\Adobe Substance 3D Painter.exe'
                        ])
                        for year in range(2020, 2027):
                            paths.extend([
                                f'{letter}:\\Program Files\\Adobe\\Adobe Substance 3D Painter {year}\\Adobe Substance 3D Painter.exe',
                                f'{letter}:\\Program Files (x86)\\Adobe\\Adobe Substance 3D Painter {year}\\Adobe Substance 3D Painter.exe',
                                f'{letter}:\\Program Files\\Steam\\steamapps\\common\\Substance Painter {year}\\Adobe Substance 3D Painter.exe'
                                f'{letter}:\\Program Files (x86)\\Steam\\steamapps\\common\\Substance Painter {year}\\Adobe Substance 3D Painter.exe'
                                f'{letter}:\\Program Files\\Steam\\steamapps\\common\\Substance 3D Painter {year}\\Adobe Substance 3D Painter.exe'
                                f'{letter}:\\Program Files (x86)\\Steam\\steamapps\\common\\Substance 3D Painter {year}\\Adobe Substance 3D Painter.exe'
                            ])
                else:
                    paths.extend([
                        f'/Applications/Adobe Substance 3D Painter.app/Contents/MacOS/Adobe Substance 3D Painter',
                        f'/Applications/Adobe Substance 3D Painter/Adobe Substance 3D Painter.app/Contents/MacOS/Adobe Substance 3D Painter',
                        f'~/Library/Application Support/Steam/steamapps/common/Substance 3D Painter/Adobe Substance 3D Painter.app/Contents/MacOS/Adobe Substance 3D Painter'
                    ])
                    for year in range(2020, 2027):
                        paths.extend([
                            f'/Applications/Adobe Substance 3D Painter {year}.app/Contents/MacOS/Adobe Substance 3D Painter',
                            f'/Applications/Adobe Substance 3D Painter/Adobe Substance 3D Painter {year}.app/Contents/MacOS/Adobe Substance 3D Painter',
                            f'~/Library/Application Support/Steam/steamapps/common/Substance 3D Painter {year}/Adobe Substance 3D Painter.app/Contents/MacOS/Adobe Substance 3D Painter'
                        ])
                for path in paths:
                    if os.path.exists(path):
                        print(f"找到 Substance Painter 安装路径：{path}")
                        sp_exe_path = path
                        break
                else:
                    raise Exception(f"❌ 未找到 Substance Painter 的安装路径。")
                # 导出目录
                addon_prefs = context.preferences.addons[__addon_name__].preferences
                sp_folder = addon_prefs.filepath
                os.makedirs(sp_folder, exist_ok=True)
                # FBX 文件路径
                fbx_filename = "huancunlaji.fbx"
                fbx_filepath = os.path.join(sp_folder, fbx_filename)
                # 导出选中对象为 FBX
                bpy.ops.export_scene.fbx(
                    filepath=fbx_filepath,
                    path_mode='COPY',        # 复制贴图文件
                    embed_textures=True,
                    use_selection=True,
                    axis_forward='-Z',
                    axis_up='Y',
                    apply_scale_options='FBX_SCALE_UNITS',
                    bake_space_transform=True
                )

                print(f"FBX 文件已导出到: {fbx_filepath}")

                # 使用 --mesh 参数打开 PT 并加载 FBX
                subprocess.Popen([
                    sp_exe_path,
                    '--mesh', fbx_filepath
                ])
        elif self.action == "exportup":
            selected_objs = bpy.context.selected_objects
            if len(selected_objs) == 1:
                # Substance Painter 可执行文件路径（确保路径正确）
                # sp_exe_path = r"C:\Program Files\Adobe\Adobe Substance 3D Painter\Adobe Substance 3D Painter.exe"
                paths = []
                if os.name == 'nt':
                    for letter in 'CDEFGHIJKLMNOPQRSTUVWXYZ':
                        paths.extend([
                            f'{letter}:\\Program Files\\Adobe\\Adobe Substance 3D Painter\\Adobe Substance 3D Painter.exe',
                            f'{letter}:\\Program Files (x86)\\Adobe\\Adobe Substance 3D Painter\\Adobe Substance 3D Painter.exe',
                            f'{letter}:\\Program Files\\Steam\\steamapps\\common\\Substance Painter\\Adobe Substance 3D Painter.exe'
                            f'{letter}:\\Program Files (x86)\\Steam\\steamapps\\common\\Substance Painter\\Adobe Substance 3D Painter.exe'
                            f'{letter}:\\Program Files\\Steam\\steamapps\\common\\Substance 3D Painter\\Adobe Substance 3D Painter.exe'
                            f'{letter}:\\Program Files (x86)\\Steam\\steamapps\\common\\Substance 3D Painter\\Adobe Substance 3D Painter.exe'
                        ])
                        for year in range(2020, 2027):
                            paths.extend([
                                f'{letter}:\\Program Files\\Adobe\\Adobe Substance 3D Painter {year}\\Adobe Substance 3D Painter.exe',
                                f'{letter}:\\Program Files (x86)\\Adobe\\Adobe Substance 3D Painter {year}\\Adobe Substance 3D Painter.exe',
                                f'{letter}:\\Program Files\\Steam\\steamapps\\common\\Substance Painter {year}\\Adobe Substance 3D Painter.exe'
                                f'{letter}:\\Program Files (x86)\\Steam\\steamapps\\common\\Substance Painter {year}\\Adobe Substance 3D Painter.exe'
                                f'{letter}:\\Program Files\\Steam\\steamapps\\common\\Substance 3D Painter {year}\\Adobe Substance 3D Painter.exe'
                                f'{letter}:\\Program Files (x86)\\Steam\\steamapps\\common\\Substance 3D Painter {year}\\Adobe Substance 3D Painter.exe'
                            ])
                else:
                    paths.extend([
                        f'/Applications/Adobe Substance 3D Painter.app/Contents/MacOS/Adobe Substance 3D Painter',
                        f'/Applications/Adobe Substance 3D Painter/Adobe Substance 3D Painter.app/Contents/MacOS/Adobe Substance 3D Painter',
                        f'~/Library/Application Support/Steam/steamapps/common/Substance 3D Painter/Adobe Substance 3D Painter.app/Contents/MacOS/Adobe Substance 3D Painter'
                    ])
                    for year in range(2020, 2027):
                        paths.extend([
                            f'/Applications/Adobe Substance 3D Painter {year}.app/Contents/MacOS/Adobe Substance 3D Painter',
                            f'/Applications/Adobe Substance 3D Painter/Adobe Substance 3D Painter {year}.app/Contents/MacOS/Adobe Substance 3D Painter',
                            f'~/Library/Application Support/Steam/steamapps/common/Substance 3D Painter {year}/Adobe Substance 3D Painter.app/Contents/MacOS/Adobe Substance 3D Painter'
                        ])
                for path in paths:
                    if os.path.exists(path):
                        print(f"找到 Substance Painter 安装路径：{path}")
                        sp_exe_path = path
                        break
                else:
                    raise Exception(f"❌ 未找到 Substance Painter 的安装路径。")
                # 导出目录
                addon_prefs = context.preferences.addons[__addon_name__].preferences
                sp_folder = addon_prefs.filepath
                os.makedirs(sp_folder, exist_ok=True)
                # FBX 文件路径
                fbx_filename = "huancunlaji.fbx"
                fbx_filepath = os.path.join(sp_folder, fbx_filename)
                # 导出选中对象为 FBX
                bpy.ops.export_scene.fbx(
                    filepath=fbx_filepath,
                    path_mode='COPY',        # 复制贴图文件
                    embed_textures=True,
                    use_selection=True,
                    axis_forward='-Z',
                    axis_up='Y',
                    apply_scale_options='FBX_SCALE_UNITS',
                    bake_space_transform=True,
                    global_scale=100.0
                )

                print(f"FBX 文件已导出到: {fbx_filepath}")

                # 使用 --mesh 参数打开 PT 并加载 FBX
                subprocess.Popen([
                    sp_exe_path,
                    '--mesh', fbx_filepath
                ])
        elif self.action == "exportdown":
            selected_objs = bpy.context.selected_objects
            if len(selected_objs) == 1:
                # Substance Painter 可执行文件路径（确保路径正确）
                # sp_exe_path = r"C:\Program Files\Adobe\Adobe Substance 3D Painter\Adobe Substance 3D Painter.exe"
                paths = []
                if os.name == 'nt':
                    for letter in 'CDEFGHIJKLMNOPQRSTUVWXYZ':
                        paths.extend([
                            f'{letter}:\\Program Files\\Adobe\\Adobe Substance 3D Painter\\Adobe Substance 3D Painter.exe',
                            f'{letter}:\\Program Files (x86)\\Adobe\\Adobe Substance 3D Painter\\Adobe Substance 3D Painter.exe',
                            f'{letter}:\\Program Files\\Steam\\steamapps\\common\\Substance Painter\\Adobe Substance 3D Painter.exe'
                            f'{letter}:\\Program Files (x86)\\Steam\\steamapps\\common\\Substance Painter\\Adobe Substance 3D Painter.exe'
                            f'{letter}:\\Program Files\\Steam\\steamapps\\common\\Substance 3D Painter\\Adobe Substance 3D Painter.exe'
                            f'{letter}:\\Program Files (x86)\\Steam\\steamapps\\common\\Substance 3D Painter\\Adobe Substance 3D Painter.exe'
                        ])
                        for year in range(2020, 2027):
                            paths.extend([
                                f'{letter}:\\Program Files\\Adobe\\Adobe Substance 3D Painter {year}\\Adobe Substance 3D Painter.exe',
                                f'{letter}:\\Program Files (x86)\\Adobe\\Adobe Substance 3D Painter {year}\\Adobe Substance 3D Painter.exe',
                                f'{letter}:\\Program Files\\Steam\\steamapps\\common\\Substance Painter {year}\\Adobe Substance 3D Painter.exe'
                                f'{letter}:\\Program Files (x86)\\Steam\\steamapps\\common\\Substance Painter {year}\\Adobe Substance 3D Painter.exe'
                                f'{letter}:\\Program Files\\Steam\\steamapps\\common\\Substance 3D Painter {year}\\Adobe Substance 3D Painter.exe'
                                f'{letter}:\\Program Files (x86)\\Steam\\steamapps\\common\\Substance 3D Painter {year}\\Adobe Substance 3D Painter.exe'
                            ])
                else:
                    paths.extend([
                        f'/Applications/Adobe Substance 3D Painter.app/Contents/MacOS/Adobe Substance 3D Painter',
                        f'/Applications/Adobe Substance 3D Painter/Adobe Substance 3D Painter.app/Contents/MacOS/Adobe Substance 3D Painter',
                        f'~/Library/Application Support/Steam/steamapps/common/Substance 3D Painter/Adobe Substance 3D Painter.app/Contents/MacOS/Adobe Substance 3D Painter'
                    ])
                    for year in range(2020, 2027):
                        paths.extend([
                            f'/Applications/Adobe Substance 3D Painter {year}.app/Contents/MacOS/Adobe Substance 3D Painter',
                            f'/Applications/Adobe Substance 3D Painter/Adobe Substance 3D Painter {year}.app/Contents/MacOS/Adobe Substance 3D Painter',
                            f'~/Library/Application Support/Steam/steamapps/common/Substance 3D Painter {year}/Adobe Substance 3D Painter.app/Contents/MacOS/Adobe Substance 3D Painter'
                        ])
                for path in paths:
                    if os.path.exists(path):
                        print(f"找到 Substance Painter 安装路径：{path}")
                        sp_exe_path = path
                        break
                else:
                    raise Exception(f"❌ 未找到 Substance Painter 的安装路径。")
                # 导出目录
                addon_prefs = context.preferences.addons[__addon_name__].preferences
                sp_folder = addon_prefs.filepath
                os.makedirs(sp_folder, exist_ok=True)
                # FBX 文件路径
                fbx_filename = "huancunlaji.fbx"
                fbx_filepath = os.path.join(sp_folder, fbx_filename)
                # 导出选中对象为 FBX
                bpy.ops.export_scene.fbx(
                    filepath=fbx_filepath,
                    path_mode='COPY',        # 复制贴图文件
                    embed_textures=True,
                    use_selection=True,
                    axis_forward='-Z',
                    axis_up='Y',
                    apply_scale_options='FBX_SCALE_UNITS',
                    bake_space_transform=True,
                    global_scale=0.01
                )

                print(f"FBX 文件已导出到: {fbx_filepath}")

                # 使用 --mesh 参数打开 PT 并加载 FBX
                subprocess.Popen([
                    sp_exe_path,
                    '--mesh', fbx_filepath
                ])
        elif self.action == "clear":
            # 清空历史材质
            bpy.ops.outliner.orphans_purge(do_recursive=True)
        elif self.action == "exportfbx":
            doubi = context.preferences.addons[__addon_name__].preferences
            hanhan = True
            try:
                # 你原本骨骼的名字，比如 Rig 集合下第一个骨骼
                orig_bone_name = None
                # 找 Rig 集合第一个骨骼
                rig_collection = bpy.data.collections.get("Rig")
                if not rig_collection:
                    raise Exception("找不到 Rig 集合")
                armature_obj = None
                for obj in rig_collection.all_objects:
                    if obj.type == 'ARMATURE':
                        armature_obj = obj
                        break
                if not armature_obj:
                    raise Exception("Rig集合中没有骨骼对象")
                orig_bone_name = armature_obj.name
                # 临时重命名
                armature_obj.name = "Armature"
            except:
                hanhan = False


            # 清空当前选择
            bpy.ops.object.select_all(action='DESELECT')
            # 选中 Mesh 集合所有 Mesh
            mesh_collection = bpy.data.collections.get("Mesh")
            if not mesh_collection:
                raise Exception("找不到 Mesh 集合")
            for obj in mesh_collection.all_objects:
                if obj.type == 'MESH':
                    obj.select_set(True)
            if hanhan:
                # 选中刚才临时重命名的骨骼
                armature_obj.select_set(True)
            if not bpy.context.selected_objects:
                raise Exception("没有选中任何对象")
            # 导出路径
            # 院士路径
            addon_prefs = context.preferences.addons[__addon_name__].preferences
            sp_folder = addon_prefs.filepath
            # 获取当前时间，格式为 MMDDHHMM
            time_str = datetime.now().strftime("%m%d%H%M")
            # 文件名（你可以自定义）
            if not doubi.mystring:
                doubi.mystring = "demo"
            if doubi.boolean:
                filename = f"{time_str}-"+doubi.mystring
            else:
                filename = doubi.mystring
            # 拼接路径
            output_path = os.path.join(sp_folder, filename+".fbx")
            # 替换为 Blender 风格路径（正斜杠）
            output_path = output_path.replace("\\", "/")

            # 设置单位为厘米
            bpy.context.scene.unit_settings.system = 'METRIC'
            bpy.context.scene.unit_settings.scale_length = 0.01  # 1单位 = 1厘米
            # 导出FBX
            bpy.ops.export_scene.fbx(
                filepath=output_path,
                use_selection=True,
                global_scale=1,
                apply_unit_scale=True,
                apply_scale_options='FBX_SCALE_ALL',
                bake_space_transform=False,
                object_types={'MESH', 'ARMATURE', 'EMPTY'},
                use_mesh_modifiers=True,
                mesh_smooth_type='EDGE',
                add_leaf_bones=False,
                path_mode='COPY',
                embed_textures=False,
                axis_forward='-Z',
                axis_up='Y',
                bake_anim_force_startend_keying=True,
                bake_anim_use_all_actions=False
            )
            print(f"FBX导出完成: {output_path}")
            if hanhan:
                # 还原骨骼名字
                armature_obj.name = orig_bone_name
        elif self.action == "debuff1":
            def auto_retopo_decimate_collection(high_collection_name="h", low_collection_name="l", target_faces_min=5000, target_faces_max=50000):
                high_col = bpy.data.collections.get(high_collection_name)
                if high_col is None:
                    print(f"❌ 未找到集合: {high_collection_name}")
                    return
                # 创建或获取 Low 集合
                low_col = bpy.data.collections.get(low_collection_name)
                if low_col is None:
                    low_col = bpy.data.collections.new(low_collection_name)
                    bpy.context.scene.collection.children.link(low_col)
                for obj in high_col.objects:
                    if obj.type != 'MESH':
                        continue
                    # 复制对象（深拷贝）
                    new_obj = obj.copy()
                    new_obj.data = obj.data.copy()
                    new_obj.name = f"{obj.name}_low"
                    new_obj.parent = None
                    # 移除复制体从 High 集合中（重要）
                    for col in new_obj.users_collection:
                        col.objects.unlink(new_obj)
                    # 加入 Low 集合
                    low_col.objects.link(new_obj)
                    # 设置为活动对象
                    bpy.ops.object.select_all(action='DESELECT')
                    new_obj.select_set(True)
                    bpy.context.view_layer.objects.active = new_obj
                    # 应用变换
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                    # 获取面数
                    original_faces = len(new_obj.data.polygons)
                    target_faces = int((target_faces_min + target_faces_max) / 2)
                    ratio = target_faces / original_faces
                    ratio = max(min(ratio, 1.0), 0.01)
                    print(f"🔄 正在处理: {new_obj.name}, 原始面数: {original_faces}, 目标: {target_faces}, 比例: {ratio:.4f}")
                    # 添加 Decimate 修改器
                    decimate_mod = new_obj.modifiers.new(name="AutoDecimate", type='DECIMATE')
                    decimate_mod.ratio = ratio
                    decimate_mod.use_collapse_triangulate = False
                    # 应用修改器
                    bpy.ops.object.modifier_apply(modifier=decimate_mod.name)
                    # 打印结果
                    new_faces = len(new_obj.data.polygons)
                    print(f"✅ {new_obj.name} 重拓扑完成，当前面数: {new_faces}")
                print("🎉 所有 High 集合对象已保留，Low 集合中已生成重拓扑副本。")
                bpy.context.view_layer.layer_collection.children['h'].hide_viewport = True
            # 执行
            auto_retopo_decimate_collection("h", "l", 5000, 50000)
        elif self.action == "debuff2":
            def auto_retopo_and_assign_material(
                    high_collection_name="h",
                    low_collection_name="l",
                    target_faces_min=5000,
                    target_faces_max=50000,
                    texture_size=1024
            ):
                high_col = bpy.data.collections.get(high_collection_name)
                if high_col is None:
                    print(f"❌ 未找到集合: {high_collection_name}")
                    return

                # 创建或获取 Low 集合
                low_col = bpy.data.collections.get(low_collection_name)
                if low_col is None:
                    low_col = bpy.data.collections.new(low_collection_name)
                    bpy.context.scene.collection.children.link(low_col)

                for obj in high_col.objects:
                    if obj.type != 'MESH':
                        continue

                    # 复制对象（深拷贝）
                    new_obj = obj.copy()
                    new_obj.data = obj.data.copy()
                    new_obj.name = f"{obj.name}_low"
                    new_obj.parent = None

                    # 移除复制体从所有集合中
                    for col in new_obj.users_collection:
                        col.objects.unlink(new_obj)

                    # 加入 Low 集合
                    low_col.objects.link(new_obj)

                    # 设置为活动对象
                    bpy.ops.object.select_all(action='DESELECT')
                    new_obj.select_set(True)
                    bpy.context.view_layer.objects.active = new_obj

                    # 应用变换
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

                    # 计算目标面数和比例
                    original_faces = len(new_obj.data.polygons)
                    target_faces = int((target_faces_min + target_faces_max) / 2)
                    ratio = target_faces / original_faces
                    ratio = max(min(ratio, 1.0), 0.01)

                    print(f"🔄 正在处理: {new_obj.name}, 原始面数: {original_faces}, 目标: {target_faces}, 比例: {ratio:.4f}")

                    # 添加 Decimate 修改器
                    decimate_mod = new_obj.modifiers.new(name="AutoDecimate", type='DECIMATE')
                    decimate_mod.ratio = ratio
                    decimate_mod.use_collapse_triangulate = False

                    # 应用修改器
                    bpy.ops.object.modifier_apply(modifier=decimate_mod.name)

                    # 打印结果
                    new_faces = len(new_obj.data.polygons)
                    print(f"✅ {new_obj.name} 重拓扑完成，当前面数: {new_faces}")

                    # ✳️ 清空材质槽并添加新材质
                    new_obj.data.materials.clear()
                    mat = bpy.data.materials.new(name=f"{new_obj.name}_Material")
                    mat.use_nodes = True
                    new_obj.data.materials.append(mat)

                    # 获取节点树
                    nodes = mat.node_tree.nodes
                    links = mat.node_tree.links
                    nodes.clear()

                    # 创建 1024x1024 图像
                    img = bpy.data.images.new(name=f"{new_obj.name}_Texture", width=texture_size, height=texture_size, alpha=True)
                    print(f"🖼️ 创建图像: {img.name}")

                    # 创建节点结构
                    tex_node = nodes.new(type='ShaderNodeTexImage')
                    tex_node.image = img
                    tex_node.location = (-600, 0)

                    bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
                    bsdf_node.location = (-200, 0)

                    output_node = nodes.new(type='ShaderNodeOutputMaterial')
                    output_node.location = (200, 0)

                    links.new(tex_node.outputs['Color'], bsdf_node.inputs['Base Color'])
                    links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

                    print(f"✅ {new_obj.name} 材质设置完毕（统一结构）")

                print("🎉 所有 High 集合对象已重拓扑并生成统一材质低模副本。")
                bpy.context.view_layer.layer_collection.children[high_collection_name].hide_viewport = True

            # 执行
            auto_retopo_and_assign_material("h", "l", 5000, 50000)

        elif self.action == "debuff3":
            # 1. 获取活动对象
            active_obj = bpy.context.active_object
            if not active_obj:
                raise Exception("没有活动对象")

            # 2. 复制原材质节点树
            original_material = active_obj.active_material

            # 创建一个新的材质
            new_mat = bpy.data.materials.new(name="BakedMaterial")
            new_mat.use_nodes = True
            nodes = new_mat.node_tree.nodes
            links = new_mat.node_tree.links

            # 清空节点
            nodes.clear()

            # 3. 添加 Principled BSDF, 材质输出 和 图像纹理节点
            output_node = nodes.new(type='ShaderNodeOutputMaterial')
            output_node.location = (400, 0)

            bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
            bsdf_node.location = (0, 0)

            tex_image_node = nodes.new(type='ShaderNodeTexImage')
            tex_image_node.location = (-400, 0)

            # 创建新的图像纹理
            baked_image = bpy.data.images.new("BakedTexture", width=1024, height=1024, alpha=True)
            tex_image_node.image = baked_image

            # 连接节点
            links.new(tex_image_node.outputs['Color'], bsdf_node.inputs['Base Color'])
            links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

            # 4. 清除旧材质槽并赋予新材质
            active_obj.data.materials.clear()
            active_obj.data.materials.append(new_mat)

            # 5. 选择要烘焙的对象（除了活动对象）
            for obj in bpy.context.selected_objects:
                if obj != active_obj:
                    obj.select_set(True)
                else:
                    obj.select_set(True)  # 保证活动对象选中
                    bpy.context.view_layer.objects.active = active_obj

            # 6. 设置 Bake 参数
            bpy.context.scene.render.engine = 'CYCLES'
            bpy.context.scene.cycles.bake_type = 'DIFFUSE'

            # 关闭直接光和间接光，只保留颜色
            bpy.context.scene.render.bake.use_pass_direct = False
            bpy.context.scene.render.bake.use_pass_indirect = False
            bpy.context.scene.render.bake.use_pass_color = True
            bpy.context.scene.render.bake.margin = 16  # 防止缝隙，可以按需调整
            bpy.context.scene.render.bake.cage_extrusion = 0.1
            bpy.context.scene.render.bake.use_selected_to_active = True

            # 7. 选中贴图节点
            tex_image_node.select = True
            nodes.active = tex_image_node

            # 8. 执行烘焙
            bpy.ops.object.bake(type='DIFFUSE')

            # 9. 隐藏
            bpy.context.view_layer.layer_collection.children['h'].hide_viewport = True
            # 10. 保存烘焙结果图像到指定路径
            addon_prefs = context.preferences.addons[__addon_name__].preferences
            sp_folder = addon_prefs.filepath

            save_path = os.path.join(sp_folder, "manshe.png")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            baked_image.filepath_raw = save_path
            baked_image.file_format = 'PNG'
            baked_image.save()

            print(f"✅ 已保存烘焙贴图到: {save_path}")

        elif self.action == "debuff4":
            # 1. 获取活动对象
            active_obj = bpy.context.active_object
            if not active_obj:
                raise Exception("没有活动对象")

            # 2. 复制原材质节点树
            original_material = active_obj.active_material

            # 创建一个新的材质
            new_mat = bpy.data.materials.new(name="BakedMaterial")
            new_mat.use_nodes = True
            nodes = new_mat.node_tree.nodes
            links = new_mat.node_tree.links

            # 清空节点
            nodes.clear()

            # 3. 添加 Principled BSDF, 材质输出 和 图像纹理节点
            output_node = nodes.new(type='ShaderNodeOutputMaterial')
            output_node.location = (400, 0)

            bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
            bsdf_node.location = (0, 0)

            tex_image_node = nodes.new(type='ShaderNodeTexImage')
            tex_image_node.location = (-400, 0)

            # 创建新的图像纹理
            baked_image = bpy.data.images.new("BakedTexture", width=1024, height=1024, alpha=True)
            tex_image_node.image = baked_image

            # 连接节点
            links.new(tex_image_node.outputs['Color'], bsdf_node.inputs['Base Color'])
            links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

            # 4. 清除旧材质槽并赋予新材质
            active_obj.data.materials.clear()
            active_obj.data.materials.append(new_mat)

            # 5. 选择要烘焙的对象（除了活动对象）
            for obj in bpy.context.selected_objects:
                if obj != active_obj:
                    obj.select_set(True)
                else:
                    obj.select_set(True)  # 保证活动对象选中
                    bpy.context.view_layer.objects.active = active_obj

            cage_obj = bpy.context.scene.wrapper_object
            print(888)
            print(cage_obj.name)

            # 6. 设置 Bake 参数
            bpy.context.scene.render.engine = 'CYCLES'
            bpy.context.scene.cycles.bake_type = 'DIFFUSE'

            # 关闭直接光和间接光，只保留颜色
            bpy.context.scene.render.bake.use_pass_direct = False
            bpy.context.scene.render.bake.use_pass_indirect = False
            bpy.context.scene.render.bake.use_pass_color = True
            bpy.context.scene.render.bake.margin = 16  # 防止缝隙，可以按需调整
            bpy.context.scene.render.bake.use_selected_to_active = True
            bpy.context.scene.render.bake.use_cage = True  # 启用 Cage 烘焙
            bpy.context.scene.render.bake.cage_object = cage_obj  # 设置包裹器名称
            bpy.context.scene.render.bake.cage_extrusion = 0.01

            # 7. 选中贴图节点
            tex_image_node.select = True
            nodes.active = tex_image_node

            # 8. 执行烘焙
            bpy.ops.object.bake(type='DIFFUSE')

            # 9. 隐藏
            bpy.context.view_layer.layer_collection.children['h'].hide_viewport = True
            # 10. 保存烘焙结果图像到指定路径
            addon_prefs = context.preferences.addons[__addon_name__].preferences
            sp_folder = addon_prefs.filepath

            save_path = os.path.join(sp_folder, "manshe.png")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            baked_image.filepath_raw = save_path
            baked_image.file_format = 'PNG'
            baked_image.save()

            print(f"✅ 已保存烘焙贴图到: {save_path}")

        return {'FINISHED'}
