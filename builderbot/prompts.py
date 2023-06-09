from typing import List
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.schema import BaseMessage
from .stages import DevPhase, InferenceStep

phase2file = {
    DevPhase.UNDERSTAND: "1_understand_requirement",
    DevPhase.ARCHITECTURE: "2_choose_architecture",
    DevPhase.STRUCTURE_CODE: "3_create_code_skeleton",
    DevPhase.STRUCTURE_TESTS: "4_create_test_skeleton",
    DevPhase.FLESH_OUT_CODE: "5_flesh_out_code",
    DevPhase.FLESH_OUT_TESTS: "6_flesh_out_test",
    DevPhase.DEPLOY: "7_deploy",
    DevPhase.IMPROVE: "8_improve"
}

step2file = {
    InferenceStep.IDEATE: "ideate",
    InferenceStep.CRITIQUE: "reflect",
    InferenceStep.RESOLVE: "resolve",
}


def prompt_file(phase: DevPhase, step: InferenceStep) -> str:
    return phase2file[phase] + "__" + step2file[step]

def load_prompt(phase: DevPhase, step: InferenceStep) -> ChatPromptTemplate:
    path_to_system_prompt = "prompts/system.txt"
    path_to_human_prompt = f"prompts/{prompt_file(phase, step)}.txt"
    with open(path_to_system_prompt, "r") as file: system_file_contents = file.read()
    with open(path_to_human_prompt, "r") as file: human_file_contents = file.read()
    system_msg = SystemMessagePromptTemplate.from_template(system_file_contents)
    human_msg = HumanMessagePromptTemplate.from_template(human_file_contents)
    return ChatPromptTemplate.from_messages([system_msg, human_msg])

def get_prompt(stage: DevPhase, step: InferenceStep, **prompt_vars) -> List[BaseMessage]:
    prompt_template = load_prompt(stage, step)
    return prompt_template.format_prompt(**prompt_vars).to_messages()
