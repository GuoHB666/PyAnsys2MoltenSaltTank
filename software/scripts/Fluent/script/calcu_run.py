
"""Fluent calculation"""
fluent_tui_file = r"D:\GuoHB\MyFiles\Code\PyAnsysWorkbench\software\scripts\fluent\script\Fluent_tui_command.jou"
jou_command = '/file/read-journal \"{}\" yes yes'.format(fluent_tui_file)
setup_fluent.SendCommand(Command='/file/set-tui-version "21.2"')
setup_fluent.SendCommand(Command=jou_command)
