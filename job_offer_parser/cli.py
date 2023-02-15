import argparse
import textwrap


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
