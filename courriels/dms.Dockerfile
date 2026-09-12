FROM mailserver/docker-mailserver

RUN apt update && apt install jq -y