import yaml

from mau.visitors.base_visitor import BaseVisitor


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


class YamlVisitor(BaseVisitor):
    format_code = "yaml"
    extension = "yaml"

    def _postprocess(self, result, *args, **kwargs):
        result = super()._postprocess(result, *args, **kwargs)

        return yaml.dump(result, Dumper=NoAliasDumper)
