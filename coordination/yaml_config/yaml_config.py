def valider_config(config : dict, structure : dict, nom : str = "") -> list[str]:
    """Valide les paramètres de la configuration.

    Fonction récursive qui valide le contenu du dictionnaire en fonction de son nom de paramètre.
    Si le dictionnaire contient un autre dictionnaire, la fonction s'appèle elle-même avec le nom du paramètre.

    [ATTENTION] : Cette fonction présume que la configuration et la structure sont valides. 
    Veuillez utiliser `valider_config()` et `valider_structure()` respectivement avant
    d'utiliser cette fonction.

    Args:
        config (dict): Dictionnaire à valider.
        structure (dict): Dictionnaire de définission de la configuration
        nom (str): Nom de la section analysé. Est `""` par défaut pour la racine.

    Returns:
        list[str]: Liste d'erreurs
    """

    erreurs = []
    for k,v in config.items():
        if k not in structure.keys():
            erreurs.append(f"Le paramètre {nom}.{k} est invalide")
        if not isinstance(v, type(structure[k]["defaut"])):
            erreurs.append(f"Le paramètre {nom}.{k} doit être du type {type(structure[k]["defaut"])}, pas {type(k)}")
        if "enum" in structure.keys():
            valeurs = []
            for e in structure[k]["enum"]:
                valeurs.append(e["nom"])
            
            if v not in valeurs:
                erreurs.append(f"'{v}' n'est pas une valeur valide de {nom}.{k}. Valeurs acceptées : {valeurs}")
        
        if isinstance(v, dict):
            erreurs.extend(valider_config(v,structure[k]["defaut"], f"{nom}.{k}"))
    
    return erreurs

def valider_structure(structure : dict, nom : str="") -> list[str]:
    """Valide le formattage du dictionnaire de structure.

    Args:
        structure (dict): dictionnaire de définition de la structure
        nom (str) : nom du paramètre à valider. Utilisé pour la récursion.

    Returns:
        list[str]: liste d'erreurs
    """

    erreurs = []

    for k,v in structure.items():
        if not isinstance(v, dict):
            erreurs.append(f"{nom}.{k} doit être un dictionnaire.")
            continue
        if "description" not in v.keys():
            erreurs.append(f"{nom}.{k} doit contenir la clé 'description'.")
        elif not isinstance(v["description"], str):
            erreurs.append(f"{nom}.{k}.description doit être un 'str'.")
        
        if "defaut" not in v.keys():
            erreurs.append(f"{nom}.{k} doit contenir la clé 'defaut'.")
        elif not isinstance(v["defaut"], (str, int, float, bool, dict, list)):
            erreurs.append(f"{nom}.{k}.defaut doit être 'str', 'int', 'float', 'bool', 'list' ou 'dict', pas {type(v["defaut"])}")

        for vk in v.keys():
            if vk not in ["defaut","description","est_obligatoire","enum"]:
                erreurs.append(f"[{nom}.{k}] Le paramètre {vk} n'est pas supporté. Doit être 'defaut', 'description', 'est_obligatoire' ou 'enum'.")

        if "est_obligatoire" in v.keys() and not isinstance(v["est_obligatoire"], bool):
            erreurs.append(f"{nom}.{k}.est_obligatoire doit être de type 'bool', pas {type(v["est_obligatoire"])}")
        
        if "enum" in v.keys() and isinstance(v["defaut"], (dict, list)):
            erreurs.append(f"[{nom}.{k}] Les enums ne sont pas supportés avec les valeurs de type '{type(v["defaut"])}'.")
        elif "enum" in v.keys():
            if not isinstance(v["enum"], list):
                erreurs.append(f"{nom}.{k}.enum doit être de type 'list', pas {type(v["enum"])}")
            else:
                if len(v["enum"]) < 1:
                    erreurs.append(f"{nom}.{k}.enum doit avoir au moins une option.")

                i = -1
                for e in v["enum"]:
                    i += 1
                    if not isinstance(e, dict):
                        erreurs.append(f"{nom}.{k}.enum[{i}] doit être de type 'dict', pas {type(e)}")
                        continue
                    if "nom" not in e.keys():
                        erreurs.append(f"{nom}.{k}.enum[{i}] doit contenir le paramètre 'nom'.")
                    elif not isinstance(e["nom"], (str, int, float, bool, dict, list)):
                        erreurs.append(f"{nom}.{k}.enum[{i}].nom doit être de type  'str', 'int', 'float', 'bool', 'list' ou 'dict', pas {type(e["nom"])}")
                    
                    if "description" not in e.keys():
                        erreurs.append(f"{nom}.{k}.enum[{i}] doit contenir le paramètre 'description'.")
                    elif not isinstance(e["description"], str):
                        erreurs.append(f"{nom}.{k}.enum[{i}].description doit être de type  'str', pas {type(e["description"])}")

                    for ek in e.keys():
                        if ek not in ["description", "nom"]:
                            erreurs.append(f"[{nom}.{k}.enum[{i}]] Le paramètre {ek} n'est pas supporté.")
        
        if "defaut" in v.keys() and isinstance(v["defaut"], dict):
            valider_structure(v["defaut"], f"{k}.defaut")
    
    return erreurs

