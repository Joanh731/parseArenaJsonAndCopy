import os
import shutil
from tqdm import tqdm
import time
from colorama import Fore
from concurrent.futures import ThreadPoolExecutor


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


def single_thread_copy(file_list, source_folder, dst_dir):
    """
    单线程拷贝
    :param file_list:
    :param source_folder:
    :param dst_dir:
    :return:
    """
    for wait_copyfile_name in tqdm(file_list, desc=Fore.CYAN + '文件拷贝中'):
        source_file = os.path.join(source_folder, wait_copyfile_name)
        destination_file = os.path.join(dst_dir, wait_copyfile_name)
        shutil.copy(source_file, destination_file)  # 复制文件


# 遍历文件夹并复制特定文件
def copy_files_with_prefix(source_folder, destination_folder, prefixes):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)  # 创建目标文件夹

    print('源文件总数：' + str(len(os.listdir(source_folder))))

    wait_copy_file = []
    for filename in tqdm(os.listdir(source_folder), desc=Fore.RED + '文件名匹配中'):
        match = False
        for prefix in prefixes:
            if prefix in filename:
                match = True
        if match:
            wait_copy_file.append(filename)

    print('待拷贝文件数量：' + str(len(wait_copy_file)))
    time.sleep(0.1)

    # 常识多线程拷贝
    wait_copy_file = [os.path.join(source_folder, s) for s in wait_copy_file]
    multi_thread_copy(wait_copy_file, destination_folder)


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

    print(extracted_values)

    copy_files_with_prefix(source_folder_path, destination_folder_path, extracted_values)
