import re
from typing import List, Optional, Tuple, Dict


def str_to_project_description(text: str) -> Tuple[List[str], List[str], Optional[List[str]]]:
    sections = re.split(r'\n\n', text)
    requirements = re.findall(r'- (.*)', sections[0])
    assumptions = re.findall(r'- (.*)', sections[1])
    
    if 'no questions' in sections[2]:
        questions = None
    else:
        questions = re.findall(r'- (.*)', sections[2])
    
    return requirements, assumptions, questions


def str_to_codebase(string: str) -> Dict[str, str]:
    files_str = string.split("--\n")
    codebase = {}
    for file_str in files_str:
        if file_str:  # Skip empty strings that might result from split
            split_file_str = file_str.split("\n", 1)
            codebase[split_file_str[0][6:]] = split_file_str[1]
    return codebase
