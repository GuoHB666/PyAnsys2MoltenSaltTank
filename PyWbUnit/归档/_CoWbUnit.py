# -*- coding: utf-8 -*-
import shutil
from socket import *
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Union
import time
from ._Errors import (handleException, CoWbUnitRuntimeError)
from PyQt5.QtCore import QObject, pyqtSignal, QThread

__all__ = ["CoWbUnitProcess", "WbServerClient", "__version__",
           "__author__"]

__version__ = ".".join(("0", "5", "0"))
__author__ = "GUO HB"


class CoWbUnitProcess(QObject):

    """Unit class for co-simulation with Workbench using Python.
    >>> coWbUnit = CoWbUnitProcess()
    >>> coWbUnit.initialize()
    >>> command = 'GetTemplate(TemplateName="Static Structural", Solver="ANSYS").CreateSystem()'
    >>> coWbUnit.execWbCommand(command)
    >>> coWbUnit.execWbCommand('systems=GetAllSystems()')
    >>> print(coWbUnit.queryWbVariable('systems'))
    >>> coWbUnit.saveProject(r'D:/example.wbpj')
    >>> coWbUnit.finalize()
    """
    _aasName = "aaS_WbId.txt"
    progressChanged = pyqtSignal(int) # 创建一个自定义信号 progressChanged，这个信号用于向主线程发送进度信息
    def __init__(self, workDir=None, wbpjName="py_ansys.wbpj",version=212, interactive=True):
        """
        Constructor of CoWbUnitProcess.
        :param workDir: str, the directory where the Workbench starts.
        :param version: int, workbench version: 2019R1-190/2020R1-201/2021R1-211.
        :param interactive: bool, whether to display the Workbench interface
        注：变量名前面的下划线"_"代表该变量是私有变量，使得调用者不能轻易访问
        """
        super().__init__()
        self._wbpj_name = wbpjName
        self._workDir = Path(workDir) if workDir else Path(".") # 当前py文件所在位置
        self._wbjpFolder = self._workDir / "software"
        self._wbjpFile = self._wbjpFolder / self._wbpj_name
        self._geo_folder = self._wbjpFolder / "geometry"
        self._ansysDir = Path(os.environ[f"AWP_ROOT{version}"])
        self._wbExe = self._ansysDir / "Framework" / "bin" / "Win64" / "runwb2.exe" # ansys workbench软件位置
        self._interactive = interactive
        self._process = None
        self._coWbUnit = None
        #self.scripts_path = self.get_scripts_path()
        self.scripts_path = self.get_scripts_path_fluent()
        if f"AWP_ROOT{version}" not in os.environ:
            raise CoWbUnitRuntimeError(f"ANSYS version: v{version} is not installed!")
    def get_scripts_path(self):
        script_foder = self._wbjpFolder / "scripts"
        script_names = ["systems_building.py", "geo_creation.py","geo_import.py",
                        "mat_creations.py","calcu_launch.py", "calcu_run.py"]
        scripts = [str((script_foder / name).absolute()) for name in script_names]
        return scripts
    def get_scripts_path_fluent(self):
        script_foder = self._wbjpFolder / "scripts" / "Fluent" / "script"
        script_names = ["systems_building.py", "geo_creation.py","geo_import.py",
                        "meshing.py", "calcu_launch.py", "calcu_run.py"]
        scripts = [str((script_foder / name).absolute()) for name in script_names]
        return scripts
    def simula_system_run(self):
        try:
            # 发送初始化信号，并进行初始化
            self.progressChanged.emit(0)
            self.initialize()
            # ! 按顺序依次展开建模、计算
            for count,script_path in enumerate(self.scripts_path):
                # 发送信号，将当前进度发送给主线程
                self.progressChanged.emit(count+1)
                # 获取脚本、生成命令、执行
                if count == 1:
                    self.geo_modeling(script_path)
                else:
                    cmd = "RunScript(FilePath=\"%s\")" % script_path
                    self.execWbCommand(cmd)
            self.progressChanged.emit(len(self.scripts_path) - 1 + 2) # 最终的进度需考虑到不在for循环里的两次计数
            self.finalize()
        except Exception as e:
            print("An exception occurred:", e)
    def initialize(self) -> None:
        """Called before `execWbCommand`: Start the Workbench in interactive
        mode and open the TCP server port to create a socket connection
        :return: None
        """
        # 打开AnsysWorkbench
        if self._coWbUnit is not None:
            raise RuntimeError("Workbench client already started!")
        aasFile = self._workDir / self._aasName
        self._clear_aasFile()
        stateOpt = fr'''-p "[9000:9200]" --server-write-connection-info "{aasFile}"'''
        batchArgs = fr'"{self._wbExe}" -I {stateOpt}' if self._interactive else fr'"{self._wbExe}" -s {stateOpt}'
        # 启动ansys workbench的批处理命令
        self._process = subprocess.Popen(batchArgs, cwd=str(self._workDir.absolute()),
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # 建立连接
        self._coWbUnit = WbServerClient(self._readWbId())
    def geo_modeling(self,geo_script):
        # 确定建模软件、几何模型及其建模脚本的路径
        geo_folder = self._wbjpFolder / "geometry" # 这个路径得和建模脚本中生成的几何模型保存位置相对应，还得精细修改
        scdm_path = str((self._ansysDir / "scdm").absolute())
        # 创建存放几何模型的文件夹
        geo_folder.mkdir(parents=True, exist_ok=True)
        # 启动SpaceClaim软件并根据输入的几何建模脚本，创建几何
        stateOpt = r" /Headless=True /Splash=False /Welcome=False /ExitAfterScript=True"
        batchArgs = 'SpaceClaim.exe /RunScript=' + geo_script + stateOpt
        subprocess.run(batchArgs, shell=True, cwd=scdm_path, stdout=subprocess.DEVNULL)
    def _clear_aasFile(self):
        aasFile = self._workDir / self._aasName
        if aasFile.exists(): aasFile.unlink()
    def execWbCommand(self, command: str) -> str:
        """Send python script command to the Workbench for execution
        :param command: str, python script command
        :return: str, execution result
        """
        if self._coWbUnit is None:
            raise CoWbUnitRuntimeError("Please initialize() first!")
        return self._coWbUnit.execWbCommand(command)

    def queryWbVariable(self, variable: str):
        """Query the value of `variable` in the workbench script environment
        :param variable: str, script variable name
        :return: str
        """
        return self._coWbUnit.queryWbVariable(variable)

    def terminate(self):
        """Terminates the current Workbench client process
        :return: bool
        """
        if self._process:
            try:
                self._process.terminate()
                tempDir = tempfile.mkdtemp()
                filePath = os.path.join(tempDir, "temp.wbpj")
                self.saveProject(filePath)
                self.finalize()
                while True:
                    try:
                        shutil.rmtree(tempDir)
                        break
                    except OSError:
                        time.sleep(2)
                return True
            except PermissionError:
                return False
    def finalize(self):
        """
        Exit the current workbench and close the TCP Server connection
        :return: None
        """
        # self.saveProject()
        self.saveProject(str(self._wbjpFile.absolute())) # _wbjpFile是Path对象，即使转换成绝对路径，也不是字符串
        self.exitWb()
        self._clear_aasFile()
        self._process = None
        self._coWbUnit = None
    def saveProject(self, filePath=None, overWrite=True):
        """Save the current workbench project file to `filePath`
        If the Project has not been saved, using method: `saveProject()`
        will raise `CommandFailedException`
        :param filePath: Optional[str, None], if
        :param overWrite: bool, Whether to overwrite the original project
        :return: str, execution result
        """
        if filePath is None:
            return self.execWbCommand(f'Save(Overwrite={overWrite})')
        return self.execWbCommand(f'Save(FilePath={filePath!r}, Overwrite={overWrite})')

    def finalize(self):
        """
        Exit the current workbench and close the TCP Server connection
        :return: None
        """
        # self.saveProject()
        self.saveProject(str(self._wbjpFile.absolute())) # _wbjpFile是Path对象，即使转换成绝对路径，也不是字符串
        self.exitWb()
        self._clear_aasFile()
        self._process = None
        self._coWbUnit = None

    def exitWb(self) -> str:
        """
        `Exit` the current Workbench client process
        :return: str
        """
        return self.execWbCommand("Exit")

    def _readWbId(self) -> Union[str, None]:
        if not self._process: return None
        aasFile = self._workDir / self._aasName
        while True:
            if not aasFile.exists():
                time.sleep(0.5)
                continue
            with aasFile.open("r") as data:
                for line in data:
                    if 'localhost' in line:
                        return line
class WbServerClient:
    """Client Class for the Workbench server connection
    >>> aas_key = 'localhost:9000'
    >>> wbClient = WbServerClient(aas_key)
    >>> wbClient.execWbCommand('<wb_python_command>')
    >>> print(wbClient.queryWbVariable('<wb_python_var>'))
    """
    _suffix = '<EOF>'
    _coding = 'UTF-8'
    _buffer = 1024

    def __init__(self, aasKey: str):
        aasList = aasKey.split(':')
        self._address = (aasList[0], int(aasList[1]))

    def execWbCommand(self, command: str) -> str:
        sockCommand = command + self._suffix

        with socket(AF_INET, SOCK_STREAM) as sock:
            sock.connect(self._address)
            sock.sendall(sockCommand.encode(self._coding))
            data = sock.recv(self._buffer).decode()

        if data != '<OK>' and 'Exception:' in data:
            raise handleException(data)
        return data

    def queryWbVariable(self, variable) -> str:
        self.execWbCommand("__variable__=" + variable + ".__repr__()")
        retValue = self.execWbCommand("Query,__variable__")
        return retValue[13:]
