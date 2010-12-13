
'''
    This file is part of batti, a battery monitor for the system tray.
    Copyright (C) 2010  Arthur Spitzer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from Battery import DeviceKitBattery
from Battery import UPowerBattery
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
        iface = self.__get_interface()
        devices = iface.EnumerateDevices()
        
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
        
        properties = dbus.Interface(iface, 'org.freedesktop.DBus.Properties')

        if properties.Get(self.dbus_interface, 'CanSuspend'):
            self.__can_suspend = True
        else:
            self.__can_suspend = False
        
        if properties.Get(self.dbus_interface, 'CanHibernate'):
            self.__can_hibernate = True
        else:
            self.__can_hibernate = False
    
    
    def __get_interface(self):
        dkit_obj = self.__bus.get_object(self.dbus_service, self.dbus_object)
        return dbus.Interface(dkit_obj, self.dbus_interface)
    
    
    def __mc_action(self, widget, event, data=None):
        if not self.__mc_action is None:
            self.__mc_action(widget, event, data)
            
         
    def can_suspend(self):   
        return self.__can_suspend and self.__get_interface().SuspendAllowed()

    def can_hibernate(self):
        return self.__can_hibernate and self.__get_interface().HibernateAllowed()

    def suspend(self):
        self.__get_interface().Suspend()

    def hibernate(self):
        self.__get_interface().Hibernate()


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
            bat = self.__batteries.pop(udi)
            bat.destroy()
        except KeyError:
            pass
    
    
    def update_batteries(self, startup=False):
        for bat in self.__batteries.itervalues():
            notvis = bat.get_notification_enabled()
            if startup:
                bat.set_notification_enabled(False)
            bat.update()
            bat.set_notification_enabled(notvis)
    
