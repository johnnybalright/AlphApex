"""
This module is designed to fetch and process water level data for the
Suwannee River. It depends on several libraries such as selenium,
pyautogui, and pdfplumber to interact with web elements, automate GUI
interactions, and extract text content from PDFs, respectively.

Key Functions:
- water_level: Takes a project number and a centerline milepost as
inputs and returns the URLs for two PDFs containing water level data
for the Suwannee River. It utilizes a selenium webdriver to navigate
web pages, fetch necessary data, and saves this data as PDFs.
pdfplumber is then used to extract text from the saved PDFs for further
processing.

Environment Setup:
- The environment variables are loaded from a `.env` file using the
dotenv library.
- A virtual display is set up using pyvirtualdisplay to allow for
browser automation in a headless environment.

External Configurations:
- Configurations such as DATA_DIR are imported from an external config
module.
- undetected_chromedriver is used as a dependency to bypass bot
detection mechanisms on websites.

Error Handling:
- The code includes error-handling mechanisms to manage potential
errors during webdriver interactions,
  logging checkpoints and errors for debugging purposes.

This module is primarily configured to run in a Linux environment,
with paths and configurations
suited to a Linux OS. Adjustments may be necessary to execute this
script in a different OS environment.
"""
import os
import os.path
import time
from bs4 import BeautifulSoup
from configs.config import DATA_DIR
from helpers.misc_helper import find_index_of_substring_in_list, url_active
from loggers.logger import setup_logger
import setproctitle
import aiohttp
import asyncio

logger = setup_logger(__name__, __name__)


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()
    
    
def water_level_url(
    projectnumber,
    gdf_center_xs_line_mile,
    river_frontage_length
    ):
    """
    Given a project number and a centerline milepost, returns the URLs
    for two PDFs containing water level data for the Suwannee River.
    The URLs are determined based on the centerline milepost value,
    which is used to determine which section of the river the project
    is located in. The function returns None if the centerline milepost
    is outside the range of the river's sections.

    Args:
    - projectnumber: str, the project number
    - gdf_center_xs_line_mile: float, the centerline milepost

    Returns:
    - water_level_url_1: str or None, the URL for the first PDF
    containing water level data
    - water_level_url_2: str or None, the URL for the second PDF
    containing water level data
    """
    try:
        if river_frontage_length == 0:
            logger.debug("get_water_level_data: skipped")
            delta_water_level_el = None
            upper_xs = None
            lower_xs = None
            result = (delta_water_level_el, upper_xs, lower_xs)
            return result
        setproctitle.setproctitle('alpha_water_level')
        logger.debug(gdf_center_xs_line_mile)
        water_level_path_1 = DATA_DIR / f"{projectnumber}-WaterLevel1.pdf"
        water_level_path_2 = DATA_DIR / f"{projectnumber}-WaterLevel2.pdf"
        if float(221) >= float(gdf_center_xs_line_mile) >= float(196):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02314500"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02315000"
            upper_xs = int(221)
            lower_xs = int(196)
        else:
            pass
        if float(196) >= float(gdf_center_xs_line_mile) >= float(171):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02315000"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02315500"
            upper_xs = int(196)
            lower_xs = int(171)
        else:
            pass
        if float(171) >= float(gdf_center_xs_line_mile) >= float(150):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02315500"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02315550"
            upper_xs = int(171)
            lower_xs = int(150)
        else:
            pass
        if float(150) >= float(gdf_center_xs_line_mile) >= float(135):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02315550"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02315650"
            upper_xs = int(150)
            lower_xs = int(135)
        else:
            pass
        if float(135) >= float(gdf_center_xs_line_mile) >= float(127):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02315650"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02319500"
            upper_xs = int(135)
            lower_xs = int(127)
        else:
            pass
        if float(127) >= float(gdf_center_xs_line_mile) >= float(113):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02319500"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02319800"
            upper_xs = int(127)
            lower_xs = int(113)
        else:
            pass
        if float(113) >= float(gdf_center_xs_line_mile) >= float(103):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02319800"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02320000"
            upper_xs = int(113)
            lower_xs = int(103)
        else:
            pass
        if float(103) >= float(gdf_center_xs_line_mile) >= float(98):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02320000"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02320000"
            upper_xs = int(103)
            lower_xs = int(98)
        else:
            pass
        if float(98) >= float(gdf_center_xs_line_mile) >= float(76):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02320000"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02320500"
            upper_xs = int(98)
            lower_xs = int(76)
        else:
            pass
        if float(76) >= float(gdf_center_xs_line_mile) >= float(57):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02320500"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323000"
            upper_xs = int(76)
            lower_xs = int(57)
        else:
            pass
        if float(57) >= float(gdf_center_xs_line_mile) >= float(43):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323000"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323150"
            upper_xs = int(57)
            lower_xs = int(43)
        else:
            pass
        if float(43) >= float(gdf_center_xs_line_mile) >= float(34):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323150"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323500"
            upper_xs = int(43)
            lower_xs = int(34)
        else:
            pass
        if float(34) >= float(gdf_center_xs_line_mile) >= float(25):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323500"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323567"
            upper_xs = int(34)
            lower_xs = int(25)
        else:
            pass
        if float(25) >= float(gdf_center_xs_line_mile) >= float(17):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323567"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323590"
            upper_xs = int(25)
            lower_xs = int(17)
        else:
            pass
        if float(17) >= float(gdf_center_xs_line_mile) >= float(9):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323590"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323592"
            upper_xs = int(17)
            lower_xs = int(9)
        else:
            pass
        return water_level_url_1, water_level_url_2, upper_xs, lower_xs
    except Exception as e:
        logger.debug(f"water_level_url: failed-{e}")
    
