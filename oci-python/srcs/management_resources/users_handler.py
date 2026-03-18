import sys

import oci
from classes import ConfigState
from InquirerPy import inquirer
from utils.config import RED, YELLOW, RESET, STYLE
from utils.config import define_tags
from utils.inquire_handler import user_validation_by_y_n

def create_new_user(identity_client, group_name):
    name = inquirer.text(
        message="enter new user with this format: firstname-lastname: ",
        style=STYLE,
        default="",
    ).execute()
    user_name = f"U-{group_name}-{name}"
    _, defined_tags = define_tags(user_name)

    description = inquirer.text(
        message="enter user description: ",
        style=STYLE,
        default=""
    ).execute()

    inquirer_message = ("Do you want to create this user: \n"
                f"- user name: {YELLOW}{user_name}{RESET}\n"
                f"- description: {YELLOW}{description}{RESET}\n"
                f"- email: {YELLOW}{name}@{group_name}.ch{RESET}\n"
                f"- tags: {YELLOW}{defined_tags}{RESET}\n"
                f"select your answer (Y/n) : ")

    user_validation = user_validation_by_y_n(inquirer_message)

    if user_validation == 'Y':
        identity_client.create_user(
            create_user_details=oci.identity.models.CreateUserDetails(
                compartment_id=ConfigState.target_compartment_credentials['cmp_ocid'],
                name=user_name,
                description=description,
                email=f"{name}@{group_name}.ch",
                defined_tags=defined_tags
            )
        )
    else:
        print(f"{RED}exit program ...{RESET}")
        sys.exit(0)

def users_handler(identity_client, config_class):
    print(f"target data: {ConfigState.get_groups()}")
    # create_new_user(identity_client, ConfigState.target_compartment_credentials['cmp_ocid'])