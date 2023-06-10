from builderbot.models.code_base import CodeBase, CodeFile, CodeLine
from builderbot.code_base_summarizer import SimpleSummarizer

def test_simple_summarizer():
    code = CodeBase(files=[
        CodeFile(name="file1.py", content="print('Hello, world!')"),
        CodeFile(name="file2.py", content="def add(a, b):\n    return a + b"),
    ])

    summarizer = SimpleSummarizer()
    summary = summarizer.summarize(code)

    expected_summary = "file1.py:\n1   print('Hello, world!')\n\nfile2.py:\n1   def add(a, b):\n2       return a + b\n\n"
    assert summary == expected_summary
