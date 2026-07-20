import importlib

class ModuleLoader:
    def __init__(self, base_package="acid_engine"):
        self.base_package = base_package
        self._modules = {}

    def get_module(self, name: str):
        if name in self._modules:
            return self._modules[name]
        try:
            module = importlib.import_module(f".{name}", package=self.base_package)
            self._modules[name] = module
            return module
        except ImportError:
            raise ValueError(f"Module {name} not found in {self.base_package}")