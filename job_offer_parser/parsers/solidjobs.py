from enum import auto
from typing import Dict, List, Optional

from job_offer_parser.parsers.base_parser import (
    AutoNameEnum,
    ElementTypeHTML,
    Parser,
    Selector,
)


class SolidJobsAttributes(AutoNameEnum):
    COMPANY_NAME = auto()
    JOB_TITLE = auto()


SOLIDJOBS_SELECTORS = {
    SolidJobsAttributes.COMPANY_NAME.value: Selector(
        ElementTypeHTML.SPAN.value, "mr-1"
    ),
    SolidJobsAttributes.JOB_TITLE.value: Selector(
        ElementTypeHTML.H1.value, "font-weight-900 color-grey"
    ),
}


class SolidJobsParser(Parser):
    def __init__(
        self,
        text: str,
        selectors: Optional[Dict[str, Selector]] = None,
        attributes: Optional[SolidJobsAttributes] = None,
    ) -> None:
        selectors = selectors or SOLIDJOBS_SELECTORS
        attrs = attributes or SolidJobsAttributes
        self._attributes = attrs
        super().__init__(text, selectors)

    @staticmethod
    def meets_condition(source: str) -> bool:
        return "solid.jobs" in source

    def get_company_name(self) -> str:
        company_name = self.get_attribute(
            self._attributes.COMPANY_NAME.value
        ).get_text()
        company_name = " ".join(company_name.split())
        return company_name

    def get_job_title(self) -> str:
        job_title = self.get_attribute(self._attributes.JOB_TITLE.value).get_text()
        job_title = " ".join(job_title.split())
        return job_title

    def parse(self) -> List[str]:
        return ["Parsing will be implemented later..."]
