# Liste des Défis

Ce dossier regroupe la liste des défis de l'événement.

Veuillez diviser les défis selon leur catégorie dans des dossiers différents

## Liste des défis

### Catégorie

- [défi](./catégorie/lien_vers_le_défi)
- ...

Chaque défi doit inclure un fichier `description.yaml` structuré comme suit :

```yaml
est_ctfd: true # Si false, ne sera pas importé dans ctfd
titre: "titre du défi"
# Vous pouvez inscrire un string à plusieurs lignes comme ceci : 
# description: |
#   ligne 1
#   ligne 2
description: "Description du défi (supporte le markdown)"
drapeau: "flag du défi"
indices:
    - "indice1 (facultatif) (supporte le markdown)"
    - "indice2"
    - ...
solution: "solution"

necessite_un_traitement_special: false # Mettre à true si l'importation dans ctfd nécessite un traitement spécial
```