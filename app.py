import gi
import json
from urllib.request import urlopen

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# If you have UTF-8 problems then uncomment next 3 lines
#import sys
#reload(sys)
#sys.setdefaultencoding("utf-8")

# HELP: https://discourse.pi-hole.net/t/pi-hole-api/1863
# HELP: https://github.com/pi-hole/AdminLTE/issues/575
# HELP: https://python-gtk-3-tutorial.readthedocs.io/en/latest/introduction.html

# Change to Your Pi-Hole Admin Console Url
pihole = "http://pi.hole/admin/"
# Change to Your Pi-Hole Admin Console Hashed Password (see WEBPASSWORD in /etc/pihole/setupVars.conf)
passwd = ""

class GridWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="PiHole-Panel")

        url = pihole + "api.php?summary" #api.php?enable&auth=" + passwd
        result = urlopen(url, timeout = 15).read()
        json_obj = json.loads(result)
        
        # auth example
        #url2 = pihole + "api.php?enable&auth=" + passwd
        #result2 = urlopen(url2, timeout = 15).read()
        #json_obj2 = json.loads(result2)

        grid = Gtk.Grid(margin=4)
        grid.set_column_homogeneous(True)
        self.add(grid)

        frame_vert = Gtk.Frame(label='Stats')

        button1 = Gtk.Switch(halign=Gtk.Align.END)
        #button1.connect("notify::active", self.on_switch_activated)
        #button1.set_active(True)

        box = Gtk.Box(spacing=8)

        status = Gtk.Label(label="Status: " + str(json_obj['status']), margin=4)

        stats = Gtk.Label(label="Blocked Today: " + str(json_obj['ads_blocked_today']) + "\n" +
        "Ads Percentage Today: " + str(json_obj['ads_percentage_today']) + "%\n"
        "DNS Queries Today: " + str(json_obj['dns_queries_today']) + "\n"
        "Unique Domains: " + str(json_obj['unique_domains']) + "\n"
        "Queries Forwarded: " + str(json_obj['queries_forwarded']) + "\n"
        "Queries Cached: " + str(json_obj['queries_cached']) + "\n"
        "Clients Ever Seen: " + str(json_obj['clients_ever_seen']) + "\n"
        "Unique Clients: " + str(json_obj['unique_clients']), 
        margin=4, halign=Gtk.Align.START)

        box.pack_start(stats, True, True, 0)

        frame_vert.add(box)

        grid.attach(status, 1, 1, 1, 1)
        grid.attach_next_to(button1, status, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach(frame_vert, 0, 2, 3, 3)

win = GridWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
