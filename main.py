import json
import os
import shutil
from tqdm import tqdm
import time


def extract_strings(obj, result_list):
    if isinstance(obj, dict):
        for value in obj.values():
            extract_strings(value, result_list)  # 递归处理值
    elif isinstance(obj, list):
        for item in obj:
            extract_strings(item, result_list)  # 递归处理列表中的每个项
    elif isinstance(obj, str):
        result_list.append(obj)  # 添加字符串
    # 修改为只提取字典的值
    elif isinstance(obj, dict):
        for value in obj.values():
            result_list.append(value)  # 直接添加字典的值


# 遍历文件夹并复制特定文件
def copy_files_with_prefix(source_folder, destination_folder, prefixes):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)  # 创建目标文件夹

    print_colored('源文件总数：' + str(len(os.listdir(source_folder))))

    wait_copy_file = []
    for filename in tqdm(os.listdir(source_folder), desc='文件名匹配中'):
        match = False
        for prefix in prefixes:
            if prefix in filename:
                match = True
        if match:
            wait_copy_file.append(filename)

    print_colored('待拷贝文件数量：' + str(len(wait_copy_file)))
    time.sleep(0.1)
    for wait_copyfile_name in tqdm(wait_copy_file, desc='文件拷贝中'):
        source_file = os.path.join(source_folder, wait_copyfile_name)
        destination_file = os.path.join(destination_folder, wait_copyfile_name)
        shutil.copy(source_file, destination_file)  # 复制文件


def print_colored(text, color='blue'):
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'reset': '\033[0m'
    }
    print(f"{colors.get(color, colors['reset'])}{text}{colors['reset']}")


if __name__ == '__main__':
    json_file_path = 'C:\\Users\\l4486\\Desktop\\file\\arena_000_int\\level.json'  # JSON 文件路径
    source_folder_path = 'C:\\Users\\l4486\\Desktop\\file\\arena_000_int'  # 源文件夹路径
    destination_folder_path = 'C:\\Users\\l4486\\Desktop\\file\\copy'  # 目标文件夹路径

    print_colored('开始加载json文件')
    all_keys_and_values = []

    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)  # 解析 JSON 数据
        extract_strings(data, all_keys_and_values)  # 提取所有键和值
    print_colored('加载完毕，开始处理json文件')

    stripped_strings = [s.rsplit('.', 1)[0] for s in tqdm(all_keys_and_values, desc='删除文件中的字符串后缀') if
                        '.' in s]

    print_colored('处理完毕，开始过滤文件')

    copy_files_with_prefix(source_folder_path, destination_folder_path, stripped_strings)  # 复制文件

    os.system('pause')
