# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import yaml
import logging
import sys
import logging
import sys
import os

# 设定日志文件的路径
log_file_path = os.path.join('/root/mfem/mfem-code-analyzer/get_normal_testcase_covarage', 'log.log')
info_log_file_path = os.path.join('/root/mfem/mfem-code-analyzer/get_normal_testcase_covarage', 'info.log')

# 如果文件存在，则移除
if os.path.exists(log_file_path):
    os.remove(log_file_path)
if os.path.exists(info_log_file_path):
    os.remove(info_log_file_path)

# 创建logger
logger = logging.getLogger('my_application')
logger.setLevel(logging.DEBUG)  # 捕获所有级别的日志
logger.handlers.clear()  # 清除旧的处理器

# 创建文件处理器并设置级别
all_levels_handler = logging.FileHandler(log_file_path)
all_levels_handler.setLevel(logging.DEBUG)

info_handler = logging.FileHandler(info_log_file_path)
info_handler.setLevel(logging.INFO)

# 创建日志格式器并设置给处理器
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
all_levels_handler.setFormatter(formatter)
info_handler.setFormatter(formatter)

# 添加处理器到logger
logger.addHandler(all_levels_handler)
logger.addHandler(info_handler)

# StreamToLogger类
class StreamToLogger(object):
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

# 重定向stdout和stderr到日志
sys.stdout = StreamToLogger(logger, logging.DEBUG)  # 注意这里改成了DEBUG
sys.stderr = StreamToLogger(logger, logging.ERROR)

# 测试日志输出
logger.info("这是一条INFO级别的日志")
logger.debug("这是一条DEBUG级别的日志")


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
        self.mfem_path = os.path.abspath(
            os.path.join(self.root_path, "..", "mfem"))

    def process_mfem_issue(self, issue_data):
        logger.info(f"Processing issue: {issue_data}")
        name = issue_data.get("name", "")
        bug_sha = issue_data.get("bug_sha", "").split(",")[0]
        fix_sha = issue_data.get("fix_sha", "")
        testcase = issue_data.get("testcase", "")
        testname = issue_data.get("testname", "")
        url = issue_data.get("url", "")

        # 根据issue_name 定位测试用例文件位置

        # 根据testcase 定位文件位置
        # 你可以在这里添加进一步的逻辑来处理文件位置

        # 根据test_case是否为空来判断是否为正常的issue
        self.copy_testcase(name, testcase)
        # 运行bug版本
        logger.info(f"Running bug version: {bug_sha}")
        self.switch_version(bug_sha)
        self.copy_testcase(name, testcase)
        self.compile_mfem()
        testnames=testname.split(",")
        for testname in testnames:
            self.run_unit_test(testname)

        logger.info(f"Running fix version: {fix_sha}")
        # 运行修复版本
        print("Processing issue:")
        self.switch_version(fix_sha)
        self.compile_mfem()
        for testname in testnames:
            self.run_unit_test(testname)

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
        target_path = os.path.join(
            self.bugs_path, name, testcase_path.split("/")[-1])

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
            print(
                f"Permission denied: Could not create directory {os.path.dirname(target_path)}")
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

                # 重置所有更改到上一个提交
                subprocess.check_call(["git", "reset", "--hard", "HEAD"])

                # 删除所有未跟踪文件
                subprocess.check_call(["git", "clean", "-fd"])

                 # 切换到master分支
                subprocess.check_call(["git", "checkout", "master"])

                # 从完整的SHA生成短SHA
                short_sha = sha[:7]
                branch_name = f"branch_{short_sha}"

                # 首先尝试删除旧分支（如果存在）
                try:
                    subprocess.check_call(["git", "branch", "-D", branch_name])
                    print(f"Deleted old branch {branch_name}")
                except subprocess.CalledProcessError:
                    print(
                        f"No existing branch named {branch_name}, continue...")

                # 检出新的分支
                subprocess.check_call(
                    ["git", "checkout", "-b", branch_name, sha])
                print(f"Switched to new branch {branch_name} at {sha}")

            except subprocess.CalledProcessError as e:
                print(f"Failed to checkout to {sha}: {e}")
                logger.error(f"Failed to checkout to {sha}: {e}")
            except Exception as e:
                print(
                    f"An error occurred while switching the git version: {e}")
                logger.error(
                    f"An error occurred while switching the git version: {e}")

    def compile_mfem(self):
        bash_path = os.path.join(
            self.root_path, "get_normal_testcase_covarage", "compile_mfem.sh")

        try:
            subprocess.check_call(["bash", bash_path])
        except subprocess.CalledProcessError as e:
            print(f"Failed to complete mfem: {e}")
            logger.error(f"Failed to complete mfem: {e}")
        except Exception as e:
            print(f"An error occurred while completing mfem: {e}")
            logger.error(f"An error occurred while completing mfem: {e}")


    # 复制测试用例
    def copy_testcase(self,name, testcase):
        source_path = os.path.join(self.bugs_path, name, testcase.split("/")[-1])
        target_path = os.path.join(self.mfem_path, testcase)
        shutil.copy(source_path, target_path)
        print(f"Copied fix file {source_path} to {target_path}")

        pass


    # 运行unit test中的测试用例
    def run_unit_test(self, testname):
        cmd_path = os.path.join(self.mfem_path, "build/tests/unit")
        os.chdir(cmd_path)

        try:
            # 使用capture_output来捕获输出
            result = subprocess.run(["/root/mfem/mfem-code-analyzer/get_normal_testcase_covarage/run_tesscase.sh", testname], capture_output=True, text=True)
            # 将标准输出和错误输出记录到日志
            logger.info(f"Running test case: {testname}")
            logger.info(result.stdout)
            if result.stderr:
                logger.error(result.stderr)
        except Exception as e:
            logger.error(f"An error occurred while running the test case '{testname}': {e}")


if __name__ == "__main__":
    processor = MFEMIssueProcessor(is_get_normal_testcase=True)
    processor.process_yaml_file()
