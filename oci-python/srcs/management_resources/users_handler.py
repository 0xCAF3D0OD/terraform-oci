import sys

import oci
from oci.identity_domains.models import User, GroupMembers
from InquirerPy import inquirer
from classes import ConfigState

from management_resources.groupes_handler import groups_handler

from utils.config import RED, YELLOW, RESET, STYLE, GREEN
from utils.config import define_tags
from utils.inquire_handler import user_validation_by_y_n

SEPARATOR = f"{GREEN} ------------------- {RESET}"

def build_credentials(config_class: ConfigState):
    name = inquirer.text(
        message="enter new user with this format: firstname-lastname: ",
        style=STYLE,
        default="",
    ).execute()

    group_name = config_class.get_groups("name")
    group_ocid = config_class.get_groups("ocid")
    description = inquirer.text(
        message="enter user description: ",
        style=STYLE,
        default=""
    ).execute()

    _, team, role, grp_id = group_name.split("-")

    user_name = f"U-{team}{role}-{name}"

    email = f"{name}@{team}{role}.ch"

    return name, user_name, description, email, group_name, group_ocid


def create_new_user(identity_domains_client, config_class: ConfigState):
    name, user_name, description, email, group_name, group_ocid = build_credentials(config_class)
    _, defined_tags = define_tags(user_name, "user", config_class)

    print(f"{SEPARATOR}"
        f"Do you want to create this user: \n"
        f"- user name: {YELLOW}{user_name}{RESET}\n"
        f"- given name: {YELLOW}{name.split("-")[0]}{RESET}\n"
        f"- family Name: {YELLOW}{name.split("-")[1] if "-" in name else "User"}{RESET}\n"
        f"- description: {YELLOW}{description}{RESET}\n"
        f"- email: {YELLOW}{email}{RESET}\n"
        f"- tags: {YELLOW}{defined_tags}{RESET}\n"
        f"- group appartenance: {YELLOW}{group_name}{RESET}\n"
    )

    user_validation = user_validation_by_y_n("select your answer (Y/n) : ")
    if user_validation == 'Y':
        identity_domains_client.create_user(
            user=User(
                schemas=["urn:ietf:params:scim:schemas:core:2.0:User"],
                user_name=user_name,
                name={
                    "givenName": name.split("-")[0].lower(),
                    "familyName": name.split("-")[1].lower() if "-" in name else user_name
                },
                emails=[{
                    "value": email,
                    "type": "work",
                    "primary": True
                }],
                groups=[{
                    "value": group_ocid,
                    "name": group_name,
                    "type": "direct",
                }],
                display_name=user_name
            )
        )

        # member = GroupMembers(
        #     value=user_id,  # ID du user
        #     type="User"  # Type du member
        # )

        print(f"{GREEN}✅ User created successfully!{RESET}")
    else:
        print(f"{RED}exit program ...{RESET}")
        sys.exit(0)

def users_handler(identity_domains_client, identity_client, config_class):
    groups_handler(identity_client, config_class)
    create_new_user(identity_domains_client, config_class)