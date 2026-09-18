#!/bin/python3
import sys
import os

sys.path.insert(0,"../coordination/yaml_config")
import yaml_config

sys.path.insert(0,"../ctfd/ctfd-config")
import ctfd_config

def main():
    print("Configuration nginx")

    if len(sys.argv) < 3:
        print("[ERREUR] Veuillez indiquer le répertoire des défis")
        print(message_aide)
        sys.exit()
    
    rep_defis = sys.argv[1]

    defis = ctfd_config.lire_defis(rep_defis)
    configurer_nginx(defis)

def configurer_nginx(defis : dict):
    config = ""
    for d in defis:
        config += f"""
server {{
    server_name {d["nom_domaine"]}.defis.{os.getenv("DOMAINE_GLOBAL","aucun_domaine.lan")};

    location / {{
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Proxy "";

        proxy_pass http://{d["ip"]};
    }}
}}\n
"""

    with open("./defis.nginx.conf","w") as f:
        f.write(config)

message_aide = """
USAGE nginx-setup <dossier défis>
"""

if __name__ == "__main__":
    main()