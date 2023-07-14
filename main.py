import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from multiprocessing.connection import Client
from threading import Thread
from time import sleep


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        self.brunning = True
        self.running = True
        super().__init__(*args, **kwargs)
        self.Mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.NormalBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.ImmersiveBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.lightbar = Gtk.LevelBar(orientation=Gtk.Orientation.HORIZONTAL)
        self.lightbar.set_min_value(0)
        self.lightbar.set_max_value(255)

        self.set_child(self.Mainbox)
        self.initModeSelect()
        self.initMultiplier()
        self.initOffset()
        self.initTarget()
        self.initMargin()
        #self.Mainbox.append(self.NormalBox)

        self.header = Gtk.HeaderBar()
        self.set_titlebar(self.header)

        self.button = Gtk.Button(label="Hello")
        #self.header.pack_start(self.button)
        self.button.connect('clicked', self.hello)
        while True:
            try:
                self.conn = Client(address=("localhost", 21827))
                break
            except:
                pass
        while True:
            try:
                self.bconn = Client(address=("localhost", 21828))
                break
            except:
                pass
        self.connect("close-request", self.closea)

        Bart = Thread(target=self.bars)
        Bart.start()

    def closea(self,arg):
        self.brunning = False
        self.running = False
        self.close()

    def initModeSelect(self):
        self.buttonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.radio1 = Gtk.CheckButton(label="disable")
        self.radio2 = Gtk.CheckButton(label="normal")
        self.radio3 = Gtk.CheckButton(label="cinema(lcd)")
        self.radio2.set_group(self.radio1)
        self.radio3.set_group(self.radio1)
        self.radio1.connect("toggled", self.toggled)
        self.radio2.connect("toggled", self.toggled)
        self.radio3.connect("toggled", self.toggled)
        self.buttonBox.append(self.radio1)
        self.buttonBox.append(self.radio2)
        self.buttonBox.append(self.radio3)
        self.radio1.set_active(True)
        self.Mainbox.append(self.buttonBox)

    def toggled(self,arg):
        if self.radio1.get_active():
            self.brunning = False
            try:
                self.conn.send(["mode","disabled"])
            except:
                pass

            try:
                self.Mainbox.remove(self.NormalBox)
            except:
                pass

            try:
                self.Mainbox.remove(self.ImmersiveBox)
            except:
                pass

            try:
                self.Mainbox.remove(self.lightbar)
            except:
                pass

        elif self.radio2.get_active():
            self.conn.send(["mode","normal"])
            self.brunning = True
            try:
                self.Mainbox.remove(self.ImmersiveBox)
            except:
                pass

            try:
                self.Mainbox.remove(self.lightbar)
                self.Mainbox.append(self.lightbar)
            except:
                self.Mainbox.append(self.lightbar)

            self.Mainbox.append(self.NormalBox)

        elif self.radio3.get_active():
            self.conn.send(["mode","immersive"])
            self.brunning = True
            try:
                self.Mainbox.remove(self.NormalBox)
            except:
                pass

            try:
                self.Mainbox.remove(self.lightbar)
                self.Mainbox.append(self.lightbar)
            except:
                self.Mainbox.append(self.lightbar)

            self.Mainbox.append(self.ImmersiveBox)
    def bars(self):
        while self.running:
            while self.brunning :
                self.bconn.send("value")
                try :
                    self.lightbar.set_value(self.bconn.recv())
                except:
                    try:
                        self.Mainbox.remove(self.lightbar)
                        self.Mainbox.append(self.lightbar)
                    except:
                        self.Mainbox.append(self.lightbar)
                sleep(0.08)
            sleep(0.5)

    def initOffset(self):
        self.offsetbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.offsetadj = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.offsetframe = Gtk.Frame()
        self.offsetframe.set_margin_top(15)
        self.offsetframe.set_margin_end(10)
        self.offsetframe.set_child(self.offsetbox)
        self.offsetlabel = Gtk.Label()
        self.offsetlabel.set_margin_top(10)
        self.offsetlabel.set_label("offset")

        self.offsetslider = Gtk.Scale()
        self.offsetslider.set_digits(2)  # Number of decimal places to use
        self.offsetslider.set_range(0, 254)
        self.offsetslider.set_draw_value(True)  # Show a label with current value
        self.offsetslider.set_value(1)  # Sets the current value/position
        self.offsetslider.connect('value-changed', self.offsetslider_changed)
        self.offsetslider.set_hexpand(True)  #

        self.offsetadj.append(self.offsetslider)
        self.offsetbox.append(self.offsetlabel)
        self.offsetbox.append(self.offsetadj)
        self.ImmersiveBox.append(self.offsetframe)
    def initMultiplier(self):
        self.multiplierbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.multiplieradj = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.multiplierframe = Gtk.Frame()
        self.multiplierframe.set_margin_top(15)
        self.multiplierframe.set_margin_end(10)
        self.multiplierframe.set_child(self.multiplierbox)
        self.multiplierlabel = Gtk.Label()
        self.multiplierlabel.set_margin_top(10)
        self.multiplierlabel.set_label("multiplier")

        self.multiplierslider = Gtk.Scale()
        self.multiplierslider.set_digits(2)  # Number of decimal places to use
        self.multiplierslider.set_range(0.1, 4)
        self.multiplierslider.set_draw_value(True)  # Show a label with current value
        self.multiplierslider.set_value(1)  # Sets the current value/position
        self.multiplierslider.connect('value-changed', self.multiplierslider_changed)
        self.multiplierslider.set_hexpand(True)  #

        self.multiplieradj.append(self.multiplierslider)
        self.multiplierbox.append(self.multiplierlabel)
        self.multiplierbox.append(self.multiplieradj)
        self.ImmersiveBox.append(self.multiplierframe)

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
        self.NormalBox.append(self.targetframe)

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
        self.NormalBox.append(self.marginframe)

    def targetslider_changed(self, slider):
        self.conn.send(["target",int(self.targetslider.get_value())])

    def multiplierslider_changed(self, slider):
        self.conn.send(["multiplier",float(self.multiplierslider.get_value())])

    def offsetslider_changed(self, slider):
        self.conn.send(["offset",int(self.offsetslider.get_value())])

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