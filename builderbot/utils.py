import pkg_resources

def load_file(filename: str) -> str:
    return load_binary_file(filename).decode('utf-8')

def load_binary_file(filename: str) -> bytes:
    return pkg_resources.resource_string(__name__, filename)
