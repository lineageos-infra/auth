from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import os
import yaml

from github import Github

data = yaml.load(open('data.yml', 'r').read())

GITHUB_TOKEN=os.environ['GITHUB_TOKEN']
gh = Github(GITHUB_TOKEN)
org = gh.get_organization('LineageOS')

for t in data.keys():
    team_id = data[t]['meta']['id']
    desired_members = set([x.lower() for x in data[t]['members']])
    team = org.get_team(team_id)
    current_members = set([x.login.lower() for x in team.get_members()])

    add = desired_members.difference(current_members)
    delete = current_members.difference(desired_members)

    for member in add:
        print("Adding {} to {}".format(member, t))
        team.add_to_members(gh.get_user(member))
    for member in delete:
        print("Removing {} from {}".format(member, t))
        team.remove_from_members(gh.get_user(member))
