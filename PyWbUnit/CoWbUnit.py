# -*- coding: utf-8 -*-
import shutil
from socket import *
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Union
import time
from .Errors import (handleException, CoWbUnitRuntimeError)
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
__all__ = ["CoWbUnitProcess", "WbServerClient", "__version__",
           "__author__"]

__version__ = ".".join(("0", "5", "0"))
__author__ = "GUO HB"


class CoWbUnitProcess:

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
    def __init__(self, wbjpFolder=None, wbpjName="py_ansys.wbpj",version=212, interactive=True):
        """
        Constructor of CoWbUnitProcess.
        :param workDir: str, the directory where the Workbench starts.
        :param version: int, workbench version: 2019R1-190/2020R1-201/2021R1-211.
        :param interactive: bool, whether to display the Workbench interface
        注：变量名前面的下划线"_"代表该变量是私有变量，使得调用者不能轻易访问
        """
        self._wbpj_name = wbpjName
        self._wbjpFolder = Path(wbjpFolder) if wbjpFolder else Path(".") # 当前py文件所在位置
        # self._wbjpFolder = self._workDir / "software"
        self._wbjpFile = self._wbjpFolder / self._wbpj_name
        self._ansysDir = Path(os.environ[f"AWP_ROOT{version}"])
        self._wbExe = self._ansysDir / "Framework" / "bin" / "Win64" / "runwb2.exe" # ansys workbench软件位置
        self._interactive = interactive
        self._process = None
        self._coWbUnit = None
        self.clean_wbjp_folder(self._wbjpFolder,self._wbpj_name.split(".")[0])
        if f"AWP_ROOT{version}" not in os.environ:
            raise CoWbUnitRuntimeError(f"ANSYS version: v{version} is not installed!")
    def clean_wbjp_folder(self, base_path, key_name):
        """
        删除 base_path 下包含 target_string 的所有文件和文件夹。

        :param base_path: 要搜索的基路径
        :param key_name: 要搜索的字符串片段
        """
        base_path = Path(base_path)
        # 删除匹配的文件
        for file_path in base_path.rglob('*'):
            if file_path.is_file() and key_name in file_path.name:
                print(f"Deleting file: {file_path}")
                file_path.unlink()
        # 删除匹配的文件夹
        for dir_path in base_path.rglob('*'):
            if dir_path.is_dir() and key_name in dir_path.name:
                print(f"Deleting directory: {dir_path}")
                shutil.rmtree(dir_path)
    def simulation_run(self, script_multiphysics):
        try:
            # 发送初始化信号，并进行初始化
            self.initialize()
            # 保存数据
            self.saveProject(str(self._wbjpFile.absolute()))
            # 开展计算
            cmd = f"RunScript(FilePath=\"{script_multiphysics}\")"
            self.execWbCommand(cmd)
            # 计算完成、退出
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
        aasFile = self._wbjpFolder / self._aasName
        self._clear_aasFile()
        stateOpt = fr'''-p "[9000:9200]" --server-write-connection-info "{aasFile}"'''
        batchArgs = fr'"{self._wbExe}" -I {stateOpt}' if self._interactive else fr'"{self._wbExe}" -s {stateOpt}'
        # 启动ansys workbench的批处理命令
        self._process = subprocess.Popen(batchArgs, cwd=str(self._wbjpFolder.absolute()),
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # 建立连接
        self._coWbUnit = WbServerClient(self._readWbId())

    def _clear_aasFile(self):
        aasFile = self._wbjpFolder / self._aasName
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
        aasFile = self._wbjpFolder / self._aasName
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
