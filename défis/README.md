# Liste des Défis

Ce dossier regroupe la liste des défis de l'événement.

Veuillez diviser les défis selon leur catégorie dans des dossiers différents

## Liste des défis

### Catégorie

- [défi](./catégorie/lien_vers_le_défi)
- ...

Chaque défi doit inclure un fichier `description.json` structuré comme suit :

```json
{
    "est_ctfd":true, // Si false, ne serat pas importé dans ctfd et les autres attributs seront facultatifs
    "titre":"titre du défi",
    "description":"Description du défi (supporte le markdown)",
    "catégorie":"catégorie",
    "drapeau":"flag du défi",
    "indices":[
        "indice1 (facultatif) (supporte le markdown)",
        "indice2",
        ...
    ],
    "solution":"solution",
    "nécessite_un_traitement_spécial":false // Mettre à true si l'importation dans ctfd nécessite un traitement spécial
}
```