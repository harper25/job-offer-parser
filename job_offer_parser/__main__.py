import argparse
import asyncio
import os
import textwrap
import urllib.parse
from datetime import date
from typing import Callable

from bs4 import BeautifulSoup
from job_offer_parser.base_parser import Parser, ParserGenerateFilename
from pyppeteer import launch  # type: ignore

RAW_OFFERS_DIR = "raw"
OFFERS_DIR = "offers"
DEFAULT_RAW_OFFER_FILENAME = "test.html"


def get_portal_parser(portal: str) -> Callable:
    for parser_cls in Parser.__subclasses__():
        if parser_cls.meets_condition(portal):
            return parser_cls
    raise NotImplementedError(f"No parser found for {portal}!")


def identify_portal(page_content: str) -> str:
    soup = BeautifulSoup(page_content, features="html.parser")
    url = soup.find("meta", property="og:url")["content"]  # type: ignore
    portal = get_portal_from_url(url)  # type: ignore
    return portal


def get_portal_from_url(url: str) -> str:
    parsed_url = urllib.parse.urlparse(url)
    return parsed_url.hostname or ""


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
