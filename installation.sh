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

infra_ip="$(jq -r '."infra-reseau".ip' infra-reseau/machines_services.json)"
infra_usr="$(jq -r '."infra-reseau".usr' infra-reseau/machines_services.json)"
infra_mdp="$(jq -r '."infra-reseau".mdp' infra-reseau/machines_services.json)"
infra_local="$(jq -r '."infra-reseau".local' infra-reseau/machines_services.json)"

courriels_ip="$(jq -r '.courriels.ip' infra-reseau/machines_services.json)"
courriels_usr="$(jq -r '.courriels.usr' infra-reseau/machines_services.json)"
courriels_mdp="$(jq -r '.courriels.mdp' infra-reseau/machines_services.json)"
courriels_local="$(jq -r '.courriels.local' infra-reseau/machines_services.json)"

ctfd_ip="$(jq -r '.ctfd.ip' infra-reseau/machines_services.json)"
ctfd_usr="$(jq -r '.ctfd.usr' infra-reseau/machines_services.json)"
ctfd_mdp="$(jq -r '.ctfd.mdp' infra-reseau/machines_services.json)"
ctfd_local="$(jq -r '.ctfd.local' infra-reseau/machines_services.json)"

defis_ip="$(jq -r '.defis.ip' infra-reseau/machines_services.json)"
defis_usr="$(jq -r '.defis.usr' infra-reseau/machines_services.json)"
defis_mdp="$(jq -r '.defis.mdp' infra-reseau/machines_services.json)"
defis_local="$(jq -r '.defis.local' infra-reseau/machines_services.json)"

