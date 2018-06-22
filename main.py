# Temp mqtt
import network
import machine
import os
import esp
import dht
import utime as time
from umqtt.simple import MQTTClient

dht_pin = 2
rtc = machine.RTC()
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)


def check_temp(d):
    """ Return an average of two measurements for temp and humidity
    :param d: dht-object attached to correct pin
    :return: temp and humidity
    """
    d.measure()
    t1 = d.temperature()
    h1 = d.humidity()
    time.sleep(2)
    d.measure()
    t2 = d.temperature()
    h2 = d.humidity()
    print('t1: {}, t2: {}'.format(t1, t2))
    print('h1: {}, h2: {}'.format(h1, h2))
    return (t1+t2)/2, (h1+h2)/2

gc.enable()
esp.osdebug(None)
time.sleep(1)

while True:  # Start endless loop
    wlan = network.WLAN(network.STA_IF)  # create station interface
    wlan.active(True)       # activate the interface
    wlan.scan()             # scan for access points
    wlan.isconnected()      # check if the station is connected to an AP
    wlan.connect('', '')  # connect to an AP
    while not wlan.isconnected():
        pass
    print(wlan.ifconfig())  # print interface's IP/netmask/gw/DNS

    rtc.alarm(rtc.ALARM0, 300000)  # every five minutes
    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        print('Just woke from a deep sleep')

    c = MQTTClient("temp1", "10.0.30.117")
    c.connect(clean_session=False)

    d = dht.DHT22(machine.Pin(dht_pin))
    temp, humid = check_temp(d)

    print('publish to telemetry, temp: {} , humid: {}'.format(temp, humid))
    c.publish(b'telemetry/temp1', str(temp))
    c.publish(b'telemetry/humid1', str(humid))
    c.disconnect()
    time.sleep(1)
    print('Going to sleep')
    machine.deepsleep()
