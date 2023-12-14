#!/usr/local/bin/python3
import math

import joblib
import os
import runcmd
from runcmd import exccmd
import pandas as pd
import time


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

# 缩减文件大小，将没有覆盖的行删除，保存缩减后的文件 以及 缩减文件与源文件的映射


def get_reduced_files(need_muta_files):
    f = open("coverage1.info", 'r')
    lines = f.readlines()
    f.close()

    for file_name in need_muta_files:
        origin_f = open(file_name, 'r')
        origin_lines = origin_f.readlines()
        origin_f.close()

        need_to_delete_lines = set()

        choose_lines = []
        for i in range(len(lines)):
            line = lines[i].strip()
            if line.endswith(file_name):
                for j in range(i + 1, len(lines)):
                    if lines[j].find("end_of_record") != -1:
                        break
                    choose_lines.append(lines[j])
                break

        for line in choose_lines:
            line = line.strip()
            if line.startswith("DA:"):
                line = line.strip().replace("DA:", "")
                lineNumber, runtimes = map(int, line.split(","))

                if runtimes == 0:  # 删除没有覆盖的有效行
                    if lineNumber - 1 in need_to_delete_lines:
                        continue

                    # 考虑两种语法问题的情况
                    stm = origin_lines[lineNumber - 1].strip()

                    pre_stm = "" if lineNumber == 1 else origin_lines[lineNumber - 2].strip(
                    )
                    next_stm = "" if lineNumber == len(
                        origin_lines) else origin_lines[lineNumber].strip()

                    if pre_stm.endswith(","):  # 如果上一句还没结束

                        candidates = set()
                        candidates.add(lineNumber - 1)
                        candidates.add(lineNumber - 2)
                        # 删除前面行，直到末尾不为逗号
                        now_lineNum = lineNumber - 3
                        flag = True

                        if origin_lines[now_lineNum].strip().find("if") != -1 or origin_lines[now_lineNum].strip().find(
                                "else") != -1:
                            flag = False

                        while now_lineNum >= 0 and origin_lines[now_lineNum].strip().endswith(","):
                            if origin_lines[now_lineNum].strip().find("if") != -1 or origin_lines[
                                    now_lineNum].strip().find("else") != -1:
                                flag = False
                            candidates.add(now_lineNum)
                            now_lineNum -= 1
                        if flag:
                            need_to_delete_lines = need_to_delete_lines | candidates

                    if stm.endswith(","):  # 如果这一句还没结束
                        if stm.find("if") != -1 or stm.find("else") != -1 or pre_stm.find("if") != -1 or pre_stm.find(
                                "else") != -1:
                            continue

                        need_to_delete_lines.add(lineNumber - 1)
                        now_lineNum = lineNumber  # 从下一句开始
                        while now_lineNum < len(origin_lines) and origin_lines[now_lineNum].strip().endswith(","):
                            need_to_delete_lines.add(now_lineNum)
                            now_lineNum += 1
                        need_to_delete_lines.add(now_lineNum)

                        lineNumber = now_lineNum + 1  # 重新布置光标
                        stm = origin_lines[lineNumber - 1].strip()
                        next_stm = "" if lineNumber == len(
                            origin_lines) else origin_lines[lineNumber].strip()

                    if stm.endswith("{") or next_stm == "{":  # 如果是函数行或分支行
                        if stm.find("if") != -1 or stm.find("else") != -1 or pre_stm.find("if") != -1 or pre_stm.find(
                                "else") != -1:
                            continue
                        # 找到右括号，删除所有中间语句
                        symbol_num = 0
                        if stm.endswith("{"):
                            symbol_num = 1
                        need_to_delete_lines.add(lineNumber - 1)  # 删除当前行
                        # now_lineNum直接对origin_lines索引，从当前行的下一行开始
                        for now_lineNum in range(lineNumber, len(origin_lines)):
                            now_line = origin_lines[now_lineNum].strip()
                            if now_line.startswith("//"):
                                continue
                            for char_str in now_line:
                                if char_str == "{":
                                    symbol_num += 1
                                elif char_str == "}":
                                    symbol_num -= 1
                            need_to_delete_lines.add(now_lineNum)
                            if symbol_num == 0:
                                break

        # 保存缩减后的行到原有行的映射
        mutate_line2origin_line = dict()

        mutate_line_idx = 0
        mutate_lines = []
        for i in range(len(origin_lines)):
            if i not in need_to_delete_lines:
                mutate_line2origin_line[mutate_line_idx] = i
                mutate_lines.append(origin_lines[i])
                mutate_line_idx += 1
        # 保存缩减后的文件
        project_relative_file_name = "reduced_files/" + \
            file_name[file_name.find("iverilog") + 9:]
        os.makedirs(os.path.dirname(project_relative_file_name), exist_ok=True)
        f = open(project_relative_file_name, 'w')
        f.writelines(mutate_lines)
        f.close()
        # 保存缩减后文件和源文件的行映射关系
        project_relative_file_name = "mutate_line2origin_line/" + \
            file_name[file_name.find("iverilog") + 9:]
        os.makedirs(os.path.dirname(project_relative_file_name), exist_ok=True)
        joblib.dump(mutate_line2origin_line,
                    project_relative_file_name+".dump")

