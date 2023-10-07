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


class SolidJobsAttributes(AutoNameEnum):
    COMPANY_NAME = auto()
    JOB_TITLE = auto()


SOLIDJOBS_SELECTORS = Selectors(
    {
        SolidJobsAttributes.COMPANY_NAME.value: Selector(HTMLTag.SPAN.value, "mr-1"),
        SolidJobsAttributes.JOB_TITLE.value: Selector(
            HTMLTag.H1.value, "font-weight-900 color-grey"
        ),
    }
)


class SolidJobsParser(BaseParser, Parser):
    portal_identifier = "solid.jobs"

    def __init__(
        self,
        text: str,
        selectors: Optional[Selectors] = None,
    ) -> None:
        selectors = selectors or SOLIDJOBS_SELECTORS
        super().__init__(text, selectors)
