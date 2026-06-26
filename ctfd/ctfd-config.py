#!/bin/python3
import requests
import re
import yaml
import sys
import os
import mimetypes

sys.path.insert(0,"../../coordination/yaml_config")
import yaml_config

def main():
    
    if "--help" in sys.argv or "-h" in sys.argv or "-?" in sys.argv:
        print(message_aide)
        exit()

    if "--defaut" in sys.argv or "-d" in sys.argv:
        rep = sys.argv[sys.argv.index("-d" if "-d" in sys.argv else "--default") + 1]
        if rep.startswith("-"):
            rep = "./config.json"

        with open(rep,"w") as f:
            f.write(yaml_config.creer_yaml_defaut(structure_config))
        exit()

    if len(sys.argv) < 2:
        print("[ERREUR] Veuillez indiquer le répertoire du fichier de configuration")
        print(message_aide)
        exit()
    
    rep_config = sys.argv[1]

    config = lire_configuration(rep_config)
    configurer_ctfd(config)

def lire_configuration(rep_config : str) -> dict:
    """Lit de fichier de configuration et renvoie un dictionnaire contenant tous les paramètres.

    Args:
        rep_config (str): Répertoire du fichier de configuration

    Returns:
        dict: Représentation de la configuration
    """
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
    rep = requests.get("http://localhost:8000/setup")
    print(rep)
    if "Set-Cookie" not in rep.headers.keys():
        print("[ERREUR] Il semblerait que CTFd soit déjà configuré, car le site n'a pas fournis de témoin de session.")
        
    témoins = rep.headers["Set-Cookie"].split("; ")

    témoin_session = ""
    for t in témoins:
        if t.startswith("session="):
            témoin_session = t
            break

    print(témoin_session)

    jeton_csrf = re.search(r"'csrfNonce': \"([0-9a-f]*)\"",rep.content.decode("utf8")).group(1)
    print(jeton_csrf)

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
    if config["apparence"]["logo"]:
        if os.path.exists(config["apparence"]["logo"]):
            ctf_logo = (os.path.basename(config["apparence"]["logo"]), open(config["apparence"]["logo"]), mimetypes.guess_type(config["apparence"]["logo"]))
        else:
            print(f"[ERREUR] Le fichier {config["apparence"]["logo"]} n'est pas accessible ou n'existe pas.")

    ctf_banniere = (None, None, None)
    if config["apparence"]["banniere"]:
        if os.path.exists(config["apparence"]["banniere"]):
            ctf_banniere = (os.path.basename(config["apparence"]["banniere"]), open(config["apparence"]["banniere"]), mimetypes.guess_type(config["apparence"]["banniere"]))
        else:
            print(f"[ERREUR] Le fichier {config["apparence"]["banniere"]} n'est pas accessible ou n'existe pas.")

    ctf_icone = (None, None, None)
    if config["apparence"]["icone"]:
        if os.path.exists(config["apparence"]["icone"]):
            ctf_icone = (os.path.basename(config["apparence"]["icone"]), open(config["apparence"]["icone"]), mimetypes.guess_type(config["apparence"]["icone"]))
        else:
            print(f"[ERREUR] Le fichier {config["apparence"]["icone"]} n'est pas accessible ou n'existe pas.")

    config_form_fichiers = {
        "ctf_logo": ctf_logo,
        "ctf_banner": ctf_banniere,
        "ctf_small_icon": ctf_icone,
    }

    rep = requests.post(
        url="http://localhost:8000/setup", 
        data=config_form, 
        files=config_form_fichiers,
        headers={"Cookie":témoin_session}
        )
    
    if rep.status_code != 200:
        print(f"[ERREUR] CTFd a répondu avec un code d'erreur {rep.status_code}")

message_aide = """
USAGE ctfd-config <fichier-config>

    --help -h -?
        Présenter ce message

    --defaut -d [répertoire]
        Générer un fichier de configuration par défaut
"""

structure_config = {
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
                "defaut": "./logo.png"
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

main()