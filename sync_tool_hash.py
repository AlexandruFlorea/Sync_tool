import os
import time
import hashlib
import shutil
import argparse


# Logging function
def log(message, log_file, log_type, recursive=False):
    if not recursive or log_type == 'change':
        timestamp = time.strftime('[%Y-%m-%d %H:%M:%S] ', time.localtime())
        log_entry = timestamp + message
        print(log_entry)
        with open(log_file, 'a') as file:
            file.write(log_entry + '\n')


# File hash comparison
def compare_file_hash(file1, file2):
    with open(file1, 'rb') as f1:
        with open(file2, 'rb') as f2:
            if hashlib.md5(f1.read()).hexdigest() == hashlib.md5(f2.read()).hexdigest():
                return True
            else:
                return False


# Folder comparison
def compare_folder_hash(source_folder, replica_folder):
    source_files = os.listdir(source_folder)
    replica_files = os.listdir(replica_folder)
    if len(source_files) != len(replica_files):
        return False

    for file in source_files:
        if file in replica_files:
            if not compare_file_hash(os.path.join(source_folder, file),
                                     os.path.join(replica_folder, file)):
                return False
        else:
            return False
    return True


# Command line argument reader
def parse_arguments():
    parser = argparse.ArgumentParser(description='Data synchronization')
    parser.add_argument('source_folder', help='Path to the source folder')
    parser.add_argument('replica_folder', help='Path to the replica folder')
    parser.add_argument('interval', type=int, help='Synchronization interval in seconds')
    parser.add_argument('log_file', help='Path to the log file')
    return parser.parse_args()


# Recursive folder synchronization function
def folder_sync(source_folder, replica_folder, log_file, recursive=False):
    # Log entry only when starting sync
    if not recursive:
        log('Starting data synchronization.', log_file, log_type='info')

    # Compare files and sub-folders
    source_files = os.listdir(source_folder)
    replica_files = os.listdir(replica_folder)

    # Check replica folder for deleted files and sub-folders
    for file in replica_files:
        replica_path = os.path.join(replica_folder, file)
        source_path = os.path.join(source_folder, file)

        if file in source_files:
            if os.path.isdir(source_path):
                if os.path.isdir(replica_path):
                    # Recursively sync sub-folder
                    folder_sync(source_path, replica_path, log_file, recursive=True)
                else:
                    # Remove file and copy sub-folder
                    os.remove(replica_path)
                    shutil.copytree(source_path, replica_path)
                    # Pass the value of the recursive parameter from the folder_sync function to the log function
                    log(f'"{file}" updated at "{replica_path}".', log_file, log_type='change', recursive=recursive)
            else:
                if not compare_file_hash(source_path, replica_path):
                    # Remove file and copy new version
                    os.remove(replica_path)
                    shutil.copy2(source_path, replica_path)
                    log(f'"{file}" updated at "{replica_path}".', log_file, log_type='change', recursive=recursive)
        else:
            if os.path.isdir(replica_path):
                # Remove sub-folder
                shutil.rmtree(replica_path)
            else:
                # Remove file
                os.remove(replica_path)
            log(f'"{file}" deleted from "{replica_path}".', log_file, log_type='change', recursive=recursive)

    # Check source folder for new files and sub-folders
    for file in source_files:
        source_path = os.path.join(source_folder, file)
        replica_path = os.path.join(replica_folder, file)

        if file not in replica_files:
            if os.path.isdir(source_path):
                # Copy new sub-folder
                shutil.copytree(source_path, replica_path)
            else:
                # Copy new file
                shutil.copy2(source_path, replica_path)
            log(f'"{file}" copied from "{source_path}" to "{replica_path}".',
                log_file, log_type='change', recursive=recursive)
    if not recursive:
        log('Data synchronization complete.', log_file, log_type='info')


def main():
    args = parse_arguments()

    while True:
        folder_sync(args.source_folder, args.replica_folder, args.log_file)
        time.sleep(args.interval)  # Sync interval


if __name__ == '__main__':
    main()
