from bs4 import BeautifulSoup
from datetime import date
from pyppeteer import launch

import asyncio
import os


FILENAME = ""
URL = ""

from enum import Enum, auto
from dataclasses import dataclass


class ElementTypeHTML(Enum):
    A = "a"
    DIV = "div"
    SPAN = "span"


class Attribute(Enum):
    COMPANY_NAME = auto()
    JOB_TITLE = auto()


@dataclass
class Selector:
    html: str
    class_: str


SELECTORS = {
    Attribute.COMPANY_NAME: Selector(ElementTypeHTML.A.value, "css-l4opor"),
    "company_name": Selector(ElementTypeHTML.A.value, "css-l4opor"),
    Attribute.JOB_TITLE: Selector(ElementTypeHTML.DIV.value, "css-1id4k1"),
    "job_title": Selector(ElementTypeHTML.DIV.value, "css-1id4k1"),

}

async def download_page():
    browser = await launch()
    page = await browser.newPage()

    await page.goto(URL)
    page_content = await page.content()

    # propose filename & wait for input

    with open(FILENAME, "w") as file:
        file.write(page_content)

    await browser.close()


asyncio.get_event_loop().run_until_complete(download_page())


def get_attribute(soup, attribute):
    element = soup.find(SELECTORS[attribute].html, class_=SELECTORS[attribute].class_)
    return element


def get_company_name(soup):
    company_name = soup.find(
        name= SELECTORS[Attribute.COMPANY_NAME].html,
        class_=SELECTORS[Attribute.COMPANY_NAME].class_
    )
    # company_name = soup.find(SELECTORS["company_name"].html, class_=SELECTORS["company_name"].class_)
    return company_name.get_text()


def get_job_title(soup):
    job_title = soup.find(SELECTORS["job_title"].html, class_=SELECTORS["job_title"].class_)
    return job_title.get_text()


def get_job_title2(soup):
    job_title = get_attribute(soup, Attribute.JOB_TITLE)
    return job_title.get_text()


def get_current_date():
    today = date.today()
    return today.strftime("%y%m%d")


def generate_filename(soup):
    today = get_current_date()
    company_name = get_company_name(soup)
    job_title = get_job_title(soup)
    return f"{today} {company_name} - {job_title}"



def parse():
    with open(FILENAME, "r") as file:
        page_content = file.read()

    soup = BeautifulSoup(page_content, features="html.parser")

    debug_filename = generate_filename(soup)
    print("-"*len(debug_filename))
    print(debug_filename)
    print("-"*len(debug_filename))

    job_title = get_attribute(soup, "job_title")
    print(job_title.get_text())
    job_title = get_attribute(soup, Attribute.JOB_TITLE)
    print(job_title.get_text())

    # import sys
    # sys.exit(0)


    job_title = soup.find("div", class_="css-1id4k1")
    print(job_title.get_text())

    summary_soup = soup.find("div", class_="css-1kgdb8a")
    company_name = summary_soup.find("a", class_="css-l4opor")
    print(company_name.get_text())
    print(company_name["href"])
    print()

    location_soup = soup.find("div", class_="css-1f4p1d3")
    # print("Location soup:", location_soup)
    company_location = location_soup.find("span", class_="css-9wmrp4")
    working_location = location_soup.find("span", class_="css-13p5d07")
    print(company_location.get_text())
    if working_location:
        print(working_location.get_text())
    print()

    salary_soups = soup.find_all("div", class_="css-1wla3xl")
    for salary_soup in salary_soups:
        print(salary_soup.get_text())

    print()
    company_details = summary_soup.find_all("div", class_="css-1ji7bvd")
    for desc, item in zip(["Company Size:", "Level:"], company_details):
        print(desc, item.get_text().strip())
    print()

    # print("Tech stack")
    tech_stack_soup = soup.find("div", class_="css-1ikoimk")
    # print(tech_stack_soup)
    stack_soups = tech_stack_soup.find_all("div", class_="css-1q98d5e")
    for stack_soup in stack_soups:
        tech = stack_soup.find("div", class_="css-1eroaug")
        level = stack_soup.find("div", class_="css-19mz16e")
        print(f"{tech.get_text()}: {level.get_text()}")

    print()
    details = soup.find("div", class_="css-p1hlmi")
    # print(details.get_text())



parse()
