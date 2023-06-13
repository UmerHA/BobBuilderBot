import os
from typing import List, Optional, Tuple
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from .code_base_summarizer import SimpleSummarizer
from .inference import LLMInferer
from .models import CodeBase, code_base_parser, code_change_parser, project_description_parser
from .models.project_description import Requirement
from .run_manager import RunManager
from .stages import DevPhase
from .validation.syntax import syntax_validator_from_file_type, FILE_TYPES_TO_IGNORE


class BuilderBot:

    MAX_ITER_PER_FEATURE = 10

    def __init__(self, model_name: str ="gpt-3.5-turbo", cache_filename: Optional[str] = None) -> None:
        load_dotenv()
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(openai_api_key=openai_api_key, model_name=model_name)
        self.run_manager = RunManager()
        self.cache_filename = cache_filename
        self.inferer = LLMInferer(self.llm, self.run_manager, self.cache_filename)

    def build(self, goal: str, verbose=False) -> None:
        self.goal = goal
        self.verbose = verbose
        self.run_manager.start_run()

        common_kwargs = {
            "llm": self.llm,
            "run_manager": self.run_manager,
            "verbose": self.verbose,
        }

        # Step 1: Understand
        project_description = self.inferer.get_thoughtful_reponse(
            DevPhase.UNDERSTAND,
            **common_kwargs,
            user_goal=self.goal,
            format_instructions=project_description_parser.get_format_instructions()
        )
        parsed_project_description = project_description_parser.parse(project_description)
        self.requirements = parsed_project_description.requirements
        self.assumptions = parsed_project_description.assumptions
        project_description = parsed_project_description.to_str()

        # Step 2: Architect
        architecture = self.inferer.get_thoughtful_reponse(
            DevPhase.ARCHITECTURE,
            **common_kwargs,
            project_description=project_description
        )

        # Step 2.5: Setup project


        # Step 3: Structure Code
        code_base = self.inferer.get_thoughtful_reponse(
            DevPhase.STRUCTURE_CODE,
            **common_kwargs,
            project_description=project_description,
            architecture=architecture,
            format_instructions=code_base_parser.get_format_instructions()
        )
        self.code_base = code_base_parser.parse(code_base)
        self.code_base.set_directory("project")
        self.code_base.save(output_dir=self.run_manager.output_dir)

        # Step 3: Structure Tests
        test_base = self.inferer.get_thoughtful_reponse(
            DevPhase.STRUCTURE_TESTS,
            **common_kwargs,
            project_description=project_description,
            architecture=architecture,
            format_instructions=code_base_parser.get_format_instructions()
        )
        self.test_base = code_base_parser.parse(test_base)
        self.test_base.set_directory("test")
        self.test_base.save(output_dir=self.run_manager.output_dir)

        # Step 4: Write code
        for req in self.requirements:
            self.code_base = self.implement_feature(req)
            self.code_base.save(output_dir=self.run_manager.output_dir)

        # Step 5: Write tests
        pass

        # Step 6: Deploy
        pass # out of scope -  will be done manu

        # Step 7: Improve
        pass # out of scope

    def implement_feature(self, requirement: Requirement) -> CodeBase:
        print(f"Implementing feature: {requirement.content}")
        max_iter, i = self.MAX_ITER_PER_FEATURE, 1
        current_errors = []
        while True:
            errors_as_str = self.format_errors(current_errors) if len(current_errors)>0 else None
            new_codebase = self.try_implementing_feature(requirement, try_no=i, errors=errors_as_str)
            current_errors = self.find_errors(requirement, new_codebase)
            if len(current_errors) == 0: break
            else:
                if self.verbose: print(f"Implementation not sucessful.\nErrors:\n{current_errors}\nTrying again.\n\n")
                if i >= max_iter: raise Exception(f"Could not implement this requirements: {requirement}")
            i += 1
        return new_codebase

    def try_implementing_feature(self, requirement: Requirement, try_no:int, errors: Optional[str]) -> CodeBase:
        code = SimpleSummarizer().summarize(self.code_base)  # represent code base as str
        common_kwargs = {
            "llm": self.llm,
            "run_manager": self.run_manager,
            "verbose": True, # todo: change back
            "try_no": try_no,
            "user_goal": self.goal,
            "code_base": code,
            "feature": requirement,
            "format_instructions": code_change_parser.get_format_instructions()
        }
        if not errors: errors = "code not checked yet, so no errors yet"
        change_json = self.inferer.get_simple_response(DevPhase.IMPROVE_CODE, errors=errors, **common_kwargs)
        change = code_change_parser.parse(change_json)
        return self.code_base.with_change(change)

    def find_errors(self, requirement: Requirement, code: CodeBase) -> List[Tuple[str, str]]:
        '''Check if the requirement is correctly implmented in the codebase'''

        errors: List[Tuple[str, str]] = []

        # check syntax (ie compilation)
        for file in code.files:
            if file.name.split(".")[-1] in FILE_TYPES_TO_IGNORE: continue
            
            validator = syntax_validator_from_file_type(file.name)

            code_in_file = str(file)
            sucess, err_msg = validator.check_syntax(code_in_file)

            if sucess:
                formatted_code = validator.format(code_in_file)
                file.overwrite(formatted_code)
            else:
                errors.append((file.name, err_msg))

        # check semancitc (ie if tests pass)
        # todo

        return errors

    def format_errors(self, errors: List[Tuple[str, str]]) -> str:
        bla = "\n\n".join([f"In {filename}:\n{err_msg}" for filename, err_msg in errors])
        return bla
