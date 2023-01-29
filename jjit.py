from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from datetime import date
from pyppeteer import launch

import argparse
import asyncio
import os
import urllib.parse


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



class Parser(ABC):
    def __init__(self, text, selectors=None, attributes=None):
        self._text = text
        self._selectors = selectors
        self._attributes = attributes
        self._soup = BeautifulSoup(self._text, features="html.parser")
        self._parsed = []

    @abstractmethod
    def generate_filename(self):
        pass

    @abstractmethod
    def parse(self):
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


class JustJoinITParser(Parser):
    def __init__(self, text, selectors=None, attributes=None):
        selectors = selectors or SELECTORS
        attributes = attributes or Attributes
        super().__init__(text, selectors=selectors, attributes=attributes)

    @staticmethod
    def meets_condition(source):
        return "justjoin" in source

    def generate_filename(self):
        today = date.today().strftime("%y%m%d")
        company_name = self.get_attribute(self._attributes.COMPANY_NAME)
        job_title = self.get_attribute(self._attributes.JOB_TITLE)
        return f"{today} {company_name.get_text()} - {job_title.get_text()}.html"

    def parse(self):
        # with open(os.path.join(RAW_OFFERS_DIR, FILENAME), "r") as file:
        #     page_content = file.read()

        debug_filename = self.generate_filename()
        print("-"*len(debug_filename))
        print(debug_filename)
        print("-"*len(debug_filename))

        job_title = self.get_attribute(Attributes.JOB_TITLE)
        print(job_title.get_text())

        # import sys
        # sys.exit(0)

        summary_soup = self.get_attribute(Attributes.SUMMARY)
        # print(summary_soup.get_text())
        company_name = self.get_attribute(Attributes.COMPANY_NAME, soup=summary_soup)
        print(company_name.get_text())
        print(company_name["href"])
        print()

        location_soup = self.get_attribute(Attributes.LOCATION)

        # print("Location self._soup:", location_soup)
        company_location = self.get_attribute(Attributes.LOCATION_COMPANY, soup=location_soup)
        working_location = self.get_attribute(Attributes.LOCATION_WORK, soup=location_soup)
        print(company_location.get_text())
        if working_location:
            print(working_location.get_text())
        print()

        salary_soups = self.get_attributes(Attributes.SALARY)
        for salary_soup in salary_soups:
            print(salary_soup.get_text())

        print()
        company_details = self.get_attributes(Attributes.COMPANY_DETAILS)
        for desc, item in zip(["Company Size:", "Level:"], company_details):
            print(desc, item.get_text().strip())
        print()

        # print("Tech stack")
        tech_stack_soup = self.get_attribute(Attributes.TECH_STACK)
        # print(tech_stack_soup)
        stack_soups = self.get_attributes(Attributes.STACKS, soup=tech_stack_soup)
        for stack_soup in stack_soups:
            tech = self.get_attribute(Attributes.TECH, soup=stack_soup)
            level = self.get_attribute(Attributes.LEVEL, soup=stack_soup)
            print(f"{tech.get_text()}: {level.get_text()}")

        print()
        details = self.get_attribute(Attributes.DESCRIPTION)
        # print(details.get_text())


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



def main():
    source = get_cli_arguments()
    is_url = source.startswith("https:")
    is_file = os.path.exists(source)

    if is_url:
        page_content = asyncio.run(download_page(source))
        portal = get_portal_from_url(source)
        proposed_filename = "text.html"

        try:
            parser_cls = get_portal_parser(portal)
            print(parser_cls)
            parser = parser_cls(page_content)
            proposed_filename = parser.generate_filename()
        except NotImplementedError as e:
            print(e)
            return
        finally:
            filename = ask_user_for_filename(proposed_filename)
            save_to_file(page_content, os.path.join(RAW_OFFERS_DIR, filename))

    elif is_file:
        with open(source, "r") as file:
            page_content = file.read()
        portal = identify_portal(page_content)

        try:
            parser_cls = get_portal_parser(portal)
            print(parser_cls)
            parser = parser_cls(page_content)
        except NotImplementedError as e:
            print(e)
            return

    parser.parse()


def ask_user_for_filename(proposition):
    print(proposition)
    user_filename = input(
        f"Provide a filename or confirm \"{proposition}\" [Enter]: "
    )
    print(user_filename)
    filename = user_filename or proposition
    return filename


def get_cli_arguments():
    parser = argparse.ArgumentParser()

    # group = parser.add_mutually_exclusive_group(required=True)
    # group.add_argument("--url", default=None)
    # group.add_argument("--file", default=None)

    parser.add_argument("source")
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
