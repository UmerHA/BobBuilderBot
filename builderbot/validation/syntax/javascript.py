import json
import subprocess
from typing import Optional, Tuple
from typing_extensions import override
from .base import SyntaxValidator


class JavascriptValidator(SyntaxValidator):

    # todo: ensure eslint is installed

    @classmethod
    @override
    def check_syntax(cls, code: str) -> Tuple[bool, Optional[str]]:
        return True, None
        #try:
        #    result = subprocess.run(
        #        ["eslint", "-f", "json", "--stdin"], 
        #        input=code, 
        #        text=True,
        #        capture_output=True
        #    )
        #    errors = json.loads(result.stdout)
        #    return len(errors[0]["messages"]) == 0, result.stdout
        #except Exception as e:
        #    return False, str(e)

    @classmethod
    def format(cls, code: str) -> str:
        return code
        #result = subprocess.run(
        #    ["prettier", "--parser", "babel"],
        #    input=code,
        #    text=True,
        #    capture_output=True
        #)
        #return result.stdout

    @override
    @property
    def language(cls) -> str: return "JavaScript"
