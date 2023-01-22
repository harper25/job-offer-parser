from bs4 import BeautifulSoup
from datetime import date
from pyppeteer import launch

import asyncio
import os


FILENAME = ""
URL = ""

RAW_OFFERS_DIR = "offers_raw"
OFFERS_DIR = "offers"


from enum import Enum, auto
from dataclasses import dataclass


class ElementTypeHTML(Enum):
    A = "a"
    DIV = "div"
    SPAN = "span"


class Attributes(Enum):
    COMPANY_NAME = auto()
    JOB_TITLE = auto()
    SUMMARY = auto()
    LOCATION = auto()
    LOCATION_COMPANY = auto()
    LOCATION_WORK = auto()
    SALARY = auto()
    COMPANY_DETAILS = auto()
    TECH_STACK = auto()
    STACKS = auto()
    TECH = auto()
    LEVEL = auto()
    DESCRIPTION = auto()


@dataclass
class Selector:
    html: str
    class_: str


SELECTORS = {
    Attributes.COMPANY_NAME: Selector(ElementTypeHTML.A.value, "css-l4opor"),
    Attributes.JOB_TITLE: Selector(ElementTypeHTML.DIV.value, "css-1id4k1"),
    Attributes.SUMMARY: Selector(ElementTypeHTML.DIV.value, "css-1kgdb8a"),
    Attributes.LOCATION: Selector(ElementTypeHTML.DIV.value, "css-1f4p1d3"),
    Attributes.LOCATION_COMPANY: Selector(ElementTypeHTML.SPAN.value, "css-9wmrp4"),
    Attributes.LOCATION_WORK: Selector(ElementTypeHTML.SPAN.value, "css-13p5d07"),
    Attributes.SALARY: Selector(ElementTypeHTML.DIV.value, "css-1wla3xl"),
    Attributes.COMPANY_DETAILS: Selector(ElementTypeHTML.DIV.value, "css-1ji7bvd"),
    Attributes.TECH_STACK: Selector(ElementTypeHTML.DIV.value, "css-1ikoimk"),
    Attributes.STACKS: Selector(ElementTypeHTML.DIV.value, "css-1q98d5e"),
    Attributes.TECH: Selector(ElementTypeHTML.DIV.value, "css-1eroaug"),
    Attributes.LEVEL: Selector(ElementTypeHTML.DIV.value, "css-19mz16e"),
    Attributes.DESCRIPTION: Selector(ElementTypeHTML.DIV.value, "css-p1hlmi"),
}

async def download_page():
    browser = await launch()
    page = await browser.newPage()

    await page.goto(URL)
    page_content = await page.content()

    # propose filename & wait for input

    with open(os.path.join(RAW_OFFERS_DIR, FILENAME), "w") as file:
        file.write(page_content)

    await browser.close()


asyncio.get_event_loop().run_until_complete(download_page())


def get_attribute(soup, attribute, selectors=SELECTORS):
    element = soup.find(selectors[attribute].html, class_=selectors[attribute].class_)
    return element


def get_attributes(soup, attribute, selectors=SELECTORS):
    element = soup.find_all(selectors[attribute].html, class_=selectors[attribute].class_)
    return element


def get_current_date():
    today = date.today()
    return today.strftime("%y%m%d")


def generate_filename(soup):
    today = get_current_date()
    company_name = get_attribute(soup, Attributes.COMPANY_NAME)
    job_title = get_attribute(soup, Attributes.JOB_TITLE)

    return f"{today} {company_name.get_text()} - {job_title.get_text()}"



def parse():
    with open(os.path.join(RAW_OFFERS_DIR, FILENAME), "r") as file:
        page_content = file.read()

    soup = BeautifulSoup(page_content, features="html.parser")

    debug_filename = generate_filename(soup)
    print("-"*len(debug_filename))
    print(debug_filename)
    print("-"*len(debug_filename))

    job_title = get_attribute(soup, Attributes.JOB_TITLE)
    print(job_title.get_text())

    # import sys
    # sys.exit(0)

    summary_soup = get_attribute(soup, Attributes.SUMMARY)
    # print(summary_soup.get_text())
    company_name = get_attribute(summary_soup, Attributes.COMPANY_NAME)
    print(company_name.get_text())
    print(company_name["href"])
    print()

    location_soup = get_attribute(soup, Attributes.LOCATION)

    # print("Location soup:", location_soup)
    company_location = get_attribute(location_soup, Attributes.LOCATION_COMPANY)
    working_location = get_attribute(location_soup, Attributes.LOCATION_WORK)
    print(company_location.get_text())
    if working_location:
        print(working_location.get_text())
    print()

    salary_soups = get_attributes(soup, Attributes.SALARY)
    for salary_soup in salary_soups:
        print(salary_soup.get_text())

    print()
    company_details = get_attributes(soup, Attributes.COMPANY_DETAILS)
    for desc, item in zip(["Company Size:", "Level:"], company_details):
        print(desc, item.get_text().strip())
    print()

    # print("Tech stack")
    tech_stack_soup = get_attribute(soup, Attributes.TECH_STACK)
    # print(tech_stack_soup)
    stack_soups = get_attributes(tech_stack_soup, Attributes.STACKS)
    for stack_soup in stack_soups:
        tech = get_attribute(stack_soup, Attributes.TECH)
        level = get_attribute(stack_soup, Attributes.LEVEL)
        print(f"{tech.get_text()}: {level.get_text()}")

    print()
    details = get_attribute(soup, Attributes.DESCRIPTION)
    # print(details.get_text())



parse()
