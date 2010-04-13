'''
@author: Arthur Spitzer <arthapex@gmail.com>
'''

from dbus.exceptions import DBusException
from dbus.mainloop.glib import DBusGMainLoop
import gettext
import gtk
import sys

from PowerBackend import DeviceKitBackend, UPowerBackend

NAME = 'batti'
VERSION = '0.3.1'
DESCRIPTION = 'A battery monitor for the system tray'
AUTHOR = 'Arthur Spitzer'
AUTHOR_EMAIL = 'arthapex@gmail.com'
URL = 'http://code.google.com/p/batti-gtk'

_ = lambda msg: gettext.dgettext(NAME, msg)

class BatteryMonitor(object):
    def __init__(self):
        DBusGMainLoop(set_as_default=True)
        self.__rmenu = None
        self.__lmenu = None
        try:
            self.__backend = UPowerBackend()
            self.__backend.set_right_popup_menu_action(self.__mc_action)
        except DBusException as e_upower:
            try:
                self.__backend = DeviceKitBackend()
                self.__backend.set_right_popup_menu_action(self.__mc_action)
            except DBusException as e_devkit:
                sys.stderr.write(""" 
Neither UPower nor DeviceKit.Power could be initialized!
This can have multiple reasons. You do not want to use Hal, do you?
Here is the error for UPower:

    %s

And this is the error for DeviceKit.Power:

    %s

""" % (e_upower, e_devkit))
                self.close(None)
                
        
    
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
        sys.stderr.write(exception)
    
    
    def __get_left_click_menu(self):
        if self.__lmenu is None:
            self.__lmenu = gtk.Menu()
            if self.__backend.can_suspend():
                suspend_item = gtk.ImageMenuItem(_('Suspend'))
                suspend_icon = gtk.image_new_from_icon_name('batti-suspend', gtk.ICON_SIZE_MENU)
                suspend_item.set_image(suspend_icon)
                suspend_item.connect('activate', self.__suspend)
                self.__lmenu.append(suspend_item)
            if self.__backend.can_hibernate():
                hibernate_item = gtk.ImageMenuItem(_('Hibernate'))
                hibernate_icon = gtk.image_new_from_icon_name('batti-hibernate', gtk.ICON_SIZE_MENU)
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
            if self.__backend.can_suspend() or self.__backend.can_hibernate():
                self.__get_left_click_menu().popup(None, None, None, event.button, event.time)
        elif event.button == 3:
            self.__get_right_click_menu().popup(None, None, None, event.button, event.time)
        
        
    def close(self,button):
        # Check if we're already in gtk.main loop
        if gtk.main_level() > 0:
            gtk.main_quit()
        else:
            exit(1)


    def about(self, button):
        about_dg = gtk.AboutDialog()
        about_dg.set_name(_("Battery Monitor"))
        about_dg.set_program_name(NAME)
        about_dg.set_version(VERSION)
        about_dg.set_comments(DESCRIPTION)
        about_dg.set_authors(['%s <%s>' % (AUTHOR, AUTHOR_EMAIL)])
        copying = open('../COPYING', 'r')
        about_dg.set_license(copying.read())
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
