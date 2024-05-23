def script_builder(script_paths, cmd_key, cmd_complete):
    is_success = False
    file_origin = script_paths[0]
    file_new = script_paths[1]
    with open(file_origin, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    # 遍历每一行，查找需要修改的内容
    for i, line in enumerate(lines):
        if cmd_key in line:
            lines[i] = cmd_complete
            is_success = True
            break
    if is_success:
        # 生成新文件
        with open(file_new, 'w', encoding='utf-8') as file:
            file.writelines(lines)
    return is_success