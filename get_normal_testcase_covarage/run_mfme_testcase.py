# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import yaml


class MFEMIssueProcessor:
    def __init__(self, is_get_normal_testcase=False):
        # 通过设置这个值来指定是否为把所有测试用例都复制到bugs文件夹下
        self.is_get_normal_testcase = is_get_normal_testcase
        # 配置文件路径相关
        self.pre_filepath()

    def pre_filepath(self):
        self.root_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), ".."))
        self.bugs_path = os.path.join(self.root_path, "bugs")
        self.bugs_yaml_path = os.path.join(self.bugs_path, "bugs.yaml")
        self.mfem_path = os.path.abspath(os.path.join(self.root_path, "..", "mfem"))

    def process_mfem_issue(self, issue_data):
        name = issue_data.get("name", "")
        bug_sha = issue_data.get("bug_sha", "")
        fix_sha = issue_data.get("fix_sha", "")
        testcase = issue_data.get("testcase", "")
        url = issue_data.get("url", "")

        # 根据issue_name 定位测试用例文件位置

        # 根据testcase 定位文件位置
        # 你可以在这里添加进一步的逻辑来处理文件位置

        # 根据test_case是否为空来判断是否为正常的issue
        # 在这里执行其他操作，例如打印或处理数据
        print("---------------------------")
        print(f"Name: {name}")
        print(f"Bug SHA: {bug_sha}")
        print(f"Fix SHA: {fix_sha}")
        print(f"Test Case: {testcase}")
        print(f"URL: {url}")
        print("---------------------------")

    def process_yaml_file(self):
        try:
            with open(self.bugs_yaml_path, 'r') as file:
                data = yaml.safe_load(file)
        except FileNotFoundError:
            print(f"YAML 文件 '{self.bugs_yaml_path}' 未找到")
            return
        except yaml.YAMLError as e:
            print(f"YAML 文件解析错误: {e}")
            return

        # 遍历每个mfem issue部分并处理
        for issue_name, issue_data in data.items():
            if issue_name.startswith("mfem issue"):
                print(f"Processing {issue_name}")
                if self.is_get_normal_testcase:
                    # 提取测试用例
                    self.pre_issue_file(issue_name, issue_data)
                # 将issue_name和issue_data传递给process_mfem_issue函数
                self.process_mfem_issue(issue_data)

    def pre_issue_file(self, issue_name, issue_data):
        # 获取Git SHA for fix
        fix_sha = issue_data.get("fix_sha", "")
        self.switch_version(fix_sha)

        # 获取测试用例路径
        testcase_path = issue_data.get("testcase", "")
        if not testcase_path:
            print(f"Test case path is not specified for {issue_name}")
            return

        # 创建目标文件夹
        name = issue_data.get("name", "")
        target_path = os.path.join(self.bugs_path, name,testcase_path.split("/")[-1])

        # 检查源文件是否存在
        if not os.path.exists(testcase_path):
            print(f"Source file {testcase_path} does not exist.")
            return

        # 创建目标目录，如果不存在
        try:
            print(f"Target directory: {os.path.dirname(target_path)}")
            if not os.path.exists(os.path.dirname(target_path)):
                os.makedirs(os.path.dirname(target_path))
        except PermissionError:
            print(f"Permission denied: Could not create directory {os.path.dirname(target_path)}")
        except Exception as e:
            print(f"An error occurred while creating the directory: {e}")

        # 复制文件
        try:
            shutil.copy(testcase_path, target_path)
            print(f"Copied {testcase_path} to {target_path}")
        except Exception as e:
            print(f"An error occurred while copying the file: {e}")

        return 0

    # 切换版本
    def switch_version(self, sha):
        if sha:
            try:
                # 确保在Git仓库的根目录中
                os.chdir(self.mfem_path)

                # 切换到master分支
                subprocess.check_call(["git", "checkout", "master"])

                # 重置所有更改到上一个提交
                subprocess.check_call(["git", "reset", "--hard", "HEAD"])

                # 删除所有未跟踪文件
                subprocess.check_call(["git", "clean", "-fd"])

                # 从完整的SHA生成短SHA
                short_sha = sha[:7]
                branch_name = f"branch_{short_sha}"

                # 首先尝试删除旧分支（如果存在）
                try:
                    subprocess.check_call(["git", "branch", "-D", branch_name])
                    print(f"Deleted old branch {branch_name}")
                except subprocess.CalledProcessError:
                    print(f"No existing branch named {branch_name}, continue...")

                # 检出新的分支
                subprocess.check_call(["git", "checkout", "-b", branch_name, sha])
                print(f"Switched to new branch {branch_name} at {sha}")

            except subprocess.CalledProcessError as e:
                print(f"Failed to checkout to {sha}: {e}")
                return
            except Exception as e:
                print(f"An error occurred while switching the git version: {e}")
                return

if __name__ == "__main__":
    processor = MFEMIssueProcessor(is_get_normal_testcase=True)
    processor.process_yaml_file()
