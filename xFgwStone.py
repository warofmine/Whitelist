from phBot import *
from threading import Timer
import random
import QtBind

pName = 'xFgwStone_Evasion'

# Hedef konum
target_position = None
retry_count = 0
max_retry = 3

def handle_joymax(opcode, data):
    if opcode == 0xB070:
        if data[0] == 1 and data[1] == 0 and data[3] == 84 and data[4] == 128:
            log('[%s] Sereness taş saldırısı algılandı, kaçış başlatılıyor...' % pName)
            stop_bot()
            evade_from_stone()
    return True

def evade_from_stone(radius=6):
    global target_position, retry_count
    retry_count = 0  # sıfırla
    pos = get_position()
    if pos:
        offset_x = random.uniform(-radius, radius)
        offset_y = random.uniform(-radius, radius)
        new_x = pos['x'] + offset_x
        new_y = pos['y'] + offset_y

        target_position = (round(new_x, 1), round(new_y, 1))
        move_to(new_x, new_y, pos['z'])
        log('[%s] Kaçış → Yeni konum: (X:%.1f, Y:%.1f)' % (pName, new_x, new_y))

        Timer(1.0, check_if_arrived).start()
    else:
        log('[%s] Konum alınamadı, kaçış başarısız.' % pName)

def check_if_arrived():
    global target_position, retry_count
    current = get_position()
    if not current or not target_position:
        return

    current_x = round(current['x'], 1)
    current_y = round(current['y'], 1)

    if (current_x, current_y) == target_position:
        log('[%s] Yeni konuma ulaşıldı, bot yeniden başlatılıyor.' % pName)
        start_bot()
        target_position = None
    else:
        retry_count += 1
        if retry_count >= max_retry:
            log('[%s] Konuma ulaşamadı (muhtemelen stun oldu). Alternatif kaçış başlatılıyor...' % pName)
            force_alternate_escape()
        else:
            Timer(1.0, check_if_arrived).start()

def force_alternate_escape():
    global target_position
    pos = get_position()
    if pos:
        # Alternatif yön oluştur
        new_x = pos['x'] + random.uniform(-3, 3)
        new_y = pos['y'] + random.uniform(-3, 3)
        target_position = (round(new_x, 1), round(new_y, 1))
        move_to(new_x, new_y, pos['z'])
        log('[%s] Alternatif kaçış denemesi: (X:%.1f, Y:%.1f)' % (pName, new_x, new_y))
        Timer(1.0, check_if_arrived).start()
    else:
        log('[%s] Alternatif konum alınamadı, botu güvenli şekilde başlatıyor...' % pName)
        start_bot()

log('[%s] Plugin yüklendi ve Sereness saldırılarını izliyor...' % pName)
