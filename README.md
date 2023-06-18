# Synchronisation tool

This is a program that synchronises two folders, a source and a replica. 
All changes done in the source folder will be applied to the replica folder, recursively going through their subfolders and files.
A log file is also udated with every performed action, while also printing to the console.

To run the script, you must enter the folowing arguments via command line: source folder path, replica folder path, synchronisation interval in seconds, log file path.
Example: python sync_tool_hash.py E:\Python\Sync_tool\Origin E:\Python\Sync_tool\Replica 15 E:\Python\Sync_tool\log.txt

There are two versions of the script:
        1. sync_tool_filecmp - this uses the filecmp library to compare files/folders
        2. sync_tool_hash - this uses a hash generator function to compare file/folders

Take your pick and enjoy!
