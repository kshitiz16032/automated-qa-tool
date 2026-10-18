import importlib.util
import inspect

def read_function_source(file_path: str, function_name: str) -> str:
    spec = importlib.util.spec_from_file_location("module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    func = getattr(module, function_name)
    return inspect.getsource(func)
