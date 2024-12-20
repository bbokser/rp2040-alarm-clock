class State:
    def __init__(self, fsm):
        self.FSM = fsm

    def enter(self):
        pass

    def execute(self):
        pass

    def exit(self):
        pass

    def execute_default(self):
        if self.FSM.alarm_status is True:
            self.FSM.to_transition("toAlarming")


class Alarming(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def execute(self):
        if self.FSM.alarm_status == False:
            self.FSM.to_transition("toDefault")
            return str("end_alarming")
        return str("alarming")


class Default(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def execute(self):
        self.execute_default()
        if self.FSM.set_date == True:
            self.FSM.to_transition("toSetYear")
            return str("start_set_year")
        elif self.FSM.set_time == True:
            self.FSM.to_transition("toSetHour")
            return str("start_set_hour")
        elif self.FSM.set_alarm == True:
            self.FSM.to_transition("toSetAlarmHour")
            return str("start_set_alarm")
        elif self.FSM.set_brightness == True:
            self.FSM.to_transition("toSetBrightness")
            return str("start_set_brightness")
        else:
            pass
        return str("default")


class SetYear(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def execute(self):
        self.execute_default()
        if self.FSM.enter == True:
            self.FSM.to_transition("toSetMonth")
            return str("start_set_month")
        elif self.FSM.back == True:
            self.FSM.to_transition("toDefault")
        else:
            pass
        return str("set_year")


class SetMonth(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def execute(self):
        self.execute_default()
        if self.FSM.enter == True:
            self.FSM.to_transition("toSetDay")
            return str("start_set_day")
        elif self.FSM.back == True:
            self.FSM.to_transition("toDefault")
        else:
            pass
        return str("set_month")


class SetDay(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def execute(self):
        self.execute_default()
        if self.FSM.enter == True:
            self.FSM.to_transition("toDefault")
            return str("end_set_day")
        elif self.FSM.back == True:
            self.FSM.to_transition("toDefault")
        else:
            pass
        return str("set_day")


class SetHour(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def execute(self):
        self.execute_default()
        if self.FSM.enter == True:
            self.FSM.to_transition("toSetMin")
            return str("start_set_min")
        elif self.FSM.back == True:
            self.FSM.to_transition("toDefault")
        else:
            pass
        return str("set_hour")


class SetMin(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def execute(self):
        self.execute_default()
        if self.FSM.enter == True or self.FSM.back == True:
            self.FSM.to_transition("toDefault")
            return str("end_set_min")
        else:
            pass
        return str("set_min")


class SetAlarmHour(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def execute(self):
        self.execute_default()
        if self.FSM.enter == True:
            self.FSM.to_transition("toSetAlarmMin")
            return str("start_set_alarm_min")
        elif self.FSM.back == True:
            self.FSM.to_transition("toDefault")
            return str("set_no_alarm")
        return str("set_alarm_hour")


class SetAlarmMin(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def execute(self):
        self.execute_default()
        if self.FSM.enter == True:
            self.FSM.to_transition("toDefault")
            return str("end_set_alarm_min")
        elif self.FSM.back == True:
            self.FSM.to_transition("toDefault")
            return str("set_no_alarm")
        return str("set_alarm_min")


class SetBrightness(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def execute(self):
        self.execute_default()
        if self.FSM.enter == True:
            self.FSM.to_transition("toDefault")
            return str("end_set_brightness")
        elif self.FSM.back == True:
            self.FSM.to_transition("toDefault")
            return str("set_no_brightness")
        return str("set_brightness")


class Transition:
    def __init__(self, tostate):
        self.toState = tostate

    def execute(self):
        # return self.toState
        pass


class FSM:
    def __init__(self):
        self.states = {}
        self.transitions = {}
        self.curState = None
        self.prevState = None
        self.trans = None

        self.enter = False
        self.back = False
        self.set_date = False
        self.set_time = False
        self.set_alarm = False
        self.set_brightness = False

        self.alarm_status = False

        self.add_state("default", Default(self))
        self.add_state("alarming", Alarming(self))
        self.add_state("set_year", SetYear(self))
        self.add_state("set_month", SetMonth(self))
        self.add_state("set_day", SetDay(self))
        self.add_state("set_hour", SetHour(self))
        self.add_state("set_min", SetMin(self))
        self.add_state("set_alarm_hour", SetAlarmHour(self))
        self.add_state("set_alarm_min", SetAlarmMin(self))
        self.add_state("set_brightness", SetBrightness(self))

        self.add_transition("toAlarming", Transition("alarming"))
        self.add_transition("toSetYear", Transition("set_year"))
        self.add_transition("toSetMonth", Transition("set_month"))
        self.add_transition("toSetDay", Transition("set_day"))
        self.add_transition("toSetHour", Transition("set_hour"))
        self.add_transition("toSetMin", Transition("set_min"))
        self.add_transition("toSetAlarmHour", Transition("set_alarm_hour"))
        self.add_transition("toSetAlarmMin", Transition("set_alarm_min"))
        self.add_transition("toSetBrightness", Transition("set_brightness"))
        self.add_transition("toDefault", Transition("default"))

        self.setstate("default")

    def add_transition(self, transname, transition):
        self.transitions[transname] = transition

    def add_state(self, statename, state):
        self.states[statename] = state

    def setstate(self, statename):
        # look for whatever state we passed in within the states dict
        self.prevState = self.curState
        self.curState = self.states[statename]

    def to_transition(self, to_trans):
        # set the transition state
        self.trans = self.transitions[to_trans]

    def execute(
        self, enter, back, set_date, set_time, set_alarm, set_brightness, alarm_status
    ):
        self.enter = enter
        self.back = back
        self.set_date = set_date
        self.set_time = set_time
        self.set_alarm = set_alarm
        self.set_brightness = set_brightness
        self.alarm_status = alarm_status

        if self.trans:
            self.curState.exit()
            self.trans.execute()
            self.setstate(self.trans.toState)
            self.curState.enter()
            self.trans = None

        output = self.curState.execute()

        return output
