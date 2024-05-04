import os
import time
import sqlite3
from pathlib import Path
import subprocess
import shlex
from loggers.logger import setup_logger
import redis
import json
PARENT_DIR = Path(__file__).parents[0]
from dotenv import load_dotenv
load_dotenv(PARENT_DIR / "main.env")

logger = setup_logger("main_worker", "main_worker")

G_PARENT_DIR = Path(__file__).parents[1]
TMP_DIR = G_PARENT_DIR / "output/tmp"

r = redis.Redis(
  host=os.getenv("REDIS_HOST"),
  port=os.getenv("REDIS_PORT"),
  password=os.getenv("REDIS_PASSWORD")
)


def init_db(task_key):
    file_db = TMP_DIR / f"{task_key}.db"
    conn = sqlite3.connect(file_db)
    c = conn.cursor()
    conn.enable_load_extension(True)
    conn.execute("SELECT load_extension('mod_spatialite')")
    conn.execute("SELECT InitSpatialMetadata(1)")
    c.execute(
        'CREATE TABLE IF NOT EXISTS project_data('
        'id INTEGER, parcelid TEXT, fname TEXT,'
        'lname TEXT, email TEXT, phone TEXT, oaddr1 TEXT,'
        'ocity TEXT, ostate TEXT, ozipcd TEXT, project TEXT,'
        'phyaddr1 TEXT, phycity TEXT, phyzip TEXT, cntyname TEXT,'
        'decklength TEXT, deckwidth TEXT, gangwaylength TEXT,'
        'gangwaywidth TEXT, docklength TEXT, dockwidth TEXT,'
        'landinglength TEXT, landingwidth TEXT, handrailheight TEXT);'
    )
    conn.commit()
    conn.close()
    return file_db


def main_app(db_file):
    PARENT_DIR = Path(__file__).parents[0]
    alpha_path = PARENT_DIR / "main.py"
    python_3 = os.getenv("PYTHON_3")
    cmd_1 = f"{python_3} {alpha_path} --dbfile {db_file}"
    cmd_lst_1 = shlex.split(cmd_1)
    proc_1 = subprocess.Popen(
        cmd_lst_1,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
        )
    try:
        stdout, stderr = proc_1.communicate(timeout=300)
    except subprocess.TimeoutExpired:
        proc_1.kill()
        stdout, stderr = proc_1.communicate()
        print(f"Alpha_Main timed out: {stderr}")


def main_worker():
    while True:
        try:
            _, task_id_bytes = r.brpop("task_todo")
            task_id_str = task_id_bytes.decode('utf-8')
            print(task_id_str)
            file_db = init_db(task_id_str)
            logger.debug(f"file_db: {file_db}")
            logger.debug(type(file_db))
            hash = r.hgetall(task_id_str)
            hash = ({k.decode('utf-8'): v.decode('utf-8')
                     for k, v in hash.items()})
            data = json.loads(hash['payload'])
            with sqlite3.connect(file_db) as conn:
                c = conn.cursor()
                columns = ', '.join(data.keys())
                placeholders = ', '.join('?' for _ in data)
                sql = ('INSERT INTO project_data ({}) VALUES ({})'
                       .format(columns, placeholders))
                c.execute(sql, list(data.values()))
            main_app(file_db)
        except Exception as e:
            logger.debug(f"Error: {e}")
        time.sleep(5)


if __name__ == "__main__":
    main_worker()
