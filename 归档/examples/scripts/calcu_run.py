# encoding: utf-8
calcu_content_path = "D:\GuoHB\MyFiles\Code\PyAnsysWorkbench\examples\scripts\calcu_content.py"
calcu_content = open(calcu_content_path,'r').read()
model.SendCommand(Language="Python", Command=calcu_content)
model.Exit()
