import os


def get_files_with_size(directory):
    files_with_size = []

    # 遍历目录下的所有文件
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            files_with_size.append((file, file_size))

    return files_with_size


def sort_files_by_size(files_with_size):
    # 按文件大小排序
    return sorted(files_with_size, key=lambda x: x[1], reverse=True)[:100]


def print_sorted_files(files_with_size):
    for file, size in files_with_size:
        size_in_mb = size / (1024 * 1024)
        print(f"{file}: {size_in_mb:.2f} MB")


if __name__ == "__main__":
    directory = input("请输入要查看的目录路径: ")
    if not os.path.isdir(directory):
        print(f"{directory} 不是一个有效的目录路径")
    else:
        files_with_size = get_files_with_size(directory)
        sorted_files = sort_files_by_size(files_with_size)
        print_sorted_files(sorted_files)
