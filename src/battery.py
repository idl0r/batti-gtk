'''
@author: Arthur Spitzer <arthapex@gmail.com>
'''
import gettext
import gtk

from Notificator import Notificator


_ = lambda msg: gettext.dgettext('batti', msg)


class Battery(object):
    
    def __init__(self):
        self.__systray = gtk.StatusIcon()
        self.__notifer = Notificator()
        
        self.__shown_on_ac = False
        self.__shown_on_bat = False
        self.__shown_bat_low = False
        self.__shown_bat_critical = False
        self.__shown_bat_charged = False
        self.__show_notify = True
        
        self._set_icon_visibility(True)
        
        
    def __del__(self):
        self._set_icon_visibility(False)
        del self.__systray
    
    
    def destroy(self):
        self.__del__()
    
        
    def update(self):
        pass
    
    
    def set_left_popup_menu_action(self, menu_action):
        self.__systray.connect('button_press_event', menu_action)
        

    def set_value(self, charging, discharging, level, remaining_time):
        if charging:
            self.__systray.set_tooltip(_("On AC (Charging) \nBattery Level: %s%%") % level)
            if level >= 100:
                self.__set_tray_icon('batti-charging-100')
            elif level >= 80:
                self.__set_tray_icon('batti-charging-080')
            elif level >= 60:
                self.__set_tray_icon('batti-charging-060')
            elif level >= 40:
                self.__set_tray_icon('batti-charging-040')
            elif level >= 20:
                self.__set_tray_icon('batti-charging-020')
            else:
                self.__set_tray_icon('batti-charging-000')
            self.__systray.set_blinking(False)
            self.__shown_bat_critical = False
            self.__shown_bat_low = False
            if not self.__shown_on_ac:
                self._notify(False, 'battery_plugged', _("On AC"), _("You are currently running on AC"))
                self.__shown_on_ac = True
                self.__shown_on_bat = False
                
        elif discharging:
            self.__systray.set_tooltip(_("Battery Level: %s%% \nTime remaining %s") % (level, remaining_time))
            self.__shown_bat_charged = False
            if not self.__shown_on_bat:
                self._notify(False, 'battery_full', _("On Battery"), _("AC adapter unplugged, running on battery"))
                self.__shown_on_ac = False
                self.__shown_on_bat = True
            if level >= 100:
                self.__set_tray_icon('batti-100')
            elif level >= 80:
                self.__set_tray_icon('batti-080')
            elif level >= 60:
                self.__set_tray_icon('batti-060')
            elif level >= 40:
                self.__set_tray_icon('batti-040')
            elif level >= 20:
                self.__set_tray_icon('batti-020')
            elif level >= 10:
                self.__set_tray_icon('batti-000')
                if not self.__shown_bat_low:
                    self._notify(True, 'batti-000', _("Low Battery"), _("You have approximately <b>%s</b> remaining") % remaining_time)
                    self.__shown_bat_low = True
            else:
                self.__set_tray_icon('batti-empty')
                self.__systray.set_blinking(True)
                if not self.__shown_bat_critical:
                    self._notify(True, "batti-empty", _("Critical Battery"), _("You have approximately <b>%s</b> remaining") % remaining_time)
                    self.__shown_bat_critical = True
                    
        elif not self.__shown_bat_charged:
            self.__systray.set_tooltip(_("Charged\nApproximatery %s remaining") % remaining_time)
            self.__set_tray_icon('batti-charged')
            self._notify(False, 'batti-charged', _('Battery charged'), _("Approximately <b>%s</b> remaining") % remaining_time)
            self.__shown_bat_charged = True
    
    
    def __set_tray_icon(self, icon_name):
        self.__systray.set_from_icon_name(icon_name)
    
    
    def _set_icon_visibility(self, visible):
        self.__systray.set_visible(visible)
    
        
    def _notify(self, urgent, icon, subject, msg):
        if self.__show_notify:
            posrect = self.__systray.get_geometry()[1]
            posx = posrect.x + posrect.width/2
            posy = posrect.y + posrect.height
            self.__notifer.setPosition(posx, posy)
            if urgent:
                self.__notifer.show_urgent(icon, subject, msg)
            else: 
                self.__notifer.show(icon, subject, msg)
    
    
    def set_notification_enabled(self, enabled):
        self.__show_notify = enabled
        
        
    def get_notification_enabled(self):
        return self.__show_notify
    
    
    def _str_time(self, seconds):
        if seconds < 0:
            return _('unknown')
       
        minutes = seconds / 60
        hours = minutes / 60
        minutes = minutes % 60                    
       
        #FIXME: The string below needs to be i18n-ized properly
        return self._format_time(hours, "Hour", "Hours") + " " + self._format_time(minutes, "Minute", "Minutes")


    def _format_time(self, time, singular, plural):
        if time == 0:
            return ""
        elif time == 1:
            return "1 %s" % singular
        else:
            return "%s %s" % (time, plural)
        
 


