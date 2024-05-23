import sys
from PyQt5.QtWidgets import QApplication
from ui.PyAnsysUI import PyAnsysUI # 调动ui文件夹下的PyAnsysUI文件里的PyAnsysUI类
from pathlib import Path


if __name__ == "__main__":
    root_path_prj = Path(__file__).parent
    try:
        App = QApplication(sys.argv)
        py_ansys_ui = PyAnsysUI(root_path_prj)
        py_ansys_ui.ui.show()
        sys.exit(App.exec())
    except Exception as e:
        print("An exception occurred:", e)