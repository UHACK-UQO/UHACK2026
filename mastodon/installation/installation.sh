if [ "$(cat /opt/mastodon/installation/est_installe.bool)" = "true" ]; then
    echo "Mastodon est déjà installé"
else
    RAILS_ENV=production IGNORE_ALREADY_SET_SECRETS=true bin/rails db:encryption:init
    RAILS_ENV=production bin/rails db:setup
    RAILS_ENV=production bin/rails assets:precompile

    echo "Création du compte admin..."
    RAILS_ENV=production bin/tootctl accounts create admin --email ${ADMIN_EMAIL} --confirmed --role Owner | grep "New password: " > /opt/mastodon/installation/admin.mdp
    RAILS_ENV=production bin/tootctl accounts modify admin --approve
    echo "Mot de passe généré. Vous pouvez le consulter dans installation/admin.mdp"

    echo "Création des comptes utilisateurs..."
    jq -c ".utilisateurs[]" /opt/mastodon/comptes.json | while read compte; do
        nom=$(echo $compte | jq -r ".id")
        courriel=$(echo $compte | jq -r ".courriel")
        echo "${nom}, ${courriel}"
        RAILS_ENV=production bin/tootctl accounts create $nom --email $courriel --confirmed | grep "New password: " | sed "s/New password: /${nom}: /gm" >> /opt/mastodon/installation/utilisateurs.mdp
        RAILS_ENV=production bin/tootctl accounts modify $nom --approve
    done
    printf "true" > /opt/mastodon/installation/est_installe.bool
fi
bundle exec puma -C config/puma.rb
