from typing import List, Optional
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class Function(BaseModel):
    name: str = Field(description="name of function")
    signature: str = Field(description="signature of function")
class CodeFile(BaseModel):
    name: str = Field(description="full path to this file")
    description: str = Field(description="what does the code in this file do?")
    functions: Optional[List[Function]] = Field(description="functions in this file")    
class CodeBase(BaseModel):
    code_files: List[CodeFile] = Field(description="a code file")

code_base_parser = PydanticOutputParser(pydantic_object=CodeBase)