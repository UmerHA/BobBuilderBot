from typing import List, Literal, Union
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class Insertion(BaseModel):
    op_type: Literal['Insertion'] = Field('Insertion', description="Type of this operation")
    line_number_start: int = Field(..., description="line number where to insert the new code")
    new_code: str = Field(..., description="new lines of code")
    def __str__(self) -> str: return f"Insertion at {self.line_number_start}:\n{self.new_code}"

class Deletion(BaseModel):
    op_type: Literal['Deletion'] = Field('Deletion', description="Type of this operation")
    line_number_start: int = Field(..., description="line number where to start the deletion (inclusive)")
    line_number_end: int = Field(..., description="line number where to end the deletion (inclusive)")
    def __str__(self) -> str: return f"Deletion from {self.line_number_start} to {self.line_number_end}"

class Replacement(BaseModel):
    op_type: Literal['Replacement'] = Field('Replacement', description="Type of this operation")
    line_number_start: int = Field(..., description="line number where to start the replacement (inclusive)")
    line_number_end: int = Field(..., description="line number where to end the replacement (inclusive)")
    new_code: str = Field(..., description="new lines of code")
    def __str__(self) -> str: return f"Replace from {self.line_number_start} to {self.line_number_end}:\n{self.new_code}"

class CodeFileChange(BaseModel):
    name: str = Field(description="full path to this file")
    changes: List[Union[Replacement, Insertion, Deletion]] = Field(description="changes to this code file (either replacements, insertions or deletions)")
    def __str__(self) -> str: return "\n\n".join(str(change) for change in sorted(self.changes, key=lambda x: x.line_number_start))

class CodeChange(BaseModel):
    files: List[CodeFileChange] = Field(description="list of changes for each code file")

    def in_file(self, filename) -> CodeFileChange:
        '''Get change of a specific file'''
        for file in self.files:
            if file.name == filename: return file
        raise ValueError(f"Not change found for file {filename}")

code_change_parser = PydanticOutputParser(pydantic_object=CodeChange)
