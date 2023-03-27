from enum import auto
from typing import Dict, List, Optional

from bs4 import Tag
from job_offer_parser.module_exceptions import AttributeNotFoundError
from job_offer_parser.parsers.base_parser import (
    AutoNameEnum,
    ElementTypeHTML,
    Parser,
    Selector,
)


class JustJoinItAttributes(AutoNameEnum):
    COMPANY_NAME = auto()
    JOB_TITLE = auto()
    SUMMARY = auto()
    LOCATION = auto()
    LOCATION_COMPANY = auto()
    LOCATION_WORK = auto()
    SALARY = auto()
    COMPANY_DETAILS = auto()
    TECH_STACK = auto()
    STACKS = auto()
    TECH = auto()
    LEVEL = auto()
    DESCRIPTION = auto()


JUST_JOIN_IT_SELECTORS = {
    JustJoinItAttributes.COMPANY_NAME.value: Selector(
        ElementTypeHTML.A.value, "css-l4opor"
    ),
    JustJoinItAttributes.JOB_TITLE.value: Selector(
        ElementTypeHTML.DIV.value, "css-1id4k1"
    ),
    JustJoinItAttributes.SUMMARY.value: Selector(
        ElementTypeHTML.DIV.value, "css-1kgdb8a"
    ),
    JustJoinItAttributes.LOCATION.value: Selector(
        ElementTypeHTML.DIV.value, "css-1f4p1d3"
    ),
    JustJoinItAttributes.LOCATION_COMPANY.value: Selector(
        ElementTypeHTML.SPAN.value, "css-9wmrp4"
    ),
    JustJoinItAttributes.LOCATION_WORK.value: Selector(
        ElementTypeHTML.SPAN.value, "css-13p5d07"
    ),
    JustJoinItAttributes.SALARY.value: Selector(
        ElementTypeHTML.DIV.value, "css-1wla3xl"
    ),
    JustJoinItAttributes.COMPANY_DETAILS.value: Selector(
        ElementTypeHTML.DIV.value, "css-1ji7bvd"
    ),
    JustJoinItAttributes.TECH_STACK.value: Selector(
        ElementTypeHTML.DIV.value, "css-1ikoimk"
    ),
    JustJoinItAttributes.STACKS.value: Selector(
        ElementTypeHTML.DIV.value, "css-1q98d5e"
    ),
    JustJoinItAttributes.TECH.value: Selector(ElementTypeHTML.DIV.value, "css-1eroaug"),
    JustJoinItAttributes.LEVEL.value: Selector(
        ElementTypeHTML.DIV.value, "css-19mz16e"
    ),
    JustJoinItAttributes.DESCRIPTION.value: Selector(
        ElementTypeHTML.DIV.value, "css-p1hlmi"
    ),
}


class JustJoinITParser(Parser):
    portal_identifier = "justjoin"

    def __init__(
        self,
        text: str,
        selectors: Optional[Dict[str, Selector]] = None,
        attributes: Optional[JustJoinItAttributes] = None,
    ) -> None:
        selectors = selectors or JUST_JOIN_IT_SELECTORS
        attrs = attributes or JustJoinItAttributes
        self._attributes = attrs
        super().__init__(text, selectors)

    def get_company_name(self) -> str:
        return self.get_attribute(self._attributes.COMPANY_NAME.value).get_text()

    def get_job_title(self) -> str:
        return self.get_attribute(self._attributes.JOB_TITLE.value).get_text()

    def parse(self) -> List[str]:
        parsed_job_offer = []
        heading = self._get_heading()
        location = self._get_location()
        salary = self._get_salary()
        team_details = self._get_team_details()
        tech_stacks = self._get_tech_stack()
        detailed_description = self._get_description()
        parsed_job_offer = [
            heading,
            location,
            salary,
            team_details,
            tech_stacks,
            detailed_description,
        ]
        return parsed_job_offer

    def _get_heading(self) -> str:
        job_title = self.get_attribute(self._attributes.JOB_TITLE.value)
        summary_soup = self.get_attribute(self._attributes.SUMMARY.value)
        company_name = self.get_attribute(
            self._attributes.COMPANY_NAME.value, soup=summary_soup
        )
        company_and_job_title = f"{company_name.get_text()} - {job_title.get_text()}"
        emphasis = "-" * len(company_and_job_title)
        heading_result = "\n".join(
            [emphasis, company_and_job_title, emphasis, str(company_name["href"])]
        )
        return heading_result

    def _get_location(self) -> str:
        location_soup = self.get_attribute(self._attributes.LOCATION.value)
        company_location = self.get_attribute(
            self._attributes.LOCATION_COMPANY.value, soup=location_soup
        )
        location = [company_location.get_text()]
        try:
            working_location = self.get_attribute(
                self._attributes.LOCATION_WORK.value, soup=location_soup
            )
            location.append(working_location.get_text())
        except AttributeNotFoundError:
            pass
        location_result = "\n".join(location)
        return location_result

    def _get_salary(self) -> str:
        salary_soups = self.get_attributes(self._attributes.SALARY.value)
        salary = [salary_soup.get_text() for salary_soup in salary_soups]
        salary_result = "\n".join(salary)
        return salary_result

    def _get_team_details(self) -> str:
        company_details = self.get_attributes(self._attributes.COMPANY_DETAILS.value)
        details = []
        for desc, item in zip(["Company Size:", "Level:"], company_details):
            details.append(f"{desc} {item.get_text().strip()}")
        details_result = "\n".join(details)
        return details_result

    def _get_tech_stack(self) -> str:
        tech_stack_soup = self.get_attribute(self._attributes.TECH_STACK.value)
        stack_soups = self.get_attributes(
            self._attributes.STACKS.value, soup=tech_stack_soup
        )
        tech_stacks = []
        for stack_soup in stack_soups:
            assert isinstance(stack_soup, Tag)
            tech = self.get_attribute(self._attributes.TECH.value, soup=stack_soup)
            level = self.get_attribute(self._attributes.LEVEL.value, soup=stack_soup)
            tech_stacks.append(f"{tech.get_text()}: {level.get_text()}")
        tech_stacks_result = "\n".join(tech_stacks)
        return tech_stacks_result

    def _get_description(self) -> str:
        details = self.get_attribute(self._attributes.DESCRIPTION.value)
        return details.get_text()
