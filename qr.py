from collections import namedtuple as nt
from rute import Rute

class QR:
    def __init__(self, storrelse:int=33, maske:str='100'):
        self._storrelse = storrelse
        self._maske = maske
        self._rutenett = self._generer_tom_qr()

    
    def _generer_tom_qr(self):
        qr = self._generer_rutenett()
        self._legg_til_posisjonspunkter(qr)
        if self._storrelse > 21:
            self._legg_til_justeringspunkter(qr)
        self._legg_til_taiming_linjer(qr)
        self._legg_til_format(qr, 'L', self._maske, False)
        #TODO legg til versjonsinfo om qr er stor
        return qr

    
    def _generer_rutenett(self):
        rutenett = []
        for rad in range(self._storrelse):
            rutenett.append([Rute() for i in range(self._storrelse)])
        return rutenett


    def _legg_til_posisjonspunkter(self, rutenett:list[list]):
        moenster = [[0,0,0,0,0,0,0,0,0],
                    [0,1,1,1,1,1,1,1,0],
                    [0,1,0,0,0,0,0,1,0],
                    [0,1,0,1,1,1,0,1,0],
                    [0,1,0,1,1,1,0,1,0],
                    [0,1,0,1,1,1,0,1,0],
                    [0,1,0,0,0,0,0,1,0],
                    [0,1,1,1,1,1,1,1,0],
                    [0,0,0,0,0,0,0,0,0]]
        
        f_pos = nt('pos', ['x', 'y'])
        start_posisjoner = [f_pos(-1, -1), # Venstre topp
                            f_pos(self._storrelse-(len(moenster[0])-1), -1), # Høyre topp
                            f_pos(-1, self._storrelse-(len(moenster)-1))] # Venstre bunn
        
        for posisjon in start_posisjoner:

            for y in range(len(moenster)):
                for x in range(len(moenster[y])):
                    if (posisjon.x + x >= 0 and posisjon.x + x < self._storrelse) and (posisjon.y + y >= 0 and posisjon.y + y < self._storrelse):
                        rutenett[posisjon.y + y][posisjon.x + x].sett_fylt()
                        if moenster[y][x]:
                            rutenett[posisjon.y + y][posisjon.x + x].sett_paa()
    

    def _legg_til_justeringspunkter(self, rutenett:list[list]):
        moenster = [[1,1,1,1,1],
                    [1,0,0,0,1],
                    [1,0,1,0,1],
                    [1,0,0,0,1],
                    [1,1,1,1,1]]

        f_pos = nt('pos', ['x', 'y'])
        start_pos = f_pos(self._storrelse - len(moenster[0]) - 4, self._storrelse - len(moenster) - 4)

        for y in range(len(moenster)):
            for x in range(len(moenster[y])):
                rutenett[start_pos.y + y][start_pos.x + x].sett_fylt()
                if moenster[y][x]:
                    rutenett[start_pos.y + y][start_pos.x + x].sett_paa()
    

    def _legg_til_taiming_linjer(self, rutenett:list[list]):
        pos_inn = 6
        # Horisontal linje
        odde = True
        for rute in rutenett[pos_inn]:
            if rute.er_fylt():
                continue
            
            rute.sett_fylt()
            if odde:
                rute.sett_paa()

            odde = not odde
        
        # Vertikal linje
        odde = True
        for rad in rutenett:
            rute = rad[pos_inn]

            if rute.er_fylt():
                continue
            
            rute.sett_fylt()
            if odde:
                rute.sett_paa()

            odde = not odde
    

    def _legg_til_format(self, rutenett:list[list], EC_lvl:str='L', mask:str='100', maskeres=False):

        def maskere(bit, maske_pos, maskeres):
            XOR_maske = '101010000010010'
            if maskeres:
                if (bit and XOR_maske[maske_pos] == '1') or (not bit and not XOR_maske[maske_pos] == '1'):
                    return False
                return True
            return bit

        #* Error correction og mask
        #? Er nåværede med maske eller ikke? (skal fungere uten xor maske med disse bit-ene)
        if EC_lvl.upper() == 'L': 
            EC_bits = [1,1] #?01
        elif EC_lvl.upper() == 'M':
            EC_bits = [1,0] #?00
        elif EC_lvl.upper() == 'Q':
            EC_bits = [0,1] #?10 eller 11?
        else: # EC_lvl = 'H'
            EC_bits = [0,0] #?11 eller 10?

        mask_bits = list(mask)

        for i in range(5):
            rute = rutenett[8][i]
            if i < 2:
                rute.aktiver(maskere(EC_bits[i] == 1, i, maskeres))
            else:
                rute.aktiver(maskere(mask_bits[i-2] == '1', i, maskeres))
    
        for i in range(5):
            rute = rutenett[self._storrelse-1-i][8]
            if i < 2:
                rute.aktiver(maskere(EC_bits[i] == 1, i, maskeres))
            else:
                rute.aktiver(maskere(mask_bits[i-2] == '1', i, maskeres))
        
        #* Dark module
        rutenett[self._storrelse - 8][8].aktiver()

        #* Format error correction
        FEC = '1011110111' #TODO
        # Oppe til venstre
        rutenett[8][5].aktiver(maskere(FEC[0] == '1', 5, maskeres))
        rutenett[8][7].aktiver(maskere(FEC[1] == '1', 6, maskeres))
        rutenett[8][8].aktiver(maskere(FEC[2] == '1', 7, maskeres))
        rutenett[7][8].aktiver(maskere(FEC[3] == '1', 8, maskeres))

        for i in range(6):
            rutenett[5-i][8].aktiver(maskere(FEC[4+i] == '1', 9+1, maskeres))
        
        # Nede til venstre og oppe til høyre
        rutenett[self._storrelse-6][8].aktiver(maskere(FEC[0] == '1', 5, maskeres))
        rutenett[self._storrelse-7][8].aktiver(maskere(FEC[1] == '1', 6, maskeres))

        for i in range(8):
            rutenett[8][self._storrelse-8+i].aktiver(maskere(FEC[2+i] == '1',7+i, maskeres))

    
    
    def fyll(self, tekst:str, enc:str='0100'):
        bit_teller = 0
        retning = '^'
        
        f_pos = nt('pos', ['x', 'y'])
        pos = f_pos(self._storrelse-1, self._storrelse-1)
        
        #* Encode type del
        bit_teller, pos, retning = self._legg_til_bits(enc, self._rutenett, pos, retning, bit_teller)
        
        #* Lengde del
        bits_len = bin(len(tekst))[2:]
        byte_len = ''
        for i in range(8-len(bits_len)):
            byte_len += '0'
        byte_len += bits_len

        bit_teller, pos, retning = self._legg_til_bits(byte_len, self._rutenett, pos, retning, bit_teller)
        
        #* Tekst del
        for kar in tekst:
            bits_kar = bin(ord(kar))[2:]
            byte_kar = ''
            for i in range(8-len(bits_kar)):
                byte_kar += '0'
            byte_kar += bits_kar

            bit_teller, pos, retning = self._legg_til_bits(byte_kar, self._rutenett, pos, retning, bit_teller)

        #* Slutt
        bit_teller, pos, retning = self._legg_til_bits('0000', self._rutenett, pos, retning, bit_teller)

    
    def _legg_til_bits(self, bits:str, qr:list[list], pos, retning:str, bit_teller:int):
        for bit in bits:
            qr[pos.y][pos.x].sett_fylt()
            add_bit = int(bit)

            if self._skal_inverteres(pos.x, pos.y):
                add_bit = not add_bit

            if add_bit:
                qr[pos.y][pos.x].sett_paa()

            bit_teller += 1
            bit_teller, pos, retning = self._neste_pos(qr, pos, retning, bit_teller)

        return bit_teller, pos, retning


    def _skal_inverteres(self, x:int, y:int):
        if self._maske == '111':
            return x % 3 == 0
        elif self._maske == '110':
            return (y + x) % 3 == 0
        elif self._maske == '101':
            return (y + x) % 2 == 0
        elif self._maske == '100':
            return y % 2 == 0
        elif self._maske == '011':
            return ((y*x)%3 + y*x) % 2 == 0
        elif self._maske == '010':
            return ((y*x)%3 + y + x) % 2 == 0
        elif self._maske == '001':
            return (y/2 + x/3) % 2 == 0
        elif self._maske == '000':
            return (y*x)%2 + (y*x)%3 == 0
    

    def _neste_pos(self, qr:list[list], forrige_pos, retning:str, bit_teller:int): #forrige_pos er f_pos, bit_teller er hver posisjon i sik sak (starter på 0) - holder styr på hva som er høyre i byte-blobben
        f_pos = nt('pos', ['x', 'y'])

        if retning == '^':
            endring_y = -1
        elif retning == 'v':
            endring_y = 1
        else:
            assert False, 'Feil retningsinput'

        if bit_teller%2 == 1:
            return bit_teller, f_pos(forrige_pos.x - 1, forrige_pos.y), retning
        
        neste_pos = f_pos(forrige_pos.x + 1, forrige_pos.y + endring_y)
        if neste_pos.x < 0 or neste_pos.x >= self._storrelse or neste_pos.y < 0 or neste_pos.y >= self._storrelse:
            if retning == '^':
                retning = 'v'
            else:
                retning = '^'
            neste_pos = f_pos(forrige_pos.x - 1, forrige_pos.y)

        # if qr[neste_pos.y][neste_pos.x].er_fylt():
        #     return self._neste_pos(qr, neste_pos, retning, bit_teller+1)
        while qr[neste_pos.y][neste_pos.x].er_fylt():
            bit_teller, neste_pos, retning = self._neste_pos(qr, neste_pos, retning, bit_teller+1)
        
        return bit_teller, neste_pos, retning
    

    def print(self):
        print('\n\n')
        for rad in self._rutenett:
            for e in rad:
                print(e.ikon(), end=' ')
            print()
        print('\n\n')
