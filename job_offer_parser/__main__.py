import asyncio
import os

from job_offer_parser.cli import get_cli_arguments
from job_offer_parser.module_exceptions import AttributeNotFoundError, NoParserFound
from job_offer_parser.settings import DEFAULT_RAW_OFFER_FILENAME, RAW_OFFERS_DIR
from job_offer_parser.utils import (
    ask_user_for_filename,
    download_page,
    generate_filename,
    get_portal_from_url,
    get_portal_parsers,
    identify_portal,
    read_from_file,
    save_to_file,
)


def main() -> None:
    source = get_cli_arguments()
    is_url = source.startswith("https:")
    is_file = os.path.exists(source)

    if is_file:
        page_content = read_from_file(source)
        portal = identify_portal(page_content)

    if is_url:
        page_content = asyncio.run(download_page(source))
        portal = get_portal_from_url(source)

    try:
        parsers = get_portal_parsers(portal)
    except NoParserFound as e:
        print(e)
        if is_url:
            filename = ask_user_for_filename(DEFAULT_RAW_OFFER_FILENAME)
            save_to_file(page_content, os.path.join(RAW_OFFERS_DIR, filename))
        return

    for parser_cls in parsers:
        try:
            parser = parser_cls(page_content)
            print(f"Parsing with: {parser.__class__.__name__}")
            if is_url:
                proposed_filename = generate_filename(parser)
                filename = ask_user_for_filename(proposed_filename)
                save_to_file(page_content, os.path.join(RAW_OFFERS_DIR, filename))
            parsed_offer = parser.parse()
            print("\n\n".join(parsed_offer))
            print(f"Parsed with {parser.__class__.__name__}")
            return
        except AttributeNotFoundError as e:
            print(e)


if __name__ == "__main__":
    main()
