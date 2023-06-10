from typing import Tuple, Optional
from typing_extensions import override
import black
import traceback
from base import SyntaxValidator

class PythonValidator(SyntaxValidator):

    @classmethod
    @override
    def check_syntax(code: str) -> Tuple[bool, Optional[str]]:
        try:
            black.format_str(code, mode=black.Mode())
        except Exception as e:
            return False, traceback.format_exc()
        return True
        
    @classmethod
    def format(code: str) -> str:
        return black.format_str(code, mode=black.Mode())
        
    @classmethod
    @override
    def language() -> str: return "Python"