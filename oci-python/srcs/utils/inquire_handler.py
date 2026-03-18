from __future__ import annotations
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from classes import ConfigState
from utils.config import STYLE, RED, GREEN, RESET
from typing import Any
import oci
import sys
import os

EXIT_OPTION = "Exit"
SEPARATOR = f"{GREEN} ------------------- {RESET}"

def inquire_display_dict(dictionary: dict[str, str], key_phrase: str) -> Any:
    print(SEPARATOR)
    user_selection = inquirer.select(
        message=f"{key_phrase}",
        style=STYLE,  # On applique le style ici
        choices=[EXIT_OPTION] + list(dictionary.keys()),
        default=EXIT_OPTION
    ).execute()  # .execute() remplace inquirer.prompt()

    if user_selection == EXIT_OPTION:
        print(SEPARATOR)
        print(f"{RED}Exit program ... {RESET}")
        sys.exit(0)
    # On retourne un dictionnaire pour rester cohérent avec tes appels précédents
    return user_selection


def inquire_display_user_actions() -> Any:
    user_action = [
        Choice(value=None, name="1. -- exit"),
        Separator(),
        "2A. -- new compartment",
        # "2B. -- delete compartment",
        Separator(),
        "3A. -- new policy",
        # "3B. -- delete policy",
        Separator(),
        "4A. -- new user",
        # "4B. -- delete user",
        # Separator(),
        # "5A. -- new group",
        # "5B. -- delete group"
    ]

    choice = inquirer.select(
        message=f"Which process do you need ?",
        style=STYLE,
        choices=user_action,
        default=None
    ).execute()

    return choice

def inquirer_oci_domains(config_file, config_class: ConfigState) -> str:
    env_vars = dict(os.environ)
    oci_domains = {key: value for key, value in env_vars.items() if "DOMAIN" in key}

    answers = inquire_display_dict(oci_domains, "Which domain do you need ?")

    identity_client = oci.identity.IdentityClient(config_file)
    get_domain_response = identity_client.get_domain(
        domain_id=oci_domains[answers]
    )
    domain_url = get_domain_response.data.url

    config_class.domain_data = get_domain_response.data

    return domain_url

def inquirer_oci_users(config_file, config_class: ConfigState) \
        -> tuple[dict[str, list[Any] | Any], oci.identity_domains.IdentityDomainsClient]:
    domain_url = inquirer_oci_domains(config_file, config_class)

    identity_domains_client = oci.identity_domains.IdentityDomainsClient(config_file, domain_url)
    response = identity_domains_client.list_users(attributes="userName,groups,ocid")

    users_list = {}

    for user in response.data.resources:
        user_info = {
            "user_name": user.user_name,
            "user_id": user.id,
            "user_ocid": user.ocid,
            "groups": []
        }
        if hasattr(user, 'groups') and user.groups:
            for group in user.groups:
                group_data = {
                    "group_name": group.display,
                    "group_id": group.value,
                    "ocid": group.ocid
                }
                user_info["groups"].append(group_data)
        else:
            print("  - no groups")
        users_list[user.user_name] = user_info
    selected_user_name = inquire_display_dict(users_list, "Which user do you want ?")
    config_class.target_user_credentials = users_list[selected_user_name]
    selected_user_credentials = users_list[selected_user_name]
    return selected_user_credentials, identity_domains_client

def user_validation_by_y_n(message_for_user: str) -> bool:
    user_input = inquirer.text(
        message=message_for_user,
        style=STYLE,
        validate=lambda result: result == "Y" or result == "n",
        invalid_message="Please enter Y or n",
    ).execute()
    return user_input