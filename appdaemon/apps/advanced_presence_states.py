import appdaemon.plugins.hass.hassapi as hass

class AdvancedPresence(hass.Hass):
    STATE_ARRIVED = 'Just Arrived'
    STATE_HOME = 'Home'
    STATE_DEPARTED = 'Just Departed'
    STATE_AWAY = 'Away'
    STATE_EXT_AWAY = 'Extended Absence'

    DUR_TRANSITIONAL = 5 * 60  # 5 minutes
    DUR_EXTENDED = 24 * 60 * 60 # 24 hours
    
    def initialize(self):
        self.output_entity = self.args['output_id']
        self.watched_trackers = self.args['trackers']

        # Assume away until one of the specified trackers is home
        self.set_state(self.output_entity, state=self.STATE_AWAY)
        
        # Register internal listeners (for transitioning between states based on time)
        self.listen_state(self.mark_home, entity=self.output_entity,
                          new=self.STATE_ARRIVED, duration=self.DUR_TRANSITIONAL)
        self.listen_state(self.mark_away, entity=self.output_entity,
                          new=self.STATE_DEPARTED, duration=self.DUR_TRANSITIONAL)
        self.listen_state(self.mark_extended_away, entity=self.output_entity,
                          new=self.STATE_AWAY, duration=self.DUR_EXTENDED)
        
        for tracker in self.watched_trackers:
            # If the tracker is currently home, set the output to home
            if self.get_state(tracker) == 'home':
                self.update_output_state(new_state=self.STATE_HOME)
            
            # Register the trackers
            self.listen_state(self.mark_just_arrived, entity=tracker, old='not_home', new='home')
            self.listen_state(self.mark_just_departed, entity=tracker, old='home', new='not_home')
            
    
    
    def update_output_state(self, new_state):
        self.set_state(self.output_entity, state=new_state)

    def mark_just_arrived(self, entity, attribute, old, new, kwargs):
        # If the output was just 'Just Departed' we assume the departure was a false location and
        # jump straight to 'Home'. This avoids running arrival automations if a tracker disappears
        # and reappears or you just step outside for a minute.
        if self.get_state(self.output_entity) == self.STATE_DEPARTED:
            self.update_output_state(new_state=self.STATE_HOME)
        else:
            self.update_output_state(new_state=self.STATE_ARRIVED)

    def mark_home(self, entity, attribute, old, new, kwargs):
        self.update_output_state(new_state=self.STATE_HOME)

    def mark_just_departed(self, entity, attribute, old, new, kwargs):
        self.update_output_state(new_state=self.STATE_DEPARTED)

    def mark_away(self, entity, attribute, old, new, kwargs):
        self.update_output_state(new_state=self.STATE_AWAY)

    def mark_extended_away(self, entity, attribute, old, new, kwargs):
        self.update_output_state(new_state=self.STATE_EXT_AWAY)

