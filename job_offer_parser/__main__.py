from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from datetime import date
from pyppeteer import launch
from typing import Protocol

import argparse
import asyncio
import os
import textwrap
import urllib.parse


RAW_OFFERS_DIR = "offers_raw"
OFFERS_DIR = "offers"
DEFAULT_RAW_OFFER_FILENAME = "test.html"

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


class Parser(ABC):
    def __init__(self, text, selectors=None, attributes=None):
        self._text = text
        self._selectors = selectors
        self._attributes = attributes
        self._soup = BeautifulSoup(self._text, features="html.parser")
        self._parsed = []

    @abstractmethod
    def parse(self):
        pass

    @abstractmethod
    def get_company_name(self):
        pass

    @abstractmethod
    def get_job_title(self):
        pass

    @staticmethod
    @abstractmethod
    def meets_condition(portal):
        pass

    def get_attribute(self, attribute, soup=None):
        soup = soup or self._soup
        element = soup.find(
            self._selectors[attribute].html,
            class_=self._selectors[attribute].class_
        )
        return element

    def get_attributes(self, attribute, soup=None):
        soup = soup or self._soup
        element = soup.find_all(
            self._selectors[attribute].html,
            class_=self._selectors[attribute].class_
        )
        return element


class ParserGenerateFilename(Protocol):
    def get_company_name(self):
        ...

    def get_job_title(self):
        ...


class JustJoinITParser(Parser):
    def __init__(self, text, selectors=None, attributes=None):
        selectors = selectors or SELECTORS
        attributes = attributes or Attributes
        super().__init__(text, selectors=selectors, attributes=attributes)

    @staticmethod
    def meets_condition(source):
        return "justjoin" in source

    def get_company_name(self):
        return self.get_attribute(self._attributes.COMPANY_NAME).get_text()

    def get_job_title(self):
        return self.get_attribute(self._attributes.JOB_TITLE).get_text()

    def parse(self):
        parsed_job_offer = []
        heading = self._get_heading()
        location = self._get_location()
        salary = self._get_salary()
        team_details = self._get_team_details()
        tech_stacks = self._get_tech_stack()
        detailed_description = self._get_description()
        parsed_job_offer = [
            heading,
            location,
            salary,
            team_details,
            tech_stacks,
            detailed_description
        ]
        return parsed_job_offer

    def _get_heading(self):
        job_title = self.get_attribute(self._attributes.JOB_TITLE)
        summary_soup = self.get_attribute(self._attributes.SUMMARY)
        company_name = self.get_attribute(self._attributes.COMPANY_NAME, soup=summary_soup)
        company_and_job_title = f"{company_name.get_text()} - {job_title.get_text()}"
        emphasis = "-"*len(company_and_job_title)
        heading_result = "\n".join([emphasis, company_and_job_title, emphasis, company_name["href"]])
        return heading_result

    def _get_location(self):
        location_soup = self.get_attribute(self._attributes.LOCATION)
        company_location = self.get_attribute(self._attributes.LOCATION_COMPANY, soup=location_soup)
        working_location = self.get_attribute(self._attributes.LOCATION_WORK, soup=location_soup)
        location = [company_location.get_text()]
        if working_location:
            location.append(working_location.get_text())
        location_result = "\n".join(location)
        return location_result

    def _get_salary(self):
        salary_soups = self.get_attributes(self._attributes.SALARY)
        salary = [salary_soup.get_text() for salary_soup in salary_soups]
        salary_result = "\n".join(salary)
        return salary_result

    def _get_team_details(self):
        company_details = self.get_attributes(self._attributes.COMPANY_DETAILS)
        details = []
        for desc, item in zip(["Company Size:", "Level:"], company_details):
            details.append(f"{desc} {item.get_text().strip()}")
        details_result = "\n".join(details)
        return details_result

    def _get_tech_stack(self):
        tech_stack_soup = self.get_attribute(self._attributes.TECH_STACK)
        stack_soups = self.get_attributes(self._attributes.STACKS, soup=tech_stack_soup)
        tech_stacks = []
        for stack_soup in stack_soups:
            tech = self.get_attribute(self._attributes.TECH, soup=stack_soup)
            level = self.get_attribute(self._attributes.LEVEL, soup=stack_soup)
            tech_stacks.append(f"{tech.get_text()}: {level.get_text()}")
        tech_stacks_result = "\n".join(tech_stacks)
        return tech_stacks_result

    def _get_description(self):
        details = self.get_attribute(self._attributes.DESCRIPTION)
        return details.get_text()


def identify_portal(page_content):
    soup = BeautifulSoup(page_content, features="html.parser")
    url = soup.find("meta", property="og:url")["content"]
    portal = get_portal_from_url(url)
    return portal


def get_portal_from_url(url):
    parsed_url = urllib.parse.urlparse(url)
    return parsed_url.hostname


def get_portal_parser(portal):
    for parser_cls in Parser.__subclasses__():
        if parser_cls.meets_condition(portal):
            return parser_cls
    raise NotImplementedError(f"No parser found for {portal}!")


def generate_filename(parser: ParserGenerateFilename):
    today = date.today().strftime("%y%m%d")
    company_name = parser.get_company_name()
    job_title = parser.get_job_title()
    return f"{today} {company_name} - {job_title}.html"


def main():
    source = get_cli_arguments()
    is_url = source.startswith("https:")
    is_file = os.path.exists(source)

    if is_file:
        page_content = read_from_file(source)
        portal = identify_portal(page_content)

        try:
            parser_cls = get_portal_parser(portal)
            parser = parser_cls(page_content)
        except NotImplementedError as e:
            print(e)
            return

    elif is_url:
        page_content = asyncio.run(download_page(source))
        portal = get_portal_from_url(source)

        proposed_filename = DEFAULT_RAW_OFFER_FILENAME
        try:
            parser_cls = get_portal_parser(portal)
            parser = parser_cls(page_content)
            proposed_filename = generate_filename(parser)
        except NotImplementedError as e:
            print(e)
            return
        finally:
            filename = ask_user_for_filename(proposed_filename)
            save_to_file(page_content, os.path.join(RAW_OFFERS_DIR, filename))

    parsed_offer = parser.parse()
    print("\n\n".join(parsed_offer))
    print(f"Parsed with {parser.__class__.__name__}")


def ask_user_for_filename(proposition):
    user_filename = input(
        f"Provide a filename or confirm \"{proposition}\" [Enter]: "
    )
    filename = user_filename or proposition
    return filename


def get_cli_arguments():
    parser = argparse.ArgumentParser(
        description = textwrap.dedent(
            '''
            IT Job Offers Parser:
            -> Download raw html of a given web page
            -> Extract job offer data
            -> Save the output for future reference ;)
            '''),
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "source",
        help="Provide URL or filename with raw HTML content"
    )
    # save_raw=True
    # save_output=True # default True
    # print_to_stdout=True # default True

    args = parser.parse_args()
    return args.source


def read_from_file(filename):
    with open(filename, "r") as file:
        content = file.read()
    return content


def save_to_file(text, filename):
    with open(filename, "w") as file:
        file.write(text)


async def download_page(url):
    browser = await launch()
    page = await browser.newPage()

    await page.goto(url)
    page_content = await page.content()
    await browser.close()

    return page_content


if __name__ == "__main__":
    main()