async def get_wl_data(url_1, url_2, upper_xs, lower_xs, gdf_center_xs_line_mile):
    async with aiohttp.ClientSession() as session:
        html_1 = await fetch(session, url_1)
        html_2 = await fetch(session, url_2)
        soup_1 = BeautifulSoup(html_1, 'html.parser')
        soup_2 = BeautifulSoup(html_2, 'html.parser')
        tables_1 = soup_1.find('table')
        tables_2 = soup_2.find('table')
        last_row_1 = tables_1.find_all('tr')[-1]
        last_row_2 = tables_2.find_all('tr')[-1]
        gag_ht_1 = last_row_1.find_all('td')[1].get_text()
        gag_ht_2 = last_row_2.find_all('td')[1].get_text()
        date_1 = last_row_1.find_all('td')[0].get_text()
        date_2 = last_row_2.find_all('td')[0].get_text()
        water_level_1_at_date = gag_ht_1
        water_level_1_date = date_1
        water_level_2_at_date = gag_ht_2
        water_level_2_date = date_2
        logger.debug("water_level_1_at_date: %s", water_level_1_at_date)
        logger.debug("water_level_1_date: %s", water_level_1_date)
        logger.debug("water_level_2_at_date: %s", water_level_2_at_date)
        logger.debug("water_level_2_date: %s", water_level_2_date)
        run = float(upper_xs) - float(lower_xs)
        logger.debug("run: %s", run)
        rise = float(water_level_1_at_date) - float(water_level_2_at_date)
        logger.debug("rise: %s", rise)
        slope = float(rise) / float(run)
        logger.debug("slope: %s", slope)
        df_run = float(upper_xs) - float(gdf_center_xs_line_mile)
        logger.debug("df_run: %s", df_run)
        delta = float(df_run) * float(slope)
        logger.debug("delta: %s", delta)
        delta_water_level = float(lower_xs) + float(delta)
        logger.debug("delta_water_level: %s", delta_water_level)
        delta_water_level_el = float(water_level_1_at_date) - float(delta)
        logger.debug(delta_water_level_el)
        logger.debug("get_water_level_data: complete")
    result = (delta_water_level_el, upper_xs, lower_xs)
    return result