mastodon_ip="$(jq -r '.mastodon.ip' infra-reseau/machines_services.json)"
mastodon_usr="$(jq -r '.mastodon.usr' infra-reseau/machines_services.json)"
mastodon_mdp="$(jq -r '.mastodon.mdp' infra-reseau/machines_services.json)"
mastodon_local="$(jq -r '.mastodon.local' infra-reseau/machines_services.json)"

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
        sed -i -E "s/^DNS=\$infra_ip$/#DNS=/gm" /etc/systemd/resolved.conf
        systemctl restart systemd-resolved
    else
        sed '0,/^nameserver=\$infra_ip$/{s///}' /etc/resolv.conf
    fi


    if [ "$courriels_local" = "true" ]; then
        docker compose -f courriels/docker-compose.yaml down
    else
        ssh -o StrictHostKeyChecking=no "$courriels_usr@$courriels_ip" docker compose -f courriels/docker-compose.yaml down
    fi

    if [ "$ctfd_local" = "true" ]; then
        docker compose -f ctfd/docker-compose.yaml down
    else
        ssh -o StrictHostKeyChecking=no "$ctfd_usr@$ctfd_ip" docker compose -f ctfd/docker-compose.yaml down
    fi

    if [ "$infra_local" = "true" ]; then
        docker compose -f infra-reseau/docker-compose.yaml down
    else
        ssh -o StrictHostKeyChecking=no "$infra_usr@$infra_ip" docker compose -f infra-reseau/docker-compose.yaml down
    fi

    if [ "$mastodon_local" = "true" ]; then
        docker compose -f mastodon/docker-compose.yaml down
    else
        ssh -o StrictHostKeyChecking=no "$mastodon_usr@$mastodon_ip" docker compose -f mastodon/docker-compose.yaml down
    fi

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

    if [ "$infra_local" = "true" ]; then
        installer_reseau_local "$infra_ip"
    else
        installer_reseau_distant "$infra_ip" "$infra_usr" "$infra_mdp"
    fi
    if [ $(systemctl status systemd-resolved > /dev/null ; echo $?) = 0 ]; then
        config="$(grep -E "^#?DNS=.*$" /etc/systemd/resolved.conf | sed "s/ //gm")"
        if [ $config != "DNS=$infra_ip" ] && [ $config != "DNS=" ] && [ $config != "#DNS=" ]; then
            echo "Pour pouvoir accéder au ctf, vous aurez besoin de rediriger vos requêtes DNS à travers les services du ctf."
            echo "Votre configuration sytemd-resolved comporte le serveur DNS suivant : ${config}"
            printf "Souhaitez-vous le remplacer par celui du ctf ($infra_ip)? [O/n] : "
            read choix
            if [ "$choix" = "O" ] || [ "$choix" = "o" ]; then
                sed -i -E "s/^DNS=.*$/DNS=$infra_ip/gm" /etc/systemd/resolved.conf
            fi
        else
            sed -i -E "s/^#?DNS=.*$/DNS=$infra_ip/gm" /etc/systemd/resolved.conf
        fi
        systemctl restart systemd-resolved > /dev/null
    else
        sed -i -E '0,/^nameserver=(.*)$/{s//namserver=$infra_ip\nameserver=\1/}' /etc/resolv.conf
    fi

    if [ "$courriels_local" = "true" ]; then
        installer_courriels_local
    else
        installer_courriels_distant "$courriels_ip" "$courriels_usr" "$courriels_mdp"
    fi

    if [ "$ctfd_local" = "true" ]; then
        installer_ctfd_local
    else
        installer_ctfd_distant "$ctfd_ip" "$ctfd_usr" "$ctfd_mdp"
    fi

    if [ "$defis_local" = "true" ]; then
        installer_defis_local
    else
        installer_defis_distant "$defis_ip" "$defis_usr" "$defis_mdp"
    fi

    if [ "$mastodon_local" = "true" ]; then
        installer_mastodon_local
    else
        installer_mastodon_distant "$mastodon_ip" "$mastodon_usr" "$mastodon_mdp"
    fi

    echo ""
    echo "Comptes utilisateurs : "
    jq -c ".utilisateurs[]" coordination/comptes_utilisateurs.json | while read compte; do
        nom="$(echo $compte | jq -r ".nom")"
        id="$(echo $compte | jq -r ".id")"
        mdp="$(echo $compte | jq -r ".mdp")"
        if [ "$id" = "admin" ] && [ "$mastodon_local" = "true" ]; then
            mdp_mstdn="$(echo "$(cat mastodon/installation/admin.mdp)" | grep -E 'New password: ' | sed -E 's/.+: (.+)/\1/gm')"
        elif [ "$id" != "admin" ] && [ "$mastodon_local" = "true" ]; then
            mdp_mstdn="$(echo "$(cat mastodon/installation/utilisateurs.mdp)" | grep -E "${id}: " | sed -E 's/.+: (.+)/\1/gm')"
        elif [ "$id" = "admin" ] && [ "$mastodon_local" != "true" ]; then
            ssh -o StrictHostKeyChecking=no "$mastodon_usr@$mastodon_ip" \ 
                mdp_mstdn="$(echo "$(cat mastodon/installation/admin.mdp)" | grep -E 'New password: ' | sed -E 's/.+: (.+)/\1/gm')"
        elif [ "$id" != "admin" ] && [ "$mastodon_local" != "true" ]; then
            ssh -o StrictHostKeyChecking=no "$mastodon_usr@$mastodon_ip" \ 
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

installer_reseau_local() {
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
}

installer_courriels_local() {
    echo ""
    echo "Installation du serveur SMTP."
    printf '\n===== Docker =====\n'
    docker compose -f courriels/docker-compose.yaml up -d
    printf '===== Docker =====\n\n'
}

installer_mastodon_local() {
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
}

installer_ctfd_local() {
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
}

