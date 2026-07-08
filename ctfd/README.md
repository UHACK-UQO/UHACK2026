# CTFd

Ce dossier contient un serveur [CTFd](https://ctfd.io), une plateforme de CTFs, ainsi que ses outils de configuration et de déploiement.

## Déploiement

1. Exécutez `docker compose up` dans le dossier pour démarrer le service
2. Installez les dépendances avec `python3 -m pip install -r requirements.txt`
3. Configurez CTFd avec `python3 ctfd-config.py config.yaml`

## Structure

Le service docker-compose est composé de trois images : ctfd, mysql et redis. Leurs données sont stockées dans leur dossier respectif dans `donnees/x`.

Le script `ctfd-config.py` configure automatiquement CTFd à partir du fichier de configuration `config.yaml`.

Générez un fichier de configuration par défaut avec la commande `ptyhon3 ctfd-config.py --defaut`

## Documentation

### `ctfd-config.py`

> [!WARNING]
> La documentation suivante pourrait ne pas être à jour. Exécutez `python3 ctfd-config.py --help` pour vérifier la documentation la plus à jour.

```
USAGE ctfd-config <fichier-config>

    --help -h -?
        Présenter ce message

    --defaut -d [répertoire]
        Générer un fichier de configuration par défaut
```

### Fichier de configuration

> [!WARNING]
> La documentation suivante pourrait ne pas être à jour. Vérifiez les commentaires dans le fichier de configuration par défaut généré par `python3 ctfd-config.py --defaut` pour vérifier la documentation la plus à jour.

```yaml
# Paramètres du compte admin
# [OBLIGATOIRE]
admin:
  # Nom d'utilisateur
  # [OBLIGATOIRE]
  nom: "admin"
  
  # Courriel de l'administrateur. Doit être un 
  # courriel valide, mais n'a pas besoin d'être 
  # une vrai adresse.
  # [OBLIGATOIRE]
  courriel: "courriel@admin.tld"
  
  # Mot de passe admin
  # [OBLIGATOIRE]
  mdp: "0a3a865dc4d272a6a21617ef94e07c33903c382c6e18765b31709ef29b2c313d"

# Paramètres généraux du CTF
# [OBLIGATOIRE]
general:
  # Nom de l'événement
  # [OBLIGATOIRE]
  nom: "Super CTF"
  
  # Description de l'événement
  description: "Un super Capture The Flag, où les participants auront à résoudre des défis de cybersécurité pour gagner des points."
  
  # Mode de jeu. Est-ce que les participants 
  # jouent en équipe ou seuls?
  # Valeurs acceptées :
  #   equipes :
  #     Les participants jouent en équipe
  #   seuls :
  #     Les participants jouent seuls
  mode: "equipes"
  
  # Taille des équipes. Ne doit être indiqué que 
  # si general.mode = 'equipes'
  taille_equipes: 5
  
  # Permettre la création de compte?
  # Valeurs acceptées :
  #   True :
  #     Un nouvel utilisateur pourra se créer un 
  #     compte pour participer à l'événement
  #   False :
  #     Seuls les participants possédant un 
  #     compte pourront participer à l'événement
  creation_compte: False
  
  # Date d'ouverture de l'événement. Les 
  # participants n'auront pas accès à la 
  # plateforme avant cette date.
  # Format : Unix Epoch
  #   ex. : 1781751060 = mer 17 jun 2026 22:51:00 
  #   EDT
  debut: 1781751060
  
  # Date de fermeture de l'événement. Les 
  # participants n'auront pas accès à la 
  # plateforme après cette date.
  # Format : Unix Epoch
  #   ex. : 1781751060 = mer 17 jun 2026 22:51:00 
  #   EDT
  fin: 1781751060
  
  # Les participants peuvent-ils partager les 
  # défis sur les réseaux sociaux?
  partage_sociaux: True

# Apparence de CTFd
apparence:
  # Logo de l'événement. Doit être le répertoire 
  # de l'image
  logo: "./logo.png"
  
  # Bannière de l'événement. Doit être le 
  # répertoire de l'image
  banniere: "./banniere.png"
  
  # Icone de l'onglet du navigateur. Doit être le 
  # répertoire de l'image
  icone: "./icone.png"
  
  # Thème utilisé lors de l'événement. Doit être 
  # le nom du thème
  theme: "core"
  
  # Couleur du thème de l'événement. Doit être un 
  # code hexadécimal RVB dans le format : #FFFFFF
  couleur: "#FF6615"

# Paramètres de visibilité
visibilite:
  # Visibilité des défis
  # Valeurs acceptées :
  #   publiques :
  #     Les défis sont visibles par tous, même 
  #     les non-participants
  #   prives :
  #     Les défis ne sont visibles que par les 
  #     participants authentifiés
  #   admins :
  #     Les défis ne sont visibles qu'aux admins
  defis: "publiques"
  
  # Visibilité des scores des participants/équipes
  # Valeurs acceptées :
  #   publiques :
  #     Les scores sont visibles par tous, même 
  #     les non-participants
  #   prives :
  #     Les scores ne sont visibles que par les 
  #     participants authentifiés
  #   caches :
  #     Les scores ne sont visibles qu'aux admins
  #   admin :
  #     Les scores ne sont visibles qu'aux admins 
  #     et le tableau des scores sera caché
  scores: "publiques"
  
  # Visibilité des informations de compte
  # Ceci inclut, entre autres :
  #   - Le nom
  #   - L'équipe
  #   - Le score
  #   - Les défis résolus
  #   - Le pourcentage de résolution
  #   - etc...
  # [ATTENTION]
  #   La visibilité du compte devrait être en 
  #   accord avec la visibilité du score pour 
  #   éviter les conflits. Un conflit pourrait 
  #   mener à des comportements inattendus, comme 
  #   un score visible dans son profile, mais pas 
  #   sur le tableau des résultats.
  # Valeurs acceptées :
  #   publiques :
  #     Les comptes sont visibles par tous, 
  #     incluant les non-participants
  #   prives :
  #     Les comptes ne sont visibles que par les 
  #     participants authentifiés
  #   admins :
  #     Les comptes ne sont visibles qu'aux admins
  comptes: "publiques"
```

### API CTFd

L'API de la page de configuration initiale n'est pas documentée.

La page envoie un formulaire multi-part contenant toutes les informations nécessaires.

Les paramètres sont les suivants : 

- `ctf_name`
- `ctf_description`
- `user_mode`
- `challenge_visibility`
- `account_visibility`
- `score_visibility`
- `registration_visibility`
- `verify_emails`
- `team_size`
- `name` (nom admin)
- `email` (courriel admin)
- `password` (mdp admin)
- `ctf_theme`
- `theme_color`
- `start`
- `end`
- `social_shares`
- `_submit` = `"Fin"`
- `nonce` = `jeton_csrf`

Tous ces paramètres sont documentés [dans le manuel de configuration de CTFd](https://docs.ctfd.io/docs/settings/overview).

La syntaxe des paramètres peut être référencée à partir du travail de [ctfd-setup](https://github.com/ctfer-io/ctfd-setup/blob/main/config.go).

De plus, CTFd utilises un témoin de session et un jeton CSRF pour valider le formulaire renvoyé. Ces derniers sont [documentés ici](https://github.com/CTFd/CTFd/issues/2816).
