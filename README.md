# File-Synchronizer

## File Synchronizer using command line arguments

**Main Task**

This script keeps two directories synchronized by copying updated or new files from the source directory to the replica directory and removing files from the replica directory that are not present in the source directory. It uses SHA3 hashing to check for file updates and performs hash calculation in parallel to improve performance.

### Functions

+ **calculate_hash(file_path: str)**

Calculates the SHA3 hash of a file. The file is read in chunks to avoid using too much memory for large files.

**gather_files_and_initialize_hash(directory: str)**

Walks through a directory and returns a dictionary where the keys are the relative paths of the files and the values are initialized to None. The relative paths are obtained by removing the provided directory path from the full file path.

**calculate_hashes_in_parallel(files_with_hash: dict, directory: str)**

Calculates the SHA3 hash for each file in the provided dictionary in parallel using Python's ThreadPoolExecutor. The maximum number of worker threads used is equal to the number of CPUs. After the calculation, replaces the None values in the dictionary with the calculated hash values.

**sync_files(source_files: dict, replica_files: dict, source_dir: str, replica_dir: str)**

Synchronizes the files from the source directory to the replica directory. If a file is present in the source directory but not in the replica directory or if the file's hash in the source directory is different from that in the replica directory, then the file is copied from the source to the replica directory. The function logs the operation (either "Created" or "Updated") along with the replica file path and the source file path.

**remove_extra_files_in_replica(source_files: dict, replica_files: dict, replica_dir: str)**

Removes files from the replica directory that are not present in the source directory. If a file is present in the replica directory but not in the source directory, then the file is deleted from the replica directory. The function logs the removed file path or any error that occurs during the removal.

**synchronize_directories(source_dir: str, replica_dir: str)**

Synchronizes the source directory to the replica directory by calling the gather_files_and_initialize_hash, calculate_hashes_in_parallel, sync_files, and remove_extra_files_in_replica functions in order.

**get_user_inputs()**

Prompts the user to enter the source directory path, the replica directory path, the synchronization interval in seconds, and the log file path. Returns these values as a tuple.

**setup_logging(log_file_path: str)**

Sets up the logging for the script. If the log file path is a directory, then the log file is named 'logfile.log' and is placed in that directory. The log file is rotated when it reaches a size of 5MB and the two most recent log files are kept. The log messages are also printed to the console (standard output).

**main()**
The main function that runs the script. It first gets the user inputs and sets up the logging. Then it enters a loop where it repeatedly synchronizes the source and replica directories and then waits for the specified synchronization interval. If any error occurs during the synchronization, it is logged and the script continues with the next synchronization after the interval. The loop is exited if the user interrupts the script (e.g., by pressing Ctrl+C), and a message is logged before the script exits.

***Sample Video***


