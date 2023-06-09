from typing import List, Union
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class Insertion(BaseModel):
    line_number_start: int = Field(..., description="line number where to insert the new lines of code")
    new_lines: List[str] = Field(..., description="new lines of code")

class Deletion(BaseModel):
    line_number_start: int = Field(..., description="line number where to start the deletion (inclusive)")
    line_number_end: int = Field(..., description="line number where to end the deletion (inclusive)")

class Update(BaseModel):
    line_number_start: int = Field(..., description="line number where to start the update (inclusive)")
    line_number_end: int = Field(..., description="line number where to end the update (inclusive)")
    new_lines: List[str] = Field(..., description="new lines of code")

class CodeFileChange(BaseModel):
    name: str = Field(description="full path to this file")
    changes: List[Union[Update, Insertion, Deletion]] = Field(description="changes to this code file (either updates, insertions or deletions)")

class CodeChange(BaseModel):
    files: List[CodeFileChange] = Field(description="list of changes for each code file")

code_change_parser = PydanticOutputParser(pydantic_object=CodeChange)
