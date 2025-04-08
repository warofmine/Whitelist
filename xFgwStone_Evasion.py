from phBot import *
from threading import Timer
import random
import QtBind

pName = 'xFgwStone_Evasion'

# GUI oluştur
gui = QtBind.init(__name__, pName)
lblTitle = QtBind.createLabel(gui, "Sereness Saldırı Takibi Ayarları", 20, 10)

# Kullanıcıdan alınacak değerler
tbData0 = QtBind.createLineEdit(gui, "1", 20, 40, 50, 20)
tbData1 = QtBind.createLineEdit(gui, "0", 80, 40, 50, 20)
tbData3 = QtBind.createLineEdit(gui, "84", 140, 40, 50, 20)
tbData4 = QtBind.createLineEdit(gui, "128", 200, 40, 50, 20)

QtBind.createLabel(gui, "data[0]", 20, 25)
QtBind.createLabel(gui, "data[1]", 80, 25)
QtBind.createLabel(gui, "data[3]", 140, 25)
QtBind.createLabel(gui, "data[4]", 200, 25)

# Hedef konum ve kontrol sayacı
target_position = None
retry_count = 0
max_retry = 3

# Opcode paketi yakalama
def handle_joymax(opcode, data):
    if opcode == 0xB070:

        try:
            # GUI'den kullanıcıdan alınan değerleri oku
            val0 = int(QtBind.text(gui, tbData0))
            val1 = int(QtBind.text(gui, tbData1))
            val3 = int(QtBind.text(gui, tbData3))
            val4 = int(QtBind.text(gui, tbData4))
        except ValueError:
            log('[%s] Hatalı veri formatı! Tüm değerler integer olmalıdır.' % pName)
            return True

        # Karşılaştır
        if data[0] == val0 and data[1] == val1 and data[3] == val3 and data[4] == val4:
            log('[%s] Belirtilen saldırı paketi algılandı. Kaçış başlatılıyor...' % pName)
            stop_bot()
            evade_from_stone()

    return True

# Kaçış fonksiyonu
def evade_from_stone(radius=6):
    global target_position, retry_count
    retry_count = 0
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
            log('[%s] Konuma ulaşamadı. Alternatif kaçış deneniyor...' % pName)
            force_alternate_escape()
        else:
            Timer(1.0, check_if_arrived).start()

def force_alternate_escape():
    global target_position
    pos = get_position()
    if pos:
        new_x = pos['x'] + random.uniform(-3, 3)
        new_y = pos['y'] + random.uniform(-3, 3)
        target_position = (round(new_x, 1), round(new_y, 1))
        move_to(new_x, new_y, pos['z'])
        log('[%s] Alternatif kaçış: (X:%.1f, Y:%.1f)' % (pName, new_x, new_y))
        Timer(1.0, check_if_arrived).start()
    else:
        log('[%s] Alternatif konum alınamadı. Bot yeniden başlatılıyor...' % pName)
        start_bot()

log('[%s] Plugin yüklendi. GUI üzerinden data[0,1,3,4] değerlerini ayarlayabilirsiniz.' % pName)
