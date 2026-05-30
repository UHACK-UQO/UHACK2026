# CTFD

Ce dossier contient un serveur [ctfd](https://ctfd.io), une plateforme de CTFs.

## Déploiement

Exécutez `docker compose up` dans le dossier et connectez-vous sur `http://localhost:8000`

## Structure

Le service docker-compose est composé de trois images : ctfd, mysql et redis. Leurs données sont stockées dans leur dossier respectif dans `donnees/x`.