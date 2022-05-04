from importlib import import_module
from importlib.resources import contents, is_resource, read_binary
from typing import Any

from jinja2 import BaseLoader, TemplateNotFound


class ImportLibLoader(BaseLoader):
    """ """

    IGNORED = ["py", "pyo", "pyc", "__pycache__"]

    @staticmethod
    def _get_path_template(path_template: str) -> tuple[str, str]:
        path_template_splitted = path_template.rsplit("/", maxsplit=1)
        if len(path_template_splitted) == 2:
            path = f"/{path_template_splitted[0]}"
            template = path_template_splitted[1]
        else:
            path = "/"
            template = path_template_splitted[0]
        path = path.replace("/", ".")
        return path, template

    @staticmethod
    def _has_resource(module, template) -> bool:
        return any(
            [
                content == template
                for content in contents(module)
                if is_resource(module, template)
            ]
        )

    def __init__(self, module, encoding="utf-8"):
        self.module = module
        self.encoding: str = encoding

    def _get_module(self, path_template, module=None) -> tuple[Any, str]:
        path, template = ImportLibLoader._get_path_template(path_template)
        try:
            module = module
            if module is None:
                module = self.module
            if path:
                module = import_module(path, package=str(self.module.__package__))
            return module, template
        except ModuleNotFoundError:
            raise TemplateNotFound(
                f'{self.module.__package__}{f"{path}" if path else ""}'
            )

    def get_source(self, _, path_template):
        module, template = self._get_module(path_template)
        if not ImportLibLoader._has_resource(module, template):
            raise TemplateNotFound(template)
        source = read_binary(module, template)

        def uptodate():
            return True

        return source.decode(self.encoding), None, uptodate

    def list_templates(self):
        results = []

        def _walk(module):
            for content in contents(module):
                if any(content.endswith(f".{ending}") for ending in self.IGNORED):
                    continue
                if not is_resource(module, content):
                    new_module, path = self._get_module(f"{content}/", module)
                    _walk(new_module)
                else:
                    results.append(f"{module.__package__}.{content}")

        _walk(self.module)
        results.sort()
        return results
