import os
import subprocess
from logger_module import info
# def exccmd(cmd):
#     p=os.popen(cmd,"r")
#     rs=[]
#     line=""
#     while True:
#          line=p.readline()
#          if not line:
#               break
#          rs.append(line.strip())
#     return rs


def exccmd(command, timeout=500000):
    print("run command: " + command)
    stdout_lines = []

    with subprocess.Popen([command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, bufsize=1, universal_newlines=True) as p:
        try:
            # 逐行读取并打印标准输出
            for line in p.stdout:
                line = line.strip()
                print(line)
                stdout_lines.append(line)

            p.wait(timeout=timeout)
        except Exception as e:
            print("Timeout ---------------------------")
            p.terminate()

    return stdout_lines


# result = exccmd("cd /home/dpc/Documents/project/bug_02/runfile/bin && ./iverilog test.v -o test.o && ./test.o")
# print("run commend result:")
# print(result)
