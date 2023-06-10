import os
from dotenv import load_dotenv
from typing import List, Optional, Tuple
from langchain.chat_models import ChatOpenAI
from .inference import LLMInferer
from .run_manager import RunManager
from .parsers import code_skeleton_parser, code_change_parser, project_description_parser, CodeSkeleton, CodeBase
from .parsers.project_description import Requirement
from .stages import DevPhase
from .code_base_summarizer import SimpleSummarizer
from .validation.syntax import SyntaxValidator

class BuilderBot:
    def __init__(self, model_name: str ="gpt-3.5-turbo", cache_filename: Optional[str] = None) -> None:
        load_dotenv()
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(openai_api_key=openai_api_key, model_name=model_name)
        self.run_manager = RunManager()
        self.cache_filename = cache_filename
        self.inferer = LLMInferer(self.llm, self.run_manager, self.cache_filename)

    def build(self, goal: str, verbose=True) -> None:
        self.goal = goal
        self.verbose = verbose
        self.run_manager.start_run()

        # Step 1: Understand
        project_description = self.inferer.get_thoughtful_reponse(
            DevPhase.UNDERSTAND,
            llm=self.llm,
            run_manager=self.run_manager,
            verbose=self.verbose,
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
            llm=self.llm,
            run_manager=self.run_manager,
            verbose=self.verbose,
            project_description=project_description
        )

        # Step 3: Structure Code
        code_skeleton = self.inferer.get_thoughtful_reponse(
            DevPhase.STRUCTURE_CODE,
            llm=self.llm,
            run_manager=self.run_manager,
            verbose=self.verbose,
            project_description=project_description,
            architecture=architecture,
            format_instructions=code_skeleton_parser.get_format_instructions()
        )
        self.code_skeleton = code_skeleton_parser.parse(code_skeleton)
        self.create_project(self.code_skeleton, directory="project")
        self.code_base = CodeBase.from_skeleton(self.code_skeleton)

        # Step 3: Structure Tests
        test_skeleton = self.inferer.get_thoughtful_reponse(
            DevPhase.STRUCTURE_TESTS,
            llm=self.llm,
            run_manager=self.run_manager,
            verbose=self.verbose,
            project_description=project_description,
            architecture=architecture,
            format_instructions=code_skeleton_parser.get_format_instructions()
        )
        self.test_skeleton = code_skeleton_parser.parse(test_skeleton)
        self.create_project(self.test_skeleton, directory="test")

        # Step 4: Write code
        for req in self.requirements:
            self.implement_feature(req)

        # Step 5: Write tests
        pass

        # Step 6: Deploy
        pass

        # Step 7: Improve
        pass


    # # # # # # # # # # # # # # # # # #
    # Helper functions for each phase #
    # # # # # # # # # # # # # # # # # #

    def comment_indicators(self, filename:str):
        if filename.endswith(".py"): return "# ", ""
        if filename.endswith(".js"): return "// ", ""
        if filename.endswith(".html"): return "<!-- ", " -->"
        if filename.endswith(".css"): return "/* ", " */"
        raise ValueError(f"Couldn't figure out how to indicate comments in this file: {filename}")

    def create_project(self, codebase: CodeSkeleton, directory: str) -> None:
        home_dir = f"output/run_{self.run_manager.run_no}/{directory}/"
        for code_file in codebase.files:
            comment_pre, comment_suf = self.comment_indicators(code_file.name)    
            full_path = os.path.join(home_dir, code_file.name)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)           
            with open(full_path, "w") as f:
                f.write(comment_pre+code_file.description+comment_suf+'\n\n')
                if code_file.functions:
                    for func in code_file.functions:
                        f.write(comment_pre+func.signature+comment_suf+'\n\n')

    def format_errors(errors: List[Tuple[str, str]]) -> str:
        "\n\n".join([f"In {filename}:\n{err_msg}" for filename, err_msg in errors])

    def implement_feature(self, requirement: Requirement) -> None:
        if self.verbose: print(f"Implementing feature: {requirement.content}")
        max_iter, i = 3, 1
        current_errors = []
        while True:
            errors_as_str = self.format_errors(current_errors) if len(current_errors)>0 else None
            new_codebase = self.try_implementing_feature(requirement, try_no=i, errors=errors_as_str)
            current_errors = self.find_errors(requirement, new_codebase)
            if len(current_errors) == 0: break
            else:
                if self.verbose: print("Implementation not sucessful. Trying again.")
                if i >= max_iter: raise Exception(f"Could not implement this requirements: {requirement}")
            i += 1
        return

    def try_implementing_feature(self, requirement: Requirement, try_no:int, errors: Optional[str]) -> CodeBase:
        code = SimpleSummarizer().summarize(self.code_base)  # get context
        common_kwargs = {
            "llm": self.llm,
            "run_manager": self.run_manager,
            "verbose": self.verbose,
            "try_no": try_no,
            "user_goal": self.goal,
            "code_base": code,
            "feature": requirement,
            "format_instructions": code_change_parser.get_format_instructions()
        }
        if len(errors)==0:
            change_json = self.inferer.get_thoughtful_reponse(DevPhase.WRITE_CODE, **common_kwargs)
        else:
            change_json = self.inferer.get_simple_response(DevPhase.IMPROVE_CODE, errors=errors, **common_kwargs)
        change = code_change_parser.parse(change_json)
        return self.code_base.with_change(change)

    def find_errors(self, requirement: Requirement, code: CodeBase) -> List[str, str]:
        '''Check if the requirement is correctly implmented in the codebase'''

        errors: List[Tuple[str, str]] = []

        # check syntax (ie compilation)
        for file in code.files:
            validator = SyntaxValidator.from_file_type(file.name)

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
