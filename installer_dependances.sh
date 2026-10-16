# TODO Supporter d'autres gestionnaires de packets

if [ "$EUID" -ne 0 ]; then
    sudo -sS "$0" "$@" 2> /dev/null
fi

apt update &> /dev/null
echo "Installation de jq, sshpass, git, python3 et python3-venv"
apt install -y jq sshpass git python3 python3-venv &> /dev/null

if [ -z "$(which docker)" ]; then
    printf '\tInstallation de docker...\n\n'
    # Add Docker's official GPG key:
    apt -y install ca-certificates curl &> /dev/null
    install -m 0755 -d /etc/apt/keyrings > /dev/null
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc &> /dev/null
    chmod a+r /etc/apt/keyrings/docker.asc > /dev/null

    # Add the repository to Apt sources:
    printf "Types: deb\n\
URIs: https://download.docker.com/linux/ubuntu\n\
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")\n\
Components: stable\n\
Architectures: $(dpkg --print-architecture)\n\
Signed-By: /etc/apt/keyrings/docker.asc" > /etc/apt/sources.list.d/docker.sources

    apt update &> /dev/null

    apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin &> /dev/null
fi

echo "Dépendances installées"