import traceback
from typing import Optional, Tuple
import black
from typing_extensions import override

from .base import SyntaxValidator


class PythonValidator(SyntaxValidator):

    @classmethod
    @override
    def check_syntax(cls, code: str) -> Tuple[bool, Optional[str]]:
        try:
            black.format_str(code, mode=black.Mode())
        except Exception as e:
            return False, traceback.format_exc()
        return True
        
    @classmethod
    def format(cls, code: str) -> str:
        return black.format_str(code, mode=black.Mode())
        
    @classmethod
    @override
    def language(cls) -> str: return "Python"