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

main() {
    if [ "$1" = "-i" ] || [ "$1" = "--installer" ]; then
        installer
        printf "actif" > ./installation_etat.txt
    elif [ "$1" = "-r" ] || [ "$1" = "--desinstaller" ]; then
        desinstaller
        printf "desinstalle" > ./installation_etat.txt
    elif [ "$1" = "-d" ] || [ "$1" = "--demarrer" ]; then
        demarrer
        printf "actif" > ./installation_etat.txt
    elif [ "$1" = "-a" ] || [ "$1" = "--arreter" ]; then
        arreter
        printf "inactif" > ./installation_etat.txt
    elif [ "$1" = "-h" ] || [ "$1" = "-?" ] || [ "$1" = "--help" ]; then
        echo "USAGE ctf <OPTION>"
        echo "  -i --installer      Installe et démarre le ctf. Si le ctf est déjà installe, le désinstalle, puis l'installe."
        echo "  -r --desinstaller   Désinstalle le ctf."
        echo "  -d --demarrer       Démarre le ctf s'il est déjà installé."
        echo "  -a --arreter        Arrête le ctf s'il est déjà installé."
    else 
        if [ -z "./installation_etat.txt" ]; then
            printf "desinstalle" > ./installation_etat.txt
        fi
# 
        etat=$(cat ./installation_etat.txt)
        if [ "$etat" = "desinstalle" ]; then
            installer
            printf "actif" > ./installation_etat.txt
        elif [ "$etat" = "actif" ]; then
            arreter
            printf "inactif" > ./installation_etat.txt
        elif [ "$etat" = "inactif" ]; then
            demarrer
            printf "actif" > ./installation_etat.txt
        else
            installer
            printf "actif" > ./installation_etat.txt
        fi
    fi
}

demarrer() {
    docker compose -f courriels/docker-compose.yaml up -d
    docker compose -f ctfd/docker-compose.yaml up -d
    docker compose -f infra-reseau/docker-compose.yaml up -d
    docker compose -f mastodon/docker-compose.yaml up -d
}

arreter() {
    docker compose -f courriels/docker-compose.yaml down
    docker compose -f ctfd/docker-compose.yaml down
    docker compose -f infra-reseau/docker-compose.yaml down
    docker compose -f mastodon/docker-compose.yaml down
}

desinstaller() {
    printf "\nDésinstallation du CTF\n\n"

    if [ $(systemctl status systemd-resolved > /dev/null ; echo $?) = 0 ]; then
        sed -i -E "s/^DNS=173.10.10.2$/#DNS=/gm" /etc/systemd/resolved.conf
        systemctl restart systemd-resolved
    else
        sed '0,/^nameserver=173.10.10.2$/{s///}' /etc/resolv.conf
    fi

    docker compose -f courriels/docker-compose.yaml down
    docker compose -f ctfd/docker-compose.yaml down
    docker compose -f infra-reseau/docker-compose.yaml down
    docker compose -f mastodon/docker-compose.yaml down
    docker network rm uhack_partage
    rm -rf courriels/data \
            courriels/dms \
            courriels/installation/est_installe.bool \
            ctfd/.venv \
            ctfd/donnees \
            ctfd/config_prod.yaml \
            infra-reseau/dnsmasq.conf \
            infra-reseau/nginx.conf \
            infra-reseau/defis.nginx.conf \
            infra-reseau/TLS/*.pem \
            mastodon/installation/*.bool \
            mastodon/installation/*.mdp \
            mastodon/postgres*/ \
            mastodon/public/ \
            mastodon/redis/ 
}

