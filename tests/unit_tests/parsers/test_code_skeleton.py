from builderbot.parsers.code_skeleton import CodeSkeleton, CodeFileSkeleton, Function

def test_to_str() -> None:
    code  = CodeSkeleton(
        files=[
            CodeFileSkeleton(
                name="bla.py",
                description="does bla stuff",
                functions=[Function(name="foo", signature="def foo(bar: str)")]
            ),
            CodeFileSkeleton(name="index.html", description="web app")
        ]
    )
    assert type(code.to_str()) == str
