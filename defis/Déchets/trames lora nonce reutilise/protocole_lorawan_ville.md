# Protocole de report des capteurs de bennes (ville — v3.2)

Les capteurs de remplissage remontent leurs mesures en LoRaWAN vers la
passerelle municipale, qui ré-émet les payloads sur le bus interne.

## Format des trames en clair (ports applicatifs)

- **Port 2 — heartbeat périodique** (toutes les 300 s) :

  ```
  HB;benne=<identifiant>;niveau=<0-100>;pile=<0-100>;ts=<ISO8601>;commentaire=<texte>
  ```

  Exemple réel capturé en maintenance (le champ `commentaire`, rempli par le
  technicien de garde, peut être long) :

  ```
  HB;benne=B-014;niveau=63;pile=81;ts=2026-09-24T03:12:07Z;commentaire=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  ```

- **Port 3 — réservé** : non documenté publiquement. La DSI soupçonne que
  les attaquants l'utilisent pour leurs ordres.

## Chiffrement

Les payloads applicatifs sont chiffrées en **AES-CTR 128 bits** avec la clé
de session de la passerelle. Le compteur CTR est initialisé avec le nonce
joint à la trame. La passerelle journalise, pour chaque trame : l'heure de
réception, le port et le ciphertext en hexadécimal.
