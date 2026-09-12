if [ "$(cat /tmp/installation/est_installe.bool)" != "true" ]; then
    echo "Création des comptes utilisateurs"
    jq -c ".utilisateurs[]" /tmp/comptes.json | while read compte; do
        id=$(echo $compte | jq -r ".courriel" | grep -Eo "^[^@]+")
        mdp=$(echo $compte | jq -r ".mdp_courriel")
        echo "$id"
        setup email add ${id}@${DOMAINE} ${mdp}
    done

    printf "true" > /tmp/installation/est_installe.bool
fi