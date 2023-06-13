import subprocess
import shlex

from typing import Optional, Tuple
from typing_extensions import override
from .base import SyntaxValidator


class JavascriptValidator(SyntaxValidator):

    # todo: ensure eslint is installed

    @classmethod
    @override
    def check_syntax(cls, code: str) -> Tuple[bool, Optional[str]]:
        return True, None

        command = f"npx eslint {filename}"
        process = subprocess.run(shlex.split(command), capture_output=True, text=True)
        
        if process.returncode != 0:
            print("Syntax errors found:")
            print(process.stdout)
        else:
            print("No syntax errors found.")

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
