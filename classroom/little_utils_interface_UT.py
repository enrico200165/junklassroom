
import unittest
import logging
from  logging import handlers


# Import the necessary packages
from consolemenu import *
from consolemenu.items import *


from  little_utils_interface import *


# --- Logging ---
logging.basicConfig(
    format='%(asctime)s %(filename)s %(lineno)s %(levelname)-8s \n%(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
# logging.basicConfig(format='%(asctime)s - %(message)s', level = LOG_LEVEL)
logfh = logging.handlers.RotatingFileHandler("logging.log", mode='a', maxBytes=1024*4, backupCount=0, 
encoding=None, delay=False, errors=None)
log = logging.getLogger(__name__)
log.addHandler(logfh)


class TestMenus(unittest.TestCase):

    def test_menu_9temsmax(self):
        log.info("test_menu_9temsmax()")
        menu_items = {}
        for i in range(10):
            menu_items[str(i)] = ("choice_"+str(i), "id_"+str(i), None)
        key, triple = menu_1_choice_(menu_items)
        log.info("key: {}".format(key)+str(triple))

def console_menu_sample_code():
    # Create the menu
    menu = ConsoleMenu("Title", "Subtitle")

    # Create some items

    # MenuItem is the base class for all items, it doesn't do anything when selected
    menu_item = MenuItem("Menu Item")

    # A FunctionItem runs a Python function when selected
    function_item = FunctionItem("Call a Python function", input, ["Enter an input"])

    # A CommandItem runs a console command
    command_item = CommandItem("Run a console command",  "touch hello.txt")

    # A SelectionMenu constructs a menu from a list of strings
    selection_menu = SelectionMenu(["item1", "item2", "item3"])

    # A SubmenuItem lets you add a menu (the selection_menu above, for example)
    # as a submenu of another menu
    submenu_item = SubmenuItem("Submenu item", selection_menu, menu)

    # Once we're done creating them, we just add the items to the menu
    menu.append_item(menu_item)
    menu.append_item(function_item)
    menu.append_item(command_item)
    menu.append_item(submenu_item)

    # Finally, we call show to show the menu and allow the user to interact
    x = menu.show()
    print(x)

if __name__ == '__main__':
    # console_menu_sample_code()
    unittest.main()