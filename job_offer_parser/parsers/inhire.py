from enum import auto
from typing import Dict, Optional

from job_offer_parser.parsers.base_parser import (
    AutoNameEnum,
    ElementTypeHTML,
    Parser,
    Selector,
)


class InhireAttributes(AutoNameEnum):
    COMPANY_NAME = auto()
    JOB_TITLE = auto()


INHIRE_SELECTORS = {
    InhireAttributes.COMPANY_NAME.value: Selector(ElementTypeHTML.A.value, "inh-link"),
    InhireAttributes.JOB_TITLE.value: Selector(
        ElementTypeHTML.H1.value,
        "inh-offer-view-header__offer-name inh-text-header inh-text-header--white inh-text-header--bold",  # noqa E501
    ),
}


class InhireParser(Parser):
    portal_identifier = "inhire"

    def __init__(
        self,
        text: str,
        selectors: Optional[Dict[str, Selector]] = None,
        attributes: Optional[InhireAttributes] = None,
    ) -> None:
        selectors = selectors or INHIRE_SELECTORS
        attrs = attributes or InhireAttributes
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
