# MFEM Code Analyzer

## 项目结构说明

- mfem-code-analyzer
  - bugs
    - bugs.yaml 报错所有bug的信息
    - issue3804 测试用例对应issue
      - test_psubmesh.cpp 测试用例文件

  - get_normal_testcase_coverage 获取测试用例覆盖率
    - complete_mfem.sh 编译脚本
    - run_mfem_testcase.py 读取bugs.yaml，运行测试用例

## 测试说明

### 测试用例

mfem issue3840:
  bug sha: 86ec2bfa8d4b38f06f8699ddd853f785f19aec91
  修复sha: 8a9ca138551bb0b3668da6a40cd636985f21039e
  testcase: tests/unit/mesh/test_psubmesh.cpp
  url: https://github.com/mfem/mfem/commit/8a9ca138551bb0b3668da6a40cd636985f21039e

### 复现分析

每个测试用例都是位于原先的tests文件下的CPP，因此可以考虑：

将每个测试用例的修复版本放到指定文件夹下，即bugs。后续直接读取。

- bug的文件夹名字是bugsha-fixsha。

### 如何运行

记得先清空所有git无效文件

```

git clean -fd

```

#### 覆盖率

```

# 添加覆盖率标志

CXXFLAGS += -fprofile-arcs -ftest-coverage

LDFLAGS += -lgcov

# Replace the default implicit rule for *.cpp files

%: $(SRC)%.cpp $(MFEM_LIB_FILE) $(CONFIG_MK)

    $(MFEM_CXX) $(MFEM_FLAGS) $(CXXFLAGS) $< -o $@ $(MFEM_LIBS) $(LDFLAGS)



    @find . -type f -name '*.gcno' -delete

    @find . -type f -name '*.gcda' -delete

```


如何运行单个测试用例

```
export OMPI_ALLOW_RUN_AS_ROOT=1
export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1

# 先编译全部

cd mefm

make all -j

# 如果需要重新编译

cd mfem/examples

# 并行
make ex0p
mpirun -np 24 ./ex0p
mpirun -np 3 ex6p -m /root/mfem-code-analyzer/bugs/issue3691/p1_prism.msh -o 2 -h1

# 串行

make ex0
./ex0

# 收集覆盖率

fastcov --gcov gcov --exclude /usr/include --include /root/mfem coverage.json
fastcov --lcov -o coverage.info
genhtml coverage.info --output-directory coverage_report

```

## BUG复现命令

### issue 3691

fix sha:a15866e212b167ab83d5384e7326cdd3fa0723b2
reset current branch to previous commit,hard reset
cd ~
cd mfem
make clean
make all -j
cd examples
mpirun -np 24 ex6p -m /root/mfem-code-analyzer/bugs/issue3691/p1_prism.msh -o 2

### issue 2884
(未复现) 编译就过不去。 修复版本编译也过不去。
url: https://github.com/mfem/mfem/issues/2884
修改test_pa_coeff.cpp中的测试用例Hcurl/Hdiv pa_coeff的299行的if语句为：mesh = Mesh::LoadFromFile("/root/mfem/data/star.mesh");
fix sha: 987d2e043bad3a99841b88354dce0c0932cb8642
cd ~
cd mfem
make clean
make unittest -j
cd tests/unit
./unit_tests --list-test-names-only
./unit_tests "Hcurl/Hdiv pa_coeff"

### issue 2878

url: https://github.com/mfem/mfem/issues/2878
bug sha:使用的是50cd7da165999d4c65a6875a24c39317acaa2c3e
修改ex3p.cpp中204行a->AddDomainIntegrator(new VectorFEMassIntegrator(*sigma)); 为：
a->AddDomainIntegrator(new VectorFEMassIntegrator(*sigma));
a->AddBoundaryIntegrator(new VectorFEMassIntegrator(*sigma));

fix sha: a4504c3c083e8d13c89c0cf72f8eb36ef3aed642
cd ~
cd mfem
make clean
make all -j
cd examples
mpirun -np 5 ex3p -m /root/mfem/data/beam-tet.mesh -o 1

### issue 2666

url: https://github.com/mfem/mfem/issues/2666
作者可以在以下两个版本复现0843a87d7953cf23e556dcfd426d27bd9cfb3e21，9d8043b9e78dcdcd86639bbb28d3bd7b514fb5e2(这个编译不过去，这个是V4.3),我不行呜呜。修复版本跑了没问题，没复现出bug
cd mfem
make clean
make all -j
cd examples
mpirun -np 2 ex15p -m /root/mfem/data/escher.mesh -r 2 -tf 0.3 -est 1

