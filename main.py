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
        for key, value in obj.items():
            if isinstance(key, str) and (key.__eq__("Script") or key.__eq__("Binary")):
                print(value)
                result_list.append(value)
            else:
                extract_strings(value, result_list)  # 递归处理值


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

    # 打开并读取文件
    with open(json_file_path, 'r') as file:
        lines = file.readlines()

    # 用于存储提取的结果
    extracted_values = []

    # 处理每一行
    for line in lines:
        # 去掉行首空白
        line = line.lstrip()
        # 检查是否包含 "Script" 或 "Binary"
        if '"Script"' in line or '"Binary"' in line:
            # 提取引号中的内容
            value = line.split(':')[-1].strip().strip('"')
            # 去掉后缀
            value = value.rsplit('.', 1)[0]  # 去掉最后一个点及其后的部分
            extracted_values.append(value)

    # 保存提取的内容到 source.txt
    with open('source.txt', 'w') as output_file:
        for item in extracted_values:
            output_file.write(f"{item}\n")

    print("提取的内容已保存到 source.txt 中。")

    # 读取文件内容
    with open('.\\source.txt', "r", encoding="utf-8") as file:
        all_keys_and_values = [line.strip() for line in file.readlines()]

    print(all_keys_and_values)

    copy_files_with_prefix(source_folder_path, destination_folder_path, all_keys_and_values)  # 复制文件
