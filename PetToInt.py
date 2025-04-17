from phBot import *
import phBotChat
import QtBind
import struct

pName = 'PetToInt'
pVersion = '1.1'

# GUI Başlat
gui = QtBind.init(__name__, pName)
btnTransfer = QtBind.createButton(gui, 'start_transfer', ' PET ➜ ÇANTA ', 80, 258)

# GUI Delay Ayarı
QtBind.createLabel(gui, "Kontrol Süresi (saniye):", 10, 220)
tbxDelay = QtBind.createLineEdit(gui, "60", 160, 217, 40, 20)

# Sayaç
last_run = 0

def start_transfer():
    """Pet içeriğini envantere aktarır."""
    pet_slot = get_filled_pet_slot()
    free_inv_slot = get_free_inventory_slot()

    if pet_slot == -1:
        log("Plugin: Pette taşınacak item bulunamadı.")
        return

    if free_inv_slot == -1:
        log("Plugin: Envanter dolu, aktarım yapılamaz.")
        return

    pets = get_pets()
    for pet_id in pets:
        if pets[pet_id]['type'] == 'pick':
            packet = b'\x1A'
            packet += struct.pack('I', pet_id)
            packet += struct.pack('B', pet_slot)
            packet += struct.pack('B', free_inv_slot)
            inject_joymax(0x7034, packet, False)
            log(f"Plugin: Pet slot {pet_slot} -> Envanter slot {free_inv_slot} taşıma başlatıldı.")
            return

def get_filled_pet_slot():
    """Pet içerisindeki ilk dolu slotu bulur."""
    pets = get_pets()
    for pet in pets.values():
        if pet['type'] == 'pick':
            for index, item in enumerate(pet.get('items', [])):
                if item:
                    return index
    return -1

def get_free_inventory_slot():
    """Envanterdeki ilk boş slotu (13 sonrası) bulur."""
    inventory = get_inventory()
    for index in range(13, len(inventory['items'])):
        if inventory['items'][index] is None:
            return index
    return -1

def event_loop():
    global last_run

    # GUI'den delay değeri al
    try:
        delay_sec = int(QtBind.text(gui, tbxDelay))
    except ValueError:
        delay_sec = 60  # Varsayılan değer

    delay_ms = delay_sec * 1000

    last_run += 500
    if last_run >= delay_ms:
        start_transfer()
        last_run = 0

def handle_event(t, data):
    pass

def handle_joymax(opcode, data, encrypted):
    return True

log(f"[{pName}] v{pVersion} yüklendi. PET'teki itemler belirli aralıklarla çantaya aktarılır.")
