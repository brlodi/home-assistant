import appdaemon.plugins.hass.hassapi as hass
from advanced_presence_states import AdvancedPresence

class PresenceBasedLighting(hass.Hass):
    ENTRYWAY_DELAY = 150
    
    
    def initialize(self):
        self.entryway_timer = None
        self.entryway_brightness = None
        
        # When front door opens, turn on the light in the entryway
        self.listen_state(self.turn_on_entryway_light,
                          entity='binary_sensor.front_door_access_control',
                          new='on')

        for entity in self.args['presence_indicators']:
            # When arriving home, turn on the light in the entryway
            self.listen_state(self.turn_on_entryway_light,
                              entity=entity,
                              new=AdvancedPresence.STATE_ARRIVED)
            # When arriving home, turn on the living room lights
            self.listen_state(self.turn_on_living_room_lights,
                              entity=entity,
                              new=AdvancedPresence.STATE_ARRIVED)

        # When the front door closes, start a timer to return the entryway light to its previous
        # state
        self.listen_state(self.delay_entryway_light,
                          entity='binary_sensor.front_door_access_control',
                          old='on', new='off')


    # TODO: make this more generic and modular by passing target light(s) as argument
    def turn_on_entryway_light(self, entity, attribute, old, new, kwargs):
        if self.entryway_timer:
            # If the timer was already scheduled by something else, reset it
            self.cancel_timer(self.entryway_timer)
            self.entryway_timer = None
        else:
            self.entryway_brightness = self.get_state('light.entryway', attribute='brightness')
            self.turn_on('light.entryway', brightness=254) # TODO: brightness based on time of day


    def delay_entryway_light(self, entity, attribute, old, new, kwargs):
        self.entryway_timer = self.run_in(self.reset_entryway_light, self.ENTRYWAY_DELAY)


    def reset_entryway_light(self, kwargs):
        self.entryway_timer = None
        if self.entryway_brightness == None:
            # Light was off
            self.turn_off('light.entryway')
        else:
            self.turn_on('light.entryway', brightness=self.entryway_brightness)
        self.entryway_brightness = None


    def turn_on_living_room_lights(self, entity, attribute, old, new, kwargs):
        target_brightness = round(max(0, -float(self.get_state('sensor.circadian_values'))) * 2.55)
        if target_brightness >= 38:
            self.turn_on('light.living_room_dimmer', brightness=target_brightness)
            self.turn_on('light.dining_nook_dimmer', brightness=target_brightness)
            self.turn_on('light.living_room_ceiling_light')
