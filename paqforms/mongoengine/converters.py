from bson.objectid import ObjectId


__all__ = (
    'ModelConverter',
)


class ModelConverter:
    def __init__(self, model_class):
        self.model_class = model_class


    def parse(self, data, locale='en'):
        if type(data) == str:
            if data:
                try:
                    id = ObjectId(data.strip())
                except Exception:
                    raise ValueError
                return self.model_class.objects.get_or_404(id=id)
            else:
                return None
        elif type(data) == ObjectId:
            return self.model_class.objects.get_or_404(id=data)
        elif type(data) == self.model_class:
            return data
        elif data is None:
            return None
        else:
            raise TypeError


    def format(self, value, locale='en'):
        return '' if value is None else str(value.id)
