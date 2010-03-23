'''
Created on 01.03.2010

@author: Arthur Spitzer
'''

import dbus

class Notificator:
    
    def __init__(self):
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
        if self.__last_id:
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
        
        