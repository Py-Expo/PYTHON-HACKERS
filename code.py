from machine import Pin, PWM, I2C
import time
from esp32_i2c_lcd import I2cLcd

# I2C configuration for ESP32 - adjust the pins to your ESP32 setup
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)  # 16x2 LCD

servo_pin = PWM(Pin(18), freq=50)
# Function to convert angle to duty for ESP32 (angle in degrees)
def angle_to_duty(angle):
    return int((angle / 180) * 102 + 26)

# Center the servo at startup
servo_pin.duty(angle_to_duty(90))

# Define sensor pins (use ADC pins if analog values are needed, here using digital)
sensor_pins = [34, 35, 32, 33, 25, 26]  # GPIOs as input, adjust as necessary
sensors = [Pin(pin, Pin.IN) for pin in sensor_pins]

flag1 = 0
flag2 = 0
slots = 6  # Assuming 6 parking slots

def read_sensor():
    # Returns a list of sensor states; True if occupied (or triggered), False otherwise
    return [not sensor.value() for sensor in sensors]

def setup():
    lcd.clear()
    global slots
    slots -= sum(read_sensor())

def loop():
    global flag1, flag2, slots
    sensor_values = read_sensor()
    total_filled = sum(sensor_values)
    slots = 6 - total_filled  # Update available slots based on sensor readings
    
    # Update LCD
    lcd.move_to(0, 0)
    lcd.putstr("Slots: {:2d}    ".format(slots))
    
    # Since it's a 16x2 LCD, let's just display a generic message on the second line
    lcd.move_to(0, 1)
    if slots > 0:
        lcd.putstr("Park Avail       ")
    else:
        lcd.putstr("Parking Full     ")

    # Simulate a car arriving or leaving (replace Pin(2) and Pin(4) with actual input triggers)
    if not Pin(2).value() and flag1 == 0:  # Car arriving
        flag1 = 1
        if slots > 0:
            servo_pin.duty(angle_to_duty(0))  # Open barrier
            time.sleep(5)  # Wait for car to pass
            servo_pin.duty(angle_to_duty(90))  # Close barrier
            slots -= 1
        flag1 = 0
    elif not Pin(4).value() and flag2 == 0:  # Car leaving
        flag2 = 1
        servo_pin.duty(angle_to_duty(0))  # Open barrier
        time.sleep(5)  # Wait for car to pass
        servo_pin.duty(angle_to_duty(90))  # Close barrier
        slots += 1
        flag2 = 0

    time.sleep(0.1)  # Small delay to debounce buttons

if _name_ == '_main_':
    try:
        setup()
        while True:
            loop()
    except KeyboardInterrupt:
        lcd.clear()
        servo_pin.deinit()
