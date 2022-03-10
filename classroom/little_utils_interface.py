

import global_defs as gd
from anyio import typed_attribute
from termcolor import colored


log = gd.log    


CTRL_a = b'\x01'
CTRL_c = b'\x03'
CTRL_u = b'\x15'
CTRL_d = b'\x04'

PG_UP = b'\x00'+b'I'
PG_UP = b'\x00'+b'Q'


# ----------------- getch() ------------------------------
# https://stackoverflow.com/questions/510357/how-to-read-a-single-character-from-the-user
# https://pypi.org/project/console-menu/

from consolemenu import * # https://pypi.org/project/console-menu/
from consolemenu.items import * # https://pypi.org/project/console-menu/

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()

class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

getch = _Getch()

# -----------------------------------------------

def get_int(prompt, min_inclusive = None, max_inclusive = None):
    
    if min_inclusive is not None or max_inclusive is not None:
        prompt += " (must be"
        if min_inclusive is not None:
            prompt += " at least {}".format(min_inclusive)
        if max_inclusive is not None:
            prompt += " at the most {}".format(max_inclusive)
        prompt += ") "
    
    got_right_input = False
    while not got_right_input:
        try:
            val = int(input(prompt))
            if min_inclusive is not None and val < min_inclusive:
                print("{} < than {}".format(val, min_inclusive))
            elif max_inclusive is not None and val > max_inclusive:
                print("{} > than {}".format(val, max_inclusive))
            else:
                return val
        except:
            print("not an int value, ignoring it")


def get_y_n(prompt):

    got_right_input = False
    while not got_right_input:
        try:
            val = input(prompt+" y/n ? ")
            if val in [b'y', b'Y',"y","Y", b'n',b'N', "n","N",CTRL_u, "u",b'0']:
                if val in [b'y', b'Y', "y","Y"]: 
                    return "y"
                elif val in [b'n', b'n',"n","N"]:
                    return "n"
                else:
                    return "0"
        except:
            pass
        print("{} is not a y/n value, ignoring it".format(val))

    return val

class ChoiceDescriptor:
    
    def __init__(self, display_name, id, object_or_value, selected = False):
        self.display_name = display_name
        self.id = id
        self.object_or_value = object_or_value
        self.selected = selected # for multiselections


def menu_1_choice(choices_dictionary, 
    start_prompt = "Select am option (return key not needed)",  
    end_prompt = "'{}' was selected", 
    key_value_prompt = "{} for {}"):
    """ takes as values a dictionary with entries of the form
    choice_ckey: [display_name: , unique_id, object/value]
    returns [display_name: , unique_object_id_object]
    """

    # convert originary choice keys into strings
    adjusted_choices = {}
    for k, v in choices_dictionary.items():
        adjusted_choices[str(k)] = v

    if start_prompt is not None: 
        print(start_prompt)

    while True:
        for choice_key, choice_descr in adjusted_choices.items():
            print(key_value_prompt.format(choice_key, choice_descr.display_name))
        choice_orig = getch()
        choice = choice_orig.decode("ascii")
        if not choice in adjusted_choices.keys():
            print("you have chosen a non available choice: '{}'".format(choice))
        else:
            break

    if end_prompt is not None: 
        print(end_prompt.format(choice+ " -> "+adjusted_choices[choice].display_name))

    return choice, adjusted_choices[choice]


def generate_menu_keys_for_list(items_list):
    indexes = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

    ret_dict = {}
    for i in items_list:
        ret_dict[indexes.pop(0)] = i
    
    return ret_dict

def menu_1_choice_autokey(triples_list, 
    start_prompt = "Select am option (return key not needed)",  
    end_prompt = "'{}' was selected", 
    key_value_prompt = "{} for {}"):
    
    if triples_list is None or len(triples_list) <= 0:
        log.warning("passed empty list to menu_1_choice_autokey()")
        return None, (None, None, None)

    choices_dict = generate_menu_keys_for_list(triples_list)

    choice, choice_descr = menu_1_choice(choices_dict, start_prompt, end_prompt, key_value_prompt)
    return choice, choice_descr
    

