from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol, Union

from bs4 import BeautifulSoup, PageElement, Tag
from job_offer_parser.module_exceptions import AttributeNotFoundError


class AutoNameEnum(Enum):
    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: List[Any]
    ) -> Any:
        return name.lower()


class ElementTypeHTML(AutoNameEnum):
    A = auto()
    DIV = auto()
    H1 = auto()
    H2 = auto()
    SPAN = auto()


@dataclass
class Selector:
    html: str
    class_: str


class Parser(ABC):
    def __init__(self, text: str, selectors: Dict[str, Selector]) -> None:
        self._text = text
        self._selectors = selectors
        self._soup = BeautifulSoup(self._text, features="html.parser")

    @abstractmethod
    def parse(self) -> List[str]:
        pass

    @abstractmethod
    def get_company_name(self) -> str:
        pass

    @abstractmethod
    def get_job_title(self) -> str:
        pass

    @staticmethod
    @abstractmethod
    def meets_condition(portal: str) -> bool:
        pass

    def get_attribute(
        self, attribute: str, soup: Optional[Union[BeautifulSoup, Tag]] = None
    ) -> Tag:
        soup = soup or self._soup
        selector = self._selectors[attribute]
        element = soup.find(selector.html, class_=selector.class_)
        if not isinstance(element, Tag):
            raise AttributeNotFoundError
        return element

    def get_attributes(
        self, attribute: str, soup: Optional[Union[BeautifulSoup, Tag]] = None
    ) -> List[PageElement]:
        soup = soup or self._soup
        selector = self._selectors[attribute]
        element = soup.find_all(selector.html, class_=selector.class_)
        return element


class ParserGenerateFilename(Protocol):
    def get_company_name(self) -> str:
        ...

    def get_job_title(self) -> str:
        ...
