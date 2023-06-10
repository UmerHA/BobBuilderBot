import json
import subprocess
from typing import Optional, Tuple
from typing_extensions import override
from .base import SyntaxValidator


class HTMLValidator(SyntaxValidator):

    # todo

    @classmethod
    @override
    def check_syntax(cls, code: str) -> Tuple[bool, Optional[str]]:
        return True, None

    @classmethod
    def format(cls, code: str) -> str:
        return code

    @override
    @property
    def language(cls) -> str: return "HTML"
