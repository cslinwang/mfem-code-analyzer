#!/bin/bash
# 覆盖率增加脚本

# 进入mfem项目目录
cd /root/mfem

# 替换makefile文件，确保使用tab进行缩进
sed -i 's|MFEM_BUILD_FLAGS = $(MFEM_PICFLAG) $(MFEM_CPPFLAGS) $(MFEM_CXXFLAGS)\\|CXXFLAGS += -fprofile-arcs -ftest-coverage\nLDFLAGS += -lgcov\n\nMFEM_BUILD_FLAGS = $(MFEM_PICFLAG) $(MFEM_CPPFLAGS) $(MFEM_CXXFLAGS) $(CXXFLAGS)\\\|' makefile
sed -i 's|$(MFEM_CXX) $(MFEM_BUILD_FLAGS) -c $(<) -o $(@)|\t$(MFEM_CXX) $(MFEM_BUILD_FLAGS) -c $(<) -o $(@) $(LDFLAGS)|' makefile

# 进入examples目录
cd /root/mfem/examples

# 替换examples中的makefile文件，确保使用tab进行缩进
sed -i 's|%: $(SRC)%.cpp $(MFEM_LIB_FILE) $(CONFIG_MK)|CXXFLAGS += -fprofile-arcs -ftest-coverage\nLDFLAGS += -lgcov\n\n&|' makefile
sed -i 's|$(MFEM_CXX) $(MFEM_FLAGS) $< -o $@ $(MFEM_LIBS)|\t$(MFEM_CXX) $(MFEM_FLAGS) $(CXXFLAGS) $< -o $@ $(MFEM_LIBS) $(LDFLAGS)|' makefile

echo "替换完成。"
