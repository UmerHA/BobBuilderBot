from builderbot.parsers.code_base import CodeBase, CodeFile, CodeLine
from builderbot.parsers.code_change import CodeChange, CodeFileChange, Insertion, Deletion, Update


def test_insertion():
    base = CodeBase(files=[CodeFile(name="test.py", lines=[CodeLine(content=f"line {i}") for i in range(1, 4)])])
    change = CodeChange(files=[CodeFileChange(name="test.py", changes=[Insertion(line_number_start=1, new_lines=["new line 2"])])])
    new_base = base.with_change(change)
    
    assert len(new_base.files[0].lines) == 4
    assert new_base.files[0].lines[1].content == "new line 2"

def test_deletion():
    base = CodeBase(files=[CodeFile(name="test.py", lines=[CodeLine(content=f"line {i}") for i in range(1, 4)])])
    change = CodeChange(files=[CodeFileChange(name="test.py", changes=[Deletion(line_number_start=2, line_number_end=2)])])
    new_base = base.with_change(change)
    
    assert len(new_base.files[0].lines) == 2
    assert new_base.files[0].lines[1].content == "line 3"

def test_update():
    base = CodeBase(files=[CodeFile(name="test.py", lines=[CodeLine(content=f"line {i}") for i in range(1, 4)])])
    change = CodeChange(files=[CodeFileChange(name="test.py", changes=[Update(line_number_start=2, line_number_end=2, new_lines=["updated line 2"])])])
    new_base = base.with_change(change)
    
    assert len(new_base.files[0].lines) == 3
    assert new_base.files[0].lines[1].content == "updated line 2"

def test_insertion_deletion_and_update():
    base = CodeBase(files=[CodeFile(name="test.py", lines=[CodeLine(content=f"line {i}") for i in range(1, 6)])])
    changes = [
        Insertion(line_number_start=1, new_lines=["new line 2"]),
        Deletion(line_number_start=3, line_number_end=3),
        Update(line_number_start=4, line_number_end=4, new_lines=["updated line 4"]),
    ]
    change = CodeChange(files=[CodeFileChange(name="test.py", changes=changes)])
    new_base = base.with_change(change)
    
    assert len(new_base.files[0].lines) == 5
    assert new_base.files[0].lines[0].content == "line 1"
    assert new_base.files[0].lines[1].content == "new line 2"
    assert new_base.files[0].lines[2].content == "line 2"
    assert new_base.files[0].lines[3].content == "updated line 4"
    assert new_base.files[0].lines[4].content == "line 5"
