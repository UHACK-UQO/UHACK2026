#!/bin/python3
import mimetypes
import os
import re
import sys
import json

import requests
import yaml

sys.path.insert(0,"../coordination/yaml_config")
import yaml_config


def main():
    # gestion des paramètres

    if "--help" in sys.argv or "-h" in sys.argv or "-?" in sys.argv:
        print(message_aide)
        sys.exit()

    if "--defaut" in sys.argv or "-d" in sys.argv:
        argi = sys.argv.index("-d" if "-d" in sys.argv else "--defaut")
        rep = ""
        if len(sys.argv) == argi + 1 or sys.argv[argi + 1].startswith('-'):
            rep = "./config.yaml" 
        else:
            rep = sys.argv[argi + 1]

        with open(rep,"w") as f:
            f.write(yaml_config.creer_yaml_defaut(structure_config))
        sys.exit()

    if "--defis-infos" in sys.argv or "-i" in sys.argv:
        argi = sys.argv.index("-i" if "-i" in sys.argv else "--defis-infos")
        rep = ""
        if len(sys.argv) == argi + 1 or sys.argv[argi + 1].startswith('-'):
            rep = "./description.yaml" 
        else:
            rep = sys.argv[argi + 1]
        
        with open(rep,"w") as f:
            f.write(yaml_config.creer_yaml_defaut(structure_description_defis))
        sys.exit()

    if len(sys.argv) < 2:
        print("[ERREUR] Veuillez indiquer le répertoire du fichier de configuration")
        print(message_aide)
        sys.exit()
    
    rep_config = sys.argv[1]

    # Configuration de CTFd

    print("Configuration de CTFd.")

    config = lire_configuration(rep_config)
    temoin_session = configurer_ctfd(config)
    capi = obtenir_clee_api(config, temoin_session)

    defis = lire_defis(config["general"]["repertoire_defis"])
    configurer_defis(config, defis, capi)

    configurer_utilisateurs(config, capi)

def lire_configuration(rep_config : str) -> dict:
    """Lit de fichier de configuration et renvoie un dictionnaire contenant tous les paramètres.

    Args:
        rep_config (str): Répertoire du fichier de configuration

    Returns:
        dict: Représentation de la configuration
    """
    print("Lecture du fichier de configuration.")

    with open(rep_config,"r") as f :
        config = yaml.safe_load(f.read())
    
    # Validation

    erreurs = yaml_config.valider_structure(structure_config)
    if len(erreurs) > 0:
        print("Erreurs dans la définition de la configuration : ")
        for e in erreurs:
            print("\t"+e)
        return None

    erreurs = yaml_config.valider_config(config, structure_config)
    if len(erreurs) > 0:
        print("Erreurs dans la configuration : ")
        for e in erreurs:
            print("\t"+e)
        return None

    return yaml_config.normaliser_config(config, structure_config)

