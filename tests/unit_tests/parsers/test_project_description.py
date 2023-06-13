from builderbot.stringify import ProjectDescription, Requirement, Assumption, UserQuestion

def test_to_str() -> None:
    descr  = ProjectDescription(
        user_goal="Build a space ship",
        requirements=[Requirement(content="Flys into space"), Requirement(content="Doesn't crash")],
        assumptions=[Assumption(content="Runs on power of friendship")]
    )
    assert type(descr.to_str()) == str

    descr.questions = [UserQuestion(content="What color should the space ship be?")]
    assert type(descr.to_str()) == str
