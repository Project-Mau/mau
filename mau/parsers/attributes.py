class AttributesManager:
    def __init__(self, parser):
        self.args = []
        self.kwargs = {}
        self.tags = []
        self.subtype = None

        self.parser = parser

    @property
    def attributes(self):
        return (
            self.args,
            self.kwargs,
            self.tags,
            self.subtype,
        )

    def push(
        self,
        args=None,
        kwargs=None,
        tags=None,
        subtype=None,
    ):
        self.args = args or self.args
        self.kwargs = kwargs or self.kwargs
        self.tags = tags or self.tags
        self.subtype = subtype or self.subtype

    def pop(self):
        args, kwargs, tags, subtype = self.attributes

        self.args = []
        self.kwargs = {}
        self.tags = []
        self.subtype = None

        return (args, kwargs, tags, subtype)
