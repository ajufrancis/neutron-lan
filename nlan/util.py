from env import NLAN_DIR 
import os, yaml

def get_roster():

    roster = os.path.join(NLAN_DIR,'roster.yaml')
    r = open(roster, 'r')
    return yaml.load(r.read())

