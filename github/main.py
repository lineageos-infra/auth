import os
import sys

from github import Github
from ruamel.yaml import YAML

yaml = YAML()

with open("data.yml", "r") as f:
    data = yaml.load(f.read())

def add_maintainer(username: str):
    gh = Github()
    user = gh.get_user(username)

    members = data["Maintainers"]["members"]

    members.append(user.login)
    members.yaml_add_eol_comment(f"id={user.id}", len(members) -1, 0)
    members.sort(key=str.lower)

    with open('data.yml', 'w') as f:
        yaml.dump(data, f)

def lint():
    for _, value in data.items():
        value["members"].sort(key=str.lower)

    with open('data.yml', 'w') as f:
        yaml.dump(data, f)

def sync():
    gh = Github(os.environ['X_GITHUB_TOKEN'])
    org = gh.get_organization('LineageOS')
    members = set(x.login.lower() for x in org.get_members())
    team_members = {
        login.lower(): [
            data[team]["meta"]["id"]
            for team, info in data.items()
            if login in info["members"]
        ]
        for login in {
            member
            for info in data.values()
            for member in info["members"]
        }
    }
    everyone = set(team_members.keys())

    # see if there's anyone to add
    for member in everyone - members:
        print("Inviting {} to org".format(member))
        org.invite_user(gh.get_user(member), teams=[org.get_team(x) for x in team_members[member]])

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
            if member in members:
                print("Adding {} to {}".format(member, name))
                team.add_to_members(gh.get_user(member))
        for member in delete:
            print("Removing {} from {}".format(member, name))
            team.remove_from_members(gh.get_user(member))


action = sys.argv[1]

match action:
    case "add_maintainer":
        add_maintainer(sys.argv[2])
    case "lint":
        lint()
    case "sync":
        sync()
    case _:
        print("Invalid action:", action)
        exit(-1)
