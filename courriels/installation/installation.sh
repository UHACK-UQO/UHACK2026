if [ "$(cat /tmp/installation/est_installe.bool)" != "true" ]; then
    echo "Création des comptes utilisateurs"
    jq -c ".utilisateurs[]" /tmp/comptes.json | while read compte; do
        id=$(echo $compte | jq -r ".id")
        mdp=$(echo $compte | jq -r ".mdp")
        echo "$id"
        setup email add ${id}@${DOMAINE_GLOBAL} ${mdp}
    done

    printf "true" > /tmp/installation/est_installe.bool
fi