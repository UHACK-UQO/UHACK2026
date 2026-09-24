# Hamming Code 15,11

with open("rancon.pdf.bin","rb") as f:
    document = f.read()

# Corriger la corruption
doc_saint : list[int] = []
for i in range(0,len(document),2):
    m = int.from_bytes([document[i], document[i+1]], byteorder='big')
    # px_r = rapporté, px_o = observé
    pp_r = (m & 0x8000) >> 15 # 10000000 00000000
    p1_r = (m & 0x4000) >> 14 # 01000000 00000000
    p2_r = (m & 0x2000) >> 13 # 00100000 00000000
    p3_r = (m & 0x0800) >> 11 # 00001000 00000000
    p4_r = (m & 0x0080) >> 7  # 00000000 10000000

    pp_o = p1_r ^ p2_r ^ p3_r ^ p4_r
    p1_o = ((m >> 12) ^ (m >> 10) ^ (m >> 8) ^ (m >> 6) ^ (m >> 4) ^ (m >> 2) ^ m) & 0x0001
    p2_o = ((m >> 12) ^ (m >> 9)  ^ (m >> 8) ^ (m >> 5) ^ (m >> 4) ^ (m >> 1) ^ m) & 0x0001
    p3_o = ((m >> 10) ^ (m >> 9)  ^ (m >> 8) ^ (m >> 3) ^ (m >> 2) ^ (m >> 1) ^ m) & 0x0001
    p4_o = ((m >> 6)  ^ (m >> 5)  ^ (m >> 4) ^ (m >> 3) ^ (m >> 2) ^ (m >> 1) ^ m) & 0x0001

    if pp_r != pp_o:
        if (p1_r ^ p1_o) + (p2_r ^ p2_o) + (p3_r ^ p3_o) + (p4_r + p4_o) > 1:
            print("[ERREUR] : Il y a trop de corruption. Impossible de récupérrer le message.")
            exit(-1)
        #else:
            #print("[ATTENTION] : Les bits de parités ont été affecté. Impossible de déterminer si le message est corrompu")
    else:
        # La combinaison des bits de parités affectés représente l'indexe du bit affecté
        j = ((p4_o ^ p4_r) << 3) | ((p3_o ^ p3_r) << 2) | ((p2_o ^ p2_r) << 1) | (p1_o ^ p1_r)
        m = m ^ (0x8000 >> j) # 10000000 00000000
    
    doc_saint.append(m >> 8)
    doc_saint.append(m & 0xFF)

# Retirer les bits de parité
doc_11 : list[int] = []
for i in range(0,len(doc_saint),2):
    m_16 = int.from_bytes([doc_saint[i], doc_saint[i+1]], byteorder='big')
    doc_11.append(
        (m_16 << 3) & 0x8000 | # 10000000 0000000
        (m_16 << 4) & 0x7000 | # 01110000 0000000
        (m_16 << 5) & 0x0FE0   # 00001111 1110000
    )

# Désérialiser les données
dec = 0
m_8 : int = 0
doc_8 : list[int] = []
for m_11 in doc_11:
    if dec <= 5:
        doc_8.append(m_8 | (m_11 >> (8 + dec)))
        m_8 = (m_11 >> dec) & 0xFF
        dec = dec+3
    else:
        doc_8.append(m_8 | (m_11 >> (8 + dec)))
        doc_8.append((m_11 >> dec) & 0xFF)
        m_8 = (m_11 << (8-dec)) & 0xFF
        dec = dec-5

with open("test.pdf","wb") as f:
    f.write(bytearray(doc_8))