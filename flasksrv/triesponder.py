from rozmowy_do_par import odpowiedz, make_trie, make_dict, get_data_from_fixed, sanitize


class Responder:

    def __init__(self, path='../../../messages'):
        self.data = get_data_from_fixed('../../../messages')
        self.rozne, self.moje = make_dict(self.data) 
        self.trie = make_trie(self.rozne)

    def answer(self, txt):
        return odpowiedz(self.trie, sanitize(txt), self.moje)