def configurer_ctfd(config : dict):
    # Cette étape n'est pas documentée dans l'API CTFd.
    # La page de configuration envoie un formulaire multi-part au serveur,
    #   contenant toutes les informations nécessaires. De plus, CTFd vérifie
    #   qu'un témoin de session est renvoyé et qu'un jeton csrf est présent
    #   dans le formulaire.
    # Voir : 
    #   Manuel de configuration CTFd : https://docs.ctfd.io/docs/settings/overview
    #   Options de configuration de ctfd-setup : https://github.com/ctfer-io/ctfd-setup/blob/main/config.go
    #   Documentation des jetons CSRF/témoins de session : https://github.com/CTFd/CTFd/issues/2816

    print("Configuration de la plateforme à l'adresse " + config["url"])

    rep = requests.get(config["url"] + "/setup")
    if "Set-Cookie" not in rep.headers.keys():
        print("[ERREUR] Il semblerait que CTFd soit déjà configuré, car le site n'a pas fournis de témoin de session.")
        return
        
    temoins = rep.headers["Set-Cookie"].split("; ")

    temoin_session = ""
    for t in temoins:
        if t.startswith("session="):
            temoin_session = t
            break

    jeton_csrf = re.search(r"'csrfNonce': \"([0-9a-f]*)\"",rep.content.decode("utf8")).group(1)
    
    # Traduction des valeurs des enums
    traductions = {
        "general.mode":{
            "equipes":"teams",
            "seuls":"users",
        },
        "general.creation_compte":{
            True:"public",
            False:"private"
        },
        "visibilite.defis":{
            "publiques":"public",
            "prives":"private",
            "admins":"admins"
        },
        "visibilite.scores":{
            "publiques":"public",
            "prives":"private",
            "caches":"hidden",
            "admin":"admins"
        },
        "visibilite.comptes":{
            "publiques":"public",
            "prives":"private",
            "admins":"admins"
        }
    }

    config_form = {
        "ctf_name":                 config["general"]   ["nom"],
        "ctf_description":          config["general"]   ["description"],
        "user_mode":                traductions["general.mode"][            config["general"]   ["mode"]],
        "challenge_visibility":     traductions["visibilite.defis"][        config["visibilite"]["defis"]],
        "account_visibility":       traductions["visibilite.comptes"][      config["visibilite"]["comptes"]],
        "score_visibility":         traductions["visibilite.scores"][       config["visibilite"]["scores"]],
        "registration_visibility":  traductions["general.creation_compte"][ config["general"]   ["creation_compte"]],
        "verify_emails": False,
        "team_size":                config["general"]   ["taille_equipes"],
        "name":                     config["admin"]     ["nom"],
        "email":                    config["admin"]     ["courriel"],
        "password":                 config["admin"]     ["mdp"],
        "ctf_theme":                config["apparence"] ["theme"],
        "theme_color":              config["apparence"] ["couleur"],
        "start":                    config["general"]   ["debut"],
        "end":                      config["general"]   ["fin"],
        "social_shares":            config["general"]   ["partage_sociaux"],
        "_submit": "Fin",
        "nonce": jeton_csrf
    }

    ctf_logo = (None, None, None)
    image_rep = config["apparence"]["logo"]
    if image_rep:
        if os.path.exists(image_rep):
            ctf_logo = (os.path.basename(image_rep), open(image_rep,"rb"), mimetypes.guess_type(image_rep)[0])  # noqa: SIM115
        else:
            print(f"[ERREUR] Le fichier {image_rep} n'est pas accessible ou n'existe pas.")

    ctf_banniere = (None, None, None)
    image_rep = config["apparence"]["banniere"]
    if image_rep:
        if os.path.exists(image_rep):
            ctf_banniere = (os.path.basename(image_rep), open(image_rep,"rb"), mimetypes.guess_type(image_rep)[0])  # noqa: SIM115
        else:
            print(f"[ERREUR] Le fichier {image_rep} n'est pas accessible ou n'existe pas.")

    ctf_icone = (None, None, None)
    image_rep = config["apparence"]["icone"]
    if image_rep:
        if os.path.exists(image_rep):
            ctf_icone = (os.path.basename(image_rep), open(image_rep,"rb"), mimetypes.guess_type(image_rep)[0])  # noqa: SIM115
        else:
            print(f"[ERREUR] Le fichier {image_rep} n'est pas accessible ou n'existe pas.")

    config_form_fichiers = {
        "ctf_logo": ctf_logo,
        "ctf_banner": ctf_banniere,
        "ctf_small_icon": ctf_icone,
    }

    rep = requests.post(
        url=config["url"] + "/setup", 
        data=config_form, 
        files=config_form_fichiers,
        headers={"Cookie":temoin_session}
        )
    
    if rep.status_code != 200:
        print(f"[ERREUR] CTFd a répondu avec un code d'erreur {rep.status_code}")
        print("Indice : Assurez-vous que ctfd (uid 1001) aie les droits d'écriture à son dossier de données.")
    
    print("CTFd configuré avec succès.")

    return temoin_session

def obtenir_clee_api(config : dict, temoin_session : str) -> str:
    """Obtient une clée API de CTFd

    Args:
        config (dict): configuration CTFd

    Returns:
        str: Clée API
    """

    print("Obtention de la clée API")

    rep = requests.get(
        url=config["url"]+"/settings",
        headers={"Cookie": temoin_session}
        )
    jeton_csrf = re.search(r"'csrfNonce': \"([0-9a-f]*)\"",rep.content.decode("utf8")).group(1)

    rep = requests.post(
        url=config["url"]+"/api/v1/tokens",
        json={"description":"Clée API de ctfd-config.py"},
        headers={"Cookie":temoin_session, "CSRF-Token":jeton_csrf}
    )

    if rep.status_code != 200:
        print(f"[ERREUR] : Le serveur a répondu avec un code d'erreur {rep.status_code}")
        return None

    print("Clée API obtenue avec succès.")
    
    return rep.json()["data"]["value"]

