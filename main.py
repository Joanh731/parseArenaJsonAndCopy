import json
import os
import shutil
from tqdm import tqdm
import time
from colorama import Fore, Style
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 创建一个线程锁，用于线程安全地更新进度
lock = threading.Lock()

from colorama import init

init()


# 自定义拷贝文件函数
def copy_file(src, dst, progress_bar):
    try:
        shutil.copy2(src, dst)
        progress_bar.update(1)  # 更新进度条
        return f"文件 {src} 成功复制到 {dst}"
    except Exception as e:
        return f"复制文件 {src} 时出错: {e}"


# 使用线程池并显示每个线程的进度
def multi_thread_copy(file_list, dst_dir, max_workers=10):
    # 确保目标目录存在
    os.makedirs(dst_dir, exist_ok=True)

    # 创建全局的进度条，管理所有文件
    with tqdm(total=len(file_list), desc="总体进度", unit="file") as pbar:
        # 使用线程池
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(copy_file, file, os.path.join(dst_dir, os.path.basename(file)), pbar) for file in
                       file_list]

            # 等待所有任务完成
            for future in futures:
                future.result()

# # 自定义拷贝文件函数
# def copy_file(src, dst):
#     try:
#         shutil.copy2(src, dst)
#         return f"文件 {src} 成功复制到 {dst}"
#     except Exception as e:
#         return f"复制文件 {src} 时出错: {e}"
#
#
# # 线程的任务，带有进度条
# def thread_task(file_list, dst_dir, progress_bar):
#     for file in file_list:
#         # 源文件路径和目标文件路径
#         src_file = file
#         dst_file = os.path.join(dst_dir, os.path.basename(file))
#
#         # 拷贝文件
#         copy_file(src_file, dst_file)
#
#         # 每复制一个文件，更新一次进度条
#         with lock:
#             progress_bar.update(1)
#
#
# # 使用线程池并显示每个线程的进度
# def multi_thread_copy(file_list, dst_dir, max_workers=10):
#     # 确保目标目录存在
#     os.makedirs(dst_dir, exist_ok=True)
#
#     # 将文件列表分割为多个子列表，每个子列表交给一个线程
#     chunk_size = len(file_list) // max_workers
#     file_chunks = [file_list[i:i + chunk_size] for i in range(0, len(file_list), chunk_size)]
#
#     # 创建全局的进度条
#     with ThreadPoolExecutor(max_workers=max_workers) as executor:
#         # 为每个线程分配一个独立的进度条
#         thread_bars = []
#         for i in range(len(file_chunks)):
#             # 创建一个进度条，表示线程的任务进度
#             progress_bar = tqdm(total=len(file_chunks[i]), desc=f"线程 {i + 1}", position=i, leave=True)
#             thread_bars.append(progress_bar)
#
#         # 提交任务给线程池，分配文件列表的不同部分给每个线程
#         futures = [executor.submit(thread_task, file_chunks[i], dst_dir, thread_bars[i]) for i in
#                    range(len(file_chunks))]
#
#         # 等待所有线程完成
#         for future in futures:
#             future.result()
#
#         # 关闭所有进度条
#         for bar in thread_bars:
#             bar.close()


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
    for filename in tqdm(os.listdir(source_folder), desc=Fore.RED + '文件名匹配中'):
        match = False
        for prefix in prefixes:
            if prefix in filename:
                match = True
        if match:
            wait_copy_file.append(filename)

    print_colored('待拷贝文件数量：' + str(len(wait_copy_file)))
    time.sleep(0.1)

    # 常识多线程拷贝
    wait_copy_file = [os.path.join(source_folder, s) for s in wait_copy_file]
    multi_thread_copy(wait_copy_file, destination_folder)

    # 单进程拷贝
    # for wait_copyfile_name in tqdm(wait_copy_file, desc=Fore.CYAN+'文件拷贝中'):
    #     source_file = os.path.join(source_folder, wait_copyfile_name)
    #     destination_file = os.path.join(destination_folder, wait_copyfile_name)
    #     shutil.copy(source_file, destination_file)  # 复制文件


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
    json_file_path = '.\\arena_000_int\\level.SCNE'  # JSON 文件路径
    source_folder_path = '.\\arena_000_int'  # 源文件夹路径
    destination_folder_path = '.\\copy'  # 目标文件夹路径

    print_colored('开始加载json文件')
    all_keys_and_values = []

    # 读取文件内容
    with open(json_file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # 为内容添加大括号
    fixed_content = "{" + content + "}"
    # 解析为JSON
    try:
        json_data = json.loads(fixed_content)  # 解析 JSON 数据
        extract_strings(json_data, all_keys_and_values)  # 提取所有键和值
        print_colored('加载完毕，开始处理json文件')

        stripped_strings = [s.rsplit('.', 1)[0]
                            for s in tqdm(all_keys_and_values, desc=Fore.GREEN + '删除文件中的字符串后缀') if
                            '.' in s]

        print_colored('处理完毕，开始过滤文件')

        copy_files_with_prefix(source_folder_path, destination_folder_path, stripped_strings)  # 复制文件

        os.system('pause')
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
