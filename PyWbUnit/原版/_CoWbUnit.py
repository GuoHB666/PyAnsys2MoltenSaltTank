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

__all__ = ["CoWbUnitProcess", "WbServerClient", "__version__",
           "__author__"]

__version__ = ".".join(("0", "3", "0"))
__author__ = "GUO HB"


class CoWbUnitProcess(object):

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
    def __init__(self, workDir=None, wbpjName="py_ansys.wbpj",version=212, interactive=True):
        """
        Constructor of CoWbUnitProcess.
        :param workDir: str, the directory where the Workbench starts.
        :param version: int, workbench version: 2019R1-190/2020R1-201/2021R1-211.
        :param interactive: bool, whether to display the Workbench interface
        注：变量名前面的下划线"_"代表该变量是私有变量，使得调用者不能轻易访问
        """
        self._workDir = Path(workDir) if workDir else Path(".") # 当前py文件所在位置
       # self._geo_folder = self._workDir / "geometry"
        self._wbjpFolder = self._workDir / "software"
        self._geo_folder = self._wbjpFolder / "geometry"
        self._wbpj_name = wbpjName
        self._wbjpFile = self._wbjpFolder / self._wbpj_name
        if f"AWP_ROOT{version}" not in os.environ:
            raise CoWbUnitRuntimeError(f"ANSYS version: v{version} is not installed!")
        self._ansysDir = Path(os.environ[f"AWP_ROOT{version}"])
        self._wbExe = self._ansysDir / "Framework" / "bin" / "Win64" / "runwb2.exe" # ansys workbench软件位置
        self._setting = None # UI界面设置的定义，之后再完善。
        self._interactive = interactive
        self._process = None
        self._coWbUnit = None
        self.material_script = None
        self.geo_script = None
        self.mech_launch_script = None
        self.mech_calcu_script = None
        # 生成执行脚本
        self.script_generation()
    def simula_system_run(self):
        self._initialize()          # ! 和Ansys Workbench建立连接
        self._simula_sys_creat()    # ! 创建仿真系统
        self._mat_import()          # ! 创建材料
        self._geo_modeling()        # ! 创建几何
        self._simula_sys_cal()      # ! 开展模拟计算
        self.finalize()             # ! 项目退出
    def _initialize(self) -> None:
        """Called before `execWbCommand`: Start the Workbench in interactive
        mode and open the TCP server port to create a socket connection
        :return: None
        """
        # 打开AnsysWorkbench并建立连接
        if self._coWbUnit is not None:
            raise RuntimeError("Workbench client already started!")
        self._start_workbecnh()
        self._coWbUnit = WbServerClient(self._readWbId())
    def _start_workbecnh(self):
        aasFile = self._workDir / self._aasName
        self._clear_aasFile()
        stateOpt = fr'''-p "[9000:9200]" --server-write-connection-info "{aasFile}"'''
        if self._interactive:
            batchArgs = fr'"{self._wbExe}" -I {stateOpt}'
        else:
            batchArgs = fr'"{self._wbExe}" -s {stateOpt}'
        # 启动ansys workbench的批处理命令
        self._process = subprocess.Popen(batchArgs, cwd=str(self._workDir.absolute()),
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    def script_generation(self,calcu_type="structural"):
        if calcu_type=="structural":
            # 脚本创建
            self.material_script = r'''
            # 创建静结构分析流程
            # 获得Engineering Data数据容器
            engData = mechSys.GetContainer(ComponentName="Engineering Data")
            # 封装创建材料的方法
            def CreateMaterial(name, density, *elastic):
                mat = engData.CreateMaterial(Name=name)
                mat.CreateProperty(Name="Density").SetData(Variables=["Density"],
                    Values=[["%s [kg m^-3]" % density]])
                elasticProp = mat.CreateProperty(Name="Elasticity", Behavior="Isotropic")
                elasticProp.SetData(Variables=["Young's Modulus"], Values=[["%s [MPa]" % elastic[0]]])
                elasticProp.SetData(Variables=["Poisson's Ratio"], Values=[["%s" % elastic[1]]])

            # 创建材料Steel，密度：7850kg/m3，杨氏模量：208e3MPa，泊松比：0.3
            CreateMaterial("Steel", 7850, 209.e3, 0.3)'''
            self.geo_script = r'''
            # Python Script, API Version = V18
            # 定义函数：通过坐标点选择面对象
            def GetFaceObjByPt(pt):
                for face in GetRootPart().GetDescendants[IDesignFace]():
                    if face.Shape.ContainsPoint(pt): return face
            # 创建悬臂梁实体区域
            BlockBody.Create(Point.Origin, Point.Create(MM(200), MM(25), MM(20)))
            GetRootPart().SetName("Beam")
            # 选择beam实体，用于后续材料赋予
            Selection.Create(GetRootPart().Bodies).CreateAGroup("ns_beamBody")
            # 定义固定约束加载面并为其命名
            fixSupFace = GetFaceObjByPt(Point.Create(0, MM(12.5), MM(10)))
            Selection.Create(fixSupFace).CreateAGroup("ns_fixSup")
            # 定义压力载荷加载面并为其命名
            pressFace = GetFaceObjByPt(Point.Create(MM(50), MM(12.5), MM(20)))
            Selection.Create(pressFace).CreateAGroup("ns_press")
            '''
            self.mech_launch_script = r'''
            # 刷新Model Component数据
            modelComp = mechSys.GetComponent(Name="Model")
            modelComp.Refresh()
            # 获得Mechanical中Model的数据容器
            model = mechSys.GetContainer(ComponentName="Model")
            model.Edit(Hidden=True)
            '''
            self.mech_calcu_script = r'''
            # encoding: utf-8
            # 基于名称选中对应面
            def GetLocByName(ns_name):
                for ns in Model.NamedSelections.Children:
                    if ns.Name == ns_name: return ns
            # 指定材料
            matAss = Model.Materials.AddMaterialAssignment()
            matAss.Material = "Steel"
            matAss.Location = GetLocByName("ns_beamBody")
            # 划分网格
            mesh = Model.Mesh
            mesh.ElementSize = Quantity("10 [mm]")
            mesh.GenerateMesh()
            # 获得Analyses对象
            analysis = Model.Analyses[0]
            # 添加固定约束
            fixSup = analysis.AddFixedSupport()
            fixSup.Location= GetLocByName("ns_fixSup")
            # 加载压力载荷
            pressLoad = analysis.AddPressure()
            pressLoad.Location = GetLocByName("ns_press")
            pressLoad.Magnitude.Output.DiscreteValues = [Quantity("0.5 [MPa]")]
            # 求解
            Model.Solve()
            # 后处理操作
            solution = analysis.Solution
            misesResult = solution.AddEquivalentStress()
            misesResult.EvaluateAllResults()
            # 设置视角
            camera = ExtAPI.Graphics.Camera
            camera.UpVector = Vector3D(0,0,1)
            camera.SceneWidth = Quantity("150 [mm]")
            camera.SceneHeight = Quantity("120 [mm]")
            camera.FocalPoint = Point((0.08,0.0125,0), 'm')
            # 输出后处理云图
            misesResult.Activate()
            ExtAPI.Graphics.ExportImage("%s")''' % str(self._workDir.absolute())
            # 缩进处理
            self.material_script = self._raw_script_process(self.material_script)
            self.geo_script = self._raw_script_process(self.geo_script)
            self.mech_launch_script = self._raw_script_process(self.mech_launch_script)
            self.mech_calcu_script = self._raw_script_process(self.mech_calcu_script)
        elif calcu_type=="thermal_structural":
            pass
        else:
            pass
    def _geo_modeling(self, geo_name='geo.scdoc', geo_pyname='geo.py'):
        # 确定建模软件、几何模型及其建模脚本的路径
        geo_py_file = str((self._geo_folder / geo_pyname).absolute())
        geo_file = str((self._geo_folder / geo_name).absolute())
        scdm_path = str(self._ansysDir / "scdm")
        # 创建相应的文件夹
        self._geo_folder.mkdir(parents=True, exist_ok=True)
        # 修正几何建模脚本：加上保存路径
        geoScript = """# 保存文件\noptions = ExportOptions.Create()\nDocumentSave.Execute(r"%s", options)""" \
                     % geo_file
        geo_script = self.geo_script + geoScript
        # 创建生成几何模型的py文件
        with open(geo_py_file, 'w', encoding="utf-8") as f:
            f.write(geo_script)
        # 启动SpaceClaim软件并创建几何
        stateOpt = r" /Headless=True /Splash=False /Welcome=False /ExitAfterScript=True"
        batchArgs = 'SpaceClaim.exe /RunScript=' + geo_py_file + stateOpt
        subprocess.run(batchArgs, shell=True, cwd=scdm_path, stdout=subprocess.DEVNULL)

        # 将几何模型导入Ansys Workbench
        self.execWbCommand('geo=mechSys.GetContainer("Geometry")')
        self.execWbCommand('geo.SetFile(FilePath="%s")' % geo_file)
    def _simula_sys_creat(self):
        command = 'mechSys = GetTemplate(TemplateName="Static Structural", Solver="ANSYS").CreateSystem()'
        self.execWbCommand(command)
        self.execWbCommand('systems=GetAllSystems()')
    def _simula_sys_cal(self):
        cal_launch_command = self.mech_launch_script
        cal_content_command = f'model.SendCommand(Language="Python", Command={self.mech_calcu_script!r})'
        cal_finish_command = 'model.Exit()'
        self.execWbCommand(cal_launch_command)
        self.execWbCommand(cal_content_command)
        self.execWbCommand(cal_finish_command)
    def _mat_import(self):
        self.execWbCommand(self.material_script)
    def _raw_script_process(self, raw_script):
        # 分割字符串为行列表
        old_lines = raw_script.split('\n')[1:]  # 将多行字符串按行分割，同时去除掉空行1
        # 计算开头制表符的数量
        nrof_space = len(old_lines[0]) - len(old_lines[0].lstrip())
        new_lines = [line[nrof_space:] for line in old_lines]
        # 重新拼接处理后的行
        new_strs = '\n'.join(new_lines)
        return new_strs

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