# git log -p m34_10_1_symbol_search -n 1 > /home/dpc/Documents/gitlog.txt 后获得本次提交修改的行号


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


# 对每一个被覆盖的文件分别进行变异，每次只能变异一个文件，执行后保存变异文件及变异行号
def mutate(need_muta_files, bug_id):
    project_path = project_name
    pre_command = "cd " + project_path + " && "
    start_time = time.time()

    idx = 1
    for file_name in need_muta_files:
        # runcmd.exccmd(command)
        # print(runcmd.exccmd(command))
        # 如果已经变异,不再变异
        command = pre_command + "git branch -a"
        all_branch = exccmd(command)
        # 如果其中一个分支是变异分支，则跳过
        is_need_mutate = True
        for branch_name in all_branch:
            if branch_name.find("master") != -1:
                continue
            if branch_name.endswith('_coefficient'):
                is_need_mutate = False
                break
        if is_need_mutate:
            command = pre_command + "mucpp applyall " + file_name + " -- -std=c++11"
            runcmd.exccmd(command)

        # 变异完成后，拿到git branch的变异分支
        command = pre_command + "git branch -a"
        all_branch = exccmd(command)
        print("branchs:{}".format(len(all_branch)))
        # 遍历每一个分支，拿到对应分支下的变异文件和变异行号
        success_mutate = 0
        for branch_name in all_branch:
            if branch_name.find("master") != -1:  # 原版本跳过
                continue
            # 如果变异的不是当前文件，则跳过
            if file_name[file_name.find("iverilog") + 9:].find(branch_name.split("_")[-1]) == -1:
                print(file_name[file_name.find("iverilog") + 9:])
                print(branch_name.split("_")[-1])
                continue
            branch_name = branch_name.strip()
            command = pre_command + "git checkout -f " + branch_name
            _ = runcmd.exccmd(command)

            # 找到修改行
            command = pre_command + "git log -p " + branch_name + " -n 1"
            gitlog = runcmd.exccmd(command)
            mutate_file = get_mutate_file(gitlog)
            if mutate_file != file_name[file_name.find("iverilog") + 9:]:
                continue
            mutate_line = get_mutate_line(gitlog)

            if mutate_line == None:  # 没找到修改行直接跳过
                print("not find mutateline.")
                continue
            # 将变异文件复制到指定目录下,88888为分隔符
            dir_name = "/home/dpc/Documents/mutateFiles/bug_{:02}".format(
                bug_id) + "/" + branch_name + "88888" + file_name[file_name.find("iverilog") + 9:].replace("/", "99999")
            if not os.path.exists(dir_name):
                os.mkdir(dir_name)
            command = "cp " + file_name + " " + dir_name + "/"
            runcmd.exccmd(command)

            # 保存变异行
            f = open(dir_name+"/mutate_line.txt", 'w')
            f.write(str(mutate_line))
            f.close()
            success_mutate += 1
        print("success_mutate:{}".format(success_mutate))
        end_time = time.time()
        print("file " + str(idx) + ":  mutate " + file_name[file_name.find(
            "iverilog") + 9:] + " complete.  already use " + str((end_time - start_time) // 60) + " minutes.")
        idx += 1

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

if __name__ == '__main__':

    for path_name in os.listdir(coverage_file_paths):
        bug_id = path_name
        # 测试，仅跑issue3566
        if bug_id != "issue3566":
            continue
        # delete_mutate_brach(bug_id)
        # prepare_source_code(bug_id) # 准备源代码
        need_muta_files = get_coverage_files(bug_id)  # 获得覆盖文件
        mutate(need_muta_files, bug_id)  # 变异
        get_coverage_mutate(bug_id)
        command = "rm -rf /home/dpc/Documents/mutateFiles/bug_{:02}".format(
            bug_id)
        runcmd.exccmd(command)
    # need_muta_files = get_coverage_files(2)
    # mutate(need_muta_files, 2)
    # check_mutate_line(2)

    # need_muta_files = get_coverage_files(79)
    # mutate(need_muta_files,79)
    # check_mutate_line(79)
    # get_coverage_mutate(79)
    # replace_mutate_file("/home/dpc/Documents/coverageMutateFiles/bug_46","/home/dpc/Documents/project/bug_46/iverilog","/home/dpc/Documents/project/bug_46/",46)
