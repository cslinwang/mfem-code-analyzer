#!/usr/local/bin/python3
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

info("开始运行mutate")


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
        is_need_mutate = True
        for branch_name in all_branch:
            if branch_name.find("master") != -1:
                continue
            if branch_name.endswith(file_name.split("/")[-1].split(".")[0]):
                is_need_mutate = False
                break
        if is_need_mutate:
            command = pre_command + "mucpp applyall " + file_name + " -- -std=c++11"
            runcmd.exccmd(command)

        # 变异完成后，拿到git branch的变异分支
        command = pre_command + \
            "git checkout master && git branch | grep -i '"+mutate_file_name+"$'"
        all_branch = exccmd(command)
        info(len(all_branch))
        save_to_excel(all_branch, mutate_result_save_path+"/all_branch.xlsx")
        print("branchs:{}".format(len(all_branch)))
        # 遍历每一个分支，拿到对应分支下的变异文件和变异行号
        success_mutate = 0
        for branch_name in all_branch:
            if branch_name.find("master") != -1:  # 原版本跳过
                continue
            # 如果变异的不是当前文件，则跳过

            a = branch_name.split("_")[-1]
            if (mutate_file_name not in (branch_name.split("_")[-1])) or not is_mutate_branch(branch_name):
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
                command = pre_command + "git checkout master && git branch -D " + branch_name
                runcmd.exccmd(command)
                continue
            mutate_line = get_mutate_line(gitlog)

            if mutate_line == None:  # 没找到修改行直接跳过
                print("not find mutateline.")
                continue
            # 将变异文件复制到指定目录下,88888为分隔符
        #     dir_name = mutate_file_save_paths+"/bug_{:02}".format(
        #         bug_id) + "/" + branch_name + "88888" + file_name[file_name.find("iverilog") + 9:].replace("/", "99999")
        #     if not os.path.exists(dir_name):
        #         os.mkdir(dir_name)
        #     command = "cp " + file_name + " " + dir_name + "/"
        #     runcmd.exccmd(command)

        #     # 保存变异行
        #     f = open(dir_name+"/mutate_line.txt", 'w')
        #     f.write(str(mutate_line))
        #     f.close()
            success_mutate += 1
        info("文件{}变异完成,有效变异分支数量:{}".format(file_name, success_mutate))
        # end_time = time.time()
        # print("file " + str(idx) + ":  mutate " + file_name[file_name.find(
        #     "iverilog") + 9:] + " complete.  already use " + str((end_time - start_time) // 60) + " minutes.")
        idx += 1
    info("变异完成,有效变异文件数量:{}".format(idx))
    # 复制变异后项目到指定目录
    command = "cp -r " + project_name + " " + \
        mutate_project_path+"/mfem_{:02}".format(bug_id)
    exccmd(command)
    return 0

# 检验bug行号是否正确，mucpp生成的修改行总是比真实的行少3


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


# 筛选覆盖行的变异体
def get_coverage_mutate(bug_id):
    mutate_project = "/home/dpc/Documents/mutateFiles/{:02}".format(bug_id)
    save_to_dir = "mutate_file_save_paths/{:02}".format(bug_id)
    if not os.path.exists(save_to_dir):
        os.mkdir(save_to_dir)
    coverage_line = get_coverage_line(bug_id)
    coverage_mutate = []

    f = open("./list_operators.txt", 'r')
    lines = f.readlines()
    f.close()
    mutate_operators = []
    for line in lines:
        line = line.strip()
        line = "/*" + line + "*/"
        mutate_operators.append(line)

    diffs = set()
    for path_name in os.listdir(mutate_project):
        dir_name = mutate_project + "/" + path_name

        mutate_line_file = "mutate_line.txt"
        mutate_file_name = path_name.split("88888")[-1].replace("99999", "/")

        # 获得修改行
        f = open(dir_name + "/" + mutate_line_file)
        print(path_name)
        str_line = f.readline()
        mutate_line = int(str_line)
        f.close()
        # 从文件中一行一行的找变异行
        f = open(dir_name + "/" + path_name.split("88888")
                 [-1].split("99999")[-1], 'r')
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
        if find_mutate_line == -1:
            continue
        if mutate_file_name in coverage_line and find_mutate_line in coverage_line[mutate_file_name]:
            coverage_mutate.append(path_name)
            saveDir = save_to_dir + "/" + path_name
            if not os.path.exists(saveDir):
                os.mkdir(saveDir)
            command = "cd "+mutate_project+" && cp " + \
                path_name + "/" + mutate_file_name + " " + saveDir
            runcmd.exccmd(command)
            mutate_line_file = saveDir + "/mutate_line.txt"
            f = open(mutate_line_file, 'w')
            f.write(str(find_mutate_line))
            f.close()

    print(diffs)
    print("not equal line size: {}".format(len(diffs)))
    print("coverageMutateFiles: {}".format(len(coverage_mutate)))
    # return coverage_mutate