def menu_main():
    choices_l = [
        ChoiceDescriptor(colored("Exit",'green'),      None, None),
        ChoiceDescriptor("controllo nomi attachments", None, None),
        ChoiceDescriptor("correzione compiti",         None, None),
    ]
    choice, choice_descr = menu_1_choice_autokey(choices_l)
    return choice, choice_descr


def menu_multiple_choice(entries_dictionary, 
    start_prompt = "Select multiple options (u to end)",  
    end_prompt = "'{}' was selected", 
    key_value_prompt = "{} for {}"):
    """ takes as values a dictionary with entries of the form
    choice_ckey: [display_name: , unique_id, object/value]
    returns [display_name: , unique_object_id_object]
    """

    # convert originary choice keys into strings
    adjusted_entries_d = {}
    for k, v in entries_dictionary.items():
        if not isinstance(v, ChoiceDescriptor):
            log.error("found wrong type{} when {} expected".format(type(v),type(ChoiceDescriptor.__name__)))
        adjusted_entries_d[str(k)] = v

    if start_prompt is not None: 
        print(start_prompt)

    choice = ""
    while choice != "u": # change it to enter or ctrl+u
        for choice_key, choice_descr in adjusted_entries_d.items():
            prompt = key_value_prompt.format(choice_key, choice_descr.display_name)
            pre_prompt = "[x]" if choice_descr.selected else "[ ]"
            print(pre_prompt+" "+prompt)
        choice_orig = getch()
        choice = choice_orig.decode("ascii") # verbose to look into it if needed
        if choice == "u": 
            break
        elif choice in adjusted_entries_d.keys():
            adjusted_entries_d[choice].selected = not adjusted_entries_d[choice].selected
        else:
            print("you entered a choice not available: '{}'".format(choice))
        print("--------------")

    choices_selected_keys_l = []; 
    choices_selected_descr_l = []; choices_nselected_descr_l = []
    for choice_key, choice_descr in adjusted_entries_d.items():
        if choice_descr.selected: 
            choices_selected_descr_l.append(choice_descr)
            choices_selected_keys_l.append(choice_key)
        else:                     choices_nselected_descr_l.append(choice_descr)

    return choices_selected_descr_l, choices_nselected_descr_l, choices_selected_keys_l 


def menu_multiple_choice_autokey(descr_list, 
    start_prompt = "Select multiple options (u to end)",  
    end_prompt = "'{}' was selected", 
    key_value_prompt = "{} for {}"):
    """"""
    choice_sel_descr_l, choice_nsel_descr_l, choices_l = [], [], []

    if descr_list is None or len(descr_list) <= 0:
        log.warning("passed empty list to menu_multiple_choice_autokey()")
    else:
        choices_dict = generate_menu_keys_for_list(descr_list)
        choice_sel_descr_l, choice_nsel_descr_l, choices_l  = menu_multiple_choice(
            choices_dict, start_prompt, end_prompt, key_value_prompt)

    return choice_sel_descr_l, choice_nsel_descr_l, choices_l




if __name__ == '__main__':

    choices_descr_l = [  ChoiceDescriptor("choice"+str(i), "id"+str(i), "object"+str(i)) for i in range(10) ]

    def test_menu_1_choice():

        choices_d = { 
            0 : ChoiceDescriptor("lo zero", "id dello 0 ", 100),
            3 : ChoiceDescriptor("1l 33", "id dello 33 ", 133),
            9 : ChoiceDescriptor("lo 99", "id 99", 1999),
        }
        choice = menu_1_choice(choices_d)
        print(choice)

    # test_menu_1_choice()

    def test_menu_multiple_choice_autokey():

        # selected_descr_l, unselec_descr_l, key_choices_l = menu_multiple_choice_autokey(choices_descr_l)
        selected_descr_l, unselec_descr_l, key_choices_l = menu_multiple_choice_autokey([])

        for descr in selected_descr_l: print("selected '{}'".format(descr.display_name)) 
        for descr in unselec_descr_l:  print("UNselec  '{}'".format(descr.display_name)) 

    # test_menu_multiple_choice_autokey()
    # 
    test_menu_1_choice()

    # get_y_n("vuoi divertirti?")
