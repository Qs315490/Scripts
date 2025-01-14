#!/bin/env python3
# -*- coding: utf-8 -*-
from os.path import isfile, exists, getsize
from os import remove
import threading
import paramiko
from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    DownloadColumn,
    TransferSpeedColumn,
)

# SFTP连接信息
hostname = '103.68.183.114'
port = 32022
username = 'open'
password = 'open'

# 要下载的文件信息
remote_file_path = 'sophon-demo/ChatGLM4/models/BM1684X/glm4-9b_int8_1dev.bmodel'
local_file_path = 'glm4-9b_int8_1dev.bmodel'
num_threads = 2  # 定义线程数量
# 定义每个线程下载的块大小
BLOCKSIZE = 1024 * 1024 * 10  # 1MB

BAR_ITEM = (
    TextColumn("[progress.description]{task.description}"),
    BarColumn(bar_width=None),
    DownloadColumn(),
    TransferSpeedColumn(),
    TimeElapsedColumn(),
    TimeRemainingColumn(),
)


# SFTP连接函数
def sftp_connect() -> paramiko.SFTPClient:
    transport = paramiko.Transport((hostname, port))
    transport.banner_timeout = 50
    transport.connect(username=username, password=password)
    back = paramiko.SFTPClient.from_transport(transport)
    assert back is not None, "SFTPClient is None"
    return back


# 下载文件块函数
def download_chunk(
    start,
    end,
    progress: Progress,
    task_id,
    total_task,
):
    sftp = sftp_connect()
    remote_file = sftp.file(remote_file_path, 'rb')
    remote_file.seek(start)

    with open(local_file_path, 'rb+') as local_file:
        local_file.seek(start)
        bytes_written = 0
        # 循环读取文件块并写入本地文件，直到文件末尾
        while bytes_written < (end - start):
            # 计算要读取的块大小，避免最后一次读取超出文件末尾
            chunk_size = min(BLOCKSIZE, end - start - bytes_written)
            chunk = remote_file.read(chunk_size)
            if not chunk:
                break  # 读取完毕

            local_file.write(chunk)
            bytes_written += len(chunk)
            # 更新进度条
            progress.update(task_id, completed=bytes_written)
            progress.update(total_task, advance=chunk_size)

    remote_file.close()
    sftp.close()


# 获取文件大小
def get_file_size() -> int:
    back = sftp.stat(remote_file_path).st_size
    assert back is not None, "file size is None"
    return back


# 创建一个与远程文件大小相同的本地文件
def create_local_file(file_size: int, block_size: int = 1024 * 1024):
    # 进度条
    with Progress(
        *BAR_ITEM,
        expand=True,
    ) as progress:
        # 检测文件是否存在
        if exists(local_file_path):
            if isfile(local_file_path):
                # 获取文件大小
                local_file_size = getsize(local_file_path)
                if local_file_size == file_size:
                    # 文件大小一致，直接返回
                    print(f"本地文件 {local_file_path} 已存在, 大小一致")
                    return
                # 文件大小不一致，询问是否覆盖
                print(f"本地文件 {local_file_path} 已存在, 大小不一致")
                back = input("是否覆盖本地文件? (y/n): ")
                if back.lower() == 'y':
                    print(f"覆盖本地文件 {local_file_path}")
                    remove(local_file_path)

            print(f"本地已存在 {local_file_path} 但不是文件")
            exit(-1)

        task = progress.add_task("创建本地文件", total=file_size)
        # 打开本地文件，如果文件不存在则创建
        with open(local_file_path, 'wb') as f:
            chunk_size = block_size
            bytes_written = 0
            # 循环写入文件，直到文件大小达到目标大小
            while bytes_written < file_size:
                chunk = b'\0' * min(chunk_size, file_size - bytes_written)
                f.write(chunk)
                bytes_written += len(chunk)
                progress.update(task, completed=bytes_written)


# 多线程下载文件
def download_file_concurrently():
    print("获取文件大小")
    file_size = get_file_size()
    assert file_size > 0, "File size is zero or negative"
    print(f"文件大小: {file_size} bytes")
    chunk_size = file_size // num_threads
    threads: list[threading.Thread] = []

    # 创建一个和远程文件大小相同的本地文件
    create_local_file(file_size)

    # 创建进度条
    with Progress(
        *BAR_ITEM,
        expand=True,
    ) as progress:
        tasks = [
            progress.add_task(f"Thread {i}", total=chunk_size)
            for i in range(num_threads)
        ]
        total_task = progress.add_task("总进度", total=file_size)
        # 创建并启动线程
        for i in range(num_threads):
            start = i * chunk_size
            # 最后一个线程下载剩余部分
            end = file_size if i == num_threads - 1 else (i + 1) * chunk_size
            thread = threading.Thread(
                target=download_chunk,
                args=(
                    start,
                    end,
                    progress,
                    tasks[i],
                    total_task,
                ),
            )
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()


# 主程序
if __name__ == "__main__":
    print("开始下载")
    sftp: paramiko.SFTPClient = sftp_connect()
    print("SFTP connected.")
    download_file_concurrently()
    sftp.close()
    print("Download completed.")
