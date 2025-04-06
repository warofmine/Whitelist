from phBot import *
from threading import Timer
from time import sleep
import struct
import random
import binascii
import QtBind

pName = 'xFgwStone' 

def handle_joymax(opcode, data):
  if opcode == 0xB070 : 
    #log(str(data[4]))
    if data[0] == 1 and data[1] == 0 and data[3] == 84 and data[4] == 128 :
      #stop_bot()  # Pharaoh tomb (Beginner)
      stop_bot()
      sleep(2.5)
      #Timer(3.0,stop_bot()).start()
      randomMovement()
      
      
  return True
  
def randomMovement(radiusMax=5):
    #Timer(2.5,stop_bot,()).start()
    p = get_position()
    pX = 5 + p["x"]
    pY = -5 + p["y"]
    # Moving to new position
    move_to(pX,pY,p["z"])
    move_to(pX,pY,p["z"])
    Timer(2.5,start_bot,()).start()
    log("Plugin: Random movement to (X:%.1f,Y:%.1f)"%(pX,pY))
    
log(''+pName+' is operational.')