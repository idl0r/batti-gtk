
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

import gettext
import gtk

from Notificator import Notificator


_ = lambda msg: gettext.dgettext('batti', msg)

# battery power state
( 
    STATE_UNKNOWN,
    STATE_CHARGING,
    STATE_DISCHARGING,
    STATE_EMPTY,
    STATE_CHARGED,
) = range(5)


class BatteryInfo(object):
    
    def __init__(self, present=True, state=STATE_UNKNOWN, percentage=0, time=0):
        self._present = present
        self._state = state
        self._percentage = percentage
        self._time = time


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
  
  
    def set_value(self, info):
        
        self._set_icon_visibility(info._present)
        
        if info._time == 0:
            tooltip = _("Battery Level: %s%%") % (info._percentage)
            notification = tooltip
        else:
            tooltip = _("Battery Level: %s%\% \nApproximately %s remaining") % (info._percentage, self._str_time(info._time))
            notification = _("Approximately <b>%s</b> remaining") % self._str_time(info._time)
        
        if info._state == STATE_CHARGING:
            self.__systray.set_tooltip(_("Charging this battery \nBattery Level: %s%%") % info._percentage)
            if info._percentage >= 100:
                self.__set_tray_icon('batti-charging-100')
            elif info._percentage >= 80:
                self.__set_tray_icon('batti-charging-080')
            elif info._percentage >= 60:
                self.__set_tray_icon('batti-charging-060')
            elif info._percentage >= 40:
                self.__set_tray_icon('batti-charging-040')
            elif info._percentage >= 20:
                self.__set_tray_icon('batti-charging-020')
            else:
                self.__set_tray_icon('batti-charging-000')
            self.__systray.set_blinking(False)
            self.__shown_bat_critical = False
            self.__shown_bat_low = False
            if not self.__shown_on_ac:
                self._notify(False, 'battery_plugged', _('Charging this battery'), _("You are currently running on AC"))
                self.__shown_on_ac = True
                self.__shown_on_bat = False
                
        elif info._state == STATE_DISCHARGING:
            self.__systray.set_tooltip(tooltip)
            self.__shown_bat_charged = False
            if not self.__shown_on_bat:
                self._notify(False, 'battery_full', _("On Battery"), _("AC adapter unplugged, running on battery"))
                self.__shown_on_ac = False
                self.__shown_on_bat = True
            if info._percentage >= 100:
                self.__set_tray_icon('batti-100')
            elif info._percentage >= 80:
                self.__set_tray_icon('batti-080')
            elif info._percentage >= 60:
                self.__set_tray_icon('batti-060')
            elif info._percentage >= 40:
                self.__set_tray_icon('batti-040')
            elif info._percentage >= 20:
                self.__set_tray_icon('batti-020')
            elif info._percentage >= 10:
                self.__set_tray_icon('batti-000')
                if not self.__shown_bat_low:
                    self._notify(True, 'batti-000', _("Low Battery"), notification)
                    self.__shown_bat_low = True
            else:
                self.__set_tray_icon('batti-empty')
                self.__systray.set_blinking(True)
                if not self.__shown_bat_critical:
                    self._notify(True, "batti-empty", _("Critical Battery"), notification)
                    self.__shown_bat_critical = True
                    
        elif (not self.__shown_bat_charged) and (info._state == STATE_CHARGED):
            self.__systray.set_tooltip(_("Charged\n%s") % tooltip)
            self.__set_tray_icon('batti-charged')
            self._notify(False, 'batti-charged', _('Battery charged'), notification)
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
        return self._format_time(hours, _('Hour'), _('Hours')) + " " + self._format_time(minutes, _('Minute'), _('Minutes'))


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
        
        info = BatteryInfo()
        
        
        info._present = self.__properties.Get(self.dbus_iface, 'is-present')

        #XXX: check if the battery is rechargable first
        state = self.__properties.Get(self.dbus_iface, 'state')
        if state == 1:
            info._state = STATE_CHARGING
        elif state == 2:
            info._state = STATE_DISCHARGING
        else:
            info._state = STATE_UNKNOWN
        
        info._time = self.__properties.Get(self.dbus_iface, 'time-to-empty')
   
        charge_level = self.__properties.Get(self.dbus_iface, 'percentage')
        info._percentage = int(float(str(charge_level)))

        self.set_value(info)




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
        
        info = BatteryInfo()
        
        present = self.__properties.Get(self.dbus_iface, 'IsPresent')
        self._set_icon_visibility(present)
        info._present = present

        state = self.__properties.Get(self.dbus_iface, 'State')

        if state == 1:
            info._state = STATE_CHARGING
        elif state == 2:
            info._state = STATE_DISCHARGING
        elif state == 3:
            info._state = STATE_EMPTY
        elif state == 4:
            info._state = STATE_CHARGED
        else:
            info._state = STATE_UNKNOWN
        
        info._time = self.__properties.Get(self.dbus_iface, 'TimeToEmpty')
   
        precise_charge = self.__properties.Get(self.dbus_iface, 'Percentage')
        info._percentage = int(float(str(precise_charge)))
        
        self.set_value(info)
