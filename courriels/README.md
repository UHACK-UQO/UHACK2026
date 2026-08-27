# Courriels

Ce dossier contient le serveur et client STMP [mox](https://github.com/mlj-/mox) sur docker pour simuler les communications internes par courriel.

## Déploiement

1. Modifiez les paramètres tels que le domaine et le mot de passe administrateur dans le fichier `.env`
2. Exécutez `docker compose up -d`

## Structure

Le fichier `.env` contient la configuration de base du serveur. Les comptes sont tirés de `/coordination/comptes_utilisateurs.json`.

Le dossier `installation/` contient un script de configuration automatique du serveur. Il installe le serveur, génère la configuration et ajoute tous les comptes utilisateurs.

Le fichier `mox.conf.template` est utilisé par le script de configuration. Il copie la section `Listeners:` (sauf `HostPrivateKeyFiles:`) dans la configuration de production. Veuillez vous familiariser avec `installation/installation.sh` avant de modifier le fichier de configuration.