#!/usr/local/bin/python3
import argparse
import math

import joblib
import os
import runcmd
from runcmd import exccmd
import pandas as pd
import time
import re
import os
import shutil
import subprocess
import yaml
import logging
import sys
import logging
import sys
import os
from tqdm import tqdm
from logger_module import info

info("Start running mutate")


class IssueInfo:
    def __init__(self, bug_id, branch_name, mutate_file, mutate_line, testcase, result, duration, is_success):
        self.bug_id = bug_id
        self.branch_name = branch_name
        self.mutate_file = mutate_file
        self.mutate_line = mutate_line
        self.testcase = testcase
        self.result = result
        self.duration = duration
        self.is_success = is_success


def save_issues_to_excel(filename="issues.xlsx"):
    # 将每个 IssueInfo 对象的属性转换为字典
    data = [vars(issue) for issue in issue_info_list]

    # 使用 pandas 创建 DataFrame
    df = pd.DataFrame(data)

    # 将 DataFrame 保存为 Excel 文件
    df.to_excel(filename, index=False)
    issue_info_list.clear()


def get_coverage_files(bug_id):
    # 根据coverage.info的覆盖信息，筛选出被测试用例覆盖的文件
    f = open(os.path.join(coverage_file_paths, bug_id, "coverage.info"), 'r')
    lines = f.readlines()

    need_muta_files = []
    now_file_name = ""
    skip_file = 0  # 跳过不是项目的文件
    need_muta = False  # 当前遍历到的文件是否需要变异
    for line in lines:
        line = line.strip()
        if line.startswith("SF:"):
            now_file_name = line.replace("SF:", "")
            now_file_name = now_file_name.strip()
            # 过滤条件自行修改，这里只筛选出项目文件，同时只筛选出hpp和cpp文件
            if now_file_name.find(project_name) == -1 or not (now_file_name.endswith(".hpp") or now_file_name.endswith(".cpp")):
                skip_file = 1
            else:
                skip_file = 0
                need_muta = False
                # now_file_name = now_file_name[now_file_name.find("iverilog") + 9:]
        if line.startswith("DA:"):
            if skip_file == 1:
                continue
            now_line, line_num = list(
                map(int, line.replace("DA:", "").split(",")))
            if line_num != 0:
                need_muta = True
        if line.startswith("end_of_record") and skip_file == 0 and need_muta:
            need_muta_files.append(now_file_name)
    print(need_muta_files)
    print(len(need_muta_files))
    return need_muta_files


def get_coverage_line(bug_id):
    # 根据coverage.info的覆盖信息，筛选出被测试用例覆盖的行
    f = open(os.path.join(coverage_file_paths, bug_id, "coverage.info"), 'r')
    lines = f.readlines()
    f.close()
    coverage_line = dict()
    now_file_name = ""
    skip_file = 0  # 跳过不是项目的文件
    for line in lines:
        line = line.strip()
        if line.startswith("SF:"):
            now_file_name = line.replace("SF:", "")
            now_file_name = now_file_name.strip()
           # 过滤条件自行修改，这里只筛选出项目文件，同时只筛选出hpp和cpp文件
            if now_file_name.find(project_name) == -1:
                skip_file = 1
            else:
                skip_file = 0
                now_file_name = now_file_name[now_file_name.find(
                    "project_name") + 9:]
        if line.startswith("DA:"):
            if skip_file == 1:
                continue
            now_line, line_num = list(
                map(int, line.replace("DA:", "").split(",")))
            if line_num != 0:
                if now_file_name in coverage_line:
                    coverage_line[now_file_name].add(now_line)
                else:
                    coverage_line[now_file_name] = {now_line}
    return coverage_line


def get_mutate_line(gitlog):
    for line in gitlog:
        if line.find("@@") != -1 and len(line.split("@@")) == 3:
            muta_line = line.split("@@")[1].strip().split(",")[0]
            return abs(int(muta_line))
    return None


def get_mutate_file(gitlog):
    for line in gitlog:
        if line.startswith("---"):
            return line.replace("--- a/", "").strip()
    return ""


def save_to_excel(data, file_name):
    # 创建一个DataFrame对象
    df = pd.DataFrame(data)
    if os.path.exists(file_name):
        os.remove(file_name)
    # 将DataFrame保存为Excel文件
    df.to_excel(file_name, index=False)

# 对每一个被覆盖的文件分别进行变异，每次只能变异一个文件，执行后保存变异文件及变异行号


