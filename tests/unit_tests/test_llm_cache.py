from typing import List, Optional
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.chat_models.base import SimpleChatModel
from langchain.schema import BaseMessage
from builderbot.inference import LLMCache

class FakeLLM(SimpleChatModel):
    def _call(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        return str(len(messages))
    
    @property
    def _llm_type(self) -> str:
        return "FakeLLM"
        
def test_cache():
    llm = FakeLLM()
    cache = LLMCache(llm, filename="cache/cache.tst.pkl")
    cache.clear()

    prompt = ["this", "is", "a", "test"]
    result = cache.get_llm_result(llm, prompt)
    assert result == "4"

    prompt = ["this", "is", "test"]
    result = cache.get_llm_result(llm, prompt)
    assert result == "3"

    cache.update(prompt, "99")
    result = cache.get_llm_result(llm, prompt)
    assert result == "99"

    cache = LLMCache(llm, filename="cache/cache.tst.pkl")