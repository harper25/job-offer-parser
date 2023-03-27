from enum import auto
from typing import Dict, Optional

from job_offer_parser.parsers.base_parser import (
    AutoNameEnum,
    ElementTypeHTML,
    Parser,
    Selector,
)


class BulldogJobAttributes(AutoNameEnum):
    COMPANY_NAME = auto()
    JOB_TITLE = auto()


BULLDOGJOB_SELECTORS = {
    BulldogJobAttributes.COMPANY_NAME.value: Selector(
        ElementTypeHTML.H2.value,
        "jsx-651043755 text-c20 leading-6 font-medium text-gray-500",
    ),
    BulldogJobAttributes.JOB_TITLE.value: Selector(
        ElementTypeHTML.H1.value,
        "jsx-651043755 text-c32 font-medium mt-3",
    ),
}


class BulldogJobParser(Parser):
    portal_identifier = "bulldogjob"

    def __init__(
        self,
        text: str,
        selectors: Optional[Dict[str, Selector]] = None,
        attributes: Optional[BulldogJobAttributes] = None,
    ) -> None:
        selectors = selectors or BULLDOGJOB_SELECTORS
        attrs = attributes or BulldogJobAttributes
        self._attributes = attrs
        super().__init__(text, selectors)

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
