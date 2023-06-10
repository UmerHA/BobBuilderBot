from builderbot.models.code_base import CodeBase, CodeFile
from builderbot.models.code_change import CodeChange, CodeFileChange, Insertion, Deletion, Replacement


def test_insertion():
    base = CodeBase(files=[CodeFile(name="test.py", content="\n".join([f"line {i}" for i in range(1, 4)]))])
    change = CodeChange(files=[CodeFileChange(name="test.py", changes=[Insertion(line_number_start=1, new_lines=["new line 2", "new line 3"])])])
    new_base = base.with_change(change)
    lines = new_base.files[0].content.lines()
    assert len(lines) == 5
    assert lines[1].content == "new line 2"
    assert lines[2].content == "new line 3"

def test_deletion():
    base = CodeBase(files=[CodeFile(name="test.py", content="\n".join([f"line {i}" for i in range(1, 4)]))])
    change = CodeChange(files=[CodeFileChange(name="test.py", changes=[Deletion(line_number_start=2, line_number_end=2)])])
    new_base = base.with_change(change)
    lines = new_base.files[0].content.lines()
    assert len(lines) == 2
    assert lines[1].content == "line 3"

def test_replacement():
    base = CodeBase(files=[CodeFile(name="test.py", content="\n".join([f"line {i}" for i in range(1, 4)]))])
    change = CodeChange(files=[CodeFileChange(name="test.py", changes=[Replacement(line_number_start=2, line_number_end=2, new_lines=["updated line 2", "updated line 3"])])])
    new_base = base.with_change(change)
    lines = new_base.files[0].content.lines()  
    assert len(lines) == 4
    assert lines[1].content == "updated line 2"
    assert lines[2].content == "updated line 3"

def test_insertion_deletion_and_replacement():
    base = CodeBase(files=[CodeFile(name="test.py", content="\n".join([f"line {i}" for i in range(1, 6)]))])
    changes = [
        Insertion(line_number_start=1, new_lines=["new line 2"]),
        Deletion(line_number_start=3, line_number_end=3),
        Replacement(line_number_start=4, line_number_end=4, new_lines=["updated line 4"]),
    ]
    change = CodeChange(files=[CodeFileChange(name="test.py", changes=changes)])
    new_base = base.with_change(change)
    lines = new_base.files[0].content.lines()  
    assert len(lines) == 5
    assert lines[0].content == "line 1"
    assert lines[1].content == "new line 2"
    assert lines[2].content == "line 2"
    assert lines[3].content == "updated line 4"
    assert lines[4].content == "line 5"
