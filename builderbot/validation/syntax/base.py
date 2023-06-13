from __future__ import annotations
from abc import abstractmethod
from typing import Tuple, Optional

FILE_TYPES_TO_IGNORE = [
    'env',
    'replit',
    'json',
    'jsx'
]

class SyntaxValidator:
    @classmethod
    def check_syntax(cls, code: str) -> Tuple[bool, Optional[str]]:
        pass

    @classmethod
    def format(cls, code: str) -> str:
        pass

    @classmethod
    def language(cls) -> str:
        '''Programming language for which this Validator works'''
