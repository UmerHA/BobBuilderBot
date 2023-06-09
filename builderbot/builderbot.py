import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from .inference import LLMInferer
from .run_manager import RunManager
from .parsers import code_skeleton_parser, code_change_parser, project_description_parser, CodeSkeleton, CodeBase
from .parsers.project_description import Requirement
from .stages import DevPhase
from .code_base_summarizer import SimpleSummarizer

class BuilderBot:
    def __init__(self, model_name: str ="gpt-3.5-turbo"):
        load_dotenv()
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(openai_api_key=openai_api_key, model_name=model_name)

    def build(self, goal: str, verbose=True):
        self.goal = goal
        self.verbose = verbose
        self.run_manager = RunManager()
        self.run_manager.start_run()
        self.inferer = LLMInferer(self.llm, self.run_manager)

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
        self.code_base = CodeBase.from_code_skeleton(self.code_skeleton)

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
        pass

        # Step 5: Write tests
        pass

        # Step 6: Deploy
        pass

        # Step 7: Improve
        pass


    # # # # # # # # # # # # # # # # # #
    # Helper functions for each phase #
    # # # # # # # # # # # # # # # # # #

    def create_project(self, codebase: CodeSkeleton, directory: str) -> None:
        home_dir = f"output/run_{self.run_manager.run_no}/{directory}/"
        for code_file in codebase.files:
            comment = "# " if code_file.name.endswith(".py") else "// "        
            full_path = os.path.join(home_dir, code_file.name)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)           
            with open(full_path, "w") as f:
                f.write(comment+code_file.description+'\n\n')
                for func in code_file.functions:
                    f.write(comment+func.signature+'\n\n')

    def implement_feature(self, requirement: Requirement) -> None:

        if self.verbose: print(f"Implementing feature: {requirement.content}")

        max_iter = 3
        i = 0
        while True:
            if i >= max_iter:
                raise Exception(f"Could not implement this requirements: {requirement}")
            new_codebase = self.try_implementing_feature(requirement)
            if self.check_implementation(requirement, new_codebase):
                break
            i += 1
        return

    def try_implementing_feature(self, requirement: Requirement) -> CodeBase:
        # get context
        code = SimpleSummarizer().summarize(self.code_base)

        # get proposed code change
        change = self.inferer.get_thoughtful_reponse(
            DevPhase.WRITE_CODE,
            llm=self.llm,
            run_manager=self.run_manager,
            verbose=self.verbose,
            user_goal=self.goal,
            code_base=code,
            feature=requirement,
            format_instructions=code_change_parser.get_format_instructions()
        )

        if self.verbose: print(f"Proposed change: {change}")

        # merge change and return
        return self.code_base.with_change(change)


    def check_implementation(self, requirement: Requirement, code: CodeBase) -> bool:
        '''Check if the requirement is correctly implmented in the codebase'''

        # check syntax (ie compilation)

        # check semantics

        # check if tests pass

        return False
