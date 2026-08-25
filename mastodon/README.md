# Serveur Mastodon

Cette instance de mastodon servira à simuler une réponse de crise par les réseaux sociaux instantanés comme twitter.

## Déploiement

1. Exécutez `chown -R 991:991 installation`
2. Exécutez `docker compose up -d`
3. Le mot de passe du compte admin se trouvera dans `installation/admin.mdp`

## Structure

Le service docker-compose est un dérivé du [service officiel](https://github.com/mastodon/mastodon/blob/main/docker-compose.yaml) fournit par Mastodon, auquel est ajouté un service nginx.
Le dossier `installation/` contient un script d'installation automatique de Mastodon et le mot de passe du compte admin s'y trouvera.