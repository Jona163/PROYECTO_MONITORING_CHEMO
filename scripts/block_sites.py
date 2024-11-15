import os

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
REDIRECT = "127.0.0.1"

def block_sites(sites):
    with open(HOSTS_PATH, "a") as file:
        for site in sites:
            file.write(f"{REDIRECT} {site}\n")

def unblock_sites(sites):
    with open(HOSTS_PATH, "r") as file:
        lines = file.readlines()
    with open(HOSTS_PATH, "w") as file:
        for line in lines:
            if not any(site in line for site in sites):
                file.write(line)
