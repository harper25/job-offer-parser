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


class PracujPLAttributes(AutoNameEnum):
    COMPANY_NAME = auto()
    JOB_TITLE = auto()


PRACUJPL_SELECTORS = Selectors(
    {
        PracujPLAttributes.COMPANY_NAME.value: Selector(
            HTMLTag.H2.value, "offer-viewwtdXJ4"
        ),
        PracujPLAttributes.JOB_TITLE.value: Selector(
            HTMLTag.H1.value,
            "offer-viewkHIhn3",
        ),
    }
)


class PracujPLParser(BaseParser, Parser):
    portal_identifier = "pracuj.pl"

    def __init__(
        self,
        text: str,
        selectors: Optional[Selectors] = None,
    ) -> None:
        selectors = selectors or PRACUJPL_SELECTORS
        super().__init__(text, selectors)
