#!/home/jpournelle/anaconda3/envs/g39/bin/python3
"""
this module runs all the pertinent modules and their functions
"""
import os
from pympler import muppy, summary
import sqlite3
import tracemalloc
import psutil
import gc
import os.path
import copy
import shlex
import setproctitle
setproctitle.setproctitle('alpha_main')
from pathlib import Path
from configs.config import (
    BASE_DIR,
    LOG_DIR,
    OUTPUT_DIR,
    RESULT_DIR,
    TMP_DIR,
    PARENT_DIR,
)
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import subprocess
import argparse
import sys
import shutil
import requests
import time
env = os.environ.copy()
from sync.remote_drive import upload_drive, dirs_strings
from sync.gdrive import gdrive
from helpers.misc_helper import log_rotation
from dotenv import load_dotenv

try:
    load_dotenv(
        "/home/jpournelle/python_projects/"
        + "plabz/river_division/main/main.env"
    )
except:
    pass
import cProfile
import pstats
import signal
import uuid
from datetime import datetime
import json
import concurrent.futures
from configs.file_paths import DB_FILE_2
from configs.parcel_vars import parcel_vars
from configs.config_dir import (
    execute_template_operations,
    configure_directories_structure,
)
from configs.create_dirs import create_directories
from research.flood_report import flood_report
from research.flood_data import fema_data
from research.pdf_fill import pdf_fillable
from multiprocessing import Process, Queue, current_process
import multiprocessing
import threading
from geometry.parcel_geometry import parcel_geometry
from research.pdf_fill import pdf_fillable
from geometry.hecras import hecras_calc
from research.river_mile import river_mile_1, river_mile_2
from helpers.misc_helper import write_pid_to_file
from lpc.lpc import lpc
from geometry.bank_geom import bank_geom
from geometry.center_line import center_line
from geometry.center_tob import center_tob
from research.water_level import water_level_url, get_wl_data
from research.research import parcel_research_1, parcel_research_2
from geometry.parcel_builder import parcel_builder
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import asyncio
import aiohttp
from loggers.logger import setup_logger
from playwright.async_api import async_playwright
import atexit

logger = setup_logger("main.logger", "main")


