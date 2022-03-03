

import os
from subprocess import Popen, PIPE
# import sys

import logging
from   logging import handlers

import global_defs as gd

log = None


def init_git_repos():
    global log
    logging.basicConfig(
        format='%(asctime)s %(filename)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    # logging.basicConfig(format='%(asctime)s - %(message)s', level = LOG_LEVEL)
    logfh = handlers.RotatingFileHandler("logging.log", mode='a', maxBytes=1024*4, backupCount=0, 
    encoding=None, delay=False, errors=None)
    log = logging.getLogger(__name__)
    log.addHandler(logfh)


def git_status(repo_dir, verbose = False):
    git_repo_updated = "Your branch is up to date with 'origin/main'"
    os.chdir(repo_dir)
    if verbose: log.info("in repo dir {}".format(os.getcwd()))
    output = os.popen('git status')

    status_output = []
    changed = True
    while True:
        line = output.readline()
        if not line:
            break
        status_output.append(line.strip())
        if git_repo_updated in line:
            changed = False
    output.close()
    if not changed:
        return False, status_output

    return True, status_output


def git_pull(repo_dir, verbose = False, message = "git pull"):

    os.chdir(repo_dir)
    if verbose: log.info("{} in {}".format(message, repo_dir))
    process = Popen(['git', 'pull'], stdout=PIPE, stderr=PIPE)

    out_lines =  [ bs.decode() for bs in process.stdout.readlines()]
    err_lines =  [ bs.decode() for bs in process.stderr.readlines()]

    return err_lines + out_lines

init_git_repos()


indiv_repos_root_dir = "indiv"

def walk_repos(root_dir):
    """
    Structure: root_dir > indiv > <student display name> <student git repos>
    """

    directory_contents = os.listdir(root_dir)
    print(directory_contents)
    for item in directory_contents:
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path):
            if item in ["indiv"]:
                ind_dirs_root = os.path.join(root_dir,indiv_repos_root_dir)
                for person_dir in  os.listdir(ind_dirs_root):
                    # log.info(person_dir)
                    person_path = os.path.join(ind_dirs_root, person_dir)
                    for repo_dir in os.listdir(person_path):
                        repo_path = os.path.join(person_path, repo_dir)
                        # log.info("----{}".format(repo_path))
                        changed, status = git_status(repo_path, False)
                        if changed:
                            log.info("\n\n--- repo of [{}] changed or empty or problem ---".format(person_dir))
                            log.info("\n"+"\n".join(status))
                            pull_output = git_pull(repo_path, True, "\n### git PULL ###")
                            log.info("\n"+"\n".join(pull_output))


if __name__ == "__main__":
    
    def main():
        root = gd.GDRIVE_ROOT
        cl3q_dev_root = os.path.join(root, r"02_insegnamento\galilei\classe_3_Q\08_dev_3q")
        walk_repos(cl3q_dev_root)
    

    main()