from .base import SyntaxValidator
from .css import CSSValidator
from .html import HTMLValidator
from .javascript import JavascriptValidator
from .python import PythonValidator


def syntax_validator_from_file_type(filename: str) -> SyntaxValidator:
        if filename.endswith(".py"): return PythonValidator
        if filename.endswith(".js"): return JavascriptValidator
        if filename.endswith(".html"): raise HTMLValidator()
        if filename.endswith(".css"): raise CSSValidator()
        raise ValueError(f"Couldn't figure the right SyntaxValidator for this file: {filename}")

__all__ = [
    "syntax_validator_from_file_type",
    "SyntaxValidator",
    "CSSValidator",
    "HTMLValidator",
    "JavascriptValidator",
    "PythonValidator",
]
