import ctypes
import time

def block_input(block):
    ctypes.windll.user32.BlockInput(block)

# Bloquear entrada por 10 segundos
block_input(True)
time.sleep(10)
block_input(False)
