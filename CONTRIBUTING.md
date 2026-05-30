# Contribution au projet

Ce document détaille les lignes directrices de contribution à l'infrastructure informatique du UHACK 2026

## Guide de structure

Le projet est divisé en plusieurs dossiers : 

- [`ctfd`](./ctfd/) contient le serveur ctfd
- [`défis`](./défis/) contient la liste des défis de l'événement
- [`mastodon`](./mastodon/) contient le serveur mastodon
- [`courriels`](./courriels/) contient un serveur smtp
- [`infra-réseau`](./infra-réseau/) contient les fichiers de configurations de l'infrastructure réseau
- [`llm`](./llm/) contient une plateforme de llm
- [`coordination`](./coordination/) contient les fichiers de coordination du déploiement de l'infrastucture (comme la définition de tous les comptes)
- [`site-web`](./site-web/) contient le site web d'accueil des participants
- [`docs`](./docs/) contient la documentation du projet

Chaque dossier contient un `README` détaillant son utilité

## Guide d'utilisation des branches git

Deux branches permanentes sont définies : 

- `main` contient la version finale de l'infrastructure. Idéalement elle devrait être une version qui fonctionne en tout temps. **AUCUNE MODIFICATION DIRECTE NE DOIT ÊTRE FAITE À LA BRANCHE MAIN!**
- `dev` contient la dernière version d'intégration des fonctionnalités en développement. Cette branche est instable et ne devrait être fusionnée avec `main` que lorsque qu'elle est jugée stable.

De plus, chaque fonctionnalitée en développement devrait recevoir sa propre branche et chaque développeur devrait se faire sa propre branche de travaille. Ces branches de travaille devraient rester locales et ne devraient pas être poussées sur le dépot principal. Il fusionnera ensuite ses modifications à la branche de la fonctionnalité sur laquelle il travaille, puis celle-ci sera fusionnée à la branche `dev` lorsqu'elle sera jugée prête.

La fusion d'une branche de fonctionnalité à la branche `dev` et la fusion de la branche `dev` à la branche `main` devraient se faire avec une demande de fusion (pull request).

## Guide des messages commits, demandes de fusions (pulls requests) et problèmes (issues)

Les messages de commits doivent résumer les changements effectués. Tentez de restreindre l'étendue des modifications afin de pouvoir rentrer la description de vos modifications à l'intérieur de une ou deux lignes.

Les titres des demandes de fusions et des problèmes doivent résumer leur contenu et être suffisament clairs et spécifiques pour être différenciés d'une autre demande / un autre problème.

Les demandes de fusions doivent décrire le raisonnement derrière les modifications ainsi que chaque modification effectuée dans le code.

Les problèmes doivent décrire :

- La nature spécifique du problème
- Le comportement attendu
- Les étapes de reproductions
- Une sauvegarde reproduisant le problème, s'il y a lieu

## Guide de style de programmation

### Langue

Toute contribution au projet, le code (noms de variables, de fonctions, de classes, etc...), la configuration (noms de macros et de variables), la documentation et les commentaires doit être faite exclusivement en français dans la mesure du possible. Les exceptions incluent, dans la mesure du raisonnable :

- les mots-clés des langages de programmation et des fichiers de configurations,
- les bibliothèques utilisées,
- du code emprunté d'ailleurs,
- des concepts sans traduction ou dont la traduction porte tellement à confusion qu'elle est contre-productive ( à confirmer avec le reste de l'équipe )

Le code doit être écrit sans accent, tandis que la documentation et les commentaires doivent être écrits avec accents.

Pour toute ambiguïté de traduction, veuillez vous référer à la [Banque de Dépannage Linguistique du Québec](https://vitrinelinguistique.oqlf.gouv.qc.ca/banque-de-depannage-linguistique)

#### Traductions supplémentaire

Les traductions suivantes ont été choisies pour traduire certains concepts :

- **Repository** (git) : Dépot [source](https://vitrinelinguistique.oqlf.gouv.qc.ca/fiche-gdt/fiche/26584236/depot-de-code-source)
- **Commit** (git) : Commit [source](https://github.com/git/git/blob/master/po/fr.po)
- **Issue** (github) : Problème [source](https://vitrinelinguistique.oqlf.gouv.qc.ca/fiche-gdt/fiche/26542750/systeme-de-suivi-de-problemes)

### Nommenclature

Les noms (noms de variables, fonctions, classes, macros, etc...) doivent décrire clairement leur nature et leur fonction. Ils doivent être composés d'au plus 5 mots et d'au plus 20 charactères. Une exception est faite pour les variables temporaires, créées et utilisées à quelques lignes d'intervalles : elles doivent idéalement être de une à trois lettres de long. Autrement, plus un nom est fréquemment utilisé, plus il doit être court.

### Style de nommenclature

À moins que spécifié autrement, les styles de nommenclatures doivent être comme suit :

- Pour les variable : la notation serpent (snake case), tout en minuscule. Ex. : la_notation_serpent
- Pour les constantes : la notation serpent (snake case), tout en majuscule. Ex. : LA_NOTATION_SERPENT
- Pour les fonctions : la notation chameau (camel case), commençant par une minuscule. Ex. : laNotationChameau
- Pour les objets (classes, structs, etc...) : la notation chameau (camel case), commençant par une majuscule. Ex. : LaNotationChameau