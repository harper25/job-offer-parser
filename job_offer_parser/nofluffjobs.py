from enum import auto
from typing import Dict, List, Optional

from job_offer_parser.base_parser import AutoNameEnum, ElementTypeHTML, Parser, Selector


class NoFluffJobsAttributes(AutoNameEnum):
    COMPANY_NAME = auto()
    JOB_TITLE = auto()


NOFLUFFJOBS_SELECTORS = {
    NoFluffJobsAttributes.COMPANY_NAME.value: Selector(
        ElementTypeHTML.A.value,
        "inline-info d-flex align-items-center text-primary ng-star-inserted",
    ),
    NoFluffJobsAttributes.JOB_TITLE.value: Selector(
        ElementTypeHTML.DIV.value,
        "posting-details-description d-flex align-items-center align-items-lg-start flex-column justify-content-center justify-content-lg-start",  # noqa E501
    ),
}


class NoFluffJobsParser(Parser):
    def __init__(
        self,
        text: str,
        selectors: Optional[Dict[str, Selector]] = None,
        attributes: Optional[NoFluffJobsAttributes] = None,
    ) -> None:
        selectors = selectors or NOFLUFFJOBS_SELECTORS
        attrs = attributes or NoFluffJobsAttributes
        self._attributes = attrs
        super().__init__(text, selectors)

    @staticmethod
    def meets_condition(source: str) -> bool:
        return "nofluffjobs" in source

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
