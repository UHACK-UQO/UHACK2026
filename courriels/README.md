# Courriels

Ce dossier contient le serveur SMTP [Docker Mail Server](https://github.com/docker-mailserver/docker-mailserver) et client IMAP [Roundcube](https://github.com/roundcube/roundcubemail) sur docker pour simuler les communications internes par courriel.

## Déploiement

1. Modifiez le nom de domaine dans le fichier `.env`
2. Exécutez `docker compose up -d`

## Structure

Le fichier `.env` contient la configuration de base du serveur. Les comptes sont tirés de `/coordination/comptes_utilisateurs.json`.

Le dossier `installation/` contient un script de configuration automatique du serveur. Il installe le serveur, génère la configuration et ajoute tous les comptes utilisateurs.