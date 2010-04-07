'''
@author: Arthur Spitzer <arthapex@gmail.com>
'''

from dbus.exceptions import DBusException
from dbus.mainloop.glib import DBusGMainLoop
import gettext
import gtk

from PowerBackend import DeviceKitBackend

NAME = 'batti'
VERSION = '0.3'

_ = lambda msg: gettext.dgettext(NAME, msg)

class BatteryMonitor(object):
    def __init__(self):
        DBusGMainLoop(set_as_default=True)
        self.__rmenu = None
        self.__lmenu = None
        self.__backend = DeviceKitBackend()
        self.__backend.set_right_popup_menu_action(self.__mc_action)
        
    
    def __suspend(self, button):
        try:
            self.__backend.suspend()
        except DBusException as e:
            self.__handle_exception(e)
        
        
    def __hibernate(self, button):
        try:
            self.__backend.hibernate()
        except DBusException as e:
            self.__handle_exception(e)
    
    
    def __handle_exception(self, exception):
        print exception
    
    
    def __get_left_click_menu(self):
        if self.__lmenu is None:
            self.__lmenu = gtk.Menu()
            if self.__backend.can_suspend():
                suspend_item = gtk.ImageMenuItem(_('Suspend'))
                suspend_icon = gtk.image_new_from_icon_name('system-suspend', gtk.ICON_SIZE_MENU)
                suspend_item.set_image(suspend_icon)
                suspend_item.connect('activate', self.__suspend)
                self.__lmenu.append(suspend_item)
            if self.__backend.can_hibernate():
                hibernate_item = gtk.ImageMenuItem(_('Hibernate'))
                hibernate_icon = gtk.image_new_from_icon_name('system-hibernate', gtk.ICON_SIZE_MENU)
                hibernate_item.set_image(hibernate_icon)
                hibernate_item.connect('activate', self.__hibernate)
                self.__lmenu.append(hibernate_item)
            self.__lmenu.show_all()
        return self.__lmenu
    
    
    def __get_right_click_menu(self):
        if self.__rmenu is None:
            self.__rmenu = gtk.Menu()
            about_menu = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
            about_menu.connect('activate', self.about)
            exit_menu = gtk.ImageMenuItem(gtk.STOCK_CLOSE)
            exit_menu.connect('activate', self.close)        
            self.__rmenu.append(about_menu)
            self.__rmenu.append(exit_menu)
            self.__rmenu.show_all()
        return self.__rmenu
    
        
    def __mc_action(self, widget, event, data=None):
        if event.button == 1:
            self.__get_left_click_menu().popup(None, None, None, event.button, event.time)
        elif event.button == 3:
            self.__get_right_click_menu().popup(None, None, None, event.button, event.time)
        
        
    def close(self,button):
        gtk.main_quit()


    def about(self, button):
        about_dg = gtk.AboutDialog()
        about_dg.set_name(_("Battery Monitor"))
        about_dg.set_program_name(NAME)
        about_dg.set_version(VERSION)
        about_dg.set_comments('A battery monitor for the system tray')
        about_dg.set_authors(["Arthur Spitzer <arthapex@gmail.com>"])
        about_dg.connect("response", lambda d, r: d.destroy())
        about_dg.show()
            
    def main(self):
        try:
            self.__backend.update_batteries(startup=True)
            gtk.main()
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    monitor = BatteryMonitor()
    monitor.main()