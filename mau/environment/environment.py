class Environment:
    def __init__(self, content=None, namespace=None):
        self._variables = {}

        if content is not None:
            self.update(content, namespace)

    def setvar(self, key, value):
        path = key.split(".")

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
        try:
            return self.getvar_nodefault(key)
        except KeyError:
            return default

    def getvar_nodefault(self, key):
        path = key.split(".")

        if len(path) == 1:
            return self._variables[path[0]]

        namespace = self._variables
        for i in path[0:-1]:
            namespace = namespace[i]

        return namespace[path[-1]]

    def getnamespace(self, namespace):
        return Environment(self.getvar(namespace))

    def update(self, adict, namespace=None):
        if not namespace:
            self._variables.update(adict)
            return

        try:
            nspc = self.getvar_nodefault(namespace)
        except KeyError:
            self.setvar(namespace, {})
            nspc = self.getvar(namespace)

        nspc.update(adict)

    def asdict(self):
        return self._variables

    def __repr__(self):
        return f"{self.asdict()}"

    def __eq__(self, other):
        return self._variables == other._variables
