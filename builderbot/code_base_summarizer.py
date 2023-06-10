from abc import abstractmethod
from .models import CodeBase

class BaseCodeBaseSummarizer:
    @abstractmethod
    def summarize(self, code: CodeBase) -> str:
        '''Summarize a codebase, so it can be used in a prompt'''

class SimpleSummarizer(BaseCodeBaseSummarizer):
    '''Return the code base in full detail'''
    def summarize(self, code: CodeBase) -> str:
        result = ""
        files = sorted(code.files, key=lambda f: f.name)
        for file in files:
            result += "> " + file.name + ":\n"
            result += file.content + "\n"
        return result

class ContextualSummarizer(BaseCodeBaseSummarizer):
    '''Only return full details on relevant parts of the code base,
    and abbreviate non-relevant parts.'''

    def __init__(self, context: str):
        self.context = context

    def summarize(self, code: CodeBase) -> str:
        raise NotImplementedError()