def is_mutate_branch(name):
    """
    检查提供的字符串是否以 'm' 开头并且包含两个下划线

    参数:
    name (str): 要检查的字符串

    返回:
    bool: 如果字符串符合模式，则为 True，否则为 False
    """
    pattern = r"m[^_]*_[^_]*_.*"
    return bool(re.match(pattern, name))


def mutate(need_muta_files, bug_id):
    project_path = project_name
    pre_command = "cd " + project_path + " && "
    start_time = time.time()

    idx = 1
    for file_name in need_muta_files:
        # runcmd.exccmd(command)
        # print(runcmd.exccmd(command))
        # 如果已经变异,不再变异
        mutate_file_name = file_name.split("/")[-1].split(".")[0]
        command = pre_command + \
            "git checkout master && git branch | grep -i '"+mutate_file_name+"$'"
        all_branch = exccmd(command)
        # 如果其中一个分支是变异分支，则跳过
        # is_need_mutate = True
        # for branch_name in all_branch:
        #     if branch_name.find("master") != -1:
        #         continue
        #     if branch_name.endswith(file_name.split("/")[-1].split(".")[0]):
        #         is_need_mutate = False
        #         break
        # if is_need_mutate:
        command = pre_command + "mucpp applyall " + file_name + " -- -std=c++11"
        runcmd.exccmd(command)

        # 变异完成后，拿到git branch的变异分支
        command = pre_command + \
            "git checkout master && git branch | grep -i '"+mutate_file_name+"$'"
        all_branch = exccmd(command)
        info("Mutation of file {} completed, number of effective mutated branches: {}".format(
            file_name, len(all_branch)))
        save_to_excel(all_branch, mutate_result_save_path +
                      "/all_branch_"+mutate_file_name+".xlsx")
        print("branchs:{}".format(len(all_branch)))
        # 遍历每一个分支，拿到对应分支下的变异文件和变异行号
        success_mutate = 0
        for branch_name in all_branch:
            if branch_name.find("master") != -1:  # 原版本跳过
                continue
            # 如果变异的不是当前文件，则跳过
            tmp = '_'.join(branch_name.split("_")[3:])
            if (mutate_file_name not in branch_name) or not is_mutate_branch(branch_name):
                print(file_name[file_name.find("iverilog") + 9:])
                print(branch_name.split("_")[-1])
                continue
            branch_name = branch_name.strip()
            command = pre_command + "git checkout -f " + branch_name
            runcmd.exccmd(command)

            # 找到修改行
            command = pre_command + "git log -p " + branch_name + " -n 1"
            gitlog = runcmd.exccmd(command)
            mutate_file = get_mutate_file(gitlog)
            # mutate_file 是相对路径，需要转换为绝对路径
            mutate_file = project_path + "/" + mutate_file
            if mutate_file != file_name:
                # 删除分支
                # command = pre_command + "git checkout master && git branch -D " + branch_name
                # runcmd.exccmd(command)
                continue
            mutate_line = get_mutate_line(gitlog)
            mutate_line = mutate_line + 3  # mucpp生成的修改行总是比真实的行少3

            if mutate_line == None:  # 没找到修改行直接跳过
                print("not find mutateline.")
                continue
            success_mutate += 1
            # 运行变异后的项目，并存储结果。
            run_mutated_project(bug_id, branch_name, mutate_file, mutate_line)

        info("Mutation of file {} completed, number of effective mutated branches: {}".format(
            file_name, success_mutate))
        # end_time = time.time()
        # print("file " + str(idx) + ":  mutate " + file_name[file_name.find(
        #     "iverilog") + 9:] + " complete.  already use " + str((end_time - start_time) // 60) + " minutes.")
        idx += 1
    info("Mutation completed, number of effective mutated files: {}".format(idx))
    save_issues_to_excel(mutate_result_save_path+"/runres.xlsx")
    return 0

# 检验bug行号是否正确，mucpp生成的修改行总是比真实的行少3


def origin_res(bug_id):
    project_path = project_name
    pre_command = "cd " + project_path + " && "
    start_time = time.time()
    run_mutated_project(bug_id, 'bug', 'bug', -1)
    return 0