def normaliser_config(config : dict, structure : dict) -> dict:
    """Normalise la configuration : donne la valeur par défaut aux paramètres non-précisés

    [ATTENTION] : Cette fonction présume que la configuration et la structure sont valides. 
    Veuillez utiliser `valider_config()` et `valider_structure()` respectivement avant
    d'utiliser cette fonction.

    Args:
        config (dict): Dictionnaire de configuration
        structure (dict): Dictionnaire de définission de la configuration

    Returns:
        dict: Configuration normalisée
    """

    config_norm = {}

    for k,v in structure.items():
        if not isinstance(v["defaut"], dict):
            if k in config.keys():
                config_norm[k] = config[k]
            else:
                config_norm[k] = v["defaut"]
        else:
            if k in config:
                config_norm[k] = normaliser_config(config[k],v["defaut"])
            else:
                config_norm = normaliser_config({},v["defaut"])
    return config_norm

def creer_yaml_defaut(structure : dict, tabulation : int=0) -> str:
    """Créée un fichier de configuration yaml par défaut à partir du dictionnaire de définission

    S'appelle elle-même pour les sous-dictionnaires.

    [ATTENTION] : Cette fonction présume que la structure est valide. Veuillez utiliser
    `valider_structure()` avant d'utiliser cette fonction.

    Args:
        structure (dict): Définission du fichier de configuration
        tabulation (int): Tabulation par défaut de cette configuration. Utilisé pour la récursivité

    Returns:
        str: Fichier yaml généré
    """

    L_LIGNE_MAX = 50 # Longueur maximale d'une ligne

    fichier = ""
    for k,v in structure.items():
        commentaire_brut = v["description"]

        # Commentaire
        commentaire = "# "
        longueur_ligne = 0
        mot = ""
        n_tabulations = 0 # tabulations définies dans le commentaire
        n_c = 0
        for c in commentaire_brut:
            if c == '\n':
                longueur_ligne = 0
                n_tabulations = 0
                commentaire += mot + "\n# "+"  "*n_tabulations
                mot = ""
                n_c += 1
                continue
            if longueur_ligne == 0 and c == '\t':
                n_tabulations += 1
                commentaire += "  "
                n_c += 1
                continue
            if longueur_ligne == L_LIGNE_MAX - 2 - 2*tabulation - 2*n_tabulations:
                commentaire += "\n# "+"  "*n_tabulations
                longueur_ligne = len(mot)
            mot += c
            n_c += 1
            longueur_ligne += 1
            if c == ' ' or n_c == len(commentaire_brut):
                commentaire += mot
                mot = ""
        
        # Valeurs acceptées
        if "enum" in v:
            enum = "# Valeurs acceptées :"
            for e in v["enum"]:
                enum += "\n#   "+str(e["nom"])+" :\n"

                description_brute = e["description"]
                description = "#     "
                longueur_ligne = 0
                mot = ""
                n_tabulations = 0 # tabulations définies dans la description
                n_c = 0
                for c in description_brute:
                    if c == '\n':
                        longueur_ligne = 0
                        n_tabulations = 0
                        commentaire += mot + "\n#     "+"  "*n_tabulations
                        mot = ""
                        n_c += 1
                        continue
                    if longueur_ligne == 0 and c == '\t':
                        n_tabulations += 1
                        n_c += 1
                        continue
                    if longueur_ligne == L_LIGNE_MAX - 6 - 2*tabulation - 2*n_tabulations:
                        description += "\n#     "+"  "*n_tabulations
                        longueur_ligne = len(mot)
                    mot += c
                    n_c += 1
                    longueur_ligne += 1
                    if c == ' ' or n_c == len(description_brute):
                        description += mot
                        mot = ""

                enum += description
            commentaire += '\n' + enum

        # Est obligatoire
        if "est_obligatoire" in v and v["est_obligatoire"]:
            commentaire += "\n# [OBLIGATOIRE]"
        
        valeur = ""
        if isinstance(v["defaut"], dict):
            valeur_brute = creer_yaml_defaut(v["defaut"],tabulation=tabulation+1)
            valeur = str(k)+":\n  "
            for c in valeur_brute:
                valeur += c
                if c == '\n':
                    valeur += "  "
        else:
            valeur = str(k)+': ' + ('"' if isinstance(v["defaut"], str) else '') +str(v["defaut"]) + ('"' if isinstance(v["defaut"], str) else '')

        fichier += ("\n\n" if len(fichier) != 0 else "") + commentaire + '\n'
        fichier += valeur

    return fichier