class DeviceKitBattery(Battery):
    
    dbus_iface = 'org.freedesktop.DeviceKit.Power.Device'
    
    def __init__(self, property_iface, device_iface):
        Battery.__init__(self)
        self.__properties = property_iface
        self.__device = device_iface
        self.__signal_id = self.__device.connect_to_signal('Changed', self.__on_property_modified)
     
     
    def __del__(self):
        self.__signal_id.remove()
        Battery.__del__(self)
    
    
    def update(self):
        self.__on_property_modified()
    
    
    def __on_property_modified(self):
        
        present = self.__properties.Get(self.dbus_iface, 'is-present')
        self._set_icon_visibility(present)

        #XXX: check if the battery is rechargable first
        state = self.__properties.Get(self.dbus_iface, 'state')
        if state == 1:
            is_charging = True
            is_discharging = False
            remaining_time = self.__properties.Get(self.dbus_iface, 'time-to-full')
        elif state == 2:
            is_charging = False
            is_discharging = True
            remaining_time = self.__properties.Get(self.dbus_iface, 'time-to-empty')
        else:
            is_charging = False
            is_discharging = False
            remaining_time = self.__properties.Get(self.dbus_iface, 'time-to-empty')
   
        charge_level = self.__properties.Get(self.dbus_iface, 'percentage')

        remaining_time_str = self._str_time(remaining_time)
        
        self.set_value(is_charging, is_discharging, charge_level, remaining_time_str)




class UPowerBattery(Battery):
    
    dbus_iface = 'org.freedesktop.UPower.Device'
    
    def __init__(self, property_iface, device_iface):
        Battery.__init__(self)
        self.__properties = property_iface
        self.__device = device_iface
        self.__signal_id = self.__device.connect_to_signal('Changed', self.__on_property_modified)
     
     
    def __del__(self):
        self.__signal_id.remove()
        Battery.__del__(self)
    
    
    def update(self):
        self.__on_property_modified()
    
    
    def __on_property_modified(self):
        
        present = self.__properties.Get(self.dbus_iface, 'IsPresent')
        self._set_icon_visibility(present)

        #XXX: check if the battery is rechargable first
        state = self.__properties.Get(self.dbus_iface, 'State')
        if state == 1:
            is_charging = True
            is_discharging = False
            remaining_time = self.__properties.Get(self.dbus_iface, 'TimeToFull')
        elif state == 2:
            is_charging = False
            is_discharging = True
            remaining_time = self.__properties.Get(self.dbus_iface, 'TimeToEmpty')
        else:
            is_charging = False
            is_discharging = False
            remaining_time = 0
   
        charge_level = self.__properties.Get(self.dbus_iface, 'Percentage')

        remaining_time_str = self._str_time(remaining_time)
        
        self.set_value(is_charging, is_discharging, charge_level, remaining_time_str)
