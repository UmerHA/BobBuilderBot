from builderbot.parsers.code_base import CodeBase
from builderbot.parsers.code_skeleton import CodeSkeleton, CodeFileSkeleton, Function

def test_from_skeleton_no_functions():
    skeleton_file = CodeFileSkeleton(name='test_file.py', description='Test file')
    code_skeleton = CodeSkeleton(files=[skeleton_file])

    code_base = CodeBase.from_skeleton(code_skeleton)

    assert len(code_base.files) == 1
    assert code_base.files[0].name == 'test_file.py'
    assert len(code_base.files[0].lines) == 1
    assert code_base.files[0].lines[0].content == ''


def test_from_skeleton_with_functions():
    skeleton_func = Function(name='test_func', signature='def test_func():')
    skeleton_file = CodeFileSkeleton(name='test_file.py', description='Test file', functions=[skeleton_func])
    code_skeleton = CodeSkeleton(files=[skeleton_file])

    code_base = CodeBase.from_skeleton(code_skeleton)

    assert len(code_base.files) == 1
    assert code_base.files[0].name == 'test_file.py'
    assert len(code_base.files[0].lines) == 1
    assert code_base.files[0].lines[0].content == '   def test_func():'

def test_from_skeleton_multiple_files_and_functions():
    skeleton_func1 = Function(name='test_func1', signature='def test_func1():')
    skeleton_func2 = Function(name='test_func2', signature='def test_func2():')
    skeleton_func3 = Function(name='test_func3', signature='def test_func3():')
    skeleton_file1 = CodeFileSkeleton(name='test_file1.py', description='Test file 1', functions=[skeleton_func1])
    skeleton_file2 = CodeFileSkeleton(name='test_file2.py', description='Test file 2', functions=[skeleton_func2, skeleton_func3])
    code_skeleton = CodeSkeleton(files=[skeleton_file1, skeleton_file2])

    code_base = CodeBase.from_skeleton(code_skeleton)

    assert len(code_base.files) == 2
    assert code_base.files[0].name == 'test_file1.py'
    assert len(code_base.files[0].lines) == 1
    assert code_base.files[0].lines[0].content == '   def test_func1():'
    assert code_base.files[1].name == 'test_file2.py'
    assert len(code_base.files[1].lines) == 3
    assert code_base.files[1].lines[0].content == '   def test_func2():'
    assert code_base.files[1].lines[1].content == ''
    assert code_base.files[1].lines[2].content == '   def test_func3():'
