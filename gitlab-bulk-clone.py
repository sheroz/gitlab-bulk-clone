### The basics are taken from the thread: 
### https://stackoverflow.com/questions/29099456/how-to-clone-all-projects-of-a-group-at-once-in-gitlab

import os
import gitlab
import subprocess
import configparser

def repo_pull(repo):
    print("Pulling repository: ", repo.name_with_namespace)
    os.chdir(repo.path)
    command = f'git pull'
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, universal_newlines=True)
    output, _ = process.communicate()
    process.wait()
    print(output)
    os.chdir("../")

def repo_clone(repo):
    print("Cloning repository: ", repo.name_with_namespace)
    command = f'git clone {repo.ssh_url_to_repo}'
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, universal_newlines=True)
    output, _ = process.communicate()
    process.wait()
    print(output)

def process_projects(projects):
    for repo in projects:
        if os.path.isdir(repo.path):
            repo_pull(repo)
        else:
            repo_clone(repo)

def process_group(group, recursive):
    name = group.name
    
    print ("Processing for the group:", name)

    group_directory_exists = os.path.isdir(name)
    if not group_directory_exists:
        os.mkdir(name)

    os.chdir(name) 

    group_object = glab.groups.get(group.id)
    process_projects(group_object.projects.list(all=True))

    if recursive:
        for subgroup in group_object.subgroups.list():
            process_group(subgroup, recursive)

    os.chdir("../")

parser = configparser.ConfigParser()
parser.read('gitlab.config')

config = parser['Config']
config_url = config.get('Url', fallback=None)
config_access_token = config.get('AccessToken', fallback=None)
config_group_name = config.get('GroupName', fallback=None)
config_group_id = config.getint('GroupId', fallback=0)
config_group_recursive = config.getboolean('Recursive', fallback=False)
config_local_path = config.get('LocalPath', fallback=None)
config_always_clone = config.getboolean('AlwaysClone', fallback=False)
config_pull_branch = config.get('PullBranch', fallback=None)

os.chdir(config_local_path)

print ("GitLab bulk clone started.")
print ("Connecting to the GitLab server ", config_url)
glab = gitlab.Gitlab(url = config_url, private_token = config_access_token)

print ("Getting list of existing groups...")
groups = glab.groups.list()

if config_group_id > 0:
    print ("Looking for the group with id:", config_group_id)
    for group in groups:
        if group.id == config_group_id:
            process_group(group, config_group_recursive)

elif config_group_name:
    print ("Looking for the group with name: ", config_group_name)
    for group in groups:
        if group.name == config_group_name:
            process_group(group, config_group_recursive)

print ("Completed.")