installer() {
    desinstaller

    printf '\nInstallation du CTF\n\n'

    printf "Veuillez indiquer le nom de domaine du CTF : "
    read DOMAINE

    printf "\nModification du nom de domaine.\n"
    sed -i -E "s/DOMAINE_GLOBAL=.*/DOMAINE_GLOBAL=${DOMAINE}/gm" coordination/nom_domaine.env
    sed -i -E "s/DOMAINE_GLOBAL=.*/DOMAINE_GLOBAL=${DOMAINE}/gm" courriels/.env
    sed -E "s/url: ?\"?((https?:\/\/)?[a-xA-Z0-9_-]+).*$/url: \"\1.${DOMAINE}\"/gm" ctfd/config.yaml > ctfd/config_prod.yaml
    sed -E "s/%DOMAINE_GLOBAL/${DOMAINE}/gm" infra-reseau/dnsmasq.exemple.conf > infra-reseau/dnsmasq.conf
    sed -i -E "s/DOMAINE_GLOBAL=.*/DOMAINE_GLOBAL=${DOMAINE}/gm" mastodon/.env.production
    sed "s/%DOMAINE_GLOBAL/${DOMAINE}/gm" infra-reseau/nginx.exemple.conf > infra-reseau/nginx.conf

    echo ""
    echo "Lancement de l'infra réseau."
    openssl req -config infra-reseau/TLS/openssl.cnf \
            -nodes -new -x509 \
            -keyout "infra-reseau/TLS/${DOMAINE}.key.pem" \
            -days 7300 -sha256 -extensions v3_ca \
            -out "infra-reseau/TLS/${DOMAINE}.cert.pem"

    cd infra-reseau
    DOMAINE_GLOBAL=${DOMAINE} python3 nginx-setup.py ../defis
    printf '\n===== Docker =====\n'
    docker compose up -d
    printf '===== Docker =====\n\n'
    cd ..
    if [ $(systemctl status systemd-resolved > /dev/null ; echo $?) = 0 ]; then
        config="$(grep -E "^#?DNS=.*$" /etc/systemd/resolved.conf | sed "s/ //gm")"
        if [ $config != "DNS=173.10.10.2" ] && [ $config != "DNS=" ] && [ $config != "#DNS=" ]; then
            echo "Pour pouvoir accéder au ctf, vous aurez besoin de rediriger vos requêtes DNS à travers les services du ctf."
            echo "Votre configuration sytemd-resolved comporte le serveur DNS suivant : ${config}"
            printf "Souhaitez-vous le remplacer par celui du ctf (173.10.10.2)? [O/n] : "
            read choix
            if [ "$choix" = "O" ] || [ "$choix" = "o" ]; then
                sed -i -E "s/^DNS=.*$/DNS=173.10.10.2/gm" /etc/systemd/resolved.conf
            else
                echo "Arrêt de l'installation"
                exit
            fi
        else
            sed -i -E "s/^#?DNS=.*$/DNS=173.10.10.2/gm" /etc/systemd/resolved.conf
        fi
        systemctl restart systemd-resolved > /dev/null
    else
        sed -i -E '0,/^nameserver=(.*)$/{s//namserver=173.10.10.2\nameserver=\1/}' /etc/resolv.conf
    fi

    echo ""
    echo "Installation du serveur SMTP."
    printf '\n===== Docker =====\n'
    docker compose -f courriels/docker-compose.yaml up -d
    printf '===== Docker =====\n\n'

    echo ""
    echo "Installation du serveur Mastodon."
    chown -R 991:911 mastodon/installation
    jq -c ".utilisateurs[]" coordination/comptes_utilisateurs.json | while read compte; do
        if [ "$(echo $compte | jq -r ".id")" = "admin" ]; then
            MDP_ADMIN_SMTP="$(echo $compte | jq -r ".mdp")"
        fi
    done
    sed -i -E "s/SMTP_PASSWORD=.*/$MDP_ADMIN_SMTP/gm" mastodon/.env.production
    printf '\n===== Docker =====\n'
    docker compose -f mastodon/docker-compose.yaml up -d
    printf '===== Docker =====\n\n'
    printf "En attente de l'installation de Mastodon"
    while [ "$(cat mastodon/installation/est_installe.bool 2> /dev/null || echo 'false')"  != "true" ]; do
        printf '.'
        sleep 1
    done

    echo ""
    echo "Installation de CTFd"
    printf '\n===== Docker =====\n'
    docker compose -f ctfd/docker-compose.yaml up -d
    printf '===== Docker =====\n\n'
    cd ctfd
    python3 -m venv .venv > /dev/null
    .venv/bin/python3 -m pip install -r requirements.txt > /dev/null
    chown -R 1001:1001 donnees/ctfd
    printf "En attente du lancement de CTFd"
    while [ $(curl -fk https://ctfd.${DOMAINE} &> /dev/null ; echo $?) != 0 ]; do
        sleep 1
        printf '.'
    done
    printf '\n'
    DOMAINE_GLOBAL=${DOMAINE} .venv/bin/python3 ctfd-config.py ./config_prod.yaml
    cd ..

    echo ""
    echo "Comptes utilisateurs : "
    jq -c ".utilisateurs[]" coordination/comptes_utilisateurs.json | while read compte; do
        nom="$(echo $compte | jq -r ".nom")"
        id="$(echo $compte | jq -r ".id")"
        mdp="$(echo $compte | jq -r ".mdp")"
        if [ "$id" = "admin" ]; then
            mdp_mstdn="$(echo "$(cat mastodon/installation/admin.mdp)" | grep -E 'New password: ' | sed -E 's/.+: (.+)/\1/gm')"
        else
            mdp_mstdn="$(echo "$(cat mastodon/installation/utilisateurs.mdp)" | grep -E "${id}: " | sed -E 's/.+: (.+)/\1/gm')"
        fi

        echo "${nom} :"
        echo "    Courriel : ${id}@${DOMAINE}"
        echo "         mdp : ${mdp}"
        echo "    Mastodon : @${id}@${DOMAINE}"
        echo "         mdp : ${mdp_mstdn}"
        echo "        CTFd : ${nom} (${id}@${DOMAINE})"
        echo "         mdp : ${mdp}"
    done
}

main "$@"