def duplicate_db(source_path, duplicate_path):
    """
    Creates an exact duplicate of an SQLite database file.
    
    Args:
    source_path (str): The file path to the source SQLite database.
    duplicate_path (str): The file path where the duplicate database should be saved.
    
    Raises:
    IOError: If the source database file does not exist or the duplicate cannot be created.
    """
    if not os.path.exists(source_path):
        raise IOError("Source database file does not exist")

    shutil.copy(source_path, duplicate_path)
    logger.debug(f"Database duplicated successfully to {duplicate_path}")
    

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
                    f"Terminated 'alpha_main' process with PID:" \
                        + f" {proc.info['pid']}"
                    )
            except psutil.NoSuchProcess:
                print(
                    f"Process with PID {proc.info['pid']} no longer exists"
                    )
            except psutil.AccessDenied:
                print(
                    f"Permission denied to terminate process with PID:" \
                        + f" {proc.info['pid']}"
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


def main(dbfile=None):
    try:
        exit_lst = [
            'alpha_hecras',
            'alpha_lpc',
            'alpha_flood_report',
            'alpha_flood_data',
            'alpha_pdf_fill',
            'alpha_parcel_geometry',
            'alpha_water_level',
            'alpha_bank_geom',
            'alpha_center_line',
            'alpha_center_tob',
            'alpha_parcel_builder',
            'alpha_parcel_research_1',
            'alpha_parcel_research_2',
            'alpha_river_mile_1',
            'alpha_river_mile_2',
            'alpha_main'
        ]
        atexit.register(cleanup_processes, exit_lst)
        atexit.register(cleanup_chromium)
        atexit.register(gc.collect)
        logger.debug("-------------------------------------------")
        logger.debug("-------------------------------------------")
        logger.debug(f"main: main started-{datetime.now()}")
        try:
            global start
            start = time.time()
            # tracemalloc.start()
            db_file_1 = dbfile
            # db_file_2 = DB_FILE_2
            # source_database = db_file_1
            # duplicate_database = db_file_2
            # try:
            #     duplicate_db(source_database, duplicate_database)
            # except Exception as e:
            #     print(f"An error occurred: {e}")
            # if args.dbfile:
            #     db_file = args.dbfile
            # else:
            #     pass
        except Exception as e:
            logger.debug(f"main: {e}")
        try:
            (projectnumber,
             parcelid,
             clean_parcelid,
             county,
             lname) = main_starter(db_file_1)
            logger.debug("main: main_starter complete")
            db_file_2 = DB_FILE_2
            source_database = db_file_1
            duplicate_database = db_file_2
            try:
                duplicate_db(source_database, duplicate_database)
            except Exception as e:
                print(f"An error occurred: {e}")
        except Exception as e:
            logger.debug(f"main: main_starter failed- {e}")
    except Exception as e:
        logger.debug(f"main: start block failed-{e}")
        sys.exit(1)
    time.sleep(5 / 100)
    try:
        subproc_lpc(projectnumber, parcelid, BASE_DIR)
        logger.debug("main: subproc_lpc executed")
    except Exception as e:
        logger.debug(f"main: subproc_lpc failed- {e}")
        logger.debug("main: async block 1 started")

    async def main():
        loop = asyncio.get_event_loop()
        try:
            with ProcessPoolExecutor() as process_executor:
                task_1 = loop.run_in_executor(
                    process_executor,
                    parcel_geometry,
                    projectnumber,
                    parcelid
                )
            task_flood_report = asyncio.create_task(
                flood_report(
                    projectnumber,
                    clean_parcelid
                    )
                )
            results = await asyncio.gather(task_1, task_flood_report)
            task_1_result = results[0]
            string = results[1]
            gs_1, river_frontage_length, gs_setback = task_1_result
            logger.debug("main: parcel_geometry complete")
            logger.debug("main: flood_report complete")
        except Exception as e:
            logger.debug(f"main: parcel_geometry and flood_report failed- {e}")
        try:
            with ThreadPoolExecutor() as thread_executor:
                task_2 = loop.run_in_executor(
                    thread_executor,
                    pdf_fillable,
                    projectnumber,
                    river_frontage_length
                )
                task_3 = loop.run_in_executor(
                    thread_executor,
                    fema_data,
                    projectnumber,
                    string
                )
                _, task_3_result = await asyncio.gather(task_2, task_3)
                yr100, yr50, yr10, firm_panel = task_3_result
            logger.debug("main: pdf_fillable and fema_data complete")
        except Exception as e:
            logger.debug(f"main: pdf_fillable and fema_data failed- {e}")
        try:
            with ProcessPoolExecutor() as process_executor:
                gdf_hxline, hecras_dict = await loop.run_in_executor(
                    process_executor,
                    hecras_calc,
                    projectnumber,
                    gs_1,
                    yr100,
                    yr50,
                    yr10,
                    firm_panel,
                    river_frontage_length
                )
                logger.debug("main: hecras_calc complete")
        except Exception as e:
            logger.debug(f"main: hecras_calc failed- {e}")
        try:
            with ThreadPoolExecutor() as thread_executor:
                map_path = await loop.run_in_executor(
                    thread_executor,
                    river_mile_1,
                    projectnumber,
                    gs_1,
                    gdf_hxline,
                )
                logger.debug("main: river_mile_1 complete")
        except Exception as e:
            logger.debug(f"main: river_mile_1 failed- {e}")
        try:
            await river_mile_2(projectnumber, map_path)
            logger.debug("main: river_mile_2 complete")
        except Exception as e:
            logger.debug(f"main: river_mile_2 failed - {e}")
        return (
            gs_1, river_frontage_length, gs_setback,
            yr100, yr50, yr10, hecras_dict
            )

    if __name__ == "__main__":
        result = asyncio.run(main())
    logger.debug("main: async block 1 complete")
    logger.debug("main: async block 2 started")

    async def main2(gs_1,
                    river_frontage_length,
                    gs_setback,
                    yr100,
                    yr50,
                    yr10
                    ):
        loop = asyncio.get_event_loop()
        try:
            with ProcessPoolExecutor() as process_executor:
                (gs_center,
                 gdf_center_xs_line_mile) = await loop.run_in_executor(
                    process_executor,
                    center_line,
                    gs_1,
                    river_frontage_length
                    )
                (gs_updated_center,
                 smooth_points) = await loop.run_in_executor(
                    process_executor,
                    center_tob,
                    gs_center,
                    river_frontage_length
                    )
                logger.debug("main: center_line and center_tob complete")
        except Exception as e:
            logger.debug(f"main: center_tob failed- {e}")
        try:
            with ThreadPoolExecutor() as thread_executor:
                (url_1,
                 url_2,
                 upper_xs,
                 lower_xs) = await loop.run_in_executor(
                    thread_executor,
                    water_level_url,
                    projectnumber,
                    gdf_center_xs_line_mile,
                    river_frontage_length
                    )
                logger.debug("main: water_level_url complete")
        except Exception as e:
            logger.debug(f"main: water_level_url failed- {e}")
        try:
            (delta_water_level_el,
             upper_xs,
             lower_xs) = await get_wl_data(
                url_1,
                url_2,
                upper_xs,
                lower_xs,
                gdf_center_xs_line_mile
                )
            logger.debug("main: get_wl_data complete")
        except Exception as e:
            logger.debug(f"main: get_wl_data failed- {e}")
        try:
            with ProcessPoolExecutor() as process_executor:
                await loop.run_in_executor(
                    process_executor,
                    bank_geom,
                    projectnumber,
                    delta_water_level_el,
                    gs_center,
                    gs_updated_center,
                    gs_1,
                    gs_setback
                    )
                await loop.run_in_executor(
                    process_executor,
                    parcel_builder,
                    projectnumber,
                    gs_center,
                    gs_setback,
                    yr100,
                    yr50,
                    yr10,
                    delta_water_level_el,
                    river_frontage_length
                    )
                logger.debug("main: bank_geom and parcel_builder complete")
        except Exception as e:
            logger.debug(f"main: bank_geom and parcel_builder failed- {e}")
        try:
            await parcel_research_1(
                projectnumber,
                parcelid,
                county
                )
            logger.debug(f"main: parcel_research_1 complete")
        except Exception as e:
            logger.debug(f"main: parcel_research_1 failed- {e}")
        try:
            async with async_playwright() as playwright:
                await parcel_research_2(
                    playwright,
                    projectnumber,
                    parcelid,
                    county
                    )
                logger.debug(f"main: parcel_research_2 complete")
        except Exception as e:
            logger.debug(f"main: parcel_research_2 failed- {e}")
    if __name__ == "__main__":
        (gs_1,
         river_frontage_length,
         gs_setback,
         yr100,
         yr50,
         yr10,
         hecras_dict) = result
        asyncio.run(
            main2(
                gs_1,
                river_frontage_length,
                gs_setback,
                yr100,
                yr50,
                yr10
                )
            )
    try:
        logger.debug("main: async block 2 complete")
        logger.debug("main:gdrive started")
        try:
            gdrive(hecras_dict)
            logger.debug("main: gdrive complete")
        except Exception as e:
            logger.debug(f"main: gdrive failed- {e}")
        logger.debug("main: cleanup block started")
        try:
            (fp_zip,
             new_dirs,
             full_pathx,
             l_name,
             project_number) = concat_clean_up(db_file_1)
            logger.debug("main: concat_clean_up complete")
        except Exception as e:
            logger.debug(f"main: concat_clean_up failed-{e}")
        sync_clean_up(
            fp_zip,
            new_dirs,
            full_pathx,
            l_name,
            project_number
            )
        slack_clean_up(l_name, project_number)
        delex_clean_up(db_file_1)
    except Exception as e:
        logger.debug(f"main: cleanup block failed-{e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AlphApex Floodway Program"
        )
    parser.add_argument(
        "--dbfile",
        help="Path to a .db file to process"
        )
    args = parser.parse_args()
    main(args.dbfile)