def run_mutated_project(bug_id, branch_name, mutate_file, mutate_line):
    # 首先检测是否有结果
    if os.path.exists(mutate_result_save_path +
                      "/runres"+bug_id+"_"+branch_name+".xlsx"):
        return 0
    # 运行变异的bug用例
    precmd = "cd " + project_name
    shell_path = "/root/mfem-code-analyzer/bugs"+"/" + \
        bug_id+"/run"+bug_id.split("issue")[-1]+"_compile.sh"
    cmd = precmd + " && " + shell_path
    exccmd(cmd)
    # 运行bug用例
    shell_path = "/root/mfem-code-analyzer/bugs"+"/" + \
        bug_id+"/run"+bug_id.split("issue")[-1]+".sh"
    start_time = time.time()
    result = subprocess.run(
        ['bash', shell_path], input='c', text=True, capture_output=True)
    end_time = time.time()
    duration = end_time - start_time
    if mutate_line != -1:
        issue_info = IssueInfo(bug_id, branch_name, mutate_file,
                               mutate_line, "bug", result, duration, 0)
        issue_info_list.append(issue_info)
    else:
        issue_info = IssueInfo(bug_id, branch_name, mutate_file,
                               mutate_line,  "bug", result, duration, 0)
        issue_info_list.append(issue_info)
        normal_result_map["bug"] = result
    # 运行example用例
    run_example_tests(bug_id, branch_name, mutate_file, mutate_line)
    # 运行unit用例
    run_unit_tests(bug_id, branch_name, mutate_file, mutate_line)
    save_issues_to_excel(mutate_result_save_path +
                         "/runres"+bug_id+"_"+branch_name+".xlsx")
    return 0


