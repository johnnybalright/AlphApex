# Filename: flood_report.py
"""
This module contains a function that performs parcel research for a
given parcel ID and county, and saves the resulting flood report as a
PDF file.

The function `parcel_research` takes in the following arguments:
- projectnumber (str): The project number associated with the parcel
research.
- path (str): The path to the directory where the PDF file will be
saved.
- parcelid (str): The parcel ID to be researched.
- clean_parcelid (str): The cleaned version of the parcel ID.
- county (str): The county where the parcel is located.

The function does not return anything.
"""
import argparse
import setproctitle
# setproctitle.setproctitle('alpha_flood_report')
import sys
sys.path.append("/home/jpournelle/python_projects/plabz/river_division/main")
from dotenv import load_dotenv
load_dotenv(
    "/home/jpournelle/python_projects/" \
        + "plabz/river_division/main/main.env"
        )
import tracemalloc
from configs.config import DATA_DIR, BASE_DIR
from configs.input_vars import *
from loggers.logger import setup_logger
import asyncio
from pyppeteer import launch
tracemalloc.start()
import time
from pathlib import Path

logger = setup_logger(__name__, __name__)


async def flood_report(projectnumber, clean_parcelid):
    try:
        setproctitle.setproctitle('alpha_flood_report')
        logger.debug("flood_report:starting")
        browser = await launch(
            headless = True,
            # executablePath = '/snap/bin/chromium',
        )
        page = await browser.newPage()
        await page.goto('https://www.srwmdfloodreport.com/')
        await page.waitFor(10000)
        selector_1 = '#button-1063-btnInnerEl'
        await page.waitForSelector(selector_1, {'visible': True})
        link_1 = await page.querySelector(selector_1)
        await link_1.click()
        await page.waitFor(5000)
        selector_2 = '#showSearchBtn-btnIconEl'
        await page.waitForSelector(selector_2, {'visible': True})
        link_2 = await page.querySelector(selector_2)
        await link_2.click()
        await page.waitFor(5000)
        selector_2_2 = '#parcelId_CountySearchForm-inputEl'
        await page.waitForSelector(selector_2_2, {'visible': True})
        await page.type('#parcelId_CountySearchForm-inputEl', f'{clean_parcelid}')
        await page.waitFor(3000)
        await page.click('#button-1070-btnEl')
        # await page.screenshot({'path': '/home/jpournelle/example_screenshot1.png'})
        await page.waitFor(5000)
        selector_3 = '#button-1006-btnInnerEl'
        await page.waitForSelector(selector_3, {'visible': True})
        link_3 = await page.querySelector(selector_3)
        await link_3.click()
        await page.waitFor(10000)
        selector_4 = '#generateRptBtn-btnInnerEl'
        await page.waitForSelector(selector_4, {'visible': True})
        link_4 = await page.querySelector(selector_4)
        await link_4.click()
        await page.waitFor(6000)
        pages = await browser.pages()
        page_lst = [p for p in pages if p != page]
        new_tab = page_lst[1]
        await new_tab.bringToFront()
        await new_tab.pdf({'path': str(DATA_DIR / f"{projectnumber}-FloodReport.pdf")})
        await browser.close()
        result = "flood_report:complete"
        logger.debug("flood_report:complete")
        return result
    except Exception as e:
        logger.debug(f"flood_report: failed- {e}")
    
# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(
#         description="AlphApex Floodway Program- Flood Report"
#         )
#     parser.add_argument(
#         "--projectnumber",
#         help="Project Number",
#         )
#     parser.add_argument(
#         "--clean_parcelid",
#         help="Parcel ID with hyphens removed",
#         )
#     parser.add_argument(
#         "--base_dir",
#         help="Base directory for project",
#         )
#     args = parser.parse_args()
#     flood_report(args.projectnumber, args.clean_parcelid, args.base_dir)
