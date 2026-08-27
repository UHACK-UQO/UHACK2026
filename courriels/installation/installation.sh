if [ "$(cat /mox/installation/est_installe.bool)" = "true" ]; then
    echo "Le serveur est déjà installé"
else
    chown -R 1000:1000 /mox

    # La configuration est dépendante du domaine spécifié.
    # Il est donc nécessaire de la regénérer avec le bon domaine
    # pour la modifier selon nos besoins.
    echo "Génération de la configuration..."
    mox quickstart -skipdial -hostname smtp.$DOMAINE admin@${DOMAINE} 1000 > /dev/null
    sed -i -E "s/^DataDir: .*$/DataDir: ..\/data/g" /mox/config/mox.conf
    # Transfère la section 'Listeners' du fichier utilisateur au fichier généré par mox
    conf="$(cat /mox/config/mox.conf | tr '\n' '%' | tr '\t' ';' | tr '/' '!')"
    template="$(cat /mox/mox.conf.template | tr '\n' '%' | tr '\t' ';' | tr '/' '!' | grep -Eo 'Listeners:%(;+[^;|%]+%|%)*')"
    # Conserver les clées générées
    keyfiles="$(echo $conf | grep -Eo 'HostPrivateKeyFiles:%(;;;;[^;|%]*%)*')"
    template=$(echo $template | sed -E "s/HostPrivateKeyFiles:%(;;;;[^;|%]*%)*/${keyfiles}/g")
    echo $conf | sed -E "s/Listeners:%(;+[^;|%]+%|%)*/${template}/g" | tr '!' '/' | tr ';' '\t' | tr '%' '\n' > /mox/mox.conf.tmp
    mv /mox/mox.conf.tmp /mox/config/mox.conf

    chown -R 1000:1000 /mox

    printf "Initialisation du serveur\n\n\n"
    mox serve &
    id=$!
    while [ ! -e /mox/data/ctl ]; do
        sleep 1
    done

    echo "Modification du mot de passe admin"
    echo $MDP_ADMIN | mox setadminpassword > /dev/null
    echo $MDP_ADMIN | mox setaccountpassword admin > /dev/null

    echo "Création des comptes utilisateurs"
    jq -c ".utilisateurs[]" /mox/comptes.json | while read compte; do
        id=$(echo $compte | jq -r ".courriel" | grep -Eo "^[^@]+")
        mdp=$(echo $compte | jq -r ".mdp_courriel")
        echo "$id"
        mox config account add $id ${id}@${DOMAINE} > /dev/null
        echo $mdp | mox setaccountpassword $id > /dev/null
    done

    kill $id
    sleep 2
    chown -R 1000:1000 /mox
    echo   "Initialisation terminée"
    printf "=======================\n\n"
    printf "true" > /mox/installation/est_installe.bool
fi

mox serve