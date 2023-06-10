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

    def with_change(self, codebase_change: CodeChange) -> CodeBase:
        new_code_base = deepcopy(self)
        for file_change in codebase_change.files:
            for file in new_code_base.files:
                if file.name != file_change.name: continue  # Find corresponding file
                # 1) split content into lines, 2) apply change ops on list of lines, 3) join back
                lines = file.lines()
                for change in reversed(sorted(file_change.changes, key=lambda x: x.line_number_start)):
                    if isinstance(change, Insertion):
                        new_lines = change.new_code.split("\n")
                        for index, new_line in enumerate(new_lines):
                            lines.insert(change.line_number_start + index, new_line)
                    elif isinstance(change, Deletion):
                        del lines[change.line_number_start - 1: change.line_number_end]
                    elif isinstance(change, Replacement):
                        del lines[change.line_number_start - 1: change.line_number_end]
                        new_lines = change.new_code.split("\n")
                        for index, new_line in enumerate(new_lines):
                            lines.insert(change.line_number_start - 1 + index, new_line)
                file.overwrite("\n".join(lines))
        return new_code_base

    def show_file(self, filename) -> CodeFile:
        for file in self.files:
            if file.name == filename: return file
        raise ValueError(f"File with name {filename} not found in code base")

code_base_parser = PydanticOutputParser(pydantic_object=CodeBase)
