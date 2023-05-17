import os
import sys
import shutil
import time
import hashlib
import logging
from logging.handlers import RotatingFileHandler
from concurrent.futures import ThreadPoolExecutor


def calculate_hash(file_path):
    """Calculate and return the SHA3 hash of a file."""
    hash_sha3 = hashlib.sha3_256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_sha3.update(chunk)
    return hash_sha3.hexdigest()


def gather_files_and_initialize_hash(directory):
    """Gather all files in the directory and initialize their SHA3 hash to None."""
    files_with_hash = {}

    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            full_file_path = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(full_file_path, directory)
            files_with_hash[relative_path] = None  # Initialize the hash to None

    return files_with_hash


def calculate_hashes_in_parallel(files_with_hash, directory):
    """Calculate the SHA3 hash for each file in parallel."""
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        for relative_path in files_with_hash.keys():
            full_file_path = os.path.join(directory, relative_path)
            files_with_hash[relative_path] = executor.submit(calculate_hash, full_file_path)

    # Wait for all the hashes to be calculated
    for relative_path, future in files_with_hash.items():
        files_with_hash[relative_path] = future.result()


def sync_files(source_files, replica_files, source_dir, replica_dir):
    """Synchronize the source files to the replica directory."""
    for relative_path, hash_value in source_files.items():
        source_path = os.path.join(source_dir, relative_path)
        replica_path = os.path.join(replica_dir, relative_path)

        if relative_path not in replica_files or hash_value != replica_files[relative_path]:
            os.makedirs(os.path.dirname(replica_path), exist_ok=True)
            try:
                shutil.copy2(source_path, replica_path)
                operation = "Created" if relative_path not in replica_files else "Updated"
                logging.info(f"{operation} {replica_path} from {source_path}")
            except Exception as error:
                logging.error(f"Failed to copy {source_path} to {replica_path} due to error: {error}")


def remove_extra_files_in_replica(source_files, replica_files, replica_dir):
    """Remove files that exist in the replica but not in the source directory."""
    for relative_path in replica_files.keys():
        if relative_path not in source_files:
            replica_path = os.path.join(replica_dir, relative_path)
            try:
                os.remove(replica_path)
                logging.info(f"Removed {replica_path}")
            except Exception as error:
                logging.error(f"Failed to remove {replica_path} due to error: {error}")


def synchronize_directories(source_dir, replica_dir):
    """Synchronize the source directory to the replica directory."""
    source_files = gather_files_and_initialize_hash(source_dir)
    replica_files = gather_files_and_initialize_hash(replica_dir)

    calculate_hashes_in_parallel(source_files, source_dir)
    calculate_hashes_in_parallel(replica_files, replica_dir)

    sync_files(source_files, replica_files, source_dir, replica_dir)
    remove_extra_files_in_replica(source_files, replica_files, replica_dir)


def get_user_inputs():
    """Get inputs from the user."""
    source_dir = input("Please enter the source directory path: ")
    replica_dir = input("Please enter the replica directory path: ")
    interval = int(input("Please enter the synchronization interval in seconds: "))
    log_file_path = input("Please enter the log file path: ")

    return source_dir, replica_dir, interval, log_file_path


def setup_logging(log_file_path):
    """Set up the logging for the script."""
    if os.path.isdir(log_file_path):
        log_file_path = os.path.join(log_file_path, 'logfile.log')

    logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])

    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    log_file_handler = RotatingFileHandler(log_file_path, mode='a', maxBytes=5 * 1024 * 1024, backupCount=2)
    log_file_handler.setFormatter(log_formatter)
    log_file_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(log_file_handler)


def main():
    """The main function that runs the script."""
    source_dir, replica_dir, interval, log_file_path = get_user_inputs()
    setup_logging(log_file_path)

    try:
        while True:
            try:
                synchronize_directories(source_dir, replica_dir)
                time.sleep(interval)
            except Exception as error:
                logging.error(error)
    except KeyboardInterrupt:
        logging.info("Synchronization stopped by user. Exiting.")
        sys.exit(0)


if __name__ == "__main__":
    main()
