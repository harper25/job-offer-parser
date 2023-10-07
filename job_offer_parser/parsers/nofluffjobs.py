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


class NoFluffJobsAttributes(AutoNameEnum):
    COMPANY_NAME = auto()
    JOB_TITLE = auto()


NOFLUFFJOBS_SELECTORS = Selectors(
    {
        NoFluffJobsAttributes.COMPANY_NAME.value: Selector(
            HTMLTag.A.value,
            "inline-info d-flex align-items-center text-primary ng-star-inserted",
        ),
        NoFluffJobsAttributes.JOB_TITLE.value: Selector(
            HTMLTag.DIV.value,
            "posting-details-description d-flex align-items-center align-items-lg-start flex-column justify-content-center justify-content-lg-start",  # noqa E501
        ),
    }
)


class NoFluffJobsParser(BaseParser, Parser):
    portal_identifier = "nofluffjobs"

    def __init__(
        self,
        text: str,
        selectors: Optional[Selectors] = None,
    ) -> None:
        selectors = selectors or NOFLUFFJOBS_SELECTORS
        super().__init__(text, selectors)
