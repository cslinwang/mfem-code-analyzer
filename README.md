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
