import sys

sys.path.append(
    "/home/jpournelle/python_projects/plabz/river_division/main"
    )
import os.path
import os
import time
from pathlib import Path

import pandas as pd
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, wait
import img2pdf
import undetected_chromedriver as uc
from configs.config import (
    LOG_DIR,
    DATA_DIR,
    BASE_DIR,
    PARENT_DIR,
    OUTPUT_DIR
    )
from configs.input_vars import *
from PIL import Image
from contextlib import contextmanager
import multiprocessing
import threading
import folium
import json
import polyline
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import requests
from shapely.geometry import LineString, Polygon, Point
import logging
import setproctitle
import aiohttp
import asyncio
from pyppeteer import launch
from undetected_playwright.async_api import async_playwright, Playwright
from fpdf import FPDF
from loggers.logger import setup_logger

logger = setup_logger(__name__, __name__)


async def handle_popup(popup):
    print("Popup detected:", popup.url)
    await popup.close()


async def parcel_research_2(playwright, projectnumber, parcelid, county):
    try:
        if county == "SUWANNEE":
            return None
        elif county == "COLUMBIA":
            return None
        elif county == "LAFAYETTE":
            return None
        if county == "GILCHRIST":
            parcel_url = GILCHRIST_PARCEL_URL
            map_url = GILCHRIST_MAP_URL
            indices = None
        elif county == "DIXIE":
            parcel_url = DIXIE_PARCEL_URL
            map_url = DIXIE_MAP_URL
            indices = [2, 4, 6, 10, 14]
        elif county == "LEVY":
            parcel_url = LEVY_PARCEL_URL
            map_url = LEVY_MAP_URL
            indices = None
        elif county == "HAMILTON":
            parcel_url = HAMILTON_PARCEL_URL
            map_url = HAMILTON_MAP_URL
            indices = None
        elif county == "MADISON":
            parcel_url = MADISON_PARCEL_URL
            map_url = MADISON_MAP_URL
            indices = None
        if county == "SUWANNEE":
            return None
        elif county == "COLUMBIA":
            return None
        elif county == "LAFAYETTE":
            return None
        if county == "GILCHRIST":
            parcel_url = GILCHRIST_PARCEL_URL
            map_url = GILCHRIST_MAP_URL
            indices = None
        elif county == "DIXIE":
            parcel_url = DIXIE_PARCEL_URL
            map_url = DIXIE_MAP_URL
            indices = [2, 4, 6, 10, 14]
        elif county == "LEVY":
            parcel_url = LEVY_PARCEL_URL
            map_url = LEVY_MAP_URL
            indices = None
        elif county == "HAMILTON":
            parcel_url = HAMILTON_PARCEL_URL
            map_url = HAMILTON_MAP_URL
            indices = None
        elif county == "MADISON":
            parcel_url = MADISON_PARCEL_URL
            map_url = MADISON_MAP_URL
            indices = None
        args = []
        args.append("--disable-blink-features=AutomationControlled")
        browser = await playwright.firefox.launch(headless=True,
                                                args=args)
        page = await browser.new_page()
        page.on("popup", handle_popup)
        parcelid_value = insert_hyphens(parcelid, indices)
        url_1 = parcel_url + parcelid_value
        await page.goto(url_1)
        try:
            button_1 = await page.query_selector("#appBody > div.modal.in > div > div > div.modal-focus-target > div.modal-footer > a.btn.btn-primary.button-1")
            await button_1.click()
        except:
            pass
        try:
            button_2 = await page.query_selector('#appBody > div.modal.in > div > div > div.modal-focus-target > div.modal-footer > a')
            await button_2.click()
        except:
            pass
        try:
            button_3 = await page.query_selector('#appBody > div.modal.in > div > div > div.modal-focus-target > div.modal-footer > a')
            await button_3.click()
        except:
            pass
        png_path_1 = str(DATA_DIR / f"{projectnumber}-PropDetails.png")
        pdf_path_1 = str(DATA_DIR / f"{projectnumber}-PropDetails.pdf")
        await page.screenshot(path=png_path_1, full_page=True)
        await asyncio.sleep(5)
        url_2 = map_url + parcelid_value
        await page.goto(url_2)
        try:
            button_1 = await page.query_selector("#appBody > div.modal.in > div > div > div.modal-focus-target > div.modal-footer > a.btn.btn-primary.button-1")
            await button_1.click()
        except:
            pass
        try:
            button_2 = await page.query_selector('#appBody > div.modal.in > div > div > div.modal-focus-target > div.modal-footer > a')
            await button_2.click()
        except:
            pass
        try:
            button_3 = await page.query_selector('#appBody > div.modal.in > div > div > div.modal-focus-target > div.modal-footer > a')
            await button_3.click()
        except:
            pass
        png_path_2 = str(DATA_DIR / f"{projectnumber}-PropMap.png")
        pdf_path_2 = str(DATA_DIR / f"{projectnumber}-PropMap.pdf")
        await page.screenshot(path=png_path_2, full_page=True)
        await browser.close()
        await async_convert_png_to_pdf(png_path_1, pdf_path_1)             
        await async_convert_png_to_pdf(png_path_2, pdf_path_2)
    except Exception as e:
        logger.debug(f"parcel_research_2: failed- {e}")


