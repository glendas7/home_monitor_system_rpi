from ADCDevice import *
import firebase_setup
import camera_handler
from firebase_admin import firestore
from gpiozero import LED, LightSensor
from signal import pause
import constant
import math

adc = ADCDevice()
adc = ADS7830()    
adcVal = 0
aLed = LED(26)
bLed = LED(25)
cLed = LED(19)
dLed = LED(12)
eLed = LED(13)
fLed = LED(16)
gLed = LED(6)
hLed = LED(20)
iLed = LED(5)
jLed = LED(21)

adcIndex = [60, 81, 101, 131, 151, 171, 191, 211, 231, 251]
leds = [aLed, bLed, cLed, dLed, eLed, fLed, gLed, hLed, iLed, jLed]
db = firestore.client()

collection = firebase_setup.db.collection(constant.COLLECTION_NAME)
doc_adc_ref = collection.document(constant.ADC_DATA)
doc_buttons_ref = collection.document(constant.BUTTON_DATA)
doc_camera_ref = collection.document(constant.CAMERA_DATA)

doc_adc_ref.update({u'value':None})
doc_adc_ref.update({u'tempF':None})
doc_adc_ref.update({u'tempC':None})
doc_adc_ref.update({u'lights':None})
doc_buttons_ref.update({u'picButton':False})
doc_camera_ref.update({u'url':None})
doc_camera_ref.update({u'timestamp':None})

def on_buttonsdoc_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        global permission_status
        picture_button_status = doc.to_dict()["picButton"]
        if picture_button_status:
            print('updated pic url')
            camera_handler.capture('1.jpg')
            doc_buttons_ref.update({u'picButton':False})
            

doc_buttons_ref = collection.document(constant.BUTTON_DATA)
doc_buttons_watch = doc_buttons_ref.on_snapshot(on_buttonsdoc_snapshot)

def turn_off():
    for led in leds:
        led.off()

def updateLed(value): 
    for led, i in zip(leds, adcIndex):
        if adcVal >=i:
           led.on()
        else:
            led.off()
            
while True:
    value = adc.analogRead(5)
    value1 = adc.analogRead(7)
    voltage = value1 / 255.0 * 3.3 # voltage
    Rt = 10 * voltage / (3.3 - voltage) # resistance value of thermistor
    tempK = 1/(1/(273.15 + 25) + math.log(Rt/10)/3950.0) # kelvin
    tempC = tempK -273.15 # celsius
    tempF = round((tempC * 9/5) + 32)
    print(value)
    try:
        adcVal = value
        doc_adc_ref.update({u'value': value})
        doc_adc_ref.update({u'tempF': tempF})
        doc_adc_ref.update({u'tempC': round(tempC)})
        updateLed(value)
        if value <= 80:
            doc_adc_ref.update({u'lights': "On"})
        elif value >= 231:
            doc_adc_ref.update({u'lights': "Off"})
        else:
            doc_adc_ref.update({u'lights': "?"})
    except KeyboardInterrupt:
        turn_off()
        pause()
    except:
        print("--")
