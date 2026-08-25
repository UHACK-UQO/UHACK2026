if [ "$(cat /opt/mastodon/installation/est_installe.bool)" = "true" ]; then
    echo "Mastodon est déjà installé"
else
    RAILS_ENV=production IGNORE_ALREADY_SET_SECRETS=true bin/rails db:encryption:init
    RAILS_ENV=production bin/rails db:setup
    RAILS_ENV=production bin/rails assets:precompile
    RAILS_ENV=production bin/tootctl accounts create admin --email ${ADMIN_EMAIL} --confirmed --role Owner | grep "New password: " > /opt/mastodon/installation/admin.mdp
    echo "Mot de passe généré. Vous pouvez le consulter dans installation/admin.mdp"
    RAILS_ENV=production bin/tootctl accounts modify admin --approve
    printf "true" > /opt/mastodon/installation/est_installe.bool
fi
bundle exec puma -C config/puma.rb