installer_reseau_distant() {
    echo ""
    echo "Lancement de l'infra réseau."
    openssl req -config infra-reseau/TLS/openssl.cnf \
            -nodes -new -x509 \
            -keyout "infra-reseau/TLS/${DOMAINE}.key.pem" \
            -days 2 -sha256 -extensions v3_ca \
            -out "infra-reseau/TLS/${DOMAINE}.cert.pem"

    cd infra-reseau
    DOMAINE_GLOBAL=${DOMAINE} python3 nginx-setup.py ../defis
    cd ..

    ip="$1"
    usr="$2"
    mdp="$3"

    echo "$mdp" | ssh-copy-id -o StrictHostKeyChecking=no "$usr@$ip"
    scp -o StrictHostKeyChecking=no ./infra-reseau/ "$usr@$ip:infra-reseau/"

    printf '\n===== Docker =====\n'
    ssh -o StrictHostKeyChecking=no "$usr@$ip" docker compose up -d
    printf '===== Docker =====\n\n'
}

installer_courriels_distant() {
    echo ""
    echo "Installation du serveur SMTP."

    ip="$1"
    usr="$2"
    mdp="$3"

    echo "$mdp" | ssh-copy-id -o StrictHostKeyChecking=no "$usr@$ip"
    scp -o StrictHostKeyChecking=no ./courriels/ "$usr@$ip:courriels/"
    scp -o StrictHostKeyChecking=no ./coordination/ "$usr@$ip:coordination/"

    printf '\n===== Docker =====\n'
    ssh -o StrictHostKeyChecking=no "$usr@$ip" docker compose -f courriels/docker-compose.yaml up -d
    printf '===== Docker =====\n\n'
}

installer_mastodon_distant() {
    echo ""
    echo "Installation du serveur Mastodon."
    chown -R 991:911 mastodon/installation
    jq -c ".utilisateurs[]" coordination/comptes_utilisateurs.json | while read compte; do
        if [ "$(echo $compte | jq -r ".id")" = "admin" ]; then
            MDP_ADMIN_SMTP="$(echo $compte | jq -r ".mdp")"
        fi
    done
    sed -i -E "s/SMTP_PASSWORD=.*/$MDP_ADMIN_SMTP/gm" mastodon/.env.production

    ip="$1"
    usr="$2"
    mdp="$3"

    echo "$mdp" | ssh-copy-id -o StrictHostKeyChecking=no "$usr@$ip"
    scp -o StrictHostKeyChecking=no ./mastodon/ "$usr@$ip:mastodon/"
    scp -o StrictHostKeyChecking=no ./coordination/ "$usr@$ip:coordination/"

    printf '\n===== Docker =====\n'
    ssh -o StrictHostKeyChecking=no docker compose -f mastodon/docker-compose.yaml up -d
    printf '===== Docker =====\n\n'
    printf "En attente de l'installation de Mastodon"
    while [ "$(ssh -o StrictHostKeyChecking=no "$usr@$ip" cat mastodon/installation/est_installe.bool 2> /dev/null || echo 'false')"  != "true" ]; do
        printf '.'
        sleep 1
    done
}

installer_ctfd_distant() {
    echo ""
    echo "Installation de CTFd"

    ip="$1"
    usr="$2"
    mdp="$3"

    echo "$mdp" | ssh-copy-id -o StrictHostKeyChecking=no "$usr@$ip"
    scp -o StrictHostKeyChecking=no ./ctfd/ "$usr@$ip:ctfd/"
    scp -o StrictHostKeyChecking=no ./coordination/ "$usr@$ip:coordination/"

    printf '\n===== Docker =====\n'
    ssh -o StrictHostKeyChecking=no docker compose -f ctfd/docker-compose.yaml up -d
    printf '===== Docker =====\n\n'

    cd ctfd
    python3 -m venv .venv > /dev/null
    .venv/bin/python3 -m pip install -r requirements.txt > /dev/null
    ssh -o StrictHostKeyChecking=no chown -R 1001:1001 donnees/ctfd
    printf "En attente du lancement de CTFd"
    while [ $(curl -fk https://ctfd.${DOMAINE} &> /dev/null ; echo $?) != 0 ]; do
        sleep 1
        printf '.'
    done
    printf '\n'
    DOMAINE_GLOBAL=${DOMAINE} .venv/bin/python3 ctfd-config.py ./config_prod.yaml
    cd ..
}

main "$@"