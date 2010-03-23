'''
@author: Arthur Spitzer <arthapex@gmail.com>
'''

#import dbus.glib
from dbus.mainloop.glib import DBusGMainLoop
import gettext
import gtk

from PowerBackend import HalBackend

NAME = 'batti'
VERSION = '0.1'

_ = lambda msg: gettext.dgettext(NAME, msg)

class BatteryMonitor(object):
    def __init__(self):
        DBusGMainLoop(set_as_default=True)
        self.__menu = None
        self.__backend = HalBackend()
        self.__backend.set_popup_menu_action(self.__popup_menu)
    
    
    def __get_menu(self):
        if self.__menu is None:
            self.__menu = gtk.Menu()
            about_menu = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
            about_menu.connect('activate', self.about)
            exit_menu = gtk.ImageMenuItem(gtk.STOCK_CLOSE)
            exit_menu.connect('activate', self.close)        
            self.__menu.append(about_menu)
            self.__menu.append(exit_menu)
        return self.__menu
    
    def __popup_menu(self, button, widget, event):
        menu = self.__get_menu()
        menu.show_all()           
        menu.popup(None, None, None, 2, event)
        
        
    def close(self,button):
        gtk.main_quit()


    def about(self, button):
        about_dg = gtk.AboutDialog()
        about_dg.set_name(_("Battery Monitor"))
        about_dg.set_program_name(NAME)
        about_dg.set_version(VERSION)
        about_dg.set_comments('development release')
        about_dg.set_authors(["Arthur Spitzer"])
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