import os
import gi
import hashlib

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from pathlib import Path
import xml.etree.ElementTree as ET


# Configuration variables of the app
config_directory = str(Path.home()) + "/.config"
config_filename = "pihole_panel_configs.xml"
title = "PiHole Panel Assistant"


class AssistantApp:
    def __init__(self):
        self.assistant = Gtk.Assistant()
        self.assistant.set_default_size(-1, -1)
        self.assistant.set_wmclass ("PiHole Panel", "PiHole Panel")
        self.assistant.set_title ("PiHole Panel")
        self.create_config_dir(config_directory)

        configs = self.load_configs(config_directory, config_filename)
        page_num = self.check_configs_and_get_page_num(configs)

        self.create_preferences_page(configs)
        self.create_about_page()

        self.assistant.connect('cancel', self.on_close_cancel)
        self.assistant.connect('close', self.on_close_cancel)
        self.assistant.connect('apply', self.on_apply)
        self.assistant.connect('prepare', self.on_prepare)

        self.assistant.set_current_page(page_num)
	
        if self.is_config_file_exist(config_directory, config_filename) == False:
            self.assistant.show()


    def create_config_dir(self, config_directory):
        if not os.path.exists(config_directory):
            os.makedirs(config_directory)

    def is_config_file_exist(self, config_directory, config_file):
        filename = config_directory + "/" + config_file
        return os.path.isfile(filename)

    def on_close_cancel(self, assistant):
        assistant.destroy()
        Gtk.main_quit()

    def on_apply(self, assistant):
        assistant.hide()

        # Load main screen
        from main import GridWindow
        GridWindow()
        

    def on_prepare(self, assistant, page):
        current_page = assistant.get_current_page()
        n_pages = assistant.get_n_pages()
        title = 'GTK Assistant (%d of %d)' % (current_page + 1, n_pages)
        assistant.set_title(title)
        #assistant.set_keep_above(True)


    def on_page_one_next(self, current_page, ip_address_entry, key_code_entry):
        configs = {}
        configs['ip_address'] = ip_address_entry.get_text()
        configs['key_code'] = key_code_entry.get_text()

        # Double to prevent rainbow attack
        configs['key_code'] = hashlib.sha256(configs['key_code'].encode('utf-8')).hexdigest()
        configs['key_code'] = hashlib.sha256(configs['key_code'].encode('utf-8')).hexdigest()

        result = self.validate_configs(configs)

        if result:
            self.save_configs(config_directory, config_filename, configs)
            next_page_index = 1
        else:
            next_page_index = 0

        return next_page_index


    def validate_configs(self, configs):
        #ip_address = configs['ip_address']
        #key_code = configs['key_code']
        
        # -----------
        # Do some validation here on ip_address, key_code combination
        # -----------

        # If validation success
        return True

        # Else
        # dialog = Gtk.MessageDialog(self.assistant, 0, Gtk.MessageType.ERROR,
        #                            Gtk.ButtonsType.CANCEL, "Invalid combination of IP Address and KeyCode")
        # dialog.format_secondary_text("Additional explanation here if necessary")
        # dialog.connect("response", lambda *a: dialog.destroy()) # Cancel button removes the dialog box
        # dialog.run()
        # return False


    def save_configs(self, config_directory, config_filename, configs):
        filename = config_directory + "/" + config_filename

        root = ET.Element("gtk_assistant_configs")

        for key, value in configs.items():
            ET.SubElement(root, key).text = value

        tree = ET.ElementTree(root)
        tree.write(filename)


    def load_configs(self, config_directory, config_filename):
        filename = config_directory + "/" + config_filename
        configs = {}

        if os.path.isfile(filename):
            xml_tree = ET.parse(filename)
            xml_root = xml_tree.getroot()

            element_list = xml_root.findall("./ip_address")
            if len(element_list) > 0:
                configs['ip_address'] = element_list[0].text

            element_list = xml_root.findall("./key_code")
            if len(element_list) > 0:
                configs['key_code'] = element_list[0].text

        return configs


    def check_configs_and_get_page_num(self, configs):
        if 'ip_address' in configs and 'key_code' in configs:
            return 1

        return 0


    def create_preferences_page(self, configs):
        # Create IP Address box

        ip_address_box = Gtk.HBox(homogeneous=False, spacing=12)
        
        ip_address_label = Gtk.Label(label='Pi Address:  ')
        ip_address_box.pack_start(ip_address_label, False, False, 12)

        ip_address_entry = Gtk.Entry()
        ip_address_entry.set_text("http://pi.hole/admin/")
        ip_address_box.pack_start(ip_address_entry, False, False, 4)
        if 'ip_address' in configs:
            ip_address_entry.set_text(configs['ip_address'])

        # Create Password explanation box
        key_code_explanation_box = Gtk.VBox(homogeneous=False, spacing=12)
        key_code_explanation_box.set_border_width(12)
        key_code_explanation_label = Gtk.Label(label='Details for your Pi-hole admin console.')
        key_code_explanation_box.pack_start(key_code_explanation_label, False, False, 12)

        # Create Password box

        key_code_box = Gtk.HBox(homogeneous=False, spacing=12)
        key_code_label = Gtk.Label(label='Password:     ')
        key_code_box.pack_start(key_code_label, False, False, 12)

        key_code_entry = Gtk.Entry()
        key_code_entry.set_visibility(False)
        key_code_box.pack_start(key_code_entry, False, False, 0)
        if 'key_code' in configs:
            key_code_entry.set_text(configs['key_code'])

        # Add above boxes to single box
        page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        page_box.pack_start(key_code_explanation_box, False, False, 0)
        page_box.pack_start(ip_address_box, False, False, 0)
        page_box.pack_start(key_code_box, False, False, 0)
        page_box.show_all()

        self.assistant.append_page(page_box)

        # Set other page properties
        self.assistant.set_page_title(page_box, 'Preferences')
        self.assistant.set_page_type(page_box, Gtk.AssistantPageType.INTRO)

        self.assistant.set_page_complete(page_box, True)

        pixbuf = self.assistant.render_icon(Gtk.STOCK_DIALOG_INFO, Gtk.IconSize.DIALOG, None)

        self.assistant.set_page_header_image(page_box, pixbuf)

        self.assistant.set_forward_page_func(self.on_page_one_next, ip_address_entry, key_code_entry)


    def on_edit_preferences_clicked(self, button):
        self.assistant.set_current_page(0)


    def create_about_page(self):
        label = Gtk.Label(label='Congratulations!')

        button = Gtk.Button.new_with_label("Edit Preferences")
        button.connect("clicked", self.on_edit_preferences_clicked)

        dummy_box_left = Gtk.VBox(spacing=6)
        dummy_box_right = Gtk.VBox(spacing=6)
        dummy_box_right.pack_start(button, False, False, 0)

        dummy_container_box = Gtk.HBox(spacing=6)
        dummy_container_box.pack_start(dummy_box_left, True, True, 0)
        dummy_container_box.pack_start(dummy_box_right, False, False, 0)

        page_box = Gtk.VBox(spacing=6)
        page_box.pack_start(label, True, True, 0)
        page_box.pack_start(dummy_container_box, False, False, 0)
        page_box.show_all()

        self.assistant.append_page(page_box)
        self.assistant.set_page_complete(page_box, True)
        self.assistant.set_page_title(page_box, 'Done')
        self.assistant.set_page_type(page_box, Gtk.AssistantPageType.CONFIRM)

        pixbuf = self.assistant.render_icon(Gtk.STOCK_DIALOG_INFO, Gtk.IconSize.DIALOG, None)
        self.assistant.set_page_header_image(page_box, pixbuf)



if __name__ == '__main__':
    AssistantApp()
    Gtk.main()
