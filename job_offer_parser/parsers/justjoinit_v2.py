from enum import auto
from typing import Optional

from job_offer_parser.parsers.base_parser import (
    AutoNameEnum,
    HTMLTag,
    Parser,
    Selector,
    Selectors,
)
from job_offer_parser.parsers.justjoinit import JustJoinITParser


class JustJoinItAttributesV2(AutoNameEnum):
    COMPANY_NAME = auto()
    JOB_TITLE = auto()
    SUMMARY = auto()
    LOCATION = auto()
    LOCATION_COMPANY = auto()
    LOCATION_WORK = auto()
    SALARY = auto()
    COMPANY_DETAILS = auto()
    COMPANY_DETAIL = auto()
    COMPANY_DETAIL_VALUE = auto()
    TECH_STACK = auto()
    STACKS = auto()
    TECH = auto()
    LEVEL = auto()
    DESCRIPTION = auto()


JUST_JOIN_IT_SELECTORS_V2 = Selectors(
    {
        JustJoinItAttributesV2.COMPANY_NAME.value: Selector(
            HTMLTag.DIV.value, "css-1yxroko"
        ),
        JustJoinItAttributesV2.JOB_TITLE.value: Selector(
            HTMLTag.H1.value, "css-16ux437"
        ),
        JustJoinItAttributesV2.SUMMARY.value: Selector(HTMLTag.DIV.value, "css-vb54bv"),
        JustJoinItAttributesV2.LOCATION.value: Selector(
            HTMLTag.DIV.value, "css-u51ts9"
        ),
        JustJoinItAttributesV2.LOCATION_COMPANY.value: Selector(
            HTMLTag.DIV.value, "css-e37z09"
        ),
        JustJoinItAttributesV2.LOCATION_WORK.value: Selector(
            HTMLTag.SPAN.value, "css-13p5d07"
        ),
        JustJoinItAttributesV2.TECH_STACK.value: Selector(
            HTMLTag.DIV.value, "MuiBox-root css-1w1fbag"
        ),
        JustJoinItAttributesV2.STACKS.value: Selector(HTMLTag.DIV.value, "css-cjymd2"),
        JustJoinItAttributesV2.TECH.value: Selector(
            HTMLTag.H6.value, "MuiTypography-root MuiTypography-subtitle2 css-x1xnx3"
        ),
        JustJoinItAttributesV2.LEVEL.value: Selector(
            HTMLTag.SPAN.value, "MuiTypography-root MuiTypography-caption css-139euaa"
        ),
        JustJoinItAttributesV2.SALARY.value: Selector(HTMLTag.DIV.value, "css-j7qwjs"),
        JustJoinItAttributesV2.COMPANY_DETAIL.value: Selector(
            HTMLTag.DIV.value, "css-16i477t"
        ),
        JustJoinItAttributesV2.COMPANY_DETAIL_VALUE.value: Selector(
            HTMLTag.DIV.value, "css-15qbbm2"
        ),
        JustJoinItAttributesV2.DESCRIPTION.value: Selector(
            HTMLTag.DIV.value, "css-ncc6e2"
        ),
    }
)


class JustJoinITParserV2(JustJoinITParser, Parser):
    portal_identifier = "justjoin"

    def __init__(self, text: str, selectors: Optional[Selectors] = None) -> None:
        _selectors = selectors or JUST_JOIN_IT_SELECTORS_V2
        super().__init__(text, _selectors)

    def _get_team_details(self) -> str:
        company_details = self.get_attributes(
            JustJoinItAttributesV2.COMPANY_DETAIL.value
        )
        company_details_values = self.get_attributes(
            JustJoinItAttributesV2.COMPANY_DETAIL_VALUE.value
        )
        details = []
        for key, value in zip(company_details, company_details_values):
            details.append(f"{key.get_text().strip()}: {value.get_text().strip()}")
        details_result = "\n".join(details)
        return details_result
