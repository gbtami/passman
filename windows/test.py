import sys
from gi.repository import Gtk


class Application(Gtk.Application):
    
    app_id = 'com.idlecore.passman'
    
    def __init__(self):
        super().__init__(application_id=self.app_id)
        self.connect('activate', self.on_activate)
        self.connect('startup', self.on_startup)
    
    def on_startup(self, app):
        self.window = Gtk.ApplicationWindow(application=app)
        
    def on_activate(self, app):
        self.window.show_all()
    
    def on_quit(self, obj, param):
        self.quit()

def main():
    main_app = Application()
    exit_status = main_app.run(sys.argv)
    sys.exit(exit_status)

if __name__ == '__main__':
    main()
