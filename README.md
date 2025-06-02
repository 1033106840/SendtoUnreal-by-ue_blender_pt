# ue_blender_pt
## quick connect UE,blender,pt(sp)
## 快速桥接ue,blender,sp简化游戏开发步骤

# environment(稳定环境)
### blender4.3
### ue4.26
### Adobe Substance 3D Painter2020+

# 使用说明
## blender和pt交互(opengl坐标系)
1安装插件导入高模
![image](https://github.com/user-attachments/assets/3e9ab6d7-bd6d-44c1-8624-89eece86cd6a)
2选择资源文件夹
![image](https://github.com/user-attachments/assets/7ee3cea2-02b8-466c-b54f-7122f76036c6)
3将需要减面的高模拖入h集合点击重拓扑
![image](https://github.com/user-attachments/assets/a8c94c44-5544-4dbf-9ed0-89acae37f19d)
4烘焙高模复杂贴图(自动生成材质槽可以点击清理)
![image](https://github.com/user-attachments/assets/a4083b78-84df-4e5e-bde2-7f264d476358)
5选中低模点击cm->m自动打开pt进行二次烘焙
![image](https://github.com/user-attachments/assets/09616ef6-85dd-4df2-ab1d-e9ee9d74d45f)
6拖入刚才烘焙的基础色
![image](https://github.com/user-attachments/assets/b0550657-50c6-426b-ac25-e89810eba7f0)
7选择高模烘焙
![image](https://github.com/user-attachments/assets/72413229-a085-4456-9571-990833137306)
8pt给材质上色
![image](https://github.com/user-attachments/assets/8180ad70-238c-4456-ac39-4b7e57f71a79)
9设置ue专用tga模板
![image](https://github.com/user-attachments/assets/42403ed0-e387-4808-a9af-0b86bd70c22b)
10选择资源位置和模板点击导出
![image](https://github.com/user-attachments/assets/4b95183f-c38d-4da2-b459-e4f1fdb8245f)
11blender导入pt材质(生成的tga游戏材质)
![image](https://github.com/user-attachments/assets/943f2803-c61a-4a04-90f3-fa0a2215981c)

## blender和ue交互(directx坐标系)
1将模型拖入Mesh集合(必须是绑定这个骨骼的Mesh集合)，将骨骼拖入Rig集合(没有可以不选)
![image](https://github.com/user-attachments/assets/3d958f08-be5a-439e-920e-1d3c3b338394)
2ue中拖入插件blender.uasset
![image](https://github.com/user-attachments/assets/557abd6d-2d78-4ad9-a6d9-e9c7c2351828)
3ue中一键导入模型以及材质
![image](https://github.com/user-attachments/assets/2e13f302-d16f-46fe-b09b-ede21297f199)






