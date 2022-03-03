

import global_defs as gd
from anyio import typed_attribute

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
    
    def __init__(self, display_name, id, object_or_value): 
        self.display_name = display_name
        self.id = id
        self.object_or_value = object_or_value


def menu_1_choice_(choices_dictionary, 
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

    for choice_key, choice_descr in adjusted_choices.items():
        print(key_value_prompt.format(choice_key, choice_descr.display_name))
    choice_orig = getch()
    choice = choice_orig.decode("ascii")

    if end_prompt is not None: 
        print(end_prompt.format(choice+ " -> "+adjusted_choices[choice].display_name))

    return adjusted_choices[choice]


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

    choice_descr = menu_1_choice_(choices_dict, start_prompt, end_prompt, key_value_prompt)
    return choice_descr
    

if __name__ == '__main__':
    

    def test_menu_1_choice():

        choices_d = { 
            0 : ChoiceDescriptor("lo zero", "id dello 0 ", 100),
            3 : ChoiceDescriptor("1l 33", "id dello 33 ", 133),
            9 : ChoiceDescriptor("lo 99", "id 99", 1999),
        }
        choice = menu_1_choice_(choices_d)
        print(choice)

    # test_menu_1_choice()

    def test_menu_1_choice_autokey():

        choices_l = [
            ChoiceDescriptor("lo zero", "id dello 0 ", 100),
            ChoiceDescriptor("1l 33", "id dello 33 ", 133),
            ChoiceDescriptor("lo 99", "id 99", 1999),
        ]
        choice = menu_1_choice_autokey(choices_l)
        print(choice)

    test_menu_1_choice_autokey()

    get_y_n("vuoi divertirti?")
    
    while False:
        x = getch()
        print(x)
    