from __future__ import annotations

from copy import deepcopy
from typing import List
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from .code_change import CodeChange, Insertion, Deletion, Replacement


class CodeFile(BaseModel):
    name: str = Field(description="full path to this file")
    content: str = Field(description="content of this file")
    def __str__(self) -> str: return self.content
    def overwrite(self, content: str) -> None: self.content = content
    def lines(self) -> List[str]: return self.content.split("\n")

class CodeBase(BaseModel):
    files: List[CodeFile] = Field(description="a code file")

    def with_change(self, change: CodeChange) -> CodeBase:
        '''Update code base by including a change'''
        new_code_base = deepcopy(self)
        for file_change in change.files:

            # Find the corresponding file in the code base
            for file in new_code_base.files:
                if file.name != file_change.name:
                    continue

                for specific_change in reversed(sorted(file_change.changes, key=lambda x: x.line_number_start)):
                    if isinstance(specific_change, Insertion):
                        # For an Insertion, we insert the new lines at the given line number
                        for index, new_line in enumerate(specific_change.new_lines):
                            file.lines.insert(specific_change.line_number_start + index, CodeLine(content=new_line))
                    elif isinstance(specific_change, Deletion):
                        # For a Deletion, we delete the lines from start to end
                        del file.lines[specific_change.line_number_start - 1: specific_change.line_number_end]
                    elif isinstance(specific_change, Replacement):
                        # For a Replacement, we replace the lines from start to end with the new lines
                        del file.lines[specific_change.line_number_start - 1: specific_change.line_number_end]
                        for index, new_line in enumerate(specific_change.new_lines):
                            file.lines.insert(specific_change.line_number_start - 1 + index, CodeLine(content=new_line))
        
        return new_code_base

    def show_file(self, filename) -> CodeFile:
        for file in self.files:
            if file.name == filename: return file
        raise ValueError(f"File with name {filename} not found in code base")

code_base_parser = PydanticOutputParser(pydantic_object=CodeBase)
