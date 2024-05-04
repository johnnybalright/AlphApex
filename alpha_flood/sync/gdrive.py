from google.oauth2 import service_account
from googleapiclient.discovery import build
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import subprocess
import sqlite3
import os
import json
from configs.file_paths import (
    OUT_SHP_HXLINE,
    IN_SHP,
    DB_FILE_2
)
from configs.config import BASE_DIR, OUTPUT_DIR, PARENT_DIR
from loggers.logger import setup_logger
from dotenv import load_dotenv
try:
    load_dotenv(PARENT_DIR / "main.env")
except:
    pass

logger = setup_logger(__name__, __name__)

SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SCOPES = [os.getenv("SCOPES")]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)


def create_folder(name, parent_id=None):
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        file_metadata['parents'] = [parent_id]

    folder = service.files().create(body=file_metadata, fields='id').execute()
    print(f"Folder '{name}' created with ID: {folder.get('id')}")
    return folder.get('id')


def find_binary(binary_name):
    potential_paths = ["/usr/bin", "/usr/local/bin", "/opt/bin"]
    for path in potential_paths:
        full_path = os.path.join(path, binary_name)
        if os.path.isfile(full_path):
            return full_path
    return None


def rclone_search(full_path):
    rclone = full_path
    dir_1 = "dropbox:/PROJECTS/_River-Division"
    dir_2 = "dropbox:/PROJECTS/_River-Division/_Saltwater-Builders"
    cmd = str(f"{rclone}")
    arg1 = str("lsd")
    arg2 = str(dir_1)
    arg3 = str(dir_2)
    
    process_1 = subprocessPopen = subprocess.Popen(
        [cmd, arg1, arg2],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    process_2 = subprocessPopen = subprocess.Popen(
        [cmd, arg1, arg3],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    
    stdout_1, stderr_1 = process_1.communicate()
    stdout_2, stderr_2 = process_2.communicate()
    
    process_lst_1 = stdout_1.decode().split("-1 ")
    process_lst_2 = stdout_2.decode().split("-1 ")
    
    dirs_lst_1 = process_lst_1[0::2]
    dirs_lst_2 = process_lst_2[0::2]
    
    items_1 = [item.strip() for item in dirs_lst_1 if item.strip()]
    items_2 = [item.strip() for item in dirs_lst_2 if item.strip()]
    
    projects_dict = {'_River-Division': items_1,
                     '_River-Division/_Saltwater-Builders': items_2
                     }
    
    if process_1.returncode == 0 and process_2.returncode == 0:
        return projects_dict
    
    else:
        print("Rclone search failed:", stderr_1.decode())


def find_directory(input_dict, match_string):
    """
    Search through a dictionary where each value is a list of hyphen-separated strings.
    For each string, split it by the hyphen and compare the first part with a given string.
    If a match is found, return the whole item along with its key.

    Parameters:
    input_dict (dict): A dictionary with each value being a list of strings.
    match_string (str): The string to match against the first part of each split string.

    Returns:
    list of tuples: Each tuple contains the key from the dictionary and the matching string.
    """
    matches = []
    for key, items in input_dict.items():
        for item in items:
            parts = item.split('-')
            if parts[-1] == match_string:
                matches.append((key, item))
    
    return matches


def find_project_directory(project_number):
    full_path = find_binary("rclone")
    projects_dict = rclone_search(full_path)
    project_dirs = find_directory(projects_dict, project_number)
    if project_dirs:
        return (f"/ACE Dropbox/PROJECTS/{project_dirs[0][0]}/{project_dirs[0][1]}")
    else:
        print(f"Project {project_number} not found.")
        return None


def rclone_copy_hx(full_path, project_number, lname):
    out_shp_hxline = OUT_SHP_HXLINE
    in_shp = IN_SHP
    rclone = full_path
    dir_1 = out_shp_hxline
    dir_2 = in_shp
    dir_3 = f"gdrive:_aa_Most-Recent/{lname}-{project_number}_g/_drone"
    cmd = str(f"{rclone}")
    arg1 = str("copy")
    arg2 = str(dir_1)
    arg3 = str(dir_2)
    arg4 = str(dir_3)
    arg5 = str("--drive-server-side-across-configs")

    
    process_1 = subprocessPopen = subprocess.Popen(
        [cmd, arg1, arg2, arg4, arg5],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    process_2 = subprocessPopen = subprocess.Popen(
        [cmd, arg1, arg3, arg4, arg5],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout_1, stderr_1 = process_1.communicate()
    stdout_2, stderr_2 = process_2.communicate()

    if process_1.returncode == 0 or process_2.returncode == 0:
        return stdout_1.decode(), stdout_2.decode()
    else:
        print("Rclone copy hxline parcel_boundary failed:", stderr_1.decode(), stderr_2.decode())


def rclone_copy_gsheet(full_path, project_number, lname):
    rclone = full_path
    dir_1 = "gdrive:_aa_Most-Recent/templates/PermitTable.xlsx"
    dir_2 = f"gdrive:_aa_Most-Recent/{lname}-{project_number}_g/Cadd"
    cmd = str(f"{rclone}")
    arg1 = str("copy")
    arg2 = str(dir_1)
    arg3 = str(dir_2)
    arg4 = str("--drive-server-side-across-configs")

    process_1 = subprocessPopen = subprocess.Popen(
        [cmd, arg1, arg2, arg3, arg4],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout_1, stderr_1 = process_1.communicate()

    if process_1.returncode == 0:
        return stdout_1.decode()
    else:
        print("Rclone copy failed:", stderr_1.decode())


def rclone_gsheet_id(full_path, project_number, lname):
    rclone = full_path
    dir_1 = f"gdrive:_aa_Most-Recent/{lname}-{project_number}_g/Cadd"
    cmd = str(f"{rclone}")
    arg1 = str("lsjson")
    arg2 = str(dir_1)
    arg3 = str("--drive-server-side-across-configs")

    process_1 = subprocessPopen = subprocess.Popen(
        [cmd, arg1, arg2, arg3],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout_1, stderr_1 = process_1.communicate()

    if process_1.returncode == 0:
        logger.debug(f"rclone_gsheet_id: {stdout_1.decode()}")
        return stdout_1.decode()
    else:
        print("Rclone lsjson failed:", stderr_1.decode())
        logger.debug(f"rclone_gsheet_id: failed- {stderr_1.decode()}")


def project_vars(db_file):
    """
    Get variables for a new project from a database.

    The function fetches various project attributes from a SQLite
    database, such as project number, parcel ID, county name, and last
    name.

    :return: A tuple containing the project attributes or None if an
    exception occurs.
    """
    try:
        logger.debug(f"db_file: {db_file}")
        logger.debug(f"file_path: {BASE_DIR}")
        with sqlite3.connect(db_file) as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM project_data;")
            projectnumber = str(c.fetchone()[0])
            logger.debug(projectnumber)
            logger.debug("projectnumber: %s", projectnumber)
            c.execute("SELECT parcelid FROM project_data;")
            parcelid = str(c.fetchone()[0])
            logger.debug("parcelid: %s", parcelid)
            clean_parcelid = (parcelid.replace("-", "") \
                if "-" in parcelid else parcelid)
            c.execute("SELECT cntyname FROM project_data;")
            county = str(c.fetchone()[0])
            logger.debug("county: %s", county)
            c.execute("SELECT lname FROM project_data;")
            lname = str(c.fetchone()[0])
            logger.debug("lname: %s", lname)
            c.execute("SELECT fname FROM project_data;")
            fname = str(c.fetchone()[0])
            logger.debug("fname: %s", fname)
            c.execute("SELECT oaddr1 FROM project_data;")
            oaddr1 = str(c.fetchone()[0])
            logger.debug("oaddr1: %s", oaddr1)
            c.execute("SELECT ocity FROM project_data;")
            ocity = str(c.fetchone()[0])
            logger.debug("ocity: %s", ocity)
            c.execute("SELECT ostate FROM project_data;")
            ostate = str(c.fetchone()[0])
            logger.debug("ostate: %s", ostate)
            c.execute("SELECT ozipcd FROM project_data;")
            ozipcd = str(c.fetchone()[0])
            logger.debug("ozipcd: %s", ozipcd)
            c.execute("SELECT phyaddr1 FROM project_data;")
            phyaddr1 = str(c.fetchone()[0])
            logger.debug("pyaddr1: %s", phyaddr1)
            c.execute("SELECT phycity FROM project_data;")
            phycity = str(c.fetchone()[0])
            logger.debug("phycity: %s", phycity)
            c.execute("SELECT phyzip FROM project_data;")
            phyzip = str(c.fetchone()[0])
            logger.debug("phyzip: %s", phyzip)
            c.execute("SELECT decklength FROM project_data;")
            decklength = str(c.fetchone()[0])
            logger.debug("decklength: %s", decklength)
            c.execute("SELECT deckwidth FROM project_data;")
            deckwidth = str(c.fetchone()[0])
            logger.debug("deckwidth: %s", deckwidth)
            c.execute("SELECT gangwaylength FROM project_data;")
            gangwaylength = str(c.fetchone()[0])
            logger.debug("gangwaylength: %s", gangwaylength)
            c.execute("SELECT gangwaywidth FROM project_data;")
            gangwaywidth = str(c.fetchone()[0])
            logger.debug("gangwaywidth: %s", gangwaywidth)
            c.execute("SELECT docklength FROM project_data;")
            docklength = str(c.fetchone()[0])
            logger.debug("docklength: %s", docklength)
            c.execute("SELECT dockwidth FROM project_data;")
            dockwidth = str(c.fetchone()[0])
            logger.debug("dockwidth: %s", dockwidth)
            c.execute("SELECT phone FROM project_data;")
            phone = str(c.fetchone()[0])
            logger.debug("phone: %s", phone)
            c.execute("SELECT email FROM project_data;")
            email = str(c.fetchone()[0])
            logger.debug("email: %s", email)
            c.execute("SELECT handrailheight FROM project_data;")
            handrailheight = str(c.fetchone()[0])
            logger.debug("handrailheight: %s", handrailheight)
            c.execute("SELECT project FROM project_data;")
            project = str(c.fetchone()[0])
            logger.debug("project: %s", project)
            project_vars_dict = {
                'projectnumber': projectnumber,
                'fname': fname,
                'lname': lname,
                'email': email,
                'phone': phone,
                'oaddr1': oaddr1,
                'ocity': ocity,
                'ostate': ostate,
                'ozipcd': ozipcd,
                'project': project,
                'phyaddr1': phyaddr1,
                'phycity': phycity,
                'phyzip': phyzip,
                'cntyname': county,
                'decklength': decklength,
                'deckwidth': deckwidth,
                'gangwaylength': gangwaylength,
                'gangwaywidth': gangwaywidth,
                'docklength': docklength,
                'dockwidth': dockwidth,
                'handrailheight': handrailheight,
                'parcelid': clean_parcelid
                }

            return project_vars_dict, projectnumber, lname

    except sqlite3.Error as e:
        logger.debug(f"project_variables: failed- {e}")


def update_spreadsheet(spreadsheet_id, sheet_name, cell, value):
	gc = gspread.service_account(
		filename=SERVICE_ACCOUNT_FILE
		)
	sh = gc.open_by_key(spreadsheet_id)
	worksheet = sh.worksheet(sheet_name)
	worksheet.update([[value]], cell)
 

def gdrive(hecras_dict):
    db_file = DB_FILE_2
    project_vars_dict, project_number, lname = project_vars(db_file)
    logger.debug(f"project_vars_dict: {project_vars_dict}")
    logger.debug(f"hecras_dict: {hecras_dict}")
    dir_name = f"{lname}-{project_number}_g"
    logger.debug(f"directory_name: {dir_name}")
    dir_name_2 = "Cadd"
    dir_name_3 = "_drone"
    dir_name_4 = "shp"
    dir_name_5 = "las"
    dir_name_6 = "geojson"
    dir_name_7 = "tiff"
    dir_name_8 = "imgs"
    parent_id = os.getenv("PARENT_ID")
    new_dir = create_folder(dir_name, parent_id)
    new_dir_2 = create_folder(dir_name_2, new_dir)
    new_dir_3 = create_folder(dir_name_3, new_dir)
    new_dir_4 = create_folder(dir_name_4, new_dir_3)
    new_dir_5 = create_folder(dir_name_5, new_dir_3)
    new_dir_6 = create_folder(dir_name_6, new_dir_3)
    new_dir_7 = create_folder(dir_name_7, new_dir_3)
    new_dir_8 = create_folder(dir_name_8, new_dir_3)
    logger.debug("New directories created.")
    full_path = find_binary("rclone")
    rclone_copy_hx(full_path, project_number, lname)
    rclone_gsheet = rclone_copy_gsheet(full_path, project_number, lname)
    logger.debug(f"Rclone copy gsheet: {rclone_gsheet}")
    rclone_str = rclone_gsheet_id(full_path, project_number, lname)
    rclone_clean = rclone_str.replace("[", "").replace("]", "")
    rclone_dict = json.loads(rclone_clean)
    logger.debug(f"Rclone gsheet id: {rclone_dict}")
    spreadsheet_id = rclone_dict['ID']
    logger.debug(f"Spreadsheet ID: {spreadsheet_id}")
    try:
        project_number = project_vars_dict['projectnumber']
        parcelid = project_vars_dict['parcelid']
        phyaddr1 = project_vars_dict['phyaddr1']
        phycity = project_vars_dict['phycity']
        phyzip = project_vars_dict['phyzip']
        cntyname = project_vars_dict['cntyname']
        project = project_vars_dict['project']
        docklength = project_vars_dict['docklength']
        dockwidth = project_vars_dict['dockwidth']
        gangwaylength = project_vars_dict['gangwaylength']
        gangwaywidth = project_vars_dict['gangwaywidth']
        decklength = project_vars_dict['decklength']
        deckwidth = project_vars_dict['deckwidth']
        fname = project_vars_dict['fname']
        lname = project_vars_dict['lname']
        email = project_vars_dict['email']
        phone = project_vars_dict['phone']
        oaddr1 = project_vars_dict['oaddr1']
        ocity = project_vars_dict['ocity']
        ostate = project_vars_dict['ostate']
        ozipcd = project_vars_dict['ozipcd']
        yr100 = hecras_dict['yr100']
        yr50 = hecras_dict['yr50']
        yr10 = hecras_dict['yr10']
        river_frontage_length = hecras_dict['river_frontage_length']
        river_mile = hecras_dict['river_mile']
        left_bank_station = hecras_dict['left_bank_station']
        right_bank_station = hecras_dict['right_bank_station']
        river_mile_length = hecras_dict['river_mile_length']
        river_mile_ratio = hecras_dict['river_mile_ratio']
        yr100 = hecras_dict['yr100']
    except Exception as e:
        logger.debug(f"error: {e}")
    try:
        update_spreadsheet(spreadsheet_id, 'project_info', 'A2', project_number)
        update_spreadsheet(spreadsheet_id, 'project_info', 'B2', parcelid)
        update_spreadsheet(spreadsheet_id, 'project_info', 'C2', phyaddr1)
        update_spreadsheet(spreadsheet_id, 'project_info', 'D2', phycity)
        update_spreadsheet(spreadsheet_id, 'project_info', 'E2', phyzip)
        update_spreadsheet(spreadsheet_id, 'project_info', 'F2', cntyname)
        update_spreadsheet(spreadsheet_id, 'project_info', 'G2', project)
        update_spreadsheet(spreadsheet_id, 'project_info', 'R2', docklength)
        update_spreadsheet(spreadsheet_id, 'project_info', 'S2', dockwidth)
        update_spreadsheet(spreadsheet_id, 'project_info', 'T2', gangwaylength)
        update_spreadsheet(spreadsheet_id, 'project_info', 'U2', gangwaywidth)
        update_spreadsheet(spreadsheet_id, 'project_info', 'V2', decklength)
        update_spreadsheet(spreadsheet_id, 'project_info', 'W2', deckwidth)
        update_spreadsheet(spreadsheet_id, 'client_info', 'A2', fname)
        update_spreadsheet(spreadsheet_id, 'client_info', 'B2', lname)
        update_spreadsheet(spreadsheet_id, 'client_info', 'C2', email)
        update_spreadsheet(spreadsheet_id, 'client_info', 'D2', phone)
        update_spreadsheet(spreadsheet_id, 'client_info', 'E2', oaddr1)
        update_spreadsheet(spreadsheet_id, 'client_info', 'F2', ocity)
        update_spreadsheet(spreadsheet_id, 'client_info', 'G2', ostate)
        update_spreadsheet(spreadsheet_id, 'client_info', 'H2', ozipcd)
        update_spreadsheet(spreadsheet_id, 'flood_data', 'D2', yr100)
        update_spreadsheet(spreadsheet_id, 'flood_data', 'D3', yr50)
        update_spreadsheet(spreadsheet_id, 'flood_data', 'D4', yr10)
        update_spreadsheet(spreadsheet_id, 'flood_data', 'D11', river_frontage_length)
        update_spreadsheet(spreadsheet_id, 'hecras', 'A2', river_mile)
        update_spreadsheet(spreadsheet_id, 'hecras', 'B2', left_bank_station)
        update_spreadsheet(spreadsheet_id, 'hecras', 'C2', right_bank_station)
        update_spreadsheet(spreadsheet_id, 'hecras', 'D2', river_mile_length)
        update_spreadsheet(spreadsheet_id, 'hecras', 'E2', river_mile_ratio)
        update_spreadsheet(spreadsheet_id, 'hecras', 'F2', yr100)
        logger.debug("Spreadsheet updated.")
        logger.debug("gdrive: complete")
    except Exception as e:
        logger.debug(f"gdrive: failed- {e}")
