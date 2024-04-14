import board
import rotaryio
import digitalio

class Inputs():
    '''
    Handles encoder and button presses
    '''
    def __init__(self):
        # encoder
        self.encoder = rotaryio.IncrementalEncoder(board.D10, board.D9) #, divisor=2)
        self.zero_pos = self.encoder.position

        # encoder button (enter)
        self.button_e = self.config_button(board.D11)
        self.button_e_prev = False
        
        # back button
        self.button_b = self.config_button(board.D24)
        self.button_b_prev = False

        # set date button
        self.button_d = self.config_button(board.D12)

        # set time button
        self.button_t = self.config_button(board.D13)

        # set alarm button
        self.button_a = self.config_button(board.D5)

        # set shades button
        self.button_s = self.config_button(board.D6)
    
    def config_button(self, pin):
        button = digitalio.DigitalInOut(pin)
        button.direction = digitalio.Direction.INPUT
        button.pull = digitalio.Pull.UP
        return button

    def update_button_e(self):
        # this must run every timestep to work
        if self.button_e_prev is True and self.get_button_e() is False:
            # button was previously pressed, is no longer pressed
            self.button_e_prev = False
            return True
        self.button_e_prev = self.get_button_e()
        return False
        
    def update_button_b(self):
        # this must run every timestep to work
        if self.button_b_prev is True and self.get_button_b() is False:
            # button was previously pressed, is no longer pressed
            self.button_b_prev = False
            return True
        self.button_b_prev = self.get_button_b()
        return False
    
    def rezero(self):
        # re-zero encoder
        self.zero_pos = self.encoder.position

    def get_encoder_pos(self):
        # encoder feedback
        return self.encoder.position - self.zero_pos
    
    def get_button_e(self):
        return not self.button_e.value
    
    def get_button_b(self):
        return not self.button_b.value
    
    def get_button_d(self):
        return not self.button_d.value
    
    def get_button_t(self):
        return not self.button_t.value
    
    def get_button_a(self):
        return not self.button_a.value
    
    def get_button_s(self):
        return not self.button_s.value
        
