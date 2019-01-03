import sys
import time
import RPi.GPIO as GPIO
import socket
import signal

motor_reset = False
HOST = socket.gethostbyname('192.168.1.241')
PORT = 8082

GPIO.setmode(GPIO.BCM)
 
STEPS_PER_REVOLUTION = 64 * 64
SEQUENCE = [[1,0,0,0],
            [1,1,0,0],
            [0,1,0,0],
            [0,1,1,0],
            [0,0,1,0],
            [0,0,1,1],
            [0,0,0,1],
            [1,0,0,1]]
 
STEPPER_PINS = [17,18,27,22]

GPIO.setup(4, GPIO.IN, pull_up_down = GPIO.PUD_UP)
for pin in STEPPER_PINS:
  GPIO.setup(pin,GPIO.OUT)
  GPIO.output(pin, GPIO.LOW)

 
SEQUENCE_COUNT = len(SEQUENCE)
PINS_COUNT     = len(STEPPER_PINS)
 
sequence_index = 0
direction      = 1
wait_time      = 1/float(1000)
CUR_STEP       = 0
TAR_STEP       = 0
TAR_DIR        = 0


s = socket.socket()
s.bind((HOST, PORT))
s.listen(1)

print 'Server start at: %s:%s' %(HOST, PORT)
print 'wait for connection...'

def resetpos(channel):
    global motor_reset
    motor_reset = True
    

GPIO.add_event_detect(4, GPIO.RISING, callback = resetpos, bouncetime = 300)

try:
    while not motor_reset:
        conn, addr = s.accept()
        print 'Connected by ', addr

        TAR_DIR_r = conn.recv(1024)
        TAR_DIR = float(TAR_DIR_r)
        print TAR_DIR_r

        TAR_STEP = int(TAR_DIR * STEPS_PER_REVOLUTION)
        if TAR_STEP > CUR_STEP:
            direction = 1
        else:
            direction = -1
        while CUR_STEP != TAR_STEP:
            for pin in range(0, PINS_COUNT):
                GPIO.output(STEPPER_PINS[pin], SEQUENCE[sequence_index][pin])
            CUR_STEP += direction
            sequence_index += direction
            sequence_index %= SEQUENCE_COUNT
            time.sleep(wait_time)  

        conn.close()

    s.close()
    if CUR_STEP < 0:
        direction = 1
    else:
        direction = -1
    while CUR_STEP != 0:
        for pin in range(0, PINS_COUNT):
            GPIO.output(STEPPER_PINS[pin], SEQUENCE[sequence_index][pin])
        CUR_STEP += direction
        sequence_index += direction
        sequence_index %= SEQUENCE_COUNT
        time.sleep(wait_time)
    
    sys.exit(0)  

except KeyboardInterrupt: 
    GPIO.cleanup() 
    


