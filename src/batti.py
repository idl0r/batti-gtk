#!/usr/bin/env python

import dbus
import dbus.glib
import dbus.service

#import pygtk
import gtk
#import gobject
from optparse import OptionParser
import os,sys
from Notificator import Notificator

import gettext

_ = lambda msg: gettext.dgettext('batterymon', msg)

## code modules



#{{{ Program defaults
VERSION="1.1.2"
#}}}

# --- DBus constants
dbusObject    = '/org/gitorious/battery-monitor'
dbusService   = 'org.gitorious.battery-monitor'
dbusInterface = 'org.gitorious.battery-monitor.Interface'


# {{{ DBUSObject
class DBusObject:
    def __init__(self):
        self.bus = dbus.SystemBus()
        hal_obj = self.bus.get_object('org.freedesktop.Hal', '/org/freedesktop/Hal/Manager')
        self.hal = dbus.Interface(hal_obj, 'org.freedesktop.Hal.Manager')
#}}}

# {{{ AcAdapter
class AcAdapter(DBusObject):
    def __init__(self):
        DBusObject.__init__(self)
        self.property_modified_handler = None

        udis = self.hal.FindDeviceByCapability('ac_adapter')

        if len(udis) == 0:
            raise Exception("No AC adapter found")

        # take the first adapter
        adapter_obj = self.bus.get_object('org.freedesktop.Hal', udis[0])
        self.__adapter = dbus.Interface(adapter_obj, 'org.freedesktop.Hal.Device')
        self.__adapter.connect_to_signal('PropertyModified', self.__on_property_modified)

    def update(self):
        present = self.__adapter.GetProperty('ac_adapter.present')

        if self.property_modified_handler:
            self.property_modified_handler(present)


    def __on_property_modified(self, num_changes, property):
        property_name, added, removed = property[0] #@UnusedVariable

        if property_name != "ac_adapter.present":
            return

        self.update()
#}}}

# {{{ BatteryDetector
class BatteryDetector(DBusObject):
    def __init__(self):
        DBusObject.__init__(self)

    def get_all(self):
        udis = self.hal.FindDeviceByCapability('battery')
   
        batteries = []

        for udi in udis:
            battery_obj = self.bus.get_object('org.freedesktop.Hal', udi)
            battery = dbus.Interface(battery_obj, 'org.freedesktop.Hal.Device')

            batteries.append(Battery(battery))

        return batteries
#}}}

# {{{ Battery
class Battery:
    def __init__(self, battery):
        self.property_modified_handler = None
        self.__battery = battery
        self.__battery.connect_to_signal('PropertyModified', self.__on_property_modified)
        self.remaining_time = "unknown"  ## added this or the program crashes on a full battery
       
    def __on_property_modified(self, num_changes, property):
        #property_name, added, removed = property[0]
        self.update()

    def update(self):
        present = self.__battery.GetProperty('battery.present')

        #XXX: check if the battery is rechargable first
        is_charging = self.__battery.GetProperty('battery.rechargeable.is_charging')
                   
        is_discharging = self.__battery.GetProperty('battery.rechargeable.is_discharging')

        charge_level = self.__battery.GetProperty('battery.charge_level.percentage')

        try:
            remaining_time = self.__battery.GetProperty('battery.remaining_time')
        except dbus.DBusException:
            remaining_time = -1

        remaining_time = self.__str_time(remaining_time)

        if self.property_modified_handler:
            self.property_modified_handler(BatteryInfo(charge_level, remaining_time, is_charging, is_discharging, present))

    def __str_time(self, seconds):
        if seconds < 0:
            return 'Unknown'
       
        minutes = seconds / 60
       
        hours = minutes / 60
        minutes = minutes % 60                    
       
        #FIXME: The string below needs to be i18n-ized properly
        return self.__format_time(hours, "Hour", "Hours") + " " + self.__format_time(minutes, "Minute", "Minutes")

    def __format_time(self, time, singular, plural):
        if time == 0:
            return ""
        elif time == 1:
            return "1 %s" % singular
        else:
            return "%s %s" % (time, plural)


#}}}


# {{{ PowerEventListener
class PowerEventListener(object):
    def ac_property_modified(self, present):
        pass

    def battery_property_modified(self, battery_info):
        pass
