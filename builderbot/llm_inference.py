import os
import pickle
from typing import List
from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage
from .prompts import get_prompt
from .run_manager import RunManager
from .stages import DevPhase, InferenceStep


class LLMCache:
    def __init__(self, llm: BaseChatModel, filename: str = 'cache/cache.pkl'):
        self.llm = llm
        self.filename = filename 
        if os.path.exists(filename):
            with open(filename, 'rb') as f: self.cache = pickle.load(f)
        else:
            self.cache = {}

    def update(self, prompt: List[BaseMessage], value: str):
        prompt_key = tuple(prompt)  # convert prompt to tuple to use it as dict key
        self.cache[prompt_key] = value
        self.save_to_file()

    def save_to_file(self):
        with open(self.filename, 'wb') as f:
            pickle.dump(self.cache, f)

    def get_llm_result(self, llm, prompt):
        prompt_key = tuple(prompt)  # convert prompt to tuple to use it as dict key
        if prompt_key in self.cache:
            return self.cache[prompt_key]
        else:
            result = llm(prompt).content
            self.update(prompt, result)
            return result

    def clear(self):
            self.cache = {}
            if os.path.exists(self.filename):
                os.remove(self.filename)


# todo: better name
class LLMInferer():
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.cache = LLMCache(llm)

    # short names for logging
    phase_for_logging = {
        DevPhase.UNDERSTAND: "1_understand",
        DevPhase.ARCHITECTURE: "2_architecture",
        DevPhase.STRUCTURE_CODE: "3_skeleton_code",
        DevPhase.STRUCTURE_TESTS: "4_skeleton_test",
        DevPhase.FLESH_OUT_CODE: "5_flesh_out_code",
        DevPhase.FLESH_OUT_TESTS: "6_flesh_out_test"
    }
    step_for_logging = {
        InferenceStep.IDEATE: "__a_ideation",
        InferenceStep.CRITIQUE: "__b_critique",
        InferenceStep.RESOLVE: "__c_resolution"
    }

    def save_output(self, content: str, phase: DevPhase, stage: InferenceStep, run_manager: RunManager):
        dir_ = f"cache/run_{run_manager.run_no}/"
        os.makedirs(dir_, exist_ok=True)
        filename = f"{dir_}/{self.phase_for_logging[phase]}{self.step_for_logging[stage]}.txt"
        with open(filename, "w") as file: file.write(content)

    def llm_result(self, prompt: List[BaseMessage]):
        return self.cache.get_llm_result(self.llm, prompt)

    def get_thoughtful_reponse(self, phase: DevPhase, llm: BaseChatModel, run_manager: RunManager,
        verbose=True, save=True, save_intermediate=True, format_instructions=None,
        **prompt_vars) -> str:

        # Step 1: Initial response
        prompt = get_prompt(phase, InferenceStep.IDEATE, **prompt_vars)
        initial_response = self.llm_result(prompt).content
        if verbose: print(f"> Initial response:\n{initial_response}\n")    
        if save_intermediate: self.save_output(initial_response, phase, InferenceStep.IDEATE, run_manager=run_manager)
            
        # Step 2: Self-critique
        prompt = get_prompt(phase, InferenceStep.CRITIQUE, **prompt_vars)
        critique = self.llm_result(prompt).content
        if verbose: print(f"> Self-critique:\n{critique}\n")
        if save_intermediate: self.save_output(critique, phase, InferenceStep.CRITIQUE, run_manager=run_manager)

        # Step 3: Thoughtful response
        if format_instructions: prompt_vars["format_instructions"] = format_instructions  # only use format instructions in last step
        prompt = get_prompt(phase, InferenceStep.RESOLVE, **prompt_vars)
        thoughtful_response = self.llm_result(prompt).content
        if verbose: print(f"> Thoughtful response:\n{thoughtful_response}\n")
        if save_intermediate: self.save_output(thoughtful_response, phase, InferenceStep.RESOLVE, run_manager=run_manager)
        
        return thoughtful_response

