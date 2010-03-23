'''
@author: Arthur Spitzer <arthapex@gmail.com>
'''

import dbus

from battery import HalBattery
from dbus.exceptions import DBusException

class PowerBackend(object):
    
    def set_popup_menu_action(self, action):
        pass

class HalBackend(PowerBackend):
    
    dbus_service = 'org.freedesktop.Hal'
    dbus_object = '/org/freedesktop/Hal/Manager'
    dbus_interface = 'org.freedesktop.Hal.Manager'
    bat_capability = 'battery'
    
    def __init__(self):
        self.__menu = None
        
        self.__bus = dbus.SystemBus()
        hal_obj = self.__bus.get_object(self.dbus_service, self.dbus_object)
        self.hal = dbus.Interface(hal_obj, self.dbus_interface)
        udis = self.hal.FindDeviceByCapability(self.bat_capability)
   
        self.__batteries = {}
        for udi in udis:
            #halbat = HalBattery(self.__get_battery(udi))
            self.__batteries[udi] = HalBattery(self.__get_battery(udi))
            #del halbat
        
        self.__bus.add_signal_receiver(self.__device_added, 'DeviceAdded',
             self.dbus_interface, self.dbus_service, self.dbus_object)
        self.__bus.add_signal_receiver(self.__device_removed, 'DeviceRemoved',
             self.dbus_interface, self.dbus_service, self.dbus_object)
        self.__popup_action = None
    
    
    def __get_battery(self, udi):
        battery_obj = self.__bus.get_object(self.dbus_service, udi)
        return dbus.Interface(battery_obj, 'org.freedesktop.Hal.Device')
            
    
    def set_popup_menu_action(self, action):
        self.__popup_action = action
        for bat in self.__batteries.itervalues():
            bat.set_popup_menu_action(action)
            
            
    def __device_added(self, udi):
        bat = self.__get_battery(udi)
        try:
            if bat.QueryCapability(self.bat_capability):
                halbat = HalBattery(bat)
                halbat.set_popup_menu_action(self.__popup_action)
                halbat.update()
                self.__batteries[udi] = halbat
        except DBusException:
            pass
    
    
    def __device_removed(self, udi):
        try:
            halbat = self.__batteries.pop(udi)
            halbat.destroy()
        except KeyError:
            pass
    
    
    def update_batteries(self, startup=False):
        for bat in self.__batteries.itervalues():
            notvis = bat.get_notification_enabled()
            if startup:
                bat.set_notification_enabled(False)
            bat.update()
            bat.set_notification_enabled(notvis)
    