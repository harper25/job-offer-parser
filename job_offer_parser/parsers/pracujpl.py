from enum import auto
from typing import Dict, List, Optional

from job_offer_parser.parsers.base_parser import (
    AutoNameEnum,
    ElementTypeHTML,
    Parser,
    Selector,
)


class PracujPLAttributes(AutoNameEnum):
    COMPANY_NAME = auto()
    JOB_TITLE = auto()


PRACUJPL_SELECTORS = {
    PracujPLAttributes.COMPANY_NAME.value: Selector(
        ElementTypeHTML.H2.value, "offer-viewwtdXJ4"
    ),
    PracujPLAttributes.JOB_TITLE.value: Selector(
        ElementTypeHTML.H1.value,
        "offer-viewkHIhn3",
    ),
}


class PracujPLParser(Parser):
    def __init__(
        self,
        text: str,
        selectors: Optional[Dict[str, Selector]] = None,
        attributes: Optional[PracujPLAttributes] = None,
    ) -> None:
        selectors = selectors or PRACUJPL_SELECTORS
        attrs = attributes or PracujPLAttributes
        self._attributes = attrs
        super().__init__(text, selectors)

    @staticmethod
    def meets_condition(source: str) -> bool:
        return "pracuj.pl" in source

    def get_company_name(self) -> str:
        company_name = str(
            self.get_attribute(self._attributes.COMPANY_NAME.value).contents[0]
        )
        company_name = " ".join(company_name.split())
        return company_name

    def get_job_title(self) -> str:
        job_title = self.get_attribute(self._attributes.JOB_TITLE.value).get_text()
        job_title = " ".join(job_title.split())
        return job_title

    def parse(self) -> List[str]:
        return ["Parsing will be implemented later..."]
