import time
import board
import busio

from fsm import FSM
import utils
# hardware
from batt import Batt
from inkdisp import InkDisp
from clock import Clock
from as1115 import AS1115
from encoder import Encoder
from piezo import Piezo
from ir import IrSensor


time.sleep(5)  # to ensure serial connection does not fail

# initialize class objects
i2c = busio.I2C(scl=board.GP5, sda=board.GP4)
as1115 = AS1115(i2c)
clock = Clock(i2c)

battery = Batt()
encoder = Encoder()
buzzer = Piezo(board.GP16)
buzzer2 = Piezo(board.GP17)
ir_sensor = IrSensor()
date_str = clock.get_date_str()
alarm_str = clock.get_alarm_str()
inkdisp = InkDisp(date_init=date_str, 
                  alarm_init=alarm_str, 
                  batt=battery.get_batt_frac(), 
                  usb=battery.usb_power.value)
clock.set_refresh()

dt = 0.1
beat_rate = 0.3
k_beat = int(beat_rate/dt)
k = 0
heartbeat = True

fsm = FSM()

while True:
    if k >= k_beat:
        k = 0
        heartbeat = not heartbeat
    
    buttons = as1115.scan_keys()
    
    state = fsm.execute(enter=encoder.update_button(),
                        back=buttons[0],
                        set_date=buttons[1], 
                        set_time=buttons[2], 
                        set_alarm=buttons[3],
                        set_brightness=buttons[4],
                        alarm_status=clock.get_alarm_status(buttons[5]))
    print('state = ', state)

    if state == 'default':
        as1115.display_hourmin(clock.get_hour(), clock.get_min())
    elif state in ['start_set_month', 'start_set_day', 'start_set_min', 'start_set_alarm_min']:
        encoder.rezero()

    elif state == 'start_set_year':
        year = clock.get_year()
        month = clock.get_month()
        day = clock.get_day()
        encoder.rezero()
    elif state == 'set_year':
        year_new = utils.wrap_to_range(year + encoder.get_encoder_pos(), a=1970, b=2037)
        as1115.display_int(year_new)
        as1115.wink_left(heartbeat)
        as1115.wink_right(heartbeat)
    elif state == 'set_month':
        month_new = utils.wrap_to_range(month + encoder.get_encoder_pos(), a=1, b=12)
        as1115.display_hourmin(month_new, day)
        as1115.wink_left(heartbeat)
    elif state == 'set_day':
        day_max = utils.get_max_day(year=year_new, month=month_new)
        day_new = utils.wrap_to_range(day + encoder.get_encoder_pos(), a=1, b=day_max)
        as1115.display_hourmin(month_new, day_new)
        as1115.wink_right(heartbeat)
    elif state == 'end_set_day':
        clock.set_date(year=year_new, month=month_new, day=day_new)
        as1115.unwink()

    elif state == 'start_set_hour':
        hour = clock.get_hour()
        minute = clock.get_min()
        encoder.rezero()
    elif state == 'set_hour':
        hour_new = (hour + encoder.get_encoder_pos()) % 24
        as1115.display_hourmin(hour_new, minute)
        as1115.wink_left(heartbeat)
    elif state == 'set_min':
        min_new = (minute + encoder.get_encoder_pos()) % 60
        as1115.display_hourmin(hour_new, min_new)
        as1115.wink_right(heartbeat)
    elif state == 'end_set_min':
        clock.set_time(hour=hour_new, min=min_new)
        as1115.unwink()
    
    elif state == 'start_set_alarm':
        hour = clock.get_alarm_hour()
        minute = clock.get_alarm_min()
        encoder.rezero()
    elif state == 'set_alarm_hour':
        hour_new = (hour + encoder.get_encoder_pos()) % 24
        as1115.display_hourmin(hour_new, minute)
        as1115.wink_left(heartbeat)
    elif state == 'set_alarm_min':
        min_new = (minute + encoder.get_encoder_pos()) % 60
        as1115.display_hourmin(hour_new, min_new)
        as1115.wink_right(heartbeat)
    elif state == 'end_set_alarm_min':
        clock.set_alarm(hour=hour_new, min=min_new)
        as1115.unwink()

    elif state == 'set_no_alarm':
        clock.disable_alarm()

    elif state == 'start_set_brightness':
        encoder.rezero()
        brightness_new = as1115.brightness
    elif state == 'set_brightness':
        as1115.brightness = (brightness_new + encoder.get_encoder_pos()) % 8
        as1115.display_int(as1115.brightness)
    elif state == 'end_set_brightness':
        pass

    elif state == 'alarming':
        as1115.display_hourmin(clock.get_hour(), clock.get_min())
        #as1115.blink_rate = 1  # this interferes with button presses, add back later
        alarm_delta = clock.get_alarm_delta()
        magnitude = utils.clip(abs(alarm_delta/clock.alarm_delta_max), 0.1, 1.)
        tone = 200 #utils.translate(utils.clip(magnitude, 0.1, 1.), 262, 464)
        buzzer.play(tone=tone, amp=magnitude, on=heartbeat)
        buzzer2.play(tone=tone, amp=magnitude, on=heartbeat)
    elif state == 'end_alarming':
        #as1115.blink_rate = 0
        clock.reset_alarm()
        buzzer.shutoff()
        buzzer2.shutoff()

    # refresh inkdisp, make sure at least 3 minutes have passed before you refresh again
    if (date_str != clock.get_date_str() or alarm_str != clock.get_alarm_str()) and clock.get_refresh_delta() > 180:
        date_str = clock.get_date_str()
        alarm_str = clock.get_alarm_str()
        inkdisp.clear()
        inkdisp.apply_info(date=date_str, 
                           alarm=alarm_str, 
                           batt=battery.get_batt_frac(), 
                           usb=battery.usb_power.value)
        inkdisp.update()
        clock.set_refresh()

    k += 1
    time.sleep(dt)
