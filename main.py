import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from multiprocessing.connection import Client


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.SliderBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.Mainbox)
        self.initTarget()
        self.initMargin()
        self.Mainbox.append(self.SliderBox)

        self.header = Gtk.HeaderBar()
        self.set_titlebar(self.header)

        self.button = Gtk.Button(label="Hello")
        self.header.pack_start(self.button)
        self.button.connect('clicked', self.hello)
        while True:
            try:
                self.conn = Client(address=("localhost", 21827))
                break
            except:
                pass


    def initTarget(self):
        self.targetbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.targetadj = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.targetframe = Gtk.Frame()
        self.targetframe.set_margin_top(15)
        self.targetframe.set_margin_end(10)
        self.targetframe.set_child(self.targetbox)
        self.targetlabel = Gtk.Label()
        self.targetlabel.set_margin_top(10)
        self.targetlabel.set_label("Target")

        self.targetslider = Gtk.Scale()
        self.targetslider.set_digits(0)  # Number of decimal places to use
        self.targetslider.set_range(0, 255)
        self.targetslider.set_draw_value(True)  # Show a label with current value
        self.targetslider.set_value(100)  # Sets the current value/position
        self.targetslider.connect('value-changed', self.targetslider_changed)
        self.targetslider.set_hexpand(True)  #

        self.targetadj.append(self.targetslider)
        self.targetbox.append(self.targetlabel)
        self.targetbox.append(self.targetadj)
        self.SliderBox.append(self.targetframe)

    def initMargin(self):
        self.marginbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.marginadj = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.marginframe = Gtk.Frame()
        self.marginframe.set_margin_top(15)
        self.marginframe.set_margin_end(10)
        self.marginframe.set_child(self.marginbox)
        self.marginlabel = Gtk.Label()
        self.marginlabel.set_margin_top(10)
        self.marginlabel.set_label("margin")

        self.marginslider = Gtk.Scale()
        self.marginslider.set_digits(0)  # Number of decimal places to use
        self.marginslider.set_range(1, 255)
        self.marginslider.set_draw_value(True)  # Show a label with current value
        self.marginslider.set_value(10)  # Sets the current value/position
        self.marginslider.connect('value-changed', self.marginslider_changed)
        self.marginslider.set_hexpand(True)  #

        self.marginadj.append(self.marginslider)
        self.marginbox.append(self.marginlabel)
        self.marginbox.append(self.marginadj)
        self.SliderBox.append(self.marginframe)

    def targetslider_changed(self, slider):
        self.conn.send(["target",int(self.targetslider.get_value())])

    def marginslider_changed(self, slider):
        self.conn.send(["margin",int(self.marginslider.get_value())])

    def hello(self, button):
        print("Hello world")

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()

app = MyApp(application_id="com.example.GtkApplication")
app.run(sys.argv)