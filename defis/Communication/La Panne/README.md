```
+------+                                     +------+
| HTTP |                                     | HTTP |
+------+                                     +------+
   |  +-----+                           +-----+  |
   +--| TCP |                           | TCP |--+
      +-----+                           +-----+
         |  +----+                 +----+  |
         +--| IP |                 | IP |--+
            +----+                 +----+
              |  +------+   +------+  |
              +--| SFSS |-->| SFSS |--+
                 +------+ | +------+
                          |
+-------+-----+------+-------+---------+-------+
| SFSSH | IPH | TCPH | HTTPH | Données | SFSST |
+-------+-----+------+-------+---------+-------+
```

## 1 DONNÉES
```
> ["Message très urgent"] gzip
< ["UHACK{77711deeecde9ee1afde13c66751c66c}"] gzip
```

## 2 HTTP
```
> POST / HTTP/1.1\n
> Accept: text/plain\n
> Accept-Encoding: gzip\n
> Host: pontiac.texto.ca\n
> Content-Length: 50
> Content-Type: text/plain;charset=ASCII
< HTTP/1.1 200
< Server: pontiac-texto/0.2.1
< Date: Fri, 25 Sep 2026 03:49:23 GMT
< Content-Length: 50
< Content-Type: text/html;charset=ASCII
```

## 3 TCP
```
       0        1        2        3
   +--------+--------+--------+--------+
 0 | Source Port     | Destination Port|
 4 | Sequence Number                   |
 8 | Acknowledgement Number            |
12 | DO |RS | Flags  | Window          |
16 | Checksum        | Urgent Pointer  |
20 | Data
...                 ...
   +--------+--------+--------+--------+
```

- **Source Port & Destination Port** : serveur = 80
- **Sequence Number**
- **Acknowledgement Number**
- **Data Offset** : 5 (in 32-bit words)
- **Reserved** : 0
- **Flags** :
  - *Congestion Window Reduced* :0
  - *ECN-Echo* : 0
  - *Urgent* : 0
  - *Acknowledgement*
  - *Push Function* : 0
  - *Reset Connection*
  - *Synchronize sequence numbers*
  - *FIN* : Dernier Segment
- **Window** : 500
- **Checksum** : Le complément à un de la somme en complément à un en 16 bits de : 
  - Un pseudo-en-tête IP
    - Adresse Source (4o)
    - Adresse Destination (4o)
    - Zéros (1o)
    - Protocol=TCP (6) (1o)
    - TCP Length en octets (2o)
  - L'en-tête TCP
  - Les données
- **Urgent Pointer** : 0

## 4 IP
```
       0        1        2        3
   +--------+--------+--------+--------+
 0 |VS |IHL | ToS    | Total Length    |
 1 | Identification  |Flgs| Frag Off.  |
 2 | TTL    |Protocol| Header Checksum |
 3 | Source Address                    |
 4 | Destination Address               |
                 Données...                         
   +--------+--------+--------+--------+
```

- **Version** : 4
- **Internet Header Length** : 5
- **Type of Service** : 0
- **Total Length**
- **Identification**
- **Flags** :
  - 0
  - Peut Fragmenter?
  - Est dernier fragment?
- **Fragment Offset**
- **Time to Live** : 8
- **Protocol** : 6 (TCP)
- **Header Checksum**:  Le complément à un de la somme en complément à un des en-têtes, en 16 bits
- **Source Address et Destination Address** : serveur = 132.201.90.105

## 5 SFSS

```
   +--------+--------+--------+--------+--------+
 0 |_FST____|Protocol|CksumTyp| Frame Number    |
 4          |                                   |
 8          //              Données            //
12          |                                   |________¸
16          |                CRC                | FEN    |
20          +--------+--------+--------+--------+--------+
```

- **FST** : Q
- **Protocol** : 3 (IPv4, gzip-compressed)
- **Checksum Type** : 1 (CCIT CRC 16 (polynomial: x^16 + x^12 + x^5+1))
    ```python
    def ccit_crc16(donnees : int) -> int:
        # 1x^16 + 1x^12 + 1x^5 + 1
        # |       L--+    |      |
        # +------+   |    +-+    |
        #        |   |      |    |
        #        V   V      V    V
        poly = 0b10001000000100001
        # Ajouter un tampon de 16 bits à la fin où se
        #   trouvera le résultat
        donnees = donnees << 16
        # Aligner le coefficient avec le début du message
        poly = poly << len(donnees)-1
        d = len(donnees)-1

        # Calculer la checksum
        while len(poly) > 16:
            # Aligner le coefficient avec le premier 1
            #   restant du message.
            while poly & ( 1 << (d+16)) > donnees:
                poly >> 1
                d -= 1
            donnees ^= poly

        return donnees & 0xFFFF
    ```