def insert_hyphens(s, indices):
    """
    Inserts hyphens in the string s at the specified indices, if they are not already present.

    :param s: The original string of integers.
    :param indices: A list of indices where hyphens should be inserted.
    :return: The modified string with hyphens, or the original string if hyphens are already present.
    """
    if indices == None:
        return s
    if "-" in s:
        return s
    for index in sorted(indices, reverse=True):
        s = s[:index] + "-" + s[index:]
    return s


async def parcel_research_1(projectnumber, parcelid, county):
    try:
        if county == "GILCHRIST":
            return None
        elif county == "DIXIE":
            return None
        elif county == "LEVY":
            return None
        elif county == "HAMILTON":
            return None
        elif county == "MADISON":
            return None
        if county == "SUWANNEE":
            parcel_url = SUWANNEE_PARCEL_URL
        elif county == "COLUMBIA":
            parcel_url = COLUMBIA_PARCEL_URL
        elif county == "LAFAYETTE":
            parcel_url = LAFAYETTE_PARCEL_URL
        browser = await launch(
            headless=False,
            executablePath="/snap/bin/chromium",
        )

        page = await browser.newPage()
        await page.goto(parcel_url)
        await page.waitFor(5000)
        await page.waitForSelector("#recordSearchContent_1_iframe")
        iframe = next(
            (
                frame
                for frame in page.frames
                if frame.name == "recordSearchContent_1_iframe"
            ),
            None,
        )
        await page.waitFor(5000)
        if iframe:
            element = await iframe.querySelector("#PIN")
            if element:
                await element.click()
                await page.keyboard.type(parcelid)
                await page.keyboard.press("Enter")
        await page.waitFor(5000)
        await page.waitForSelector("#recordSearchContent_1_iframe")
        iframe_2 = next(
            (
                frame
                for frame in page.frames
                if frame.name == "recordSearchContent_1_iframe"
            ),
            None,
        )
        await iframe_2.evaluate("""() => {
            Detail('1');
        }""")
        await page.waitFor(5000)
        await page.pdf({"path": str(DATA_DIR / f"{projectnumber}-PropDetails.pdf")})
        await page.evaluate("""() => {
            parent.ClickTab(4,false);
        }""")
        print_screen = await page.querySelector("#zPRINT")
        await print_screen.click()
        await page.waitFor(5000)
        print_tab = await page.querySelector("#gisSideMenuButton_4")
        await print_tab.click()
        await page.waitFor(5000)
        await page.evaluate("""() => {
            gisSideMenu_saveGISimage_submit('2');
        }""")
        await page.waitFor(5000)
        pages = await browser.pages()
        page_lst = [p for p in pages if p != page]
        new_tab = page_lst[1]
        await new_tab.bringToFront()
        await page.waitFor(5000)
        await new_tab.pdf({"path": str(DATA_DIR / f"{projectnumber}-PropMap.pdf")})
        await browser.close()
    except Exception as e:
        logger.debug(f"parcel_research_1: failed- {e}")
    

def convert_png_to_pdf(png_file, pdf_file):
    image = Image.open(png_file)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    pdf = FPDF(unit="pt", format=[image.width, image.height])
    pdf.add_page()
    pdf.image(png_file, 0, 0)
    pdf.output(pdf_file, "F")


async def async_convert_png_to_pdf(png_file, pdf_file):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, convert_png_to_pdf, png_file, pdf_file)
