'''
@author: Arthur Spitzer <arthapex@gmail.com>
'''


from battery import DeviceKitBattery
from battery import UPowerBattery
import dbus
from dbus.exceptions import DBusException


class PowerBackend(object):
    
    def set_right_popup_menu_action(self, action):
        pass
    
    def can_suspend(self):
        pass
    
    def can_hibernate(self):
        pass

    def suspend(self):
        pass
    
    def hibernate(self):
        pass
    

class DeviceKitBackend(PowerBackend):
    
    dbus_service = 'org.freedesktop.DeviceKit.Power'
    dbus_object = '/org/freedesktop/DeviceKit/Power'
    dbus_interface = 'org.freedesktop.DeviceKit.Power'
    device_interface = 'org.freedesktop.DeviceKit.Power.Device'
    bat_type = 2
    
    def __init__(self):
        self.__rmenu = None
        
        self.__bus = dbus.SystemBus()
        dkit_obj = self.__bus.get_object(self.dbus_service, self.dbus_object)
        self.dkit = dbus.Interface(dkit_obj, self.dbus_interface)
        devices = self.dkit.EnumerateDevices()
        
        self.__batteries = {}
        for dev in devices:
            (prop_iface, dev_iface) = self.__get_battery(dev)
            type = prop_iface.Get(self.device_interface, 'type')
            if type == self.bat_type:
                power_bat = DeviceKitBattery(prop_iface, dev_iface)
                self.__batteries[dev] = power_bat
                power_bat.set_left_popup_menu_action(self.__mc_action)
                
        
        self.__bus.add_signal_receiver(self.__device_added, 'DeviceAdded',
             self.dbus_interface, self.dbus_service, self.dbus_object)
        self.__bus.add_signal_receiver(self.__device_removed, 'DeviceRemoved',
             self.dbus_interface, self.dbus_service, self.dbus_object)
        self.__mc_action = None
        

        properties = dbus.Interface(dkit_obj, 'org.freedesktop.DBus.Properties')

        if properties.Get(self.dbus_interface, 'can-suspend'):
            self.__can_suspend = True
        else:
            self.__can_suspend = False
           
        if properties.Get(self.dbus_interface, 'can-hibernate'):
            self.__can_hibernate = True
        else:
            self.__can_hibernate = False
            
    
    def __mc_action(self, widget, event, data=None):
        if not self.__mc_action is None:
            self.__mc_action(widget, event, data)
            
         
    def can_suspend(self):   
        return self.__can_suspend

    def can_hibernate(self):
        return self.__can_hibernate

    def suspend(self):
        self.dkit.Suspend()

    def hibernate(self):
        self.dkit.Hibernate()


    def __get_battery(self, udi):
        battery_obj = self.__bus.get_object(self.dbus_service, udi)
        prop_iface = dbus.Interface(battery_obj, 'org.freedesktop.DBus.Properties')
        dev_iface = dbus.Interface(battery_obj, self.device_interface)
        return (prop_iface, dev_iface)
            
    
    def set_right_popup_menu_action(self, action):
        self.__mc_action = action
            
            
    def __device_added(self, udi):
        (prop_iface, dev_iface) = self.__get_battery(udi)
        try:
            type = prop_iface.Get(self.device_interface, 'type')
            if type == self.bat_type:
                power_bat = DeviceKitBattery(prop_iface, dev_iface)
                power_bat.set_left_popup_menu_action(self.__mc_action)
                power_bat.update()
                self.__batteries[udi] = power_bat
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
    
    
    
class UPowerBackend(PowerBackend):
    
    dbus_service = 'org.freedesktop.UPower'
    dbus_object = '/org/freedesktop/UPower'
    dbus_interface = 'org.freedesktop.UPower'
    device_interface = 'org.freedesktop.UPower.Device'
    bat_type = 2
    
    def __init__(self):
        self.__rmenu = None
        
        self.__bus = dbus.SystemBus()
        dkit_obj = self.__bus.get_object(self.dbus_service, self.dbus_object)
        self.dkit = dbus.Interface(dkit_obj, self.dbus_interface)
        devices = self.dkit.EnumerateDevices()
        
        self.__batteries = {}
        for dev in devices:
            (prop_iface, dev_iface) = self.__get_battery(dev)
            type = prop_iface.Get(self.device_interface, 'type')
            if type == self.bat_type:
                power_bat = UPowerBattery(prop_iface, dev_iface)
                self.__batteries[dev] = power_bat
                power_bat.set_left_popup_menu_action(self.__mc_action)
                
        
        self.__bus.add_signal_receiver(self.__device_added, 'DeviceAdded',
             self.dbus_interface, self.dbus_service, self.dbus_object)
        self.__bus.add_signal_receiver(self.__device_removed, 'DeviceRemoved',
             self.dbus_interface, self.dbus_service, self.dbus_object)
        self.__mc_action = None
        
        if self.dkit.SuspendAllowed():
            self.__can_suspend = True
        else:
            self.__can_suspend = False
           
        if self.dkit.HibernateAllowed():
            self.__can_hibernate = True
        else:
            self.__can_hibernate = False
            
    
    def __mc_action(self, widget, event, data=None):
        if not self.__mc_action is None:
            self.__mc_action(widget, event, data)
            
         
    def can_suspend(self):   
        return self.__can_suspend

    def can_hibernate(self):
        return self.__can_hibernate

    def suspend(self):
        self.dkit.Suspend()

    def hibernate(self):
        self.dkit.Hibernate()


    def __get_battery(self, udi):
        battery_obj = self.__bus.get_object(self.dbus_service, udi)
        prop_iface = dbus.Interface(battery_obj, 'org.freedesktop.DBus.Properties')
        dev_iface = dbus.Interface(battery_obj, self.device_interface)
        return (prop_iface, dev_iface)
            
    
    def set_right_popup_menu_action(self, action):
        self.__mc_action = action
            
            
    def __device_added(self, udi):
        (prop_iface, dev_iface) = self.__get_battery(udi)
        try:
            type = prop_iface.Get(self.device_interface, 'type')
            if type == self.bat_type:
                power_bat = UPowerBattery(prop_iface, dev_iface)
                power_bat.set_left_popup_menu_action(self.__mc_action)
                power_bat.update()
                self.__batteries[udi] = power_bat
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
    