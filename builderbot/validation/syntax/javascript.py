from typing import Tuple, Optional
from typing_extensions import override
from base import SyntaxValidator

class JavascriptValidator(SyntaxValidator):

    @classmethod
    @override
    def check_syntax(code: str) -> Tuple[bool, Optional[str]]:
        raise NotImplementedError()  # todo
        
    @classmethod
    def format(code: str) -> str:
        raise NotImplementedError()  # todo

    @override
    @property
    def language() -> str: return "JavaScript"
