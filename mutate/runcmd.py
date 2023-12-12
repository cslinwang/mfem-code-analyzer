import os
import subprocess

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
    with subprocess.Popen([command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, bufsize=1, universal_newlines=True) as p:
        try:
            # 逐行读取并打印标准输出
            for line in p.stdout:
                print(line.strip())

            # 逐行读取并打印标准错误
            for line in p.stderr:
                print(line.strip())

            p.wait(timeout=timeout)
        except Exception as e:
            print("Timeout ---------------------------")
            p.terminate()

# result = exccmd("cd /home/dpc/Documents/project/bug_02/runfile/bin && ./iverilog test.v -o test.o && ./test.o")
# print("run commend result:")
# print(result)

