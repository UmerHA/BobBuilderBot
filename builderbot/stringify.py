from typing import Dict, List


def codebase_to_str(codebase: Dict[str, str]) -> str:
    result = ""
    for file_name, file_content in codebase.items():
        result += "File: " + file_name + "\n" # file name
        result += file_content + "\n"  # content
        result += "--\n"
    return result

def reqs_to_str(reqs: List[str]) -> str:
    return "\n".join(["- " + req for req in reqs])