#}}}

# {{{ BatteryInfo
class BatteryInfo:
    def __init__(self, charge_level, remaining_time, is_charging, is_discharging, present):
        self.charge_level = charge_level
        self.remaining_time = remaining_time
        self.is_charging = is_charging
        self.is_discharging = is_discharging
        self.present = present
# }}}

# {{{ Systray
class Systray(PowerEventListener):
    def __init__(self):
        self.tray_object= gtk.StatusIcon()
        self.tray_object.set_visible(False)
        #self.set_icon("full")
        self.tray_object.set_blinking(False)
        self.tray_object.connect("popup_menu", self.rightclick_menu)
        
        self.show_trayicon(1) ## fixed to one for now
        
    
    def show_trayicon(self,value):
        setting = value
        ### only changing on startup
       
        if setting == 3 : ## only show if charing or discharging
            self.tray_object.set_visible(False)
            return
            
        if setting == 1: ### always show an icon
                self.tray_object.set_visible(True)
                return
       
        if setting == 2: ## only show when discharging
            self.tray_object.set_visible(True)    
              
            return
    
    def getPosition(self):
        posrect = self.tray_object.get_geometry()[1]
        posx = posrect.x + posrect.width/2
        posy = posrect.y + posrect.height
        return (posx, posy)


    def battery_property_modified(self, battery):
        
        if battery.is_charging:       
            self.tray_object.set_tooltip(_("On AC (Charging) \nBattery Level: %s%%") % battery.charge_level)

        elif battery.is_discharging:
            
            self.tray_object.set_tooltip(_("Battery Level: %s%% \nTime remaining %s") % (battery.charge_level, battery.remaining_time))

        else:
            self.tray_object.set_tooltip(_("On AC \nBattery Level: %s%%") % battery.charge_level)
        
        if battery.is_charging == 0 and battery.is_discharging == 0 :
            
            self.set_icon("battery_charged")
            return
        
                  
        if battery.charge_level > 90:
            if battery.is_charging ==0:
                self.set_icon("battery_full")                
            else:
                self.set_icon("battery_plugged")
                self.tray_object.set_blinking(False)                                      

        elif battery.charge_level > 75:
            if battery.is_charging ==0:
                self.set_icon("battery_third_fourth")
            else:
                self.set_icon("battery_plugged")

        elif battery.charge_level > 64:
            if battery.is_charging ==0:
                self.set_icon("battery_two_thirds")
            else:
                self.set_icon("battery_plugged")

        elif battery.charge_level > 36:
            if battery.is_charging ==0:
                self.set_icon("battery-low")
            else:    
                self.set_icon("battery_plugged")

        elif battery.charge_level > 10:
            if battery.is_charging ==0:
                self.set_icon("battery-caution")
            else:
                self.set_icon("battery_plugged")

        elif battery.charge_level > 5:
            if battery.is_charging ==0:
                self.set_icon("battery_empty")
            else:
                self.set_icon("battery_plugged")

        else:
            if battery.is_charging ==0:
                self.set_icon("battery_empty")
                self.tray_object.set_blinking(True)
            else:
                self.tray_object.set_blinking(False)
                self.set_icon("battery_plugged")
        return
        
        
            
    def rightclick_menu(self, button, widget, event):
        menu = gtk.Menu()
        about_menu = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
        about_menu.connect('activate', self.about)
        exit_menu = gtk.ImageMenuItem(gtk.STOCK_CLOSE)
        exit_menu.connect('activate', self.close)        
        menu.append(about_menu)
        #menu.append(pref_menu)
        menu.append(exit_menu)
        menu.show_all()           
        menu.popup(None, None, None, 2, event)
    
        
    
    def close(self,button):
        sys.exit(0)
    
        
        
    def about(self, button):
        about_dg = gtk.AboutDialog()
        about_dg.set_name(_("Battery Monitor"))
        about_dg.set_version(VERSION)
        about_dg.set_authors(["Matthew Horsell", "Tomas Kramar"])
        about_dg.connect("response", lambda d, r: d.destroy())
        about_dg.show()
       
    def set_icon(self,name):
        self.tray_object.set_from_icon_name(name)
        self.Icon_name = name
   
