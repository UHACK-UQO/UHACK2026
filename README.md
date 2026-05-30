# UHACK2026

![Image promotionnelle](...)

Toutes les ressources et la plateforme du UHACK 2026

## Description de l'événement

Les participants, en équipe de 5, jouent dans un scénario de gestion de crise en cybersécurité. Les équipes incarnent des entreprises sous-traitantes et des départements fictifs d'une ville fictive dont la plateforme de gestion des plaintes citoyennes et des services municipaux est visée par une cyberattaque. Les scénarios visent des attaques sur les services routiers, d'aqueduc, d'électricité, de gestion des déchets de signalement citoyen, de communication citoyenne et de services d'urgence.

Les défis viennent en vagues en plus en plus difficiles et de natures différentes.

## Déploiement

***TODO***

## Structure du dépot

Ce répo comprend toutes les ressources nécessaires au déploiement de l'infrastucture informatique du UHACK 2026.

Il comprend nottamment :

- Un dossier de [défis](./défis/) contenant la liste des défis de l'événement.
- Un serveur [ctfd](https://ctfd.io/) pour gérer la partie geopadie de l'événement.
- Un serveur [mastodon](https://joinmastodon.org) pour émuler une plateforme de réseaux sociaux en temps réel comme twitter.
- Un serveur [smtp](./courriels/) pour émuler les communications courriels entreprise.
- Un dossier [d'infrastructure réseau](./infra-réseau) pour organiser les configurations réseau de l'événement.
- Un dossier contenant [une plateforme de llm](./llm/) pour inciter l'utilisation d'un LLM contrôlé pour favoriser l'apprentissage et non le remplacement des compétences.
- Un dossier [de coordination](./coordination/) pour coordonner le déploiement des différents services (comme la définition des différents comptes, etc...).
- Un dossier contenant le [site web](./site-web/) d'invitation à l'événement.
- Un dossier [de documentation](./docs/) pour documenter le tout.

## Contribution

Veuillez vous référer au document [CONTRIBUTING.md](./CONTRIBUTING.md) pour vous familiariser avec les lignes directrices de contribution au projet.