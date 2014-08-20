from bson.objectid import ObjectId


class ObjectIdConverter:
    def parse(self, data, locale='en'):
        if type(data) == str:
            if data:
                try:
                    return ObjectId(data.strip())
                except:
                    raise ValueError
            else:
                return None
        elif type(data) == ObjectId:
            return data
        elif data is None:
            return data
        else:
            raise TypeError

    def format(self, value, locale='en'):
        return '' if value is None else str(value)


__all__ = [
    'ObjectIdConverter',
]