#}}}

#{{{ commandline
class commandline:
    def passargs(self,arg):
       
        parser = OptionParser(usage='usage: %prog [options] ', version=VERSION, description="Simple Battery Monitor")  
        parser.add_option("-n", "--notify-at", action="store", help="notify me when battery level is lower than the provided value", dest="notification_level", default="90")
        parser.add_option("-c", "--critical", action="store", help="set critical level", dest="critical_level", default="5")
        parser.add_option("-e", "--on-critical", action="store", help="run this command on critical power level", dest="critical_command", default=None)
        parser.add_option("-d", "--debug"      , action="store_true",help="run in debug mode" , dest="debug", default=False)
        (options, args) = parser.parse_args() #@UnusedVariable
       
        if arg=="none":
            parser.print_help()
        return options
    
#}}}

# {{{ PowerManager
class PowerManager:
    def __init__(self):
        self.listeners = []
        self.adapter = AcAdapter()
        self.batteries = BatteryDetector().get_all()

        self.adapter.property_modified_handler = self.__ac_property_modified_handler

        for battery in self.batteries:
            battery.property_modified_handler = self.__battery_property_modified_handler

    def __ac_property_modified_handler(self, present):
        for listener in self.listeners:
            listener.ac_property_modified(present)

    def __battery_property_modified_handler(self, battery):
        for listener in self.listeners:
            listener.battery_property_modified(battery)

    def update(self):
        for battery in self.batteries:
            battery.update()

# }}}


#{{{ CommandRunner
class CommandRunner(PowerEventListener):
    def __init__(self, power_level, command):
        self.power_level = power_level
        self.command = command

    def battery_property_modified(self, battery):
                
        if int(battery.charge_level) <= int(self.power_level) and self.command:
            os.system(self.command)
#}}}

class BatteryMonitor(PowerEventListener):
    def __init__(self):
        options = commandline()
        
        cmdline = options.passargs("");
        
        self.__systray = Systray()
        executor = CommandRunner(int(cmdline.critical_level), cmdline.critical_command)
        
        self.low_level = int(cmdline.notification_level)
        self.notified = False
        self.critical_level = int(cmdline.critical_level)
        self.critically_notified = False
        self.notifer = None
        
        pm = PowerManager()
        pm.listeners.append(self)
        pm.listeners.append(self.__systray)
        pm.listeners.append(executor)
        pm.update()


    def getNotifer(self):
        if self.notifer is None:
            self.notifer = Notificator()
            self.notifer.setDuration(2000) 
        return self.notifer


    def ac_property_modified(self, present):
        (px, py) = self.__systray.getPosition()
        notif = self.getNotifer()
        notif.setPosition(px, py)
        if present:            
            notif.show("battery_plugged", _("On AC"), _("You are currently running on AC"))
        else:            
            notif.show("battery_full", _("On Battery"), _("AC adapter unplugged, running on battery"))


    def battery_property_modified(self, battery):
        (px, py) = self.__systray.getPosition()
        notif = self.getNotifer()
        notif.setPosition(px, py)
        if battery.charge_level <= self.low_level and not self.notified:
            notif.show("battery_empty", _("Low Battery"), _("You have approximately <b>%s</b> remaining") % battery.remaining_time)
            self.notified = True

        if battery.charge_level <= self.critical_level and not self.critically_notified:
            notif.show("battery_empty", _("Critical Battery"), _("You have approximately <b>%s</b> remaining") % battery.remaining_time)
            self.critically_notified = True


        if battery.is_charging and battery.charge_level > self.critical_level:
            self.critically_notified = False

        if battery.is_charging and battery.charge_level > self.low_level:
            self.notify = False

    
    def main(self):
        #gobject.threads_init()
        try:
            gtk.main()
        except KeyboardInterrupt:
            pass


    def quit(self, widget):
        gtk.main_quit()

 
if __name__ == "__main__":
    sessionBus = dbus.SessionBus()
    activeServices = sessionBus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus').ListNames()

    if not dbusService in activeServices:
        busName = dbus.service.BusName(dbusService, bus=sessionBus)
        bmon = BatteryMonitor()
        bmon.main()
    else:
        print 'Another instance of battery-monitor is already running.'
