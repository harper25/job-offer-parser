import argparse
import asyncio
import os
import textwrap
import urllib.parse
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Protocol, Union

from bs4 import BeautifulSoup, PageElement, Tag
from pyppeteer import launch  # type: ignore

RAW_OFFERS_DIR = "raw"
OFFERS_DIR = "offers"
DEFAULT_RAW_OFFER_FILENAME = "test.html"


class AutoNameEnum(Enum):
    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: List[Any]
    ) -> Any:
        return name.lower()


class ElementTypeHTML(AutoNameEnum):
    A = auto()
    DIV = auto()
    SPAN = auto()


class Attributes(AutoNameEnum):
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
    Attributes.COMPANY_NAME.value: Selector(ElementTypeHTML.A.value, "css-l4opor"),
    Attributes.JOB_TITLE.value: Selector(ElementTypeHTML.DIV.value, "css-1id4k1"),
    Attributes.SUMMARY.value: Selector(ElementTypeHTML.DIV.value, "css-1kgdb8a"),
    Attributes.LOCATION.value: Selector(ElementTypeHTML.DIV.value, "css-1f4p1d3"),
    Attributes.LOCATION_COMPANY.value: Selector(
        ElementTypeHTML.SPAN.value, "css-9wmrp4"
    ),
    Attributes.LOCATION_WORK.value: Selector(ElementTypeHTML.SPAN.value, "css-13p5d07"),
    Attributes.SALARY.value: Selector(ElementTypeHTML.DIV.value, "css-1wla3xl"),
    Attributes.COMPANY_DETAILS.value: Selector(
        ElementTypeHTML.DIV.value, "css-1ji7bvd"
    ),
    Attributes.TECH_STACK.value: Selector(ElementTypeHTML.DIV.value, "css-1ikoimk"),
    Attributes.STACKS.value: Selector(ElementTypeHTML.DIV.value, "css-1q98d5e"),
    Attributes.TECH.value: Selector(ElementTypeHTML.DIV.value, "css-1eroaug"),
    Attributes.LEVEL.value: Selector(ElementTypeHTML.DIV.value, "css-19mz16e"),
    Attributes.DESCRIPTION.value: Selector(ElementTypeHTML.DIV.value, "css-p1hlmi"),
}


class AttributeNotFoundError(Exception):
    "Indicate that selected attribute was not found in parsed html"


class Parser(ABC):
    def __init__(self, text: str, selectors: Dict[str, Selector]) -> None:
        self._text = text
        self._selectors = selectors
        self._soup = BeautifulSoup(self._text, features="html.parser")

    @abstractmethod
    def parse(self) -> List[str]:
        pass

    @abstractmethod
    def get_company_name(self) -> str:
        pass

    @abstractmethod
    def get_job_title(self) -> str:
        pass

    @staticmethod
    @abstractmethod
    def meets_condition(portal: str) -> bool:
        pass

    def get_attribute(
        self, attribute: str, soup: Optional[Union[BeautifulSoup, Tag]] = None
    ) -> Tag:
        soup = soup or self._soup
        selector = self._selectors[attribute]
        element = soup.find(selector.html, class_=selector.class_)
        if not isinstance(element, Tag):
            raise AttributeNotFoundError
        return element

    def get_attributes(
        self, attribute: str, soup: Optional[Union[BeautifulSoup, Tag]] = None
    ) -> List[PageElement]:
        soup = soup or self._soup
        selector = self._selectors[attribute]
        element = soup.find_all(selector.html, class_=selector.class_)
        return element


class ParserGenerateFilename(Protocol):
    def get_company_name(self) -> str:
        ...

    def get_job_title(self) -> str:
        ...


