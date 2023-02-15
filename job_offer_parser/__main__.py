import asyncio
import os

from job_offer_parser.cli import get_cli_arguments
from job_offer_parser.settings import DEFAULT_RAW_OFFER_FILENAME, RAW_OFFERS_DIR
from job_offer_parser.utils import (
    ask_user_for_filename,
    download_page,
    generate_filename,
    get_portal_from_url,
    get_portal_parser,
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


if __name__ == "__main__":
    main()
