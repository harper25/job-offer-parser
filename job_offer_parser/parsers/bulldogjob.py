from enum import auto
from typing import Optional

from job_offer_parser.parsers.base_parser import (
    AutoNameEnum,
    BaseParser,
    HTMLTag,
    Parser,
    Selector,
    Selectors,
)


class BulldogJobAttributes(AutoNameEnum):
    COMPANY_NAME = auto()
    JOB_TITLE = auto()


BULLDOGJOB_SELECTORS = Selectors(
    {
        BulldogJobAttributes.COMPANY_NAME.value: Selector(
            HTMLTag.H2.value,
            "jsx-651043755 text-c20 leading-6 font-medium text-gray-500",
        ),
        BulldogJobAttributes.JOB_TITLE.value: Selector(
            HTMLTag.H1.value,
            "jsx-651043755 text-c32 font-medium mt-3",
        ),
    }
)


class BulldogJobParser(BaseParser, Parser):
    portal_identifier = "bulldogjob"

    def __init__(
        self,
        text: str,
        selectors: Optional[Selectors] = None,
    ) -> None:
        selectors = selectors or BULLDOGJOB_SELECTORS
        super().__init__(text, selectors)
