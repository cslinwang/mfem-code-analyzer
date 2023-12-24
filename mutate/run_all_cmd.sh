issue1230  issue129   issue1326  issue1769  issue1887  issue1928  issue2119  issue2152  issue2343  issue2563  issue2699  issue2779  issue2878  issue3332  issue3566  issue443  issue512
issue1284  issue1322  issue1750  issue1871  issue1896  issue2035  issue2144  issue2157  issue2492  issue2599  issue2703  issue2838  issue3328  issue3436  issue413   issue463  issue685

# 如何更新
cd /root/mfem-code-analyzer
git reset --hard HEAD
git clean -fd
git pull
cp /root/mfem-code-analyzer/mutate/.screenrc ~/.screenrc
screen -r

# 如何设置中文
先更新代码，然后退出screen，然后执行
cp /root/mfem-code-analyzer/mutate/.screenrc ~/.screenrc

# ocsar10
# issue3566
docker run -it -d -p 7001:22 --name myissue3566 cslinwang/mfem:v2.4.1222
docker exec -it myissue3566  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue3566

# ocsar10
# issue1230
docker run -it -d -p 7002:22 --name myissue1230 cslinwang/mfem:v2.4.1222
docker exec -it myissue1230  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue1230

# ocsar10
# issue1284
docker run -it -d -p 7003:22 --name myissue1284 cslinwang/mfem:v2.4.1222
docker exec -it myissue1284  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue1284

# ocsar10
# issue129
docker run -it -d -p 7004:22 --name myissue129 cslinwang/mfem:v2.4.1222
docker exec -it myissue129  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue129

# ocsar10
# issue1322
docker run -it -d -p 7005:22 --name myissue1322 cslinwang/mfem:v2.4.1222
docker exec -it myissue1322  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue1322

# oscar11
# issue1326
docker run -it -d -p 7006:22 --name myissue1326 cslinwang/mfem:v2.4.1222
docker exec -it myissue1326  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue1326

# oscar11
# issue1750
docker run -it -d -p 7007:22 --name myissue1750 cslinwang/mfem:v2.4.1222
docker exec -it myissue1750  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue1750

# oscar11
# issue1769
docker run -it -d -p 7008:22 --name myissue1769 cslinwang/mfem:v2.4.1222
docker exec -it myissue1769  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue1769

# oscar11
# issue1871
docker run -it -d -p 7009:22 --name myissue1871 cslinwang/mfem:v2.4.1222
docker exec -it myissue1871  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue1871

# oscar11
# issue1887
docker run -it -d -p 7010:22 --name myissue1887 cslinwang/mfem:v2.4.1222
docker exec -it myissue1887  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue1887

# oscar12
# issue1896
docker run -it -d -p 7011:22 --name myissue1896 cslinwang/mfem:v2.4.1222
docker exec -it myissue1896  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue1896

# oscar12
# issue1928
docker run -it -d -p 7012:22 --name myissue1928 cslinwang/mfem:v2.4.1222
docker exec -it myissue1928  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue1928

# oscar12
# issue2035
docker run -it -d -p 7013:22 --name myissue2035 cslinwang/mfem:v2.4.1222
docker exec -it myissue2035  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue2035

# oscar12
# issue2119
docker run -it -d -p 7014:22 --name myissue2119 cslinwang/mfem:v2.4.1222
docker exec -it myissue2119  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue2119

# oscar12
# issue2144
docker run -it -d -p 7015:22 --name myissue2144 cslinwang/mfem:v2.4.1222
docker exec -it myissue2144  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue2144

# oscar9
# issue2152
docker run -it -d -p 7017:22 --name myissue2152 cslinwang/mfem:v2.4.1222
docker exec -it myissue2152  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue2152

# oscar9
# issue2157
docker run -it -d -p 7018:22 --name myissue2157 cslinwang/mfem:v2.4.1222
docker exec -it myissue2157  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue2157

# oscar9
# issue2343
docker run -it -d -p 7019:22 --name myissue2343 cslinwang/mfem:v2.4.1222
docker exec -it myissue2343  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue2343

# oscar9
# issue2492
docker run -it -d -p 7020:22 --name myissue2492 cslinwang/mfem:v2.4.1222
docker exec -it myissue2492  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue2492

# oscar10
# issue2563
docker run -it -d -p 7021:22 --name myissue2563 cslinwang/mfem:v2.4.1222
docker exec -it myissue2563  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue2563

# oscar10
# issue2599
docker run -it -d -p 7022:22 --name myissue2599 cslinwang/mfem:v2.4.1222
docker exec -it myissue2599  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue2599

# oscar11
# issue2703
docker run -it -d -p 7023:22 --name myissue2703 cslinwang/mfem:v2.4.1222
docker exec -it myissue2703  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue2703

# oscar11
# issue2699
docker run -it -d -p 7024:22 --name myissue2699 cslinwang/mfem:v2.4.1222
docker exec -it myissue2699  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue2699

# oscar12
# issue2779
docker run -it -d -p 7025:22 --name myissue2779 cslinwang/mfem:v2.4.1222
docker exec -it myissue2779  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue2779

# oscar12
# issue2838
docker run -it -d -p 7026:22 --name myissue2838 cslinwang/mfem:v2.4.1222
docker exec -it myissue2838  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue2838

# ocsar10
# issue2878
docker run -it -d -p 7027:22 --name myissue2878 cslinwang/mfem:v2.4.1222
docker exec -it myissue2878  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue2878

# ocsar10
# issue3328
docker run -it -d -p 7028:22 --name myissue3328 cslinwang/mfem:v2.4.1222
docker exec -it myissue3328  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue3328

# oscar11
# issue3332
docker run -it -d -p 7029:22 --name myissue3332 cslinwang/mfem:v2.4.1222
docker exec -it myissue3332  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue3332

# oscar12
# issue3436
docker run -it -d -p 7030:22 --name myissue3436 cslinwang/mfem:v2.4.1222
docker exec -it myissue3436  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue3436

# oscar11
# issue413
docker run -it -d -p 7032:22 --name myissue413 cslinwang/mfem:v2.4.1222
docker exec -it myissue413  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue413

# oscar12
# issue443
docker run -it -d -p 7033:22 --name myissue443 cslinwang/mfem:v2.4.1222
docker exec -it myissue443  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue443

# oscar9
# issue463
docker run -it -d -p 7034:22 --name myissue463 cslinwang/mfem:v2.4.1222
docker exec -it myissue463  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue463

# oscar9
# issue512
docker run -it -d -p 7035:22 --name myissue512 cslinwang/mfem:v2.4.1222
docker exec -it myissue512  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue512

# oscar9
# issue685
docker run -it -d -p 7036:22 --name myissue685 cslinwang/mfem:v2.4.1222
docker exec -it myissue685  /bin/bash
python3 /root/mfem-code-analyzer/mutate/run_mutate.py issue685

