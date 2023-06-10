from __future__ import annotations

from copy import deepcopy
from typing import List
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from .code_skeleton import CodeSkeleton
from .code_change import CodeChange, Insertion, Deletion, Replacement


class CodeLine(BaseModel):
    content: str = Field(description="a line of code")
    def __str__(self) -> str: return self.content

class CodeFile(BaseModel):
    name: str = Field(description="full path to this file")
    lines: List[CodeLine] = Field(description="content of this file")
    def __str__(self) -> str: return "\n".join([line.content for line in self.lines])
    def overwrite(self, content: str) -> None: self.lines = [CodeLine(content=line) for line in content.split("\n")]

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

    @classmethod
    def from_skeleton(cls, code_skeleton: CodeSkeleton) -> CodeBase:
        files: List[CodeFile] = []
        for file in code_skeleton.files:
            lines = [CodeLine(content=line) for line in str(file).split("\n")]
            files.append(CodeFile(name=file.name, lines=lines))
        return cls(files=files)

    def show_file(self, filename) -> CodeFile:
        for file in self.files:
            if file.name == filename: return file
        raise ValueError(f"File with name {filename} not found in code base")

code_base_parser = PydanticOutputParser(pydantic_object=CodeBase)
