# Code de Hamming 15,11

import random

# Lire le document
document : bytearray
with open("rancon.pdf","rb") as f:
    document = f.read() + b'\x00\x00'

# Extraire les mots de 11 bits
doc_11 : list[int] = [] # document en mots de 11 bits
dec = 0 # décalage de l'octet
sauter = False
for i in range(len(document)-2):
    if sauter:
        sauter = False
        continue

    # Deux scénarios possibles : 
    # dec = [0;5] : 
    #[A A A A A A A A|B B B B B B B B]C C C C C C C C
    # |-------------------| 0 0 0 0 0
    # +0
    #
    # A A A A A[A A A B B B B B|B B B C C C C C]C C C
    #        +5 |-------------------| 0 0 0 0 0
    # 
    # mot = (AA << d) | (BB >> (8-d)) , (BB & ( 0xFF << (5-d) )) << d
    #
    # dec = [6;7]
    # A A A A A A[A A B B B B B B|B B C C C C C C]C C
    #          +6 |-------------------| 0 0 0 0 0
    #
    # A A A A A A A[A B B B B B B B|B C C C C C C C]C
    #            +7 |-------------------| 0 0 0 0 0
    #
    # mot = (AA << d) | (BB >> (8-d)) , ( (BB << d) | (CC >> (8-d)) ) & (0xFF << (d-5)) & 0xFF

    if dec <= 5:
        doc_11.append( int.from_bytes(
            bytearray([
                ( ( document[i] << dec ) | ( document[i+1] >> (8-dec) ) ) & 0xFF,
                ( ( document[i+1] & (0xFF << (5-dec)) ) << dec ) & 0xFF
            ]),
            byteorder='big'
        ))
    else:
        doc_11.append( int.from_bytes(
            bytearray([
                ( ( document[i] << dec ) | ( document[i+1] >> (8-dec) ) ) & 0xFF,
                ( ( document[i+1] << dec ) | (document[i+2] >> (8-dec) )) & (0xFF << 5) & 0xFF
            ]),
            byteorder='big'
        ))

    if dec < 5:
        dec = 3+dec
    else:
        dec = dec-5
        sauter = True

# Créer les codes de Hammings
doc_16 : list[int] = []
for m_11 in doc_11:
    # Arrangement final : 
    #    pp p1 p2 d1 p3 d2 d3 d4 p4 d5 d6 d7 d8 d9 d10 d11
    # pp  x  x  x     x           x
    # p1     x     x     x     x     x     x     x       x
    # p2        x  x        x  x        x  x         x   x
    # p3              x  x  x  x              x  x   x   x
    # p4                          x  x  x  x  x  x   x   x
    
    # réarranger les bits
    m_16 = ( 
        ((m_11 & 0x0FE0) >> 5) | # 00001111 11100000 >> 5
        ((m_11 & 0x7000) >> 4) | # 01110000 00000000 >> 4
        ((m_11 & 0x8000) >> 3)   # 10000000 00000000 >> 3
        )
    
    # 01010101 01010101
    p1 = (((m_16 >> 12) ^ (m_16 >> 10) ^ (m_16 >> 8) ^ (m_16 >> 6) ^ (m_16 >> 4) ^ (m_16 >> 2) ^ m_16) & 0x0001) << 14
    # 00110011 00110011
    p2 = (((m_16 >> 12) ^ (m_16 >> 9)  ^ (m_16 >> 8) ^ (m_16 >> 5) ^ (m_16 >> 4) ^ (m_16 >> 1) ^ m_16) & 0x0001) << 13
    # 00001111 00001111
    p3 = (((m_16 >> 10) ^ (m_16 >> 9)  ^ (m_16 >> 8) ^ (m_16 >> 3) ^ (m_16 >> 2) ^ (m_16 >> 1) ^ m_16) & 0x0001) << 11
    # 00000000 11111111
    p4 = (((m_16 >> 6)  ^ (m_16 >> 5)  ^ (m_16 >> 4) ^ (m_16 >> 3) ^ (m_16 >> 2) ^ (m_16 >> 1) ^ m_16) & 0x0001) << 7
    # 01101000 10000000
    pp = (p1 << 1) ^ (p2 << 2) ^ (p3 << 4) ^ (p4 << 8)

    m_16 = m_16 | p1 | p2 | p3 | p4 | pp

    # Corruption
    m_16 = m_16 ^ (1 << random.randint(0,7))

    doc_16.append(m_16)

# Transformer en séquence d'octets
doc_8 : list[int] = []
for m_16 in doc_16:
    doc_8.append(m_16 >> 8)
    doc_8.append(m_16 & 0xFF)

doc_b = bytearray(doc_8)
with open("rancon.pdf.bin","wb") as f:
    f.write(doc_b)