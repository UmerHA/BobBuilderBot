from __future__ import annotations
from abc import abstractmethod
from typing import Tuple, Optional
from python import PythonValidator
from javascript import JavascriptValidator


class SyntaxValidator:
    @classmethod
    def check_syntax(code: str) -> Tuple[bool, Optional[str]]:
        pass

    @classmethod
    def format(code: str) -> str:
        pass

    @classmethod
    def language() -> str:
        '''Programming language for which this Validator works'''

    @classmethod
    def from_file_type(cls, filename: str) -> SyntaxValidator:
        if filename.endswith(".py"): return PythonValidator
        if filename.endswith(".js"): return JavascriptValidator
        if filename.endswith(".html"): raise NotImplementedError()
        if filename.endswith(".css"): raise NotImplementedError()
        raise ValueError(f"Couldn't figure the right SyntaxValidator for this file: {filename}")
