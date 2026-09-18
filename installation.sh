#!/bin/bash

if [ "$EUID" -ne 0 ]; then
    echo "Ce script nécessite des privilèges de superutilisateur."
    exit
fi

NOIR="\e[0;30m"
ROUGE="\e[0;31m"
VERT="\e[0;32m"
JAUNE="\e[0;33m"
BLEU="\e[0;34m"
MAUVE="\e[0;35m"
CYAN="\e[0;36m"
BLANC="\e[0;37m"
NEUTRE="\e[0m"

printf "Veuillez indiquer le nom de domaine du CTF : "
read DOMAINE

echo "Modification du nom de domaine."
sed -iE "s/DOMAINE_GLOBAL=.*/DOMAINE_GLOBAL=${DOMAINE}/gm" coordination/nom_domaine.env
sed -iE "s/DOMAINE_GLOBAL=.*/DOMAINE_GLOBAL=${DOMAINE}/gm" courriels/.env
sed -E 's/url:( ?"?\(https?:\/\/\)?[a-xA-Z0-9_-]+)\.[a-xA-Z0-9_-]+\.[a-xA-Z0-9_-]+/url:\1.${DOMAINE}/gm' ctfd/config.yaml > ctfd/config_prod.yaml
sed -E "s/%DOMAINE_GLOBAL/${DOMAINE}/gm" infra-reseau/dnsmasq.exemple.conf > infra-reseau/dnsmasq.conf
sed -iE "s/DOMAINE_GLOBAL=.*/DOMAINE_GLOBAL=${DOMAINE}/gm" mastodon/.env.production

echo "Lancement de l'infra réseau."
if [ -z "$(docker network ls | grep uhack_partage)" ]; then
    docker network create uhack_partage --subnet 172.16.10.0/24
fi
docker compose -f infra-reseau/docker-compose.yaml -d

echo "Installation du serveur SMTP."
docker compose up -f courriels/docker-compose.yaml -d

echo "Installation du serveur Mastodon."
chown -R 991:911 mastodon/installation
jq -c ".utilisateurs[]" coordination/comptes_utilisateurs.json | while read compte; do
    if [ "$(echo $compte | jq -r ".id")" = "admin" ]; then
        MDP_ADMIN_SMTP="$(echo $compte | jq -r ".mdp")"
    fi
done
sed -iE "s/SMTP_PASSWORD=.*/$MDP_ADMIN_SMTP/gm" mastodon/.env.production
docker compose up -f mastodon/docker-compose.yaml -d

echo "Installation de CTFd"
docker compose up -f ctfd/docker-compose.yaml -d

echo "Comptes utilisateurs : "
jq -c ".utilisateurs[]" coordination/comptes_utilisateurs.json | while read compte; do
    nom="$(echo compte | jq -r ".nom")"
    id="$(echo compte | jq -r ".id")"
    mdp="$(echo compte | jq -r ".mdp")"
    mdp_mstdn="$(grep -E "${id}: " | sed -E "s/.+: (.+)/\1/gm")"

    echo "${nom} :"
    echo "    Courriel : ${id}@${DOMAINE_GLOBAL}"
    echo "         mdp : ${mdp}"
    echo "    Mastodon : @${id}@{DOMAINE_GLOBAL}"
    echo "         mdp : ${mdp_mstdn}"
    echo "    CTFd : ${nom} (${id}@${DOMAINE_GLOBAL})"
    echo "     mdp : ${mdp}"
done