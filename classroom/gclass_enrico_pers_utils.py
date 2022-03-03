

from logging.config import IDENTIFIER
import re

from sqlalchemy import DDL

import global_defs as gd

""" CONVENTIONS
first level separator: _
second level separator: -
third level separator: x  (escape real x with xx)

course/class ID:  by example 1c-2021-q1 (ex 3q-2021-q1_tpsit...)    q0 for entire year

"""


log = gd.log

COURSE_ID_REGEX_QUARTER = r'[\d][a-z]-[\d]{4}-q[0-2]$'
COURSE_ID_REGEX = r'[\d][a-z]-[\d]{4}(-q[0-2])?$'
DATA_REGEX = r'[\d]{4}-[\d]{2}-[\d]{2}'
NOME_REGEX =  r'[a-z]([a-z\-])*$'

def course_id_from_title(course_title):
    """ assumes  convention that the course starts with the course ID
    """
    elements = course_title.split("_")
    # log.info(elements[0])
    if not re.match(COURSE_ID_REGEX, elements[0]):
        log.error("Naming convention violation: Course id part not compliant: \n{} of {}"
        .format(elements[0], course_title))
        return "wrong-class-id_"+course_title
    else:
        return elements[0]


def check_class_ev_id(id, class_num = None, class_letter = None, class_year = None):

    if not re.match(COURSE_ID_REGEX, id):
        return False
    
    return True



# not to do it several times
assente_errato = " sembra assente o errato/a nel formato o nei contenuti"
assente_errato += "\nnotare che potrebbe trattarsi di una segnalazione errata causata da errori precedenti"
assente_errato += "\nnotare che altri eventuali errori seguenti non vengono diagnosticati"

CWORK_TYPES = ["comp", "labo"]
MATERIE = ["tec-inf","inform","sta","sis-reti","tpsit"]
IDENTIFICATORI_ESEMPIO = ["pg001-es05", "prj-annuale"]

def generate_sample_filenames(classe, sezione, anno):
    
    samples_l = []
    for tipo in CWORK_TYPES:
        for m in MATERIE:
            for e in IDENTIFICATORI_ESEMPIO:
                comp = []
                comp.append(str(classe)+sezione+"-"+str(anno))
                comp.append(m)
                comp.append(tipo)
                comp.append("serbelloni-mazzanti-vien-dal-mare")
                comp.append("maria-ildegarda")
                comp.append("2022-01-31")
                comp.append("pg001-es5")
                comp.append("descrizione-opzionale")
                nome = "_".join(comp)
                samples_l.append(nome)
    return samples_l

def check_attachment_filename(attachment_dict):
    """ returns list of  messages"""
    name = attachment_dict['driveFile']['title']
    return check_file_name(name)



def check_file_name(name):

    msgs = []
    elements = name.split("_")
    if len(elements) < 5:
        msgs = ["nome file sembra NON rispettare le regole '{}'".format(name)]
        return False, msgs

    # 1a-2021    
    id_classe = elements[0]    
    ok = check_class_ev_id(id_classe)
    if not ok:
        msgs += ["l'id della classe '{}' in '{}'".format(id_classe, name)+ assente_errato]
        return False, msgs

    materia = elements[1]
    if materia not in ["tec-inf","inform","sta","sis-reti","tpsit"]:
        msgs += ["la materia '{}' ".format(materia)+ assente_errato]
        return False, msgs

    tipo = elements[2]
    if tipo not in ["comp","labo"] and not tipo[0] == "#": # character # to declare intentional exceptions
        msgs += ["il tipo del compito '{}', in '{}'".format(tipo, name)+assente_errato]
        return False, msgs

    cognome = elements[3]
    if not  re.match(NOME_REGEX, cognome):
        msgs += ["il cognome '{}', in '{}'".format(cognome, name)+assente_errato]
        return False, msgs

    nome = elements[4]
    if not  re.match(NOME_REGEX, nome):
        msgs += ["il nome '{}', in '{}'".format(nome, name)+assente_errato]
        return False, msgs

    data_consegna = elements[5]
    if not  re.match(DATA_REGEX, data_consegna):
        msgs += ["l'elemento data consegna '{}', in '{}' sembra assente o errato".format(data_consegna, name)]
        return False, msgs
    
    return True, []


if __name__ == "__main__":
    # course_id_from_title("1q-2021-q1")
    def test_check_attachment_filename():
        ok, msgs = check_attachment_filename("3c-2021_tpsit_labo_serbeloni-mazzanti_anna-maria_2012-01-31")
        ok, msgs = check_attachment_filename("3c-2021_tpsit_labo__anna-maria_2012-01-31")
        print("it is ok?: ", ok)
        for m in msgs: print(m)

    def test_check_attachment_filename():
        names = generate_sample_filenames(5,"c", 2023)
        for name in names:
            ok, msgs = check_file_name(name)
            if not ok:
                print("\n\n'{}' errato\n".format(name)+"\n\n".join(msgs))
                continue

    test_check_attachment_filename()