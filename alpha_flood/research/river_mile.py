"""
This module contains a function that generates a PDF file containing a
map of river mile for a given project number, using the provided
GeoDataFrames.

Functions:
- river_mile(projectnumber, gs_1, gdf_hxline, logger_1):
Generates a PDF file containing a map of river mile for a given
project number, using the provided GeoDataFrames.
"""
import os
import os.path
import setproctitle
import folium
import json
import time
import geopandas as gpd
from shapely.geometry import (
    Polygon,
    Point,
    LineString,
    MultiLineString,
    MultiPolygon,
    MultiPoint,
    mapping,
    shape
    )
from configs.config import *
from configs.file_paths import *
from configs.input_vars import *
from helpers.misc_helper import style_function
from PIL import Image
from reportlab.pdfgen import canvas
import pyproj
from shapely.ops import transform
from loggers.logger import setup_logger
import asyncio
from pyppeteer import launch

logger = setup_logger(__name__, __name__)


def river_mile_1(projectnumber, gs_1, gdf_hxline):
    """
    Generates a PDF file containing a map of river mile for a given
    project number, using the provided GeoDataFrames.

    Args:
    - projectnumber (str): The project number to use in the file name.
    - gs_1 (GeoDataFrame): A GeoDataFrame containing the data to be
    used for the map.
    - gdf_hxline (GeoDataFrame): A GeoDataFrame containing the data to
    be used for the map.

    Returns:
    - None
    """
   
    try:
        setproctitle.setproctitle('alpha_river_mile')
        crs_source = pyproj.CRS("EPSG:6441")
        crs_target = pyproj.CRS("EPSG:4326")
        project = pyproj.Transformer.from_crs(
            crs_source,
            crs_target,
            always_xy=True).transform
        gdf_gs = transform(project, gs_1)
        gdf_hx = gdf_hxline["geometry"][0]
        gdf_hx_line = transform(project, gdf_hx)
        try:
            gdf_p = gpd.GeoSeries([gdf_gs])
        except Exception as e:
            logger.error(
                f"An error occurred while processing gs_1: {e}"
                )
        try:
            gdf_xs = gpd.GeoSeries([gdf_hx_line])
        except Exception as e:
            logger.error(
                f"An error occurred while processing hx_line: {e}"
                )
    except Exception as e:
        logger.error(
            f"An error occurred while processing data1: {e}"
            )
    try:
        gs_pbound_c = gdf_p.centroid
        lon, lat = gs_pbound_c.x[0], gs_pbound_c.y[0]
        logger.debug(f"Longitude: {lon}, Latitude: {lat}")
    except Exception as e:
        logger.debug(
            f"An error occurred while processing data2: {e}"
            )
    try:
        shapefile_paths = [EFLDWY, WFLDWY, SUW, SUW_XS]
        folium_geoms = []
        for path in shapefile_paths:
            gdf = gpd.read_file(path)
            if not gdf.empty:
                geometry = shape(gdf.geometry.iloc[0])
                reprojected_geometry = transform(project, geometry)
                gs = gpd.GeoSeries(reprojected_geometry)
                folium_geoms.append(gs)
    except Exception as e:
        logger.debug(
            f"An error occurred while processing geographic data3: {e}"
            )
    time.sleep(1)
    try:
        m = folium.Map(location=[lat, lon], zoom_start=16)
        folium.GeoJson(
            gdf_xs.to_json(), style_function=style_function
        ).add_to(m)
        location = [lat, lon]
        icon = folium.DivIcon(
            html='<div style="font-size: 20pt">Proposed HECRAS XS</div>'
        )
        folium.Marker(location=location, icon=icon).add_to(m)
        folium.GeoJson(gdf_p.to_json()).add_to(m)
        folium.GeoJson(folium_geoms[0].to_json()).add_to(m)
        folium.GeoJson(folium_geoms[1].to_json()).add_to(m)
        map_path = str(DATA_DIR / f"{projectnumber}-RiverMile.html")
        logger.debug(f"map_path= {map_path}")
        m.save(map_path)
        return map_path
    except ValueError as e:
        logger.debug(f"get_river_mile_pdf: failed- {e}")
    except TypeError as e:
        logger.debug(f"get_river_mile_pdf: failed- {e}")
    except AttributeError as e:
        logger.debug(f"get_river_mile_pdf: failed- {e}")
    except FileNotFoundError as e:
        logger.debug(f"get_river_mile_pdf: failed- {e}")
    except Exception as e:
        logger.debug(f"get_river_mile_pdf: failed- {e}")


async def river_mile_2(projectnumber, map_path):
    browser = await launch(
        headless = True,
        # executablePath = '/snap/bin/chromium',
    )
    page = await browser.newPage()
    await page.goto(f"file://{map_path}")
    await page.waitFor(15000)
    await page.screenshot({'path': '/home/jpournelle/example_screenshot1.png'})
    await page.pdf({'path': str(DATA_DIR / f"{projectnumber}-RiverMile.pdf")})
    await browser.close()
    