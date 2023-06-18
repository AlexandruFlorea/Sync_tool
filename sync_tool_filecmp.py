import os
import time
import hashlib
import filecmp
import shutil
import argparse


# Logging function
def log(message, log_file):
    timestamp = time.strftime('[%Y-%m-%d %H:%M:%S] ', time.localtime())
    log_entry = timestamp + message

    print(log_entry)
    with open(log_file, 'a') as file:
        file.write(log_entry + '\n')


# Hash generator
def get_file_md5(file_path):
    with open(file_path, 'rb') as file:
        md5_hash = hashlib.md5()
        for chunk in iter(lambda: file.read(4096), b''):
            md5_hash.update(chunk)
        return md5_hash.hexdigest()


# Command line argument reader
def parse_arguments():
    parser = argparse.ArgumentParser(description='Data synchronisation')
    parser.add_argument('source_folder', help='Path to the source folder')
    parser.add_argument('replica_folder', help='Path to the replica folder')
    parser.add_argument('interval', type=int, help='Synchronisation interval in seconds')
    parser.add_argument('log_file', help='Path to the log file')
    return parser.parse_args()


# Synchronisation function
def folder_sync(source_folder, replica_folder, log_file):
    log('Starting data synchronisation.', log_file)

    data_comparison = filecmp.dircmp(source_folder, replica_folder)

    # Copying updated files
    updated_files = data_comparison.left_only + data_comparison.diff_files
    for source_file in updated_files:
        source_path = os.path.join(source_folder, source_file)
        destination_path = os.path.join(replica_folder, source_file)
        if os.path.isdir(source_path):
            shutil.copytree(source_path, destination_path)
        else:
            shutil.copy2(source_path, destination_path)  # Copy, preserving metadata
        log(f'Copied {source_path} to {destination_path}', log_file)

    # Delete files
    deleted_files = data_comparison.right_only + data_comparison.funny_files
    for deleted_file in deleted_files:
        delete_path = os.path.join(replica_folder, deleted_file)
        if os.path.isdir(delete_path):
            shutil.rmtree(delete_path)  # Remove dirs recursively
        else:
            os.remove(delete_path)
        log(f'Deleted {delete_path}', log_file)

    # Subdirectory sync
    for subdir in data_comparison.subdirs:
        folder_sync(os.path.join(source_folder, subdir),
                    os.path.join(replica_folder, subdir), log_file)

    log('Data synchronisation complete.', log_file)


def main():
    args = parse_arguments()

    while True:
        folder_sync(args.source_folder, args.replica_folder, args.log_file)
        time.sleep(args.interval)  # Sync interval


if __name__ == '__main__':
    main()
