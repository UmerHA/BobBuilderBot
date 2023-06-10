import os
import pickle
from typing import List, Optional
from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage
from .prompts import get_prompt
from .run_manager import RunManager
from .stages import DevPhase, InferenceStep


DEFAULT_CACHE_FILE = "cache/cache.pkl"

class LLMCache:
    def __init__(self, llm: BaseChatModel, filename: Optional[str] = None):
        self.llm = llm
        self.filename = filename if filename is not None else DEFAULT_CACHE_FILE
        if os.path.exists(filename):
            with open(filename, 'rb') as f: self.cache = pickle.load(f)
        else:
            self.cache = {}

    def update(self, prompt: List[BaseMessage], value: str):
        prompt_key = self.to_hashable(prompt)
        self.cache[prompt_key] = value
        self.save_to_file()

    def save_to_file(self):
        with open(self.filename, 'wb') as f:
            pickle.dump(self.cache, f)

    def to_hashable(self, prompt: List[BaseMessage]):
        return tuple([str(msg) for msg in prompt])

    def get_llm_result(self, llm, prompt):
        prompt_key = self.to_hashable(prompt)
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

    def delete_containing(self, text: str):
        '''Delete all keys containing given text'''
        keys_to_delete = [k for k in self.cache.keys() if text in str(k)]
        for k in keys_to_delete:
            del self.cache[k]
        print(f"Deleted {len(keys_to_delete)} keys")

# todo: better name
class LLMInferer():
    def __init__(self, llm: BaseChatModel, run_manager: RunManager, cache_filename: Optional[str] = None):
        self.llm = llm
        self.cache = LLMCache(llm, cache_filename)
        self.run_manager = run_manager

    # short names for logging
    phase_for_logging = {
        DevPhase.UNDERSTAND: "1_understand",
        DevPhase.ARCHITECTURE: "2_architecture",
        DevPhase.STRUCTURE_CODE: "3_skeleton_code",
        DevPhase.STRUCTURE_TESTS: "4_skeleton_test",
        DevPhase.WRITE_CODE: "5_write_code",
        DevPhase.IMPROVE_CODE: "6_improve_code",
        DevPhase.WRITE_TESTS: "7_write_test",
        DevPhase.IMPROVE_TESTS: "7_improve_test"
    }
    step_for_logging = {
        InferenceStep.SIMPLE: "",
        InferenceStep.IDEATE: "__a_ideation",
        InferenceStep.CRITIQUE: "__b_critique",
        InferenceStep.RESOLVE: "__c_resolution"
    }

    def save_output(self, content: str, phase: DevPhase, stage: InferenceStep, try_no: Optional[int] = None):
        dir_ = f"cache/run_{self.run_manager.run_no}/"
        os.makedirs(dir_, exist_ok=True)
        try_str = f"_try_{try_no}" if try_no else ""
        filename = f"{dir_}/{self.phase_for_logging[phase]}{self.step_for_logging[stage]}{try_str}.txt"
        with open(filename, "w") as file: file.write(content)

    def llm_result(self, prompt: List[BaseMessage]):
        return self.cache.get_llm_result(self.llm, prompt)

    def get_thoughtful_reponse(self, phase: DevPhase,
        verbose:bool=True, save:bool=True, format_instructions:Optional[str]=None,
        try_no:Optional[int]=None,
        **prompt_vars) -> str:
        '''Get LLM response using the SmartGPT workflow'''
        try_no_str = f" (try no {try_no})" if try_no else ""
        if verbose: print(f">>> {phase}{try_no_str}")
        common_kwargs = {
            "verbose": verbose,
            "save": save,
            "try_no": try_no,
            **prompt_vars
        }
        # Step 1: Initial response
        initial_response = self._get_response(phase, InferenceStep.IDEATE, "Initial response", **common_kwargs)
        # Step 2: Self-critique
        common_kwargs["initial_response"] = initial_response
        critique = self._get_response(phase, InferenceStep.CRITIQUE, "Self-critique", **common_kwargs)
        # Step 3: Thoughtful response
        common_kwargs["critique"] = critique
        if format_instructions: common_kwargs["format_instructions"] = format_instructions  # only use format instructions in last step
        thoughtful_response = self._get_response(phase, InferenceStep.RESOLVE, "Thoughtful response", **common_kwargs)
        return thoughtful_response
    
    def get_simple_response(self, phase: DevPhase,
        verbose:bool=True, save:bool=True, format_instructions:Optional[str]=None,
        try_no:Optional[int]=None,
        **prompt_vars) -> str:
        '''Get LLM response'''
        try_no_str = f" (try no {try_no})" if try_no else ""
        if verbose: print(f">>> {phase}{try_no_str}")
        if format_instructions: prompt_vars["format_instructions"] = format_instructions
        self._get_response(phase, InferenceStep.SIMPLE, "Response", verbose, save, try_no, **prompt_vars)

    def _get_response(self, phase: DevPhase, step: InferenceStep, response_prefix: str,
        verbose:bool=True, save:bool=True, try_no:Optional[int]=None,
        **prompt_vars) -> str:
        prompt = get_prompt(phase, step, **prompt_vars)
        response = self.llm_result(prompt)
        if verbose: print(f">  {response_prefix}:\n{response}\n")    
        if save: self.save_output(response, phase, step, try_no)
        return response