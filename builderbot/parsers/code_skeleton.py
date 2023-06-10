from typing import List, Optional
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from .code_change import CodeChange

# todo: not all code file consinsts of functions as in python (there could be classes, html, ...)

class Function(BaseModel):
    name: str = Field(description="name of function")
    signature: str = Field(description="signature of function")

class CodeFile(BaseModel):
    name: str = Field(description="full path to this file")
    description: str = Field(description="what does the code in this file do?")
    functions: Optional[List[Function]] = Field(description="functions in this file")

    def to_str(self) -> str:
        if self.functions:
            f = ["   " + func.signature for func in self.functions]
            return "\n\n".join(f) + "\n"             
        else:
            return "\n"

class CodeSkeleton(BaseModel):
    files: List[CodeFile] = Field(description="a code file")

    def to_str(self) -> str:
        '''Represent as string, so it is easier to process by LLM'''
        result = ""
        files = sorted(self.files, key=lambda f: f.name)
        for file in files:
            result += file.name + ":\n"
            result += file.to_str()
        return result

code_skeleton_parser = PydanticOutputParser(pydantic_object=CodeSkeleton)