import os
import re
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI

from .inference import LLMInferer
from .parser import str_to_codebase, str_to_project_description
from .run_manager import RunManager
from .stages import DevPhase

Requirements = List[str]
CodeBase = Dict[str, str]

class BuilderBot:

    def __init__(self, model_name: str ="gpt-3.5-turbo", cache_filename: Optional[str] = None) -> None:
        load_dotenv()
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(openai_api_key=openai_api_key, model_name=model_name)
        self.run_manager = RunManager()
        self.cache_filename = cache_filename
        self.inferer = LLMInferer(self.llm, self.run_manager, self.cache_filename)

    def build(self, task: str, verbose=False) -> None:
        self.task = task
        self.verbose = verbose
        self.run_manager.start_run()

        common_kwargs = {
            "llm": self.llm,
            "run_manager": self.run_manager,
            "verbose": self.verbose,
        }

        # Step 1: Understand
        project_description = self.inferer.get_simple_response(
            DevPhase.UNDERSTAND,
            **common_kwargs,
            task=self.task
        )
        self.save_project_description(project_description)
        self.reqs, self.assumptions, self.questions = str_to_project_description(project_description)
        self.reqs_str = reqs_to_str(self.reqs)

        # Step 2.5: Setup project


        # Step 3: Structure Code
        codebase = self.inferer.get_simple_response(
            DevPhase.STRUCTURE_CODE,
            **common_kwargs,
            task=self.task,
            reqs=self.reqs
        )
        self.codebase = str_to_codebase(codebase)
        self.save_codebase()

        # Step 3: Structure Tests
        code_base_test = self.inferer.get_simple_response(
            DevPhase.STRUCTURE_TESTS,
            **common_kwargs,
            task=self.task,
            reqs=self.reqs
        )
        self.code_base_test = str_to_codebase(code_base_test)
        self.save_codebase()

        # Step 4: Write code
        for i in range(10):
            print(f"Starting iteration {i+1} " + "🫡"*(i+1))
            codebase_str = codebase_to_str(self.codebase)

            new_codebase_str = self.inferer.get_simple_response(
                DevPhase.WRITE_CODE,
                **common_kwargs,
                task=self.task,
                reqs=self.reqs_str,
                code_base=codebase_str
            )

            if new_codebase_str == "Done":
                print("We're done!")
                break

            new_codebase = str_to_codebase(new_codebase_str)
            self.codebase = merge_codebases(self.codebase, new_codebase)
            self.save_codebase()
  
        # Step 5: Write tests
        pass

    def save_project_description(self, project_description: str) -> None:
        directory = self.run_manager.output_dir
        os.makedirs(directory, exist_ok=True)    
        file_name = "project_description.txt"
        file_path = os.path.join(directory, file_name)        
        with open(file_path, 'w') as file:
            file.write(project_description)

    def save_codebase(self) -> None:
        directory = self.run_manager.output_dir
        os.makedirs(directory, exist_ok=True)    
        for file_name, file_content in self.codebase.items():
            file_path = os.path.join(directory, file_name)        
            with open(file_path, 'w') as file:
                file.write(file_content.strip())

def merge_codebases(old_codebase: CodeBase, new_codebase: CodeBase) -> CodeBase:
    merged_codebase = {**old_codebase, **new_codebase}
    return merged_codebase

def codebase_to_str(codebase: Dict[str, str]) -> str:
    result = ""
    for file_name, file_content in codebase.items():
        result += "File: " + file_name + "\n" # file name
        result += file_content + "\n"  # content
        result += "--\n"
    return result

def reqs_to_str(reqs: List[str]) -> str:
    return "\n".join(["- " + req for req in reqs])

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
