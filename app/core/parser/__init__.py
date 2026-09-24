from typing import Union

from app.core.parser.parser import IParser
from app.core.parser.xpath import XPathParser


class ParserFactory:

    @staticmethod
    def get_parser(parser_type: str) -> Union[IParser | None]:
        if parser_type.lower() == "xpath":
            return XPathParser()
        return None
