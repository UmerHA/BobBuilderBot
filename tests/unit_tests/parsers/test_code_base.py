from builderbot.parsers.code_base import CodeBase
from builderbot.parsers.code_skeleton import CodeSkeleton, CodeFile, Function

def test_from_code_skeleton_no_functions():
    skeleton_file = CodeFile(name='test_file.py', description='Test file')
    code_skeleton = CodeSkeleton(files=[skeleton_file])

    code_base = CodeBase.from_code_skeleton(code_skeleton)

    assert len(code_base.files) == 1
    assert code_base.files[0].name == 'test_file.py'
    assert code_base.files[0].lines == ['']


def test_from_code_skeleton_with_functions():
    skeleton_func = Function(name='test_func', signature='def test_func():')
    skeleton_file = CodeFile(name='test_file.py', description='Test file', functions=[skeleton_func])
    code_skeleton = CodeSkeleton(files=[skeleton_file])

    code_base = CodeBase.from_code_skeleton(code_skeleton)

    assert len(code_base.files) == 1
    assert code_base.files[0].name == 'test_file.py'
    assert code_base.files[0].lines == ['   def test_func():', '']
