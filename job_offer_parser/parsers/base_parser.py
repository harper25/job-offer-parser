from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any, Dict, List, Optional, Protocol, Union

from bs4 import BeautifulSoup, PageElement, Tag
from job_offer_parser.module_exceptions import AttributeNotFoundError


class AutoNameEnum(StrEnum):
    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: List[Any]
    ) -> Any:
        return name.lower()


class HTMLTag(AutoNameEnum):
    A = auto()
    DIV = auto()
    H1 = auto()
    H2 = auto()
    H6 = auto()
    SPAN = auto()


@dataclass
class Selector:
    html: str
    class_: str


class Selectors:
    def __init__(self, selectors: Dict[str, Selector]) -> None:
        self._selectors = selectors

    def get_html_tags(self, attribute: str) -> Selector:
        return self._selectors[attribute]


class BaseAttributes(AutoNameEnum):
    COMPANY_NAME = auto()
    JOB_TITLE = auto()


class Parser(ABC):
    portal_identifier = ""

    def __init__(self, text: str) -> None:
        self._text = text

    @abstractmethod
    def get_company_name(self) -> str:
        pass

    @abstractmethod
    def get_job_title(self) -> str:
        pass

    @classmethod
    def meets_condition(cls, portal: str) -> bool:
        return cls.portal_identifier in portal if cls.portal_identifier else False

    @abstractmethod
    def parse(self) -> List[str]:
        pass


class BaseParser(Parser):
    def __init__(self, text: str, selectors: Selectors) -> None:
        self._text = text
        self._selectors = selectors
        self._soup = BeautifulSoup(self._text, features="html.parser")

    def get_attribute(
        self, attribute: str, soup: Optional[Union[BeautifulSoup, Tag]] = None
    ) -> Tag:
        soup = soup or self._soup
        selector = self._selectors.get_html_tags(attribute)
        element = soup.find(selector.html, class_=selector.class_)
        if not isinstance(element, Tag):
            raise AttributeNotFoundError(
                f"Attribute not found with parser: {self.__class__.__name__}"
            )
        return element

    def get_attributes(
        self, attribute: str, soup: Optional[Union[BeautifulSoup, Tag]] = None
    ) -> List[PageElement]:
        soup = soup or self._soup
        selector = self._selectors.get_html_tags(attribute)
        element = soup.find_all(selector.html, class_=selector.class_)
        return element

    def get_company_name(self) -> str:
        company_name = self.get_attribute(BaseAttributes.COMPANY_NAME.value).get_text()
        company_name = " ".join(company_name.split())
        return company_name

    def get_job_title(self) -> str:
        job_title = self.get_attribute(BaseAttributes.JOB_TITLE.value).get_text()
        job_title = " ".join(job_title.split())
        return job_title

    def parse(self) -> List[str]:
        return ["Parsing will be implemented later..."]


class ParserGenerateFilename(Protocol):
    def get_company_name(self) -> str:
        ...

    def get_job_title(self) -> str:
        ...
