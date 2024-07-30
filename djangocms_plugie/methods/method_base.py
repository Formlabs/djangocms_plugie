class MethodBase:
    type_names = [None]

    @staticmethod
    def serialize(value: any) -> any:
        raise NotImplementedError("Must implement serialize method")

    @staticmethod
    def deserialize(value: any, **kwargs) -> any:
        raise NotImplementedError("Must implement deserialize method")

    @property
    def type(self):
        return self.type_name
