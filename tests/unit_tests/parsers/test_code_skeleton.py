from builderbot.parsers.code_skeleton import CodeSkeleton, CodeFile, Function

def test_to_str() -> None:
    code  = CodeSkeleton(
        files=[
            CodeFile(
                name="bla.py",
                description="does bla stuff",
                functions=[Function(name="foo", signature="def foo(bar: str)")]
            ),
            CodeFile(name="index.html", description="web app")
        ]
    )
    assert type(code.to_str()) == str