class JustJoinITParser(Parser):
    def __init__(
        self,
        text: str,
        selectors: Optional[Dict[str, Selector]] = None,
        attributes: Optional[Attributes] = None,
    ) -> None:
        selectors = selectors or SELECTORS
        attrs = attributes or Attributes
        self._attributes = attrs
        super().__init__(text, selectors)

    @staticmethod
    def meets_condition(source: str) -> bool:
        return "justjoin" in source

    def get_company_name(self) -> str:
        return self.get_attribute(self._attributes.COMPANY_NAME.value).get_text()

    def get_job_title(self) -> str:
        return self.get_attribute(self._attributes.JOB_TITLE.value).get_text()

    def parse(self) -> List[str]:
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
            detailed_description,
        ]
        return parsed_job_offer

    def _get_heading(self) -> str:
        job_title = self.get_attribute(self._attributes.JOB_TITLE.value)
        summary_soup = self.get_attribute(self._attributes.SUMMARY.value)
        company_name = self.get_attribute(
            self._attributes.COMPANY_NAME.value, soup=summary_soup
        )
        company_and_job_title = f"{company_name.get_text()} - {job_title.get_text()}"
        emphasis = "-" * len(company_and_job_title)
        heading_result = "\n".join(
            [emphasis, company_and_job_title, emphasis, str(company_name["href"])]
        )
        return heading_result

    def _get_location(self) -> str:
        location_soup = self.get_attribute(self._attributes.LOCATION.value)
        company_location = self.get_attribute(
            self._attributes.LOCATION_COMPANY.value, soup=location_soup
        )
        location = [company_location.get_text()]
        try:
            working_location = self.get_attribute(
                self._attributes.LOCATION_WORK.value, soup=location_soup
            )
            location.append(working_location.get_text())
        except AttributeNotFoundError:
            pass
        location_result = "\n".join(location)
        return location_result

    def _get_salary(self) -> str:
        salary_soups = self.get_attributes(self._attributes.SALARY.value)
        salary = [salary_soup.get_text() for salary_soup in salary_soups]
        salary_result = "\n".join(salary)
        return salary_result

    def _get_team_details(self) -> str:
        company_details = self.get_attributes(self._attributes.COMPANY_DETAILS.value)
        details = []
        for desc, item in zip(["Company Size:", "Level:"], company_details):
            details.append(f"{desc} {item.get_text().strip()}")
        details_result = "\n".join(details)
        return details_result

    def _get_tech_stack(self) -> str:
        tech_stack_soup = self.get_attribute(self._attributes.TECH_STACK.value)
        stack_soups = self.get_attributes(
            self._attributes.STACKS.value, soup=tech_stack_soup
        )
        tech_stacks = []
        for stack_soup in stack_soups:
            assert isinstance(stack_soup, Tag)
            tech = self.get_attribute(self._attributes.TECH.value, soup=stack_soup)
            level = self.get_attribute(self._attributes.LEVEL.value, soup=stack_soup)
            tech_stacks.append(f"{tech.get_text()}: {level.get_text()}")
        tech_stacks_result = "\n".join(tech_stacks)
        return tech_stacks_result

    def _get_description(self) -> str:
        details = self.get_attribute(self._attributes.DESCRIPTION.value)
        return details.get_text()


def identify_portal(page_content: str) -> str:
    soup = BeautifulSoup(page_content, features="html.parser")
    url = soup.find("meta", property="og:url")["content"]  # type: ignore
    portal = get_portal_from_url(url)  # type: ignore
    return portal


def get_portal_from_url(url: str) -> str:
    parsed_url = urllib.parse.urlparse(url)
    return parsed_url.hostname or ""


def get_portal_parser(portal: str) -> Callable:
    for parser_cls in Parser.__subclasses__():
        if parser_cls.meets_condition(portal):
            return parser_cls
    raise NotImplementedError(f"No parser found for {portal}!")


def generate_filename(parser: ParserGenerateFilename) -> str:
    today = date.today().strftime("%y%m%d")
    company_name = parser.get_company_name()
    job_title = parser.get_job_title()
    return f"{today} {company_name} - {job_title}.html"


def main() -> None:
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


def ask_user_for_filename(proposition: str) -> str:
    proposition = proposition.replace("/", "|")
    user_filename = input(f'Provide a filename or confirm "{proposition}" [Enter]: ')
    filename = user_filename or proposition
    return filename


def get_cli_arguments() -> str:
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(
            """
            IT Job Offers Parser:
            -> Download raw html of a given web page
            -> Extract job offer data
            -> Save the output for future reference ;)
            """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("source", help="Provide URL or filename with raw HTML content")
    # save_raw=True
    # save_output=True # default True
    # print_to_stdout=True # default True

    args = parser.parse_args()
    return str(args.source)


def read_from_file(filename: str) -> str:
    with open(filename, "r") as file:
        content = file.read()
    return content


def save_to_file(text: str, filename: str) -> None:
    with open(filename, "w") as file:
        file.write(text)


async def download_page(url: str) -> str:
    browser = await launch()
    page = await browser.newPage()

    await page.goto(url)
    page_content: str = await page.content()
    await browser.close()

    return page_content


if __name__ == "__main__":
    main()
