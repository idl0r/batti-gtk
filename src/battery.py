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
        self.__show_notify = True
        
        self._set_icon_visibility(True)
        
        
    def __del__(self):
        self._set_icon_visibility(False)
        del self.__systray
    
    
    def destroy(self):
        self.__del__()
    
        
    def update(self):
        pass
    
        
    def set_popup_menu_action(self, menu_action):
        self.__systray.connect('popup_menu', menu_action)


    def set_value(self, charging, discharging, level, remaining_time):
        if charging:
            self.__systray.set_tooltip(_("On AC (Charging) \nBattery Level: %s%%") % level)
            self.__set_tray_icon('battery_plugged')
            self.__systray.set_blinking(False)
            self.__shown_bat_critical = False
            self.__shown_bat_low = False
            if not self.__shown_on_ac:
                self._notify(False, 'battery_plugged', _("On AC"), _("You are currently running on AC"))
                self.__shown_on_ac = True
                self.__shown_on_bat = False
        elif discharging:
            self.__systray.set_tooltip(_("Battery Level: %s%% \nTime remaining %s") % (level, remaining_time))
            if not self.__shown_on_bat:
                self._notify(False, 'battery_full', _("On Battery"), _("AC adapter unplugged, running on battery"))
                self.__shown_on_ac = False
                self.__shown_on_bat = True
            if level > 90:
                self.__set_tray_icon('battery_full')
            elif level > 75:
                self.__set_tray_icon('battery_third_fourth')
            elif level > 67:
                self.__set_tray_icon('battery_two_thirds')
            elif level > 33:
                self.__set_tray_icon('battery-low')
            elif level > 10:
                self.__set_tray_icon('battery-caution')
            elif level > 5:
                self.__set_tray_icon('battery_empty')
                if not self.__shown_bat_low:
                    self._notify(True, 'battery_empty', _("Low Battery"), _("You have approximately <b>%s</b> remaining") % remaining_time)
                    self.__shown_bat_low = True
            else:
                self.__set_tray_icon('battery_empty')
                self.__systray.set_blinking(True)
                if not self.__shown_bat_critical:
                    self._notify(True, "battery_empty", _("Critical Battery"), _("You have approximately <b>%s</b> remaining") % remaining_time)
                    self.__shown_bat_critical = True
        else:
            self.__systray.set_tooltip(_("On AC \nBattery Level: %s%%") % level)
            self.__set_tray_icon('battery_plugged')
    
    
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
        
        
class HalBattery(Battery):
    
    def __init__(self, battery):
        Battery.__init__(self)
        self.__battery = battery
        self.__signal_id = self.__battery.connect_to_signal('PropertyModified', self.__on_property_modified)
        #self.remaining_time = _('unknown')

    def __del__(self):
        self.__signal_id.remove()
        Battery.__del__(self)
    
    
    def update(self):
        self.__on_property_modified(0, None)
    
    
    def __on_property_modified(self, num_changes, property):
        present = self.__battery.GetProperty('battery.present')
        self._set_icon_visibility(present)

        #XXX: check if the battery is rechargable first
        is_charging = self.__battery.GetProperty('battery.rechargeable.is_charging')
                   
        is_discharging = self.__battery.GetProperty('battery.rechargeable.is_discharging')

        charge_level = self.__battery.GetProperty('battery.charge_level.percentage')

        remaining_time = -1
        if is_discharging:
            remaining_time = self.__battery.GetProperty('battery.remaining_time')

        remaining_time_str = self.__str_time(remaining_time)
        
        self.set_value(is_charging, is_discharging, charge_level, remaining_time_str)
    
    
    def __str_time(self, seconds):
        if seconds < 0:
            return _('unknown')
       
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
        