# 将变异文件替换原项目的文件


def replace_mutate_file(mutate_project, iverilog_project, bug_project, bug_id):
    start_time = time.time()
    file_to_dir = joblib.load(mutate_project + "/file2dir.dump")
    # 读取测试用例
    testcases = pd.read_csv("./chosen_files_top_100.csv")
    cases = testcases["bug_{:02}".format(bug_id)].to_list()
    # 触发bug的输出，用于判断测试用例是否触发bug
    bugs = pd.read_csv("./iverilogbugs.csv", encoding='gb18030')
    bug_output = bugs[bugs.id == 46]['fail'].values[0].split("\n")
    bug_version = bugs[bugs.id == 46]['bug version'].values[0]
    bug_command = bugs[bugs.id == 46]['command'].values[0]

    # 先在原项目上跑一遍所有测试用例，标记失败的测试用例
    testcases_result = dict()
    command = "cd " + bug_project + \
        " rm -rvf iverilog && cp -r /home/dpc/Documents/branch/master/iverilog ."
    runcmd.exccmd(command, 10000)
    command = "cd " + iverilog_project + " && git checkout -f " + bug_version
    runcmd.exccmd(command, 10000)
    command = "cd " + iverilog_project + " && sh autoconf.sh"
    runcmd.exccmd(command, 10000)
    command = "cd " + iverilog_project + \
        " && ./configure CXXFLAGS='-g -O2 -fprofile-arcs -ftest-coverage' CFLAGS='-g -O2 -fprofile-arcs -ftest-coverage' LDFLAGS='-fprofile-arcs -ftest-coverage' CPPFLAGS='-fprofile-arcs -ftest-coverage' --prefix=/home/dpc/Documents/project/bug_{}/runfile".format(
            bug_id)
    runcmd.exccmd(command, 10000)
    command = "cd " + iverilog_project + " && make && make install"
    runcmd.exccmd(command, 10000)
    for t_name in cases:
        splits = t_name.split("_")
        line_num = splits[-1]
        file_name = splits[0]
        if len(splits) == 3:
            file_name += "_" + splits[1]
        path = "/home/dpc/Documents/project/bug_24/iverilog/ivtest/" + file_name + ".list"
        f = open(path, 'r')
        line = f.readlines()[int(line_num)]
        f.close()
        elements = line.strip().split()
        test_file = elements[0] + '.v'
        # 找到编译选项并运行
        compile_choose = elements[1].split(",")[1:]
        compile_choose_str = ""
        for x in compile_choose:
            if x.find("ivltests") != -1:
                # compile_choose_str += bug_project + "iverilog/ivtest/" + x + " "
                compile_choose_str += "/home/dpc/Documents/project/bug_24/" + \
                    "iverilog/ivtest/" + x + " "
            else:
                compile_choose_str += x + " "
        # run bug project
        # if test_file == "br1005.v":
        #     continue
        run_commend = "cd " + bug_project + "runfile/bin" + " && " + bug_project + "runfile/bin/iverilog " + compile_choose_str + " " + "/home/dpc/Documents/project/bug_24/" + "iverilog/ivtest/" + \
                      elements[2] + "/" + test_file + " -o test.o && ./test.o"
        print(run_commend)
        output = runcmd.exccmd(run_commend)
        if check_failed(output, bug_output):
            testcases_result[t_name] = 1
    print(len(testcases_result))

    # 运行其他变异体
    sus_map = dict()  # 保存所有语句的可疑度值(仅有变异体的)
    if os.path.exists("sus_map.dump"):
        sus_map = joblib.load("sus_map.dump")
    mutate_idx = 0  # 输出idx，方便断点续上
    make_map = []  # 保存编译有问题的变异体结果
    total_mutates = len(os.listdir(mutate_project)) - 1  # 总共多少变异体
    tmp = []
    for path_name in os.listdir(mutate_project):
        if path_name == "file2dir.dump":
            continue
        if mutate_idx <= 187:  # 断点重连
            mutate_idx += 1
            continue

        command = "cd " + iverilog_project + " && git checkout -f " + bug_version
        runcmd.exccmd(command)
        print("mutate_idx:{},path_name:{}".format(mutate_idx, path_name))
        mutate_file, mutate_line_file = os.listdir(
            mutate_project + "/" + path_name)
        if mutate_file == "mutate_line.txt":
            mutate_file = mutate_line_file
            mutate_line_file = "mutate_line.txt"
        if not mutate_file.endswith(".c") and not mutate_file.endswith(".cc"):
            tmp.append(mutate_file)

        origin_file_name = mutate_project + "/" + path_name + "/" + mutate_file
        dest_file_name = iverilog_project + "/" + file_to_dir[mutate_file]
        f = open(mutate_project + "/" + path_name +
                 "/" + mutate_line_file, 'r')
        mutate_line = int(f.readline())
        f.close()
        print("mutate_file: {}, mutate_line : {}".format(
            file_to_dir[mutate_file], mutate_line))

        # 移动变异文件并编译安装

        command = "cp -f " + origin_file_name + " " + dest_file_name
        runcmd.exccmd(command, 10000)

        command = "cd " + iverilog_project + " && sh autoconf.sh"
        runcmd.exccmd(command, 10000)

        command = "cd " + iverilog_project + \
            " && ./configure CXXFLAGS='-g -O2 -fprofile-arcs -ftest-coverage' CFLAGS='-g -O2 -fprofile-arcs -ftest-coverage' LDFLAGS='-fprofile-arcs -ftest-coverage' CPPFLAGS='-fprofile-arcs -ftest-coverage' --prefix=/home/dpc/Documents/project/bug_{}/runfile".format(
                bug_id)
        runcmd.exccmd(command, 10000)

        command = "cd " + iverilog_project + " && make && make install"
        res = runcmd.exccmd(command, 10000)
        print(res)
        print("make over.")
        if "".join(res).find("Error") != -1:
            print(res)
            print("make step find error!!!")
            make_map.append(path_name)
            continue
        failed = 0
        passed = 0
        # 运行测试用例
        totalFailed = len(testcases_result)
        for t_name in cases:
            print("t_name:"+t_name)

            # 找到测试用例的文件
            splits = t_name.split("_")
            line_num = splits[-1]
            file_name = splits[0]
            if len(splits) == 3:
                file_name += "_" + splits[1]
            path = "/home/dpc/Documents/project/bug_24/iverilog/ivtest/" + file_name + ".list"
            f = open(path, 'r')
            line = f.readlines()[int(line_num)]
            f.close()
            elements = line.strip().split()
            test_file = elements[0] + '.v'
            # 找到编译选项并运行
            compile_choose = elements[1].split(",")[1:]
            compile_choose_str = ""
            for x in compile_choose:
                if x.find("ivltests") != -1:
                    # compile_choose_str += bug_project + "iverilog/ivtest/" + x + " "
                    compile_choose_str += "/home/dpc/Documents/project/bug_24/" + \
                        "iverilog/ivtest/" + x + " "
                else:
                    compile_choose_str += x + " "
            # run bug project
            # if test_file == "br1005.v":
            #     continue
            run_commend = "cd " + bug_project + "runfile/bin" + " && " + bug_project + "runfile/bin/iverilog " + compile_choose_str + " " + "/home/dpc/Documents/project/bug_24/" + "iverilog/ivtest/" + \
                          elements[2] + "/" + test_file + \
                " -o test.o && ./test.o"
            print(run_commend)
            mutate_output = runcmd.exccmd(run_commend)
            print("run_result: ------------------------------------------")
            print(mutate_output)
            print("======================================================")
            # 判断是否触发了bug，使用原触发bug的输出判断，如果现在的测试用例的输出包含了触发bug的输出，则认为是触发了bug
            isFailed = check_failed(mutate_output, bug_output)
            if t_name in testcases_result and not isFailed:
                failed += 1
                print("failed_testcase:")
                print(mutate_output)
                print("------")
                print(bug_output)
            if t_name not in testcases_result and isFailed:
                passed += 1
                print("passed_testcase:")
                print(mutate_output)
                print("------")
                print(bug_output)
        res_bug = runcmd.exccmd("cd " + bug_project +
                                "runfile/bin && " + bug_command)
        print("-----------res_bug:")
        print(res_bug)
        print("==========")
        if not check_failed(res_bug, bug_output):
            failed += 1
        totalFailed += 1

        print("failed: {}, passed: {}, totalFailed: {}".format(
            failed, passed, totalFailed))
        susp = 0 if totalFailed * \
            (failed + passed) == 0 else failed / math.sqrt(totalFailed * (failed + passed))
        sus_key = file_to_dir[mutate_file] + ":" + str(mutate_line)
        if sus_key in sus_map:
            sus_map[sus_key] = max(sus_map[sus_key], susp)
        else:
            sus_map[sus_key] = susp
        mutate_idx += 1
        joblib.dump(sus_map, "sus_map.dump")
        end_time = time.time()
        print("already: {} minutes, rest: {} minutes".format((end_time - start_time) //
              60, ((end_time - start_time) / mutate_idx * (total_mutates - mutate_idx)) // 60))

    sorted_list = sorted(sus_map.items(), key=lambda x: x[1], reverse=True)
    joblib.dump(sorted_list, "bug_46_res.dump")
    print(len(sorted_list))
    print(sorted_list)
    print("----------------------")
    print(make_map)
    end_time = time.time()
    print(str((end_time - start_time) // 60) + " minutes")


def check_failed(mutate_output, bug_output):
    idx = 0
    for line in mutate_output:
        if line == bug_output[idx]:
            idx += 1
        if idx == len(bug_output):
            return True
    return False


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
    cmd = "rm -rf /root/mfem && cp -r /root/mfem_"+issue+" /root/mfem"
    runcmd.exccmd(cmd)


# 覆盖率路径
coverage_file_paths = "/root/mfem-code-analyzer/bugs"
# 项目名称
project_name = "/root/mfem"
# 变异结果保存路径
mutate_file_save_paths = "/root/mfem-code-analyzer/mutateFiles"

mutate_result_save_paths = "/root/mfem-code-analyzer/mutate/result"

mutate_project_path = "/root/mfem_mutate/"

if not os.path.exists(mutate_project_path):
    os.mkdir(mutate_project_path)


if __name__ == '__main__':

    for path_name in os.listdir(coverage_file_paths):
        bug_id = path_name
        # 测试，仅跑issue3566
        # if bug_id != "issue3566":
        #     continue
        # 是否有改bug复现结果
        bug_project_path = "/root/mfem_"+bug_id
        if not os.path.exists(bug_project_path):
            continue
        # 跳过已经变异的bug
        if os.path.exists(mutate_project_path+"/mfem_{:02}".format(bug_id)):
            continue
        # delete_mutate_brach(bug_id)
        prepare_source_code(bug_id)  # 准备源代码
        mutate_result_save_path = os.path.join(
            mutate_result_save_paths, bug_id)
        if not os.path.exists(mutate_result_save_path):
            os.mkdir(mutate_result_save_path)
        need_muta_files = get_coverage_files(bug_id)  # 获得覆盖文件
        mutate(need_muta_files, bug_id)  # 变异
        # get_coverage_mutate(bug_id)
        # command = "rm -rf /home/dpc/Documents/mutateFiles/bug_{:02}".format(
        #     bug_id)
        # runcmd.exccmd(command)
        a = 1
    # need_muta_files = get_coverage_files(2)
    # mutate(need_muta_files, 2)
    # check_mutate_line(2)

    # need_muta_files = get_coverage_files(79)
    # mutate(need_muta_files,79)
    # check_mutate_line(79)
    # get_coverage_mutate(79)
    # replace_mutate_file("/home/dpc/Documents/coverageMutateFiles/bug_46","/home/dpc/Documents/project/bug_46/iverilog","/home/dpc/Documents/project/bug_46/",46)