def lire_defis(rep : str) -> list[dict]:
    """ Lit la liste de défis du répertoire fournit et retourne une liste d'objets défis.

    Le répertoire doit avoir la structure suivante : 
    
    .
    |
    +-- Catégorie_1
    |   +-- Défis_1
    |   |   +-- description.yaml
    |   |   +-- ...
    |   |
    |   +-- Défis_2
    |   |   +-- description.yaml
    |   |   +-- ...
    |
    +-- Catégorie_2
    |   +-- Défis_3
    |   |   +-- description.yaml
    |   |   +-- ...
    ... ... 

    `descritption.yaml` doit avoir la structure suivante : 

    ```yaml
    est_ctfd: true # Si false, ne sera pas importé dans ctfd
    titre: "titre du défi"
    description: "Description du défi (supporte le markdown)"
    drapeau: "flag du défi"
    indices:
        - "indice1 (facultatif) (supporte le markdown)"
        - "indice2"
        - ...
    solution: "solution"
    necessite_un_traitement_special: false # Mettre à true si l'importation dans ctfd nécessite un traitement spécial
    ```

    Args:
        rep (str) : Répertoire du dossier contenant les défis
    
    Returns:
        list[dict] : Liste des objets défis
    """

    print("Lecture des défis.")

    erreurs = yaml_config.valider_structure(structure_description_defis)
    if len(erreurs) > 0:
        print("Erreurs dans la définition des descriptions des défis : ")
        for e in erreurs:
            print("\t"+e)
        return None

    if not os.path.exists(rep):
        print("[ERREUR] le répertoire des défis n'existe pas.")
        return
    if not os.path.isdir(rep):
        print("[ERREUR] le répertoire des défis n'est pas un dossier.")
        return

    defis = []

    for c in os.listdir(rep):
        if not os.path.isdir(rep + '/' + c):
            continue

        for d in os.listdir(rep + '/' + c):
            if not os.path.isdir(rep + '/' + c + '/' + d) or "description.yaml" not in os.listdir(rep + '/' + c + '/' + d):
                continue
            
            print("Défi : " + c + '/' + d)

            with open(rep + '/' + c + '/' + d + "/description.yaml", 'r') as f:
                desc_yaml = yaml.safe_load(f.read())
            
            erreurs = yaml_config.valider_config(desc_yaml, structure_description_defis)
            if len(erreurs) > 0:
                print("Erreurs dans la description du défi :")
                for e in erreurs:
                    print("\t"+e)
                continue
            
            desc = yaml_config.normaliser_config(desc_yaml, structure_description_defis)
            desc["categorie"] = c

            for i in range(len(desc["fichiers"])):
                desc["fichiers"][i] = os.path.abspath(rep + '/' + c + '/' + d + '/' + desc["fichiers"][i])

            defis.append(desc)
    
    return defis

