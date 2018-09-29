import appdaemon.plugins.hass.hassapi as hass

class PrepareHomeKit(hass.Hass):

  def initialize(self):
    self.generate_switches_for_scenes()
    
    # Wait for ZWave network to be ready before starting HomeKit, otherwise HK
    # will delete all ZWave entities that haven't been initialized yet
    self.listen_event(self.start_homekit, 'zwave.network_ready')
  
  def generate_switches_for_scenes(self, **kwargs):
    for scene_name in self.entities.scene:
      switch_name = f'switch.activate_{scene_name}'
      self.set_state(switch_name, state = 'off')
      self.listen_state(self.activate_scene_by_switch, switch_name, new = 'on')
  
  def activate_scene_by_switch(self, **kwargs):
    switch = kwargs['entity_id']
    scene_name = switch.split('.')[1]
    self.set_state(switch, state = 'off')
    self.turn_on(f'scene.{scene_name}')
  
  def start_homekit(self, **kwargs):
    self.fire_event('AD_STARTUP_DONE')
