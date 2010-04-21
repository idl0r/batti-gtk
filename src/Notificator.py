
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

import dbus
from dbus.exceptions import DBusException

class Notificator:
    
    def __init__(self):
        try:
            bus = dbus.SessionBus()
            obj = bus.get_object('org.freedesktop.Notifications', '/org/freedesktop/Notifications')
            self.__notify = dbus.Interface(obj, 'org.freedesktop.Notifications')
            self.__last_id = dbus.UInt32(0)
            self.__posx = -1
            self.__posy = -1
            self.__positioned = True
            self.__duration = 3000
            self.__name = 'batti'
            self.__check_capabilities()
        except DBusException:
            self.__notify = None
            self.__positioned = False


    def __check_capabilities(self):
        info = self.__notify.GetServerInformation()
        if info[0] == 'notify-osd':
            self.__positioned = False


    def __show_positioned(self):
        if self.__positioned:
            return (self.__posx >= 0 and self.__posy >= 0)
        else:
            return False


    def __show(self, icon, subject, msg, urgent):
        if self.__notify is not None:
            hints = {'urgency':dbus.Byte(urgent), 'desktop-entry':dbus.String('battery-monitor')}
            if( self.__show_positioned() ):
                hints['x'] = self.__posx
                hints['y'] = self.__posy
            self.__last_id = self.__notify.Notify(self.__name, self.__last_id, icon, subject, msg, [], hints, self.__duration)


    def show(self, icon, subject, msg):
        self.__show(icon, subject, msg, 1)


    def show_urgent(self, icon, subject, msg):
        self.__show(icon, subject, msg, 2)


    def close(self):
        if (self.__notify is not None) and self.__last_id:
            self.__notify.CloseNotification(self.__last_id)


    def setPosition(self, x, y):
        self.__posx = x
        self.__posy = y
    
    
    def removePosition(self):
        self.__posx = -1
        self.__posy = -1
        
    def setDuration(self, milSec):
        ''' Set the duration on a notification with milSec milliseconds '''
        self.__duration = milSec
        
        