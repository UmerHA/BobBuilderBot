from typing import List
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.schema import BaseMessage
from .stages import DevPhase, InferenceStep
from .utils import load_file

phase2file = {
    DevPhase.UNDERSTAND: "1_understand_requirement",
    DevPhase.ARCHITECTURE: "2_choose_architecture",
    DevPhase.STRUCTURE_CODE: "3_create_code_skeleton",
    DevPhase.STRUCTURE_TESTS: "4_create_test_skeleton",
    DevPhase.WRITE_CODE: "5_write_code",
    DevPhase.IMPROVE_CODE: "6_improve_code",
    DevPhase.WRITE_TESTS: "7_write_test",
    DevPhase.IMPROVE_TESTS: "8_improve_test",
    DevPhase.DEPLOY: "9_deploy",
    DevPhase.IMPROVE: "10_improve"
}

step2file = {
    InferenceStep.SIMPLE: "",
    InferenceStep.IDEATE: "__ideate",
    InferenceStep.CRITIQUE: "__reflect",
    InferenceStep.RESOLVE: "__resolve",
}

def prompt_file(phase: DevPhase, step: InferenceStep) -> str:
    return phase2file[phase] + step2file[step]

def load_prompt(phase: DevPhase, step: InferenceStep) -> ChatPromptTemplate:
    path_to_system_prompt = "prompts/system.txt"
    path_to_human_prompt = f"prompts/{prompt_file(phase, step)}.txt"
    system_file_contents = load_file(path_to_system_prompt)
    human_file_contents = load_file(path_to_human_prompt)
    system_msg = SystemMessagePromptTemplate.from_template(system_file_contents)
    human_msg = HumanMessagePromptTemplate.from_template(human_file_contents)
    return ChatPromptTemplate.from_messages([system_msg, human_msg])

def get_prompt(stage: DevPhase, step: InferenceStep, **prompt_vars) -> List[BaseMessage]:
    prompt_template = load_prompt(stage, step)
    return prompt_template.format_prompt(**prompt_vars).to_messages()
