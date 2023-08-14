# This is a class to manage variable environments


class Environment:
    def __init__(self, content=None, namespace=None):
        self._variables = {}

        if content is not None:
            self.update(content, namespace)

    def split_namespace(self, key):
        if "." not in key:
            return [key]

        return key.split(".")

    def setvar(self, key, value):
        path = self.split_namespace(key)

        if len(path) == 1:
            self._variables[path[0]] = value
            return

        namespace = self._variables
        for i in path[0:-1]:
            if i not in namespace:
                namespace[i] = {}

            namespace = namespace[i]

        namespace[path[-1]] = value

    def getvar(self, key, default=None):
        path = self.split_namespace(key)

        try:
            if len(path) == 1:
                return self._variables[path[0]]

            namespace = self._variables
            for i in path[0:-1]:
                namespace = namespace[i]

            return namespace[path[-1]]
        except KeyError:
            if default is None:
                raise

            return default

    def update(self, adict, namespace=None):
        if namespace is None:
            self._variables = adict
        else:
            self._variables[namespace] = adict

    def asdict(self):
        return self._variables
