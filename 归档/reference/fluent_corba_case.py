# encoding: utf-8
# 导入fluent_corba下的CORBA接口类和其他必要模块
from fluent_corba import CORBA
import time
import pathlib
import os, sys
import subprocess
# 定义Fluent的启动位置，例如2020R1版本
ansysPath = pathlib.Path(os.environ["AWP_ROOT201"])
fluentExe = str(ansysPath/"fluent"/"ntbin"/"win64"/"fluent.exe")
# 定义工作目录
workPath = pathlib.Path(r"E:\Workdata\Fluent_Python")
aasFilePath = workPath/"aaS_FluentId.txt"
# 服务器会话连接之前，清除工作目录下存在的aaS*.txt文件
for file in workPath.glob("aaS*.txt"): file.unlink()
# 启动线程调用Fluent软件
fluentProcess = subprocess.Popen(f'"{fluentExe}" 3ddp -aas',
                                 shell=True, cwd=str(workPath))
# 监控aaS_FluentId.txt文件生成，等待corba连接
while True:
    try:
        if not aasFilePath.exists():
            time.sleep(0.2)
            continue
        else:
            if "IOR:" in aasFilePath.open("r").read():
                break
    except KeyboardInterrupt: sys.exit()       
# 初始化orb环境
orb = CORBA.ORB_init()
# 获得fluent服务器会话实例
fluentUnit = orb.string_to_object(aasFilePath.open("r").read())
# 获得scheme脚本控制器实例
scheme = fluentUnit.getSchemeControllerInstance()
# 发送Scheme脚本读入网格文件
result = scheme.execScheme(r'(read-case "base-design.msh")')
# 发送Scheme脚本并返回结果
result = scheme.execSchemeToString('(grid-check)')
# 发送TUI命令并返回结果,与(grid-check)对应
result = scheme.doMenuCommandToString("/mesh/check")
# 设置入口速度大小为0.987m/s
scheme.doMenuCommand("/define/bc/set/velocity inlet () vmag no 0.987 quit")
# 设置迭代步数,并开始计算
fluentUnit.setNrIterations(200)
fluentUnit.calculate()