def configurer_defis(config : dict, defis : list[dict], capi : str) -> None:
    """Téléverse les défis

    Args : 
        config (dict) : Configuration de CTFd
        defis (list[dict]) : Liste défis à téléverser
        capi (str) : Clée API de CTFd
    """

    print("Téléversement des défis")

    for d in defis:
        print(d["categorie"] + '/' + d["titre"])

        if not d["est_ctfd"]:
            print("\tSauté car non-ctfd.")
            continue

        defis_json = {
            "name": d["titre"],
            "category": d["categorie"],
            "description": d["description"]
        }

        if d["pointage"]["fonction"] == "constant":
            # TODO
            print("[ERREUR] Non implémenté")
        else:
            defis_json["type"] = "dynamic"
            defis_json["function"] = "linear" if d["pointage"]["fonction"] == "lineaire" else "logarithmic"
            defis_json["initial"] = d["pointage"]["initial"]
            defis_json["minimum"] = d["pointage"]["minimum"]
            defis_json["decay"] = d["pointage"]["decroissance"]
        
        rep = requests.post(
            url=config["url"]+"/api/v1/challenges",
            json=defis_json,
            headers={"Authorization":f"Token {capi}"}
        )

        if rep.status_code != 200:
            print(f"[ERREUR] : Le serveur a répondu avec un code d'erreur {rep.status_code}")
            
            if not rep.json():
                return
            
            for e in rep.json()["errors"]:
                print(f"\t{e}")
            return
        
        d["id"] = rep.json()["data"]["id"]

        print(f"\tTéléversé avec succés. ID : {d["id"]}")

        defis_json = {
            "challenge_id": d["id"],
            "content": d["drapeau"],
            "data": "",
            "type": "static"
        }

        rep = requests.post(
            url=config["url"] + "/api/v1/flags",
            json=defis_json,
            headers={"Authorization": f"Token {capi}"}
        )

        if rep.status_code != 200:
            print(f"[ERREUR] : Le serveur a répondu avec un code d'erreur {rep.status_code}")
            
            if not rep.json():
                return
            
            for e in rep.json()["errors"]:
                print(f"\t{e}")
            return
        
        print("\tDrapeau modifié")

        defis_form = {
            "challenge_id": d["id"],
            "type": "challenge"
        }

        for f in d["fichiers"]:
            if not os.path.exists(f) or not os.path.isfile(f):
                print(f"[ERREUR] : {f} est un dossier ou n'existe pas.")
                continue
                
            rep = requests.post(
                url=config["url"] + "/api/v1/files",
                data=defis_form,
                files={"file":(os.path.basename(f),open(f,"rb"),mimetypes.guess_type(f))},  # noqa: SIM115
                headers={"Authorization": f"Token {capi}"}
            )

            if rep.status_code != 200:
                print(f"[ERREUR] : Le serveur a répondu avec un code d'erreur {rep.status_code}")
                
                if rep.json():
                    for e in rep.json()["errors"]:
                        print(f"\t{e}")
            
        print("\tFichiers téléversés avec succès.")

    # TODO PATCH le reste des informations