def run_example_tests(bug_id, branch_name, mutate_file, mutate_line):
    print("Starting to run example cases...")
    os.chdir(os.path.expanduser('~/mfem/examples'))
    count = 0

    for testcase in os.listdir('.'):
        if os.path.isfile(testcase) and os.access(testcase, os.X_OK):
            count += 1
            print(f"Executing: {testcase}")
            start_time = time.time()
            result = ''
            process = subprocess.Popen(
                ['./' + testcase], stdin=subprocess.PIPE, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                result = process.communicate(input='c', timeout=600)
            except subprocess.TimeoutExpired:
                print("Test {} ran out of time".format(testcase))
                process.kill()  # 杀死超时的进程
                stdout, stderr = process.communicate()  # 获取进程的输出
                result = "timeout"
            result = subprocess.run(
                ['./' + testcase], input='c', text=True, capture_output=True)
            end_time = time.time()
            duration = end_time - start_time
            if mutate_line != -1:
                if testcase in normal_result_map:
                    if result == normal_result_map[testcase]:
                        result = "normal"
                issue_info = IssueInfo(bug_id, branch_name, mutate_file,
                                       mutate_line, testcase, result, duration, 0)
                issue_info_list.append(issue_info)
            else:
                issue_info = IssueInfo(bug_id, branch_name, mutate_file,
                                       mutate_line, testcase, result, duration, 0)
                issue_info_list.append(issue_info)
                normal_result_map[testcase] = result
            print(f"Test {testcase} execution time: {duration} seconds")
            print(f"Execution result:\n{result}")
            # save_issues_to_excel(mutate_result_save_path+"/runres.xlsx")

        info(f"A total of {count} example cases.")
        info("Example cases execution completed.")


def run_unit_tests(bug_id, branch_name, mutate_file, mutate_line):
    print("Starting to run unit_tests cases...")
    if os.path.exists('/root/mfem/tests/unit'):
        os.chdir('/root/mfem/tests/unit')
    else:
        info("unit_tests not compiled, skipping")
        return
    count = 0
    # 如果没有编译unit_tests，跳过
    if not os.path.exists('./unit_tests'):
        info("unit_tests not compiled, skipping")
        return
    test_names = subprocess.run(
        ['./unit_tests', '--list-test-names-only'], capture_output=True, text=True)
    test_names = test_names.stdout.strip().split('\n')[1:]  # 跳过第一行

    for testcase in test_names:
        count += 1
        print(f"Executing test: {testcase}")
        start_time = time.time()
        result = ''
        process = subprocess.Popen(
            ['./unit_tests', testcase], stdin=subprocess.PIPE, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            result = process.communicate(input='c', timeout=600)
        except subprocess.TimeoutExpired:
            print("Test {} timed out".format(testcase))
            process.kill()  # 杀死超时的进程
            stdout, stderr = process.communicate()  # 获取进程的输出
            result = "timeout"
        end_time = time.time()
        duration = end_time - start_time
        if mutate_line != -1:
            if testcase in normal_result_map:
                if result == normal_result_map[testcase]:
                    result = "normal"
            issue_info = IssueInfo(bug_id, branch_name, mutate_file,
                                   mutate_line, testcase, result, duration, 0)
            issue_info_list.append(issue_info)
        else:
            issue_info = IssueInfo(bug_id, branch_name, mutate_file,
                                   mutate_line, testcase, result, duration, 0)
            issue_info_list.append(issue_info)
            normal_result_map[testcase] = result

        info("Test {} execution time: {} seconds".format(testcase, duration))
        info("Execution result:\n{}".format(result))

    info("Total of {} unit_tests cases.".format(count))
    info("unit_tests cases execution completed.")


def check_mutate_line(bug_id):
    start_time = time.time()
    dir_name = "/home/dpc/Documents/mutateFiles/bug_{:02}/".format(bug_id)
    f = open("/home/dpc/Documents/list_operators.txt", 'r')
    lines = f.readlines()
    f.close()
    mutate_operators = []
    for line in lines:
        line = line.strip()
        line = "/*" + line + "*/"
        mutate_operators.append(line)
    diffs = set()
    for path_name in os.listdir(dir_name):
        mutate_file_name = path_name.split("88888")[-1].split("99999")[-1]
        mutate_line_name = "mutate_line.txt"
        f = open(dir_name + path_name + "/" + mutate_line_name, 'r')
        mutate_line = int(f.readline())
        f.close()
        if not os.path.exists(dir_name + path_name + "/" + mutate_file_name):
            print(dir_name + path_name + "/" + mutate_file_name)
            print("not exists.")
        f = open(dir_name + path_name + "/" + mutate_file_name, 'r')
        lines = f.readlines()
        f.close()

        find_mutate_line = -1
        line_idx = 1
        for line in lines:
            for mutate_operator in mutate_operators:
                if line.find(mutate_operator) != -1:
                    find_mutate_line = line_idx
                    break
            if find_mutate_line != -1:
                break
            line_idx += 1

        diffs.add(find_mutate_line - mutate_line)
    print(diffs)
    print(len(diffs))
    end_time = time.time()
    print("use time: {} minutes".format((end_time - start_time) // 60))


def delete_mutate_brach(bug_hash="93393c5c58ecaa3eb6fb9bbd6a822e7c3fd96be5"):
    """
    删除所有变异分支
    """
    # 先切换到bug_id分支
    precmd = "cd "+project_name
    cmd = precmd + "&& git checkout -f master"
    runcmd.exccmd(cmd)
    cmd = precmd + "&& git reset --hard {}".format(bug_hash)
    runcmd.exccmd(cmd)
    cmd = precmd + "&& git branch | grep '^m' | xargs -I {} git branch -d {}"
    runcmd.exccmd(cmd)


def prepare_source_code(issue):
    """
    准备源代码
    删除原有项目，重命名issue项目
    """
    # issue_path = mutate_project_path+"/mfem_{:02}".format(bug_id)
    # cmd = "rm -rf /root/mfem && cp -r "+issue_path+" /root/mfem"
    cmd = "rm -rf /root/mfem && cp -r /root/mfem_"+issue+" /root/mfem"
    runcmd.exccmd(cmd)


# 覆盖率路径
coverage_file_paths = "/root/mfem-code-analyzer/bugs"
# 项目名称
project_name = "/root/mfem"
# 变异结果保存路径
mutate_file_save_paths = "/root/mfem-code-analyzer/mutateFiles"

mutate_result_save_paths = "/root/mfem-code-analyzer/mutate/result"
mutate_result_save_path = ""
mutate_project_path = "/root/mfem_mutate/"

if not os.path.exists(mutate_project_path):
    os.mkdir(mutate_project_path)

# 每个测试用例运行结果
issue_info_list = []

normal_result_map = dict()

# 创建解析器
parser = argparse.ArgumentParser(description='Run tests for specified files.')
# 添加一个参数，可以传入零个或多个值，设定默认值
parser.add_argument('filenames', nargs='*', default=['issue3566'],
                    help='List of file names to run tests on')

args = parser.parse_args()

# 解析参数
args = parser.parse_args()

if __name__ == '__main__':
    info("Start running mutate")
    info("Run Issue: {}".format(args.filenames))

    for path_name in os.listdir(coverage_file_paths):
        issue_info_list = []
        bug_id = path_name
        # 测试，仅跑issue3566
        if bug_id not in args.filenames:
            continue
        # 是否有改bug复现结果
        bug_project_path = "/root/mfem_"+bug_id
        mutate_result_save_path = os.path.join(
            mutate_result_save_paths, bug_id)
        if not os.path.exists(mutate_result_save_path):
            os.mkdir(mutate_result_save_path)
        prepare_source_code(bug_id)  # 准备源代码
        origin_res(bug_id)  # 运行原始bug用例
        need_muta_files = get_coverage_files(bug_id)  # 获得覆盖文件
        mutate(need_muta_files, bug_id)  # 变异
