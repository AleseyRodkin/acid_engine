# acid_engine/modules/core.py
import yaml
import importlib.util
import os
import time
import pickle
import pandas as pd
from .tracer import Tracer

class ModuleCore:
    """
    Локальный оркестратор модуля.
    Поддерживает: манифест, топологическую сортировку, Hot Reload, чекпоинты.
    """
    def __init__(self, module_dir: str, manifest_name: str = "functions.manifest",
                 hot_reload: bool = False, resume: bool = False):
        self.module_dir = module_dir
        self.manifest_path = os.path.join(module_dir, manifest_name)
        self.hot_reload = hot_reload
        self.resume = resume
        self.functions = {}
        self.dependencies = {}
        self.function_files = {}
        self._load_manifest()
        self.tracer = Tracer()

    def _load_manifest(self):
        with open(self.manifest_path, "r") as f:
            manifest = yaml.safe_load(f)
        for func_def in manifest["functions"]:
            name = func_def["name"]
            file_path = os.path.join(self.module_dir, func_def["file"])
            self.function_files[name] = file_path
            self.dependencies[name] = func_def.get("depends_on", [])
            self._import_function(name, file_path)

    def _import_function(self, name: str, file_path: str):
        spec = importlib.util.spec_from_file_location(name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.functions[name] = module

    def _file_changed(self, file_path: str, last_mtime: float) -> bool:
        """Проверяет, изменился ли файл с момента last_mtime."""
        try:
            current_mtime = os.path.getmtime(file_path)
            return current_mtime > last_mtime
        except OSError:
            return False

    def _reload_function(self, name: str, file_path: str):
        """Перезагружает функцию из файла."""
        module = self.functions[name]
        importlib.reload(module)
        self.functions[name] = module

    def _topological_sort(self):
        visited = set()
        result = []

        def visit(func_name):
            if func_name in visited:
                return
            visited.add(func_name)
            for dep in self.dependencies.get(func_name, []):
                if dep not in self.functions:
                    raise ValueError(f"Function '{func_name}' depends on unknown function '{dep}'")
                visit(dep)
            result.append(func_name)

        for name in self.functions:
            visit(name)
        return result

    def execute(self, data):
        ordered = self._topological_sort()
        last_mtimes = {name: os.path.getmtime(self.function_files[name])
                       for name in ordered}

        for func_name in ordered:
            # Hot Reload
            if self.hot_reload:
                file_path = self.function_files[func_name]
                if self._file_changed(file_path, last_mtimes[func_name]):
                    self._reload_function(func_name, file_path)
                    last_mtimes[func_name] = os.path.getmtime(file_path)

            # Чекпоинт: загрузка
            checkpoint_path = os.path.join(self.module_dir, f".checkpoint_{func_name}.pkl")
            if self.resume and os.path.exists(checkpoint_path):
                with open(checkpoint_path, "rb") as f:
                    data = pickle.load(f)
                continue

            with self.tracer.trace(func_name):
                module = self.functions[func_name]
                data = module.execute(data)

                # Чекпоинт: сохранение
                if self.resume:
                    with open(checkpoint_path, "wb") as f:
                        pickle.dump(data, f)

        return data

    def report(self) -> str:
        return self.tracer.report()