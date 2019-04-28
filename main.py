import os
import yaml
import json
from pprint import PrettyPrinter
from urllib.parse import unquote

### CONSTANTS
WORKING_DIR = "work"

def pp(s):
    PrettyPrinter(indent=4).pprint(s)
def get_list_of_things(thing):
    return os.popen(thing).read().split("\n")[:-1]

def generate_block_visual_studio_code():
    vs_block = {'extensions': []}
    for item in get_list_of_things("code --list-extensions"):
        vs_block['extensions'].append({'name': item})
    return vs_block

def generate_block_pip3():
    #note that this generates a version attribute, but this attribute is ignored by strapped.sh
    return {'packages': json.loads(os.popen("pip3 list --format json").read())}
def generate_block_git():
    git_block = {'clone': []}
    base_path = os.path.join(os.path.expanduser("~"), WORKING_DIR)
    for folder in os.listdir(base_path):
        if os.path.isdir(os.path.join(base_path, folder)):
            if not os.system("".join(["cd ", os.path.join(base_path, folder), "&& git remote get-url origin"])): #check if it's a git repo, exit code of 1 means no
                git_block['clone'].append({
                    'folder': os.path.join("~", WORKING_DIR, folder),
                    'repo':os.popen("".join(["cd ", os.path.join(base_path, folder), "&& git remote get-url origin"])).read()[:-1]
                    })
    return git_block
def convert_path(p):
    if p[0:7] == "file://":
        p = p[7:-1]
    if p.split("/")[1] == "Users":
        p = "~" + "/".join([""] + p.split("/")[3:])
    return p
print(convert_path('file:///Users/richardsong/Downloads/'))

def generate_block_dockutil():
    du_block = {'apps':[], 'dirs':[]}
    app_counter = 1
    for entry in get_list_of_things("dockutil --list"):
        # print(entry.split("\t"))
        if entry.split("\t")[2] == 'persistent-apps':
            du_block['apps'].append({
                "name": unquote(entry.split("\t")[0]),
                "pos": app_counter,
                "path": unquote(convert_path(entry.split("\t")[1]))
            })
            app_counter += 1
        else:
            du_block['dirs'].append({ 
                "path": convert_path(entry.split("\t")[1]),      
                "view": "fan", "display": "stack", "sort": "dateadded" })
    return du_block
# print(get_list_of_things("brew cask list"))
# print(get_list_of_things("brew list"))

def generate_block_brew():
    brew_block = {'taps':[], 'packages':[], 'casks':[]}
    for item in get_list_of_things('brew tap'):
        brew_block['taps'].append({
            'name': item
        })
    for item in get_list_of_things('brew list'):
        brew_block['packages'].append({
            'name': item,
            'upgrade': True
        })
    for item in get_list_of_things('brew cask list'):
        brew_block['casks'].append({
            'name': item,
            'upgrade': True
        })
    return brew_block

output = {'strapped': {   'repo': 'https://raw.githubusercontent.com/azohra/strapped/master/straps'},
                        'bash': {'mkdir': [{'dir': '~/'+WORKING_DIR}]}
                        }

straps = ["brew", "dockutil", "git", "pip3", "visual_studio_code"]
output['visual_studio_code'] = generate_block_visual_studio_code()
output['pip3'] = generate_block_pip3()
output['git'] = generate_block_git()
output['dockutil'] = generate_block_dockutil()
output['brew'] = generate_block_brew()
pp(output)
y = yaml.dump(output).split("\n")
#stupid fucking hack because stupid yaml is stupid
y = ["  " + line if len(line) > 2 and (line[2] == '-' or line[2] == " ") else line for line in y]
with open("strapped.yaml", "w", encoding='utf8') as file:
    file.write("\n".join(y))
# with open("strapped_config.yml") as file:
#     PrettyPrinter(indent=4).pprint(yaml.safe_load(file.read()))
