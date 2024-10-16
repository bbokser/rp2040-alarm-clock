# rp2040-alarm-clock

# TODO

## Case
- Cover
- Encoder cap
- Buttons

## Electrical Hardware
### Schematic
- Reverse voltage protection
- Use MAX31328 interrupt pin?
- Since MAX31328 already has temp sense, is SHT40 still best choice?
- IR circuit
    - Add missing resistor to IR circuit
    - Fix LED/resistor values
    - Change LED to thru-hole so it sticks through cover
    - Or just switch to NRF452?
- AS1115 Brightness: max is too high and min isn't low enough
    - change Rset
- Piezos too quiet? Switch to one big one
    - Might need pwm driver
### Board Layout
- Better LED cover integration
- Change 0603s to 0805s?
- Labels on silkscreen
- Voltage plane unnecessary?
- JST 4-pin footprint all pins are incorrect
- SHT40 has voltage and ground swapped
- Put ALL surface mount on front
- FPC Connector has weird-ass feature blocking insertion
- FPC connector pins are flipped!???
    - Could be fine if we just use FPC bottom contact rather than top contact
- Could battery case overlap with thru-hole stuff? It might be doable
    - At least move it closer to the pico

## Software
- Add functionality to figure out day of week...?
- Make e-ink update for any of the displayed info changing
- Figure out why variable_frequency is invalid
- Integrate FSM better
- Improve IR accuracy (or switch to better method)
- Piezo music
- Get temperature reading from DS3231
- Gradual vs immediate alarm setting?
- The midnight-crossing problem
- Lowest brightness setting won't have visible winking
- Make disp blink when alarm sounds 
    - temp disabled because blinking interferes with button presses

## Available Pins
board.A0 board.GP26 board.GP26_A0 (GPIO26)
board.A1 board.GP27 board.GP27_A1 (GPIO27)
board.A2 board.GP28 board.GP28_A2 (GPIO28)
board.A3 board.VOLTAGE_MONITOR (GPIO29)
board.GP0 (GPIO0)
board.GP1 (GPIO1)
board.GP10 (GPIO10)
board.GP11 (GPIO11)
board.GP12 (GPIO12)
board.GP13 (GPIO13)
board.GP14 (GPIO14)
board.GP15 (GPIO15)
board.GP16 (GPIO16)
board.GP17 (GPIO17)
board.GP18 (GPIO18)
board.GP19 (GPIO19)
board.GP2 (GPIO2)
board.GP20 (GPIO20)
board.GP21 (GPIO21)
board.GP22 (GPIO22)
board.GP23 board.SMPS_MODE (GPIO23)
board.GP24 board.VBUS_SENSE (GPIO24)
board.GP25 board.LED (GPIO25)
board.GP3 (GPIO3)
board.GP4 (GPIO4)
board.GP5 (GPIO5)
board.GP6 (GPIO6)
board.GP7 (GPIO7)
board.GP8 (GPIO8)
board.GP9 (GPIO9)