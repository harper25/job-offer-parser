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


class InhireAttributes(AutoNameEnum):
    COMPANY_NAME = auto()
    JOB_TITLE = auto()


INHIRE_SELECTORS = Selectors(
    {
        InhireAttributes.COMPANY_NAME.value: Selector(HTMLTag.A.value, "inh-link"),
        InhireAttributes.JOB_TITLE.value: Selector(
            HTMLTag.H1.value,
            "inh-offer-view-header__offer-name inh-text-header inh-text-header--white inh-text-header--bold",  # noqa E501
        ),
    }
)


class InhireParser(BaseParser, Parser):
    portal_identifier = "inhire"

    def __init__(
        self,
        text: str,
        selectors: Optional[Selectors] = None,
    ) -> None:
        selectors = selectors or INHIRE_SELECTORS
        super().__init__(text, selectors)
