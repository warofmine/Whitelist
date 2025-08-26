from phBot import *
import struct
import QtBind
import time

pName = 'temple'
pVersion = '1.0'

gui = QtBind.init(__name__, pName)

packet_data = b'\x04\x00\x00\x00\x03\x00'

def temple(args=None):
    opcode = 0x705A
    encrypted = False
    log(f"[{pName}] Waiting 300ms before sending packet...")
    time.sleep(0.3)
    inject_joymax(opcode, packet_data, encrypted)


# PHBot Conditions için komut yakalama
def handle_command(cmd):
    if cmd.lower() == "temple()":
        temple()
        return True
    return False

log(f'Plugin: {pName} v{pVersion} loaded.')
