import appdaemon.plugins.hass.hassapi as hass

class PresenceActions(hass.Hass):
    
    def initialize(self):
        self.listen_state(self.arrival, entity='group.all_devices', new='home')
    
    def arrival(self):
        print('foo')
