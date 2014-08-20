class ModelConverter(object): # not optimized yet. N queries
    def __init__(self, query):
        self.query = query

    def parse(self, data, locale='en'):
        if type(data) == str:
            data = data.decode(encoding='utf-8')
        if type(data) == unicode:
            self.query._dirty = True
            return self.query.where(self.query.model_class.id == data).get()
        else:
            raise TypeError

    def format(self, value, locale='en'):
        return unicode(value.id)


__all__ = ['ModelConverter']