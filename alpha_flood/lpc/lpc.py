import os
import sys
from pathlib import Path
import argparse
sys.path.append(
    "/home/jpournelle/python_projects/plabz/river_division/main"
    )
import os.path
import time
import numpy as np
import requests
from bs4 import BeautifulSoup
from configs.config import OUTPUT_DIR, LOG_DIR, BASE_DIR
from configs.file_paths import *
from helpers.geom_helper import *
from configs.input_vars import *
from helpers.misc_helper import *
from helpers.multiprocessing_helper import *
import uuid
from multiprocessing import Pool, cpu_count
import pyproj
import rasterio.mask
import shapely.geometry
from shapely.wkt import loads
import wget
from shapely.geometry import (
    Point,
    Polygon,
    LineString,
    MultiPoint,
    MultiPolygon
    )
import geopandas as gpd
import asyncio
import aiofiles
import aiohttp
import json
import aiohttp
from io import BytesIO
import logging
import setproctitle
from loggers.logger import setup_logger

logger = setup_logger(__name__, __name__)


def check_site_speed(url, max_duration=2):
    """
    Check if the response time of the website is within the acceptable
    duration.

    :param url: URL of the website.
    :param max_duration: Maximum acceptable response time in seconds.
    :return: True if the response time is within the limit,
    False otherwise.
    """
    try:
        start_time = time.time()
        response = requests.get(url)
        response.raise_for_status()
        end_time = time.time()
        duration = end_time - start_time
        return duration <= max_duration
    except requests.RequestException as e:
        logger.debug(f"Error checking site speed: {e}")
        return False


def download_file(url, filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def lpc(projectnumber=None, parcelid=None, base_dir=None):
    try:
        gs = None
        BASE_DIR = Path(base_dir)
        setproctitle.setproctitle('alpha_lpc')
        # filename = IN_SHP_MAIN_SUBSET_2
        parcel_id = parcelid
        in_gdf = gpd.read_file(IN_SHP_MAIN_SUBSET_2)
        if in_gdf.index.name != 'PARCELID':
            in_gdf.set_index('PARCELID', inplace=True)
        try:
            out_geom = in_gdf.at[parcel_id, 'geometry']
            gs = gpd.GeoSeries(out_geom)
            logger.debug(f"PARCELID found-geometry:{out_geom}")
        except KeyError:
            logger.debug(f"PARCELID not found:{parcel_id}")
        except Exception as e:
            logger.debug(f"Error: {e}")
        # result = parcel_geom(filename, parcel_id)
        # gs = gpd.GeoSeries(result[0]['geometry'])
    except Exception as e:
        logger.debug(f"Error: {e}")
    try:
        if gs is None:
            logger.debug("gs_1= None-lpc killed")
            return None
        gdf_grid = gpd.read_file(LPC_GRID)
        mpolygons = gdf_grid
        gs_envelope = gs.envelope
        logger.debug("gs_envelope: %s", gs_envelope)
        vertices = list(gs_envelope[0].exterior.coords)
        intersects_lst = []
        unique_lst = []
        laz_lst = []
        for index, polygon in enumerate(mpolygons['geometry']):
            for vertex in vertices:
                point = Point(vertex)
                if point.intersects(polygon) or point.within(polygon):
                    laz_value = mpolygons.iloc[index]['DownloadLA']
                    if laz_value not in laz_lst:
                        unique_lst.append(vertex)
                        laz_lst.append(laz_value)
        with open(
            os.path.join(
                BASE_DIR, 'zz_python_do_not_touch/laz_files.txt'
                ), 'w') as f:
            pass
        for laz in laz_lst:
            with open(
                os.path.join(
                    BASE_DIR, 'zz_python_do_not_touch/laz_files.txt'
                    ), 'a') as f:
                f.write(f"{laz}\n")
            laz_file = str(f"{BASE_DIR}/zz_python_do_not_touch/" \
                + f"{uuid.uuid4()}_{projectnumber}.laz")
            logger.debug(laz_file)
            # download_file(laz, laz_file)
            # filename = wget.download(laz, laz_file)
            # logger.debug("laz download complete")
        logger.debug("lpc: complete")
    except (FileNotFoundError, PermissionError) as e:
        logger.debug("get_lpc_laz:failed")
        logger.debug("error: %s", e)
    except Exception as e:
        logger.debug("get_lpc_laz:failed")
        logger.debug("error: %s", e)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AlphApex Floodway Program- LPC"
        )
    parser.add_argument(
        "--projectnumber",
        help="Project Number",
        )
    parser.add_argument(
        "--parcelid",
        help="Parcel ID",
        )
    parser.add_argument(
        "--base_dir",
        help="Base Directory",
        )
    args = parser.parse_args()
    lpc(args.projectnumber, args.parcelid, args.base_dir)
