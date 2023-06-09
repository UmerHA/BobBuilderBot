import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from .inference import LLMInferer
from .run_manager import RunManager
from .parsers import code_base_parser, project_description_parser, CodeBase
from .stages import DevPhase

class BuilderBot:
    def __init__(self, model_name: str ="gpt-3.5-turbo"):
        load_dotenv()
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(openai_api_key=openai_api_key, model_name=model_name)

    def build(self, goal: str):
        self.goal = goal
        self.run_manager = RunManager()
        self.run_manager.start_run()

        inferer = LLMInferer(self.llm, self.run_manager)

        # Step 1: Understand
        project_description = inferer.get_thoughtful_reponse(
            DevPhase.UNDERSTAND,
            llm=self.llm,
            run_manager=self.run_manager,
            user_goal=self.goal,
            format_instructions=project_description_parser.get_format_instructions()
                                   )
        parsed_project_description = project_description_parser.parse(project_description)
        self.requirements = parsed_project_description.requirements
        self.assumptions = parsed_project_description.assumptions
        project_description = parsed_project_description.to_str()

        # Step 2: Architect
        architecture = inferer.get_thoughtful_reponse(
            DevPhase.ARCHITECTURE, 
            llm=self.llm,
            run_manager=self.run_manager,
            project_description=project_description
        )

        # Step 3: Structure Code
        code_skeleton = inferer.get_thoughtful_reponse(
            DevPhase.STRUCTURE_CODE,
            llm=self.llm,
            run_manager=self.run_manager,
            project_description=project_description,
            architecture=architecture,
            format_instructions=code_base_parser.get_format_instructions()
        )
        parsed_code_skeleton = code_base_parser.parse(code_skeleton)
        self.create_project(parsed_code_skeleton, directory="project")

        # Step 3: Structure Tests
        test_skeleton = inferer.get_thoughtful_reponse(
            DevPhase.STRUCTURE_TESTS,
            llm=self.llm,
            run_manager=self.run_manager,
            project_description=project_description,
            architecture=architecture,
            format_instructions=code_base_parser.get_format_instructions()
        )
        parsed_test_skeleton = code_base_parser.parse(test_skeleton)
        self.create_project(parsed_test_skeleton, directory="test")

        # Step 4: Flesh out code
        print("Now, I should process these requirements:")
        for i, req in enumerate(self.requirements):
            print(f"{i+1}: {req}")
        
        # Step 5: Flesh out tests
        pass

        # Step 6: Deploy
        pass

        # Step 7: Improve
        pass


    # # # # # # # # # # # # # # # # # #
    # Helper functions for each phase #
    # # # # # # # # # # # # # # # # # #

    def create_project(self, codebase: CodeBase, directory: str) -> None:
        home_dir = f"output/run_{self.run_manager.run_no}/{directory}/"
        for code_file in codebase.code_files:
            comment = "# " if code_file.name.endswith(".py") else "// "        
            full_path = os.path.join(home_dir, code_file.name)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)           
            with open(full_path, "w") as f:
                f.write(comment+code_file.description+'\n\n')
                for func in code_file.functions:
                    f.write(comment+func.signature+'\n\n')