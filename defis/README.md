# Liste des Défis

Ce dossier regroupe la liste des défis de l'événement.

Veuillez diviser les défis selon leur catégorie dans des dossiers différents

## Liste des défis

### Catégorie

Les catégories correspondent aux phases de l'événement.

1. [Principal](./Principal)
2. [Employés](./Employés)
3. [Déchets](./Déchets)
4. [Communication](./Communication)
5. [Données cioyennes](./Données Citoyennes)
6. [Désinformation](./Désinformation)
7. [Eau](./Eau)
8. [Électricité](./Électricité)
9. [Services d'urgence](./Services d'Urgence)
10. [Réputation](./Réputation)
11. [Réseaux Sociaux](./Réseaux Sociaux)

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