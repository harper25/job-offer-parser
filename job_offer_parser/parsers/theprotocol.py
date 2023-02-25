from enum import auto
from typing import Dict, List, Optional

from job_offer_parser.parsers.base_parser import (
    AutoNameEnum,
    ElementTypeHTML,
    Parser,
    Selector,
)


class TheProtocolAttributes(AutoNameEnum):
    COMPANY_NAME = auto()
    JOB_TITLE = auto()


THEPROTOCOL_SELECTORS = {
    TheProtocolAttributes.COMPANY_NAME.value: Selector(
        ElementTypeHTML.H2.value, "rootClass_rpqnjlt body1_b1gato5c initial_i1m6fsnc"
    ),
    TheProtocolAttributes.JOB_TITLE.value: Selector(
        ElementTypeHTML.H1.value,
        "rootClass_rpqnjlt body1_b1gato5c initial_i1m6fsnc titleClass_ttiz6zs",
    ),
}


class TheProtocolParser(Parser):
    def __init__(
        self,
        text: str,
        selectors: Optional[Dict[str, Selector]] = None,
        attributes: Optional[TheProtocolAttributes] = None,
    ) -> None:
        selectors = selectors or THEPROTOCOL_SELECTORS
        attrs = attributes or TheProtocolAttributes
        self._attributes = attrs
        super().__init__(text, selectors)

    @staticmethod
    def meets_condition(source: str) -> bool:
        return "theprotocol" in source

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
