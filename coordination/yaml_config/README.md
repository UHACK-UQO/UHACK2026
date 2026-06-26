# yaml_config

Utilitaire de manipulation de configuration YAML.

## Définition de la configuration

Définissez un dictionnaire python sous la forme suivante :

```python
structure = {
    # Pour un paramètre
    "clé":{
        "est_obligatoire": True, # Définit si le paramètre doit être présent. Optionnel
        "description": "Description du paramètre"
        "defaut": "valeur" # Valeur par défaut. Son type en est dérivé.
        # Optionnel. Si présent, le paramètre est de type enum dont les
        # valeurs possibles sont celles définies ci-dessous
        "enum":[
            {
                "nom": "nom_du_paramètre",
                "description": "Description du paramètre"
            },
            {
                ...
            }
        ]
    }

    # Pour une section
    "section":{
        "est_obligatoire": True, # Optionnel
        "description": "Description de la section"
        # La section est définie par le type 'dictionnaire'
        "defaut": {
            # Définissez une sous-structure tel que décrit ci-dessus.
            "clé":{...},
            "clé2":{...}
        }
        # Les enums ne sont pas possibles pour une section
    }
}
```

## Fonctions fournies

### `creer_config_defaut(structure : dict, tabulation : int = 0) -> str`

Créée un fichier de configuration yaml par défaut à partir du dictionnaire de définission

S'appelle elle-même pour les sous-dictionnaires.

Args:

- `structure` (`dict`): Définission du fichier de configuration
- `tabulation` (`int`): Tabulation par défaut de cette configuration. Utilisé pour la récursivité

Renvoie:

- `str`: Fichier yaml généré

### `valider_config(config : dict, structure : dict, nom : str = None) -> list [str]`

Valide les paramètres de la configuration.

Fonction récursive qui valide le contenu du dictionnaire en fonction deson nom de paramètre.
Si le dictionnaire contient un autre dictionnaire, la fonction s'appèleelle-même avec le nom du paramètre.

Args:

- `config` (`dict`): Dictionnaire à valider.
- `strucutre` (`dict`) : Dictionnaire de définission de la configuration.
- `nom` (`str`, `optionel`): Nom du paramètre. None indique la racine de la config. `None` par défaut.

Renvoie:

- `list[str]`: Liste d'erreurs

