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


class TheProtocolAttributes(AutoNameEnum):
    COMPANY_NAME = auto()
    JOB_TITLE = auto()


THEPROTOCOL_SELECTORS = Selectors(
    {
        TheProtocolAttributes.COMPANY_NAME.value: Selector(
            HTMLTag.H2.value, "rootClass_rpqnjlt body1_b1gato5c initial_i1m6fsnc"
        ),
        TheProtocolAttributes.JOB_TITLE.value: Selector(
            HTMLTag.H1.value,
            "rootClass_rpqnjlt body1_b1gato5c initial_i1m6fsnc titleClass_ttiz6zs",
        ),
    }
)


class TheProtocolParser(BaseParser, Parser):
    portal_identifier = "theprotocol"

    def __init__(
        self,
        text: str,
        selectors: Optional[Selectors] = None,
    ) -> None:
        selectors = selectors or THEPROTOCOL_SELECTORS
        super().__init__(text, selectors)
