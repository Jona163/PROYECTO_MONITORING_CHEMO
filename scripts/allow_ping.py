import os

def block_ping():
    os.system("netsh advfirewall firewall add rule name='Block Ping' protocol=icmpv4:8,any dir=in action=block")

def allow_ping():
    os.system("netsh advfirewall firewall delete rule name='Block Ping'")
