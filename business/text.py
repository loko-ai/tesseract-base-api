
class JoinerFactory:

    def __init__(self, mapping=None):
        self.mapping = mapping or dict()

    def __call__(self, key):
        for el in self.mapping:
            if el in key:
                return self.mapping[el]

class Joiner:

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, texts):
        raise Exception("not implemented")


class TextJoiner(Joiner):

    def __init__(self, join_str=None):
        self.join_str = join_str or "\n"

    def __call__(self, texts):
        return self.join_str.join(texts)

class JSONTextJoiner(Joiner):

    def __call__(self, texts):
        d = dict()
        for i,text in enumerate(texts):
            d[str(i)] = text
        return d

JOINER_FACTORY = JoinerFactory(dict(text=TextJoiner, json=JSONTextJoiner))


if __name__ == '__main__':


    texts = [ "ciao", "buongiorno", "hola"]

    tj = JOINER_FACTORY("text")()
    jtj = JOINER_FACTORY("json")()

    print(tj(texts))
    print(jtj(texts))