def configurer_utilisateurs(config : dict, capi : str) -> None:
    print("Configuration des utilisateurs")

    fichier_utilisateurs = config["general"]["fichier_utilisateurs"]
    if not os.path.exists(fichier_utilisateurs) or not os.path.isfile(fichier_utilisateurs):
        print("[ERREUR] : Le répertoire vers le fichier des utilisateurs n'existe pas ou n'est pas un fichier.")
        return

    utilisateurs : dict = None
    with open(fichier_utilisateurs, "r") as f:
        utilisateurs = json.loads(f.read())
    
    if "utilisateurs" not in utilisateurs:
        print("[ERREUR] : Le fichier des utilisateurs doit contenir la clé 'utilisateurs'")
        return
    if "equipes_ctfd" not in utilisateurs:
        print("[ERREUR] : Le fichier des utilisateurs doit contenir la clé 'equipes_ctfd'")
        return
    if not isinstance(utilisateurs["utilisateurs"], list):
        print("[ERREUR] : La clé 'utilisateurs' doit être une liste d'objets")
        return
    if not isinstance(utilisateurs["equipes_ctfd"], list):
        print("[ERREUR] : La clé 'equipes_ctfd' doit être une liste d'objets")
        return
    
    for u in utilisateurs["utilisateurs"]:
        if "nom" not in u:
            print("[ERREUR] : Les utilisateurs doivent avoir une clé 'nom'")
            continue
        if "mdp" not in u:
            print(f"[ERREUR] : {u["nom"]} ne possède pas de 'mdp'")
            continue
    
        print(f"\t{u["nom"]}, {u["id"]}@{os.getenv("DOMAINE_GLOBAL","aucun_domaine.lan")} : ", end="")

        utilisateurs_json = {
            "name": u["nom"],
            "email": f"{u["id"]}@{os.getenv("DOMAINE_GLOBAL","aucun_domaine.lan")}",
            "password": u["mdp"],
            "type": "user",
            "verified": True,
            "hidden": False,
            "change_password": False,
            "banned": False,
            "fields": []
        }

        rep = requests.post(
            url=config["url"] + "/api/v1/users",
            json=utilisateurs_json,
            headers={"Authorization":f"Token {capi}"}
            )
        
        if rep.status_code != 200:
            print(f"[ERREUR] : Le serveur a répondu avec un code {rep.status_code}")
            for e in rep.json()["errors"]:
                print(f"\t\t{e}")
            continue
        
        u["ctfd_id"] = rep.json()["data"]["id"]
        print(f" id = {u["ctfd_id"]}")

    print("Configuration des équipes")
    for e in utilisateurs["equipes_ctfd"]:
        if not "nom" in e:
            print("[ERREUR] : Les équipes doivent avoir une clé 'nom'")
            continue
        if not "mdp" in e:
            print(f"[ERREUR] : L'équipe {e["nom"]} n'a pas de 'mdp'")
            continue
        if not "chef" in e:
            print(f"[ERREUR] : L'équipe {e["nom"]} n'a pas de 'chef'")
            continue
        if not "membres" in e or not isinstance(e["membres"], list):
            print(f"[ERREUR] : L'équipe {e["nom"]} n'a pas de 'membres' ou la clé n'est pas une liste")
            continue
        if len(e["membres"]) == 0 or len(e["membres"]) > 5:
            print(f"[ERREUR] : L'équipe {e["nom"]} n'a pas de membres ou a plus de 5 membres")
            continue

        print(f"\t{e["nom"]} : ", end="")

        # Trouver le chef d'équipe pour prendre son courriel
        u_chef : dict = None
        for u in utilisateurs["utilisateurs"]:
            if u["nom"] == e["chef"]:
                u_chef = u
                break
        if u_chef == None:
            print(f"[ERREUR] : Le chef {e["chef"]} n'existe pas")
            continue

        equipe_json = {
            "name": e["nom"],
            "password": e["mdp"],
            "email": f"{u_chef["id"]}@{os.getenv("DOMAINE_GLOBAL","aucun_domaine.lan")}",
            "hidden": False,
            "banned": False,
            "fields": []
        }

        rep = requests.post(
            url=config["url"] + "/api/v1/teams",
            json=equipe_json,
            headers={"Authorization":f"Token {capi}"}
        )

        if rep.status_code != 200:
            print(f"[ERREUR] : Le serveur a répondu avec le code d'erreur {rep.status_code}")
            for e in rep.json()["errors"]:
                print(f"\t\t{e}")
            continue

        id_equipe = rep.json()["data"]["id"]

        if e["chef"] not in e["membres"]:
            e["membres"].append(e["chef"])

        for m in e["membres"]:

            u_membre : dict = None
            if m != "chef":
                for u in utilisateurs["utilisateurs"]:
                    if u["nom"] == m:
                        u_membre = u
                        break
            else:
                u_membre = u_chef
            
            if u_membre == None:
                print(f"[ERREUR] : Le membre {m} n'existe pas")

            rep = requests.post(
                url=config["url"]+f"/api/v1/teams/{id_equipe}/members",
                json={"user_id":u_membre["ctfd_id"]},
                headers={"Authorization":f"Token {capi}"}
            )

            if rep.status_code != 200:
                print(f"[ERREUR] : Le serveur a répondu avec un code d'erreur {rep.status_code}")
                for er in rep.json()["errors"]:
                    print(f"\t\t{er}")

            rep = requests.patch(
                url=config["url"]+f"/api/v1/teams/{id_equipe}",
                json={"captain_id":u_chef["ctfd_id"]},
                headers={"Authorization":f"Token {capi}"}
            )

            if rep.status_code != 200:
                print(f"[ERREUR] : Le serveur a répondu avec un code d'erreur {rep.status_code}")
                for er in rep.json()["errors"]:
                    print(f"\t\t{er}")

        print("OK")

message_aide = """
USAGE ctfd-config <fichier-config>

    --help -h -?
        Présenter ce message

    --defaut -d [répertoire]
        Générer un fichier de configuration par défaut
    
    --defis-infos -i [répertoire]
        Générer un fichier de description de défis par défaut
"""

structure_config = {
    "url":{
        "est_obligatoire": True,
        "description": "URL de connection à la plateforme ctfd.",
        "defaut": "http://localhost:8000"
    },
    "admin":{
        "est_obligatoire": True,
        "description": "Paramètres du compte admin",
        "defaut":{
            "nom":{
                "est_obligatoire": True,
                "description": "Nom d'utilisateur",
                "defaut": "admin"
            },
            "courriel":{
                "est_obligatoire": True,
                "description": "Courriel de l'administrateur. Doit être un courriel valide, mais n'a pas besoin d'être une vrai adresse.",
                "defaut": "courriel@admin.tld"
            },
            "mdp": {
                "est_obligatoire": True,
                "description": "Mot de passe admin",
                "defaut": "0a3a865dc4d272a6a21617ef94e07c33903c382c6e18765b31709ef29b2c313d"
            }
        }
    },
    "general":{
        "est_obligatoire": True,
        "description": "Paramètres généraux du CTF",
        "defaut":{
            "nom":{
                "est_obligatoire": True,
                "description": "Nom de l'événement",
                "defaut": "Super CTF"
            },
            "description": {
                "description": "Description de l'événement",
                "defaut" : "Un super Capture The Flag, où les participants auront à résoudre des défis de cybersécurité pour gagner des points."
            },
            "mode": {
                "description": "Mode de jeu. Est-ce que les participants jouent en équipe ou seuls?",
                "defaut": "equipes",
                "enum":[
                    {
                        "nom":"equipes",
                        "description":"Les participants jouent en équipe"
                    },
                    {
                        "nom":"seuls",
                        "description": "Les participants jouent seuls"
                    }
                ]
            },
            "taille_equipes": {
                "description": "Taille des équipes. Ne doit être indiqué que si general.mode = 'equipes'",
                "defaut": 5
            },
            "creation_compte": {
                "description": "Permettre la création de compte?",
                "defaut": False,
                "enum":[
                    {
                        "nom": True,
                        "description": "Un nouvel utilisateur pourra se créer un compte pour participer à l'événement"
                    },
                    {
                        "nom": False,
                        "description": "Seuls les participants possédant un compte pourront participer à l'événement"
                    }
                ]
            },
            "fichier_utilisateurs": {
                "est_obligatoire": True,
                "Description": "Répertoire du fichier JSON listant les utilisateurs et leurs équipes.",
                "defaut": "../coordination/comptes_utilisateurs.json",
            },
            "debut":{
                "description": "Date d'ouverture de l'événement. Les participants n'auront pas accès à la plateforme avant cette date.\nFormat : Unix Epoch\n\tex. : 1781751060 = mer 17 jun 2026 22:51:00 EDT",
                "defaut": 1781751060
            },
            "fin":{
                "description": "Date de fermeture de l'événement. Les participants n'auront pas accès à la plateforme après cette date.\nFormat : Unix Epoch\n\tex. : 1781751060 = mer 17 jun 2026 22:51:00 EDT",
                "defaut": 1781751060
            },
            "partage_sociaux":{
                "description": "Les participants peuvent-ils partager les défis sur les réseaux sociaux?",
                "defaut": True
            },
            "repertoire_defis":{
                "est_obligatoire": True,
                "description": "Répertoire contenant les défis. Le répertoire doit contenir un dossier par catégorie et dans chacun, un dossier par défi, qui chacun contiennent un fichier `description.yaml`. Voir /defis/README.md",
                "defaut": "../defis/"
            }
        }
    },
    "apparence":{
        "description": "Apparence de CTFd",
        "defaut":{
            "logo":{
                "description": "Logo de l'événement. Doit être le répertoire de l'image",
                "defaut": "./logo.png"
            },
            "banniere":{
                "description": "Bannière de l'événement. Doit être le répertoire de l'image",
                "defaut": "./banniere.png"
            },
            "icone":{
                "description": "Icone de l'onglet du navigateur. Doit être le répertoire de l'image",
                "defaut": "./icone.png"
            },
            "theme":{
                "description": "Thème utilisé lors de l'événement. Doit être le nom du thème",
                "defaut": "core"
            },
            "couleur":{
                "description": "Couleur du thème de l'événement. Doit être un code hexadécimal RVB dans le format : #FFFFFF",
                "defaut": "#FF6615",
                "regex": r"^#([a-fA-F0-9]{3}|[a-fA-F0-9]{6})$"
            }
        }
    },
    "visibilite":{
        "description": "Paramètres de visibilité",
        "defaut": {
            "defis": {
                "description": "Visibilité des défis",
                "defaut": "publiques",
                "enum": [
                    {
                        "nom": "publiques",
                        "description": "Les défis sont visibles par tous, même les non-participants"
                    },
                    {
                        "nom": "prives",
                        "description": "Les défis ne sont visibles que par les participants authentifiés"
                    },
                    {
                        "nom": "admins",
                        "description": "Les défis ne sont visibles qu'aux admins"
                    }
                ],
            },
            "scores": {
                "description": "Visibilité des scores des participants/équipes",
                "defaut": "publiques",
                "enum": [
                    {
                        "nom": "publiques",
                        "description": "Les scores sont visibles par tous, même les non-participants"
                    },
                    {
                        "nom": "prives",
                        "description": "Les scores ne sont visibles que par les participants authentifiés"
                    },
                    {
                        "nom": "caches",
                        "description": "Les scores ne sont visibles qu'aux admins"
                    },
                    {
                        "nom": "admin",
                        "description": "Les scores ne sont visibles qu'aux admins et le tableau des scores sera caché"
                    }
                ]
            },
            "comptes": {
                "description": "Visibilité des informations de compte\n" \
                                "Ceci inclut, entre autres :\n" \
                                "  - Le nom\n" \
                                "  - L'équipe\n" \
                                "  - Le score\n" \
                                "  - Les défis résolus\n" \
                                "  - Le pourcentage de résolution\n" \
                                "  - etc...\n" \
                                "[ATTENTION]\n" \
                                "\tLa visibilité du compte devrait être en accord avec la visibilité du score pour éviter les conflits. Un conflit pourrait mener à des comportements inattendus, comme un score visible dans son profile, mais pas sur le tableau des résultats.",
                "defaut": "publiques",
                "enum": [
                    {
                        "nom": "publiques",
                        "description": "Les comptes sont visibles par tous, incluant les non-participants"
                    },
                    {
                        "nom": "prives",
                        "description": "Les comptes ne sont visibles que par les participants authentifiés"
                    },
                    {
                        "nom": "admins",
                        "description": "Les comptes ne sont visibles qu'aux admins"
                    }
                ]
            }
        }
    }
}

