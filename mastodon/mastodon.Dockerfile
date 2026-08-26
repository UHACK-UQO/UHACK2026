FROM ghcr.io/mastodon/mastodon:v4.7.0

USER root

RUN apt-get update && apt-get install -y jq

USER 991:991