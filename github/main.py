import os
import yaml

from github import Github

with open("data.yml", "r") as f:
    data = yaml.safe_load(f.read())

GITHUB_TOKEN=os.environ['X_GITHUB_TOKEN']
gh = Github(GITHUB_TOKEN)
org = gh.get_organization('LineageOS')
members = set(x.login.lower() for x in org.get_members())
everyone = set([x.lower() for y in [y["members"] for y in data.values()] for x in y])

# see if there's anyone to add
for member in everyone - members:
    print("Inviting {} to org".format(member))
    org.add_to_members(gh.get_user(member))

# see if there's anyone to remove
# NOTE: This is a manual process, DO NOT MAKE THIS AUTOMATIC
for member in members - everyone:
    print("{} needs to be removed from org".format(member))

# add/remove from teams
for name, team in data.items():
    team_id = team['meta']['id']
    desired_members = set([x.lower() for x in team['members']])
    team = org.get_team(team_id)
    current_members = set([x.login.lower() for x in team.get_members()])

    add = desired_members.difference(current_members)
    delete = current_members.difference(desired_members)

    for member in add:
        print("Adding {} to {}".format(member, name))
        team.add_to_members(gh.get_user(member))
    for member in delete:
        print("Removing {} from {}".format(member, name))
        team.remove_from_members(gh.get_user(member))