structure_description_defis = {
    "est_ctfd": {
        "est_obligatoire": True,
        "description": "Si false, ne sera pas importé dans ctfd.",
        "defaut": True
    },
    "titre": {
        "est_obligatoire": True,
        "description": "Titre du défi",
        "defaut": "Défi"
    },
    "description": {
        "est_obligatoire": True,
        "description": "Description du défi. Supporte le markdown",
        "defaut": "description",
    },
    "fichiers": {
        "description": "Liste de fichiers à téléverser",
        "defaut":[
            "..."
        ]
    },
    "drapeau": {
        "est_obligatoire": True,
        "description": "flag du défi",
        "defaut": "UHACK{adfjkvnalkerfjgbvqap}",
    },
    "indices": {
        "description": "Liste d'indices, en ordre d'apparence. Supporte le markdown.",
        "defaut": [
            "indice1",
            "indice2",
            "..."
        ]
    },
    "solution": {
        "est_obligatoire": True,
        "description": "Solution du défi. Supporte le markdown. Cet attribut est obligatoire.",
        "defaut": "Solution."
    },
    "pointage":{
        "description": "Paramètres du pointage pour ce défi. Le nombre de points diminue à mesure que de plus en plus de solutions sont soumises au défi.",
        "defaut": {
            "initial": {
                "description": "Nombre de points initial",
                "defaut": 100
            },
            "fonction": {
                "description": "Fonction de décroissance des points.",
                "defaut": "logarithmique",
                "enum":[
                    {
                        "nom": "constant",
                        "description": "Le nombre de points reste constant tout au long de l'événement. Avec cette option, les paramètres `pointage.minimum` et `pointage.decroissance` n'ont aucun effet."
                    },
                    {
                        "nom": "lineaire",
                        "description": "Le nombre de points diminue au même rythme en fonction du nombre de solutions soumises."
                    },
                    {
                        "nom": "logarithmique",
                        "description": "Le nombre de points chute drastiquement avec les premières soumissions et de plus en plus doucement avec les suivantes."
                    }
                ]
            },
            "minimum": {
                "description": "Nombre de points minimum. La décroissance ne passera pas en-dessous de ce niveau",
                "defaut": 10
            },
            "decroissance": {
                "description": "Taux de décroissance des points. Est interprété différemment dépendamment de `pointage.fonction`.",
                "defaut": 10
            }
        }
    },
    "etat":{
        "description": "Le défi est-il visible aux participants?",
        "defaut": "visible",
        "enum":[
            {
                "nom": "visible",
                "description": "Les participants peuvent voir le défis"
            },
            {
                "nom": "cache",
                "description": "Le défi est caché aux participants."
            }
        ]
    },
    "necessite_un_traitement_special": {
        "description": "Mettre à true si l'importation dans ctfd nécessite un traitement spécial",
        "defaut": False
    }
}

if __name__ == "__main__":
    main()