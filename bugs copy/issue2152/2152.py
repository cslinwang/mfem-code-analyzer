from mfem import ser as mfem

# 创建一个简单的二维网格
mesh = mfem.Mesh(2, 3, mfem.Element.Type.QUADRILATERAL, 0, 1.0, 1.0)

# 保存网格到文件
mesh_file = 'simple_2d_mesh.mesh'
mesh.Print(mesh_file)
