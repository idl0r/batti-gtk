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
        self.__duration = 3000
        self.__name = 'battery-monitor'
        
        
    def show(self, icon, subject, msg):
        hints = {'urgency':dbus.Byte(0), 'desktop-entry':dbus.String('battery-monitor')}
        if( self.__posx >= 0 and self.__posy >= 0 ):
            hints['x'] = self.__posx
            hints['y'] = self.__posy
        self.__last_id = self.__notify.Notify(self.__name, self.__last_id, icon, subject, msg, [], hints, self.__duration)


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
        '''
        Set the duration on a notification with milSec milliseconds
        '''
        self.__duration = milSec
        
        