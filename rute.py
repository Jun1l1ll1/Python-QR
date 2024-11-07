
class Rute:
    def __init__(self):
        self._fylt = False
        self._paa = False

    def er_fylt(self):
        return self._fylt
    
    def er_paa(self):
        return self._paa
    
    def ikon(self):
        if not self._fylt:
            return '.'
        elif self._paa:
            return '■'
        return ' '
    
    def sett_fylt(self):
        self._fylt = True
    
    def sett_paa(self):
        self._paa = True
    
    def sett_av(self):
        self._paa = False
    
    def aktiver(self, paa=True):
        self._fylt = True
        self._paa = paa