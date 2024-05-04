import os
import sys
import time 
import json
import shutil
import logging
import shlex
import signal
import subprocess
import gc
from datetime import datetime
from pathlib import Path

import requests
import psutil

from loggers.logger import setup_logger


logger = setup_logger(__name__, __name__)


def cleanup_processes(names):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if any(name in ' '.join(proc.info['cmdline']) for name in names):
                logger.debug(f"Cleaning up process: PID {proc.info['pid']}, Name: {proc.info['name']}")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


def cleanup_chromium():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'chromium' in ' '.join(proc.info['cmdline']):
                logger.debug(f"Cleaning up Chromium process: PID {proc.info['pid']}, Name: {proc.info['name']}")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


def terminate_procs(proc_name):
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name']):
        if (proc.info['name'] == str(proc_name) and
            proc.info['pid'] != current_pid):
            try:
                p = psutil.Process(proc.info['pid'])
                p.terminate()
                print(
                    "Terminated 'alpha_main' process with PID: "
                    + str(proc.info['pid'])
                )
            except psutil.NoSuchProcess:
                print(
                    "Process with PID "
                    + str(proc.info['pid'])
                    + " no longer exists"
                )
            except psutil.AccessDenied:
                print(
                    "Permission denied to terminate process with PID: "
                    + str(proc.info['pid'])
                )


def combine_text_files(directory, output_filename):
    text_files = [f for f in os.listdir(directory) if f.endswith(".txt")]
    file_path = os.path.join(directory, output_filename)
    with open(os.path.join(file_path), "w") as output_file:
        for text_file in text_files:
            file_path = os.path.join(directory, text_file)
            with open(file_path, "r") as file:
                output_file.write(file.read())
                output_file.write("\n")
            return file_path


def parse_timestamp(log_line):
    try:
        timestamp_str = log_line.split(" - ")[0].strip()
        return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%f")
    except (ValueError, IndexError):
        return None


def concat_sort_logs(directory, fp_out):
    all_logs = []
    for filename in os.listdir(directory):
        if filename.endswith(".log"):
            with open(os.path.join(directory, filename), "r") as file:
                for line in file:
                    if parse_timestamp(line) is not None:
                        all_logs.append(line)
    sorted_logs = sorted(filter(None, all_logs), key=parse_timestamp)
    with open(os.path.join(fp_out, "combo.log"), "w") as file:
        file.writelines(sorted_logs)


def configure_main(projectnumber):
    time.sleep(5 / 100)
    json_string = configure_directories_structure(projectnumber)
    dir_structure = json.loads(json_string)
    create_directories(dir_structure)
    execute_template_operations(projectnumber)


def handle_sigterm(sig, frame):
    sys.exit(0)


def rclone_copy(fp_zip, directory, full_path):
    rclone = full_path
    remote2 = f"dropbox:/PROJECTS/_aa_Most-Recent/{directory}/"
    cmd = str(f"{rclone}")
    arg1 = str("copy")
    arg2 = str(fp_zip)
    arg3 = str(remote2)
    arg4 = str("--progress")
    arg5 = str("--verbose")
    process = subprocessPopen = subprocess.Popen(
        [cmd, arg1, arg2, arg3, arg4, arg5],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        logger.debug("Rclone copy successful.")
        signal.signal(signal.SIGTERM, handle_sigterm)
    else:
        logger.debug("Rclone copy failed:", stderr.decode())


def concat_clean_up(db_file):
    try:
        project_number, l_name = dirs_strings(db_file)
        concat_sort_logs(LOG_DIR, BASE_DIR)
        fp_zip, new_dirs, full_pathx = upload_drive(db_file)
        logger.debug("main: upload_drive complete")
        end_3 = time.time()
        execution_time = end_3 - start
        execution_minutes = execution_time // 60
        execution_seconds = execution_time % 60
        exec_time_2 = (
            f"main: Execution Time: {execution_minutes} minutes"
            + f" and {execution_seconds:.2f} seconds"
        )
        logger.debug(f"main: {exec_time_2}")
        return fp_zip, new_dirs, full_pathx, l_name, project_number
    except Exception as e:
        logger.debug(f"main: {e}")


def sync_clean_up(fp_zip, new_dirs, full_pathx, l_name, project_number):
    try:
        logger.debug("main: rclone_copy started")
        rclone_copy(
                fp_zip,
                new_dirs,
                full_pathx,
                )
        logger.debug("main: rclone_copy complete")
        fp_proj = RESULT_DIR / f"{l_name}-{project_number}"
        shutil.rmtree(fp_proj)
    except Exception as e:
        logger.debug(f"main: {e}")


def slack_clean_up(l_name, project_number):
    try:
        end_1 = time.time()
        execution_time = end_1 - start
        execution_minutes = execution_time // 60
        execution_seconds = execution_time % 60
        exec_time = (
            f"main: Execution Time: {execution_minutes} minutes"
            + f" and {execution_seconds:.2f} seconds"
        )
        url = os.getenv("SLACK_URL")
        headers = {
            "Content-Type": "application/json",
        }
        current_time = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime()
        )
        data = {
            "text": (
                "AlphApex Floodway Program Complete. Project"
                + f" {l_name}-{project_number} has been uploaded to"
                + f" Dropbox directory _aa_Most-Recent at {current_time}."
                + " Please unzip, download, and move all files to the"
                + " appropriate folder in the ACE Dropbox"
                + f" directory PROJECTS.{exec_time}"
            )
        }
        response = requests.post(url, json=data, headers=headers)
        logger.debug(response.text)
    except Exception as e:
        logger.debug(f"main: {e}")


def delex_clean_up(db_file):
    try:
        if os.path.exists(db_file):
            os.remove(db_file)
            logger.debug(f"{db_file} has been deleted.")
        gc.collect()
        end_2 = time.time()
        execution_time = end_2 - start
        execution_minutes = execution_time // 60
        execution_seconds = execution_time % 60
        logger.debug(
            f"main: Execution Time: {execution_minutes} minutes"
            + f" and {execution_seconds:.2f} seconds"
        )
    except Exception as e:
        logger.debug(f"main: {e}")
        sys.exit(1)
    logger.debug("main: complete- loop end")
    sys.exit(0)


def main_starter(db_file):
    try:
        (projectnumber,
            parcelid,
            clean_parcelid,
            county,
            lname) = parcel_vars(db_file)
        logger.debug("main: parcel_vars completed")
        configure_main(projectnumber)
        logger.debug("main: configure_main completed")
        logger.debug("main: start block 1 completed")
        return (projectnumber,
                parcelid,
                clean_parcelid,
                county,
                lname)
    except Exception as e:
        logger.debug(f"main: {e}")


def subproc_lpc(projectnumber, parcelid, BASE_DIR):
    try:
        alpha_lpc = PARENT_DIR / "lpc/lpc.py"
        python_3 = "/home/jpournelle/anaconda3/envs/g39/bin/python3"
        cmd_2 = (f"{python_3} {alpha_lpc} --projectnumber {projectnumber}"
                f" --parcelid {parcelid} --base_dir {BASE_DIR}")
        cmd_lst_2 = shlex.split(cmd_2)
        subprocess.Popen(cmd_lst_2)
        logger.debug("main: lpc executed")
    except subprocess.CalledProcessError as e:
        logger.debug(f"main: lpc failed- {e}")