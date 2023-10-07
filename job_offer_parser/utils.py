import urllib.parse
from datetime import date
from typing import List, Type

from bs4 import BeautifulSoup
from job_offer_parser.module_exceptions import NoParserFound
from job_offer_parser.parsers.base_parser import Parser, ParserGenerateFilename
from pyppeteer import launch  # type: ignore


def identify_portal(page_content: str) -> str:
    soup = BeautifulSoup(page_content, features="html.parser")
    url = soup.find("meta", property="og:url")["content"]  # type: ignore
    portal = get_portal_from_url(url)  # type: ignore
    return portal


def get_portal_parsers(portal: str) -> List[Type[Parser]]:
    parser_candidates = []
    for parser_cls in Parser.__subclasses__():
        if parser_cls.meets_condition(portal):
            parser_candidates.append(parser_cls)
    if not parser_candidates:
        raise NoParserFound(f"No parser found for {portal}!")
    return parser_candidates


def get_portal_from_url(url: str) -> str:
    parsed_url = urllib.parse.urlparse(url)
    return parsed_url.hostname or ""


def generate_filename(parser: ParserGenerateFilename) -> str:
    today = date.today().strftime("%y%m%d")
    company_name = parser.get_company_name()
    job_title = parser.get_job_title()
    return f"{today} {company_name} - {job_title}.html"


def ask_user_for_filename(proposition: str) -> str:
    proposition = proposition.replace("/", "|")
    user_filename = input(f'Provide a filename or confirm "{proposition}" [Enter]: ')
    filename = user_filename or proposition
    return filename


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
