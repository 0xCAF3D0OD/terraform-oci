import oci
import sys
import datetime
from classes import ConfigState
from dotenv import load_dotenv
from InquirerPy import inquirer
from management_resources.groupes_handler import get_groups_list

from utils.config import RED, YELLOW, RESET, STYLE
from utils.config import (
    POLICY_LOCA,
    POLICY_VERB,
    POLICY_SUBJECT,
    POLICY_RES_TYPE
)

from utils.inquire_handler import inquire_display_dict
from governance_resources.compartment_handler import compartment_selection

load_dotenv()

EXIT_OPTION = "exit"

def listing_policies(identity_client, selected_group_id, config_class: ConfigState) -> None:
    list_policies_response = identity_client.list_policies(
        compartment_id=config_class.get_compartment_id(),
        sort_by="NAME",
        sort_order="ASC",
        lifecycle_state="ACTIVE"
    )

def build_policy_statement(group_name, config_class: ConfigState):
    inquirer_details = [
        ("choose your subject: ", POLICY_SUBJECT, "select"),
        ("choose your verb: ", POLICY_VERB, "select"),
        ("choose your resource type(s): ", POLICY_RES_TYPE, "checkbox"),
        ("choose your location: ", POLICY_LOCA, "select"),
        ("input your condition(s): ", "text", ""),
    ]
    policy_details = []
    for inquirer_detail in inquirer_details:
        if "" in policy_details or None in policy_details:
            print(f"{RED}exit the programme ...{RESET}")
            sys.exit(1)
        if inquirer_detail[2] == 'select':
            policy_details.append(inquirer.select(
                message=inquirer_detail[0],
                choices=inquirer_detail[1],
                default=None,
                style=STYLE,
            ).execute())
        elif inquirer_detail[2] == 'checkbox':
            policy_details.append(inquirer.checkbox(
                message=inquirer_detail[0],
                choices=inquirer_detail[1],
                default=None,
                style=STYLE,
            ).execute())
        else:
            user_action = inquirer.select(
                message="Is a condition needed ?",
                choices=["Y", "n"],
                default=None,
                style=STYLE
            ).execute()
            if user_action == "Y":
                policy_details.append(inquirer.text(
                    message=inquirer_detail[0],
                    default="",
                    style=STYLE,
                ).execute())
            else:
                policy_details.append("")
                pass
    # print(f"'Allow "
    #       f"{YELLOW}{policy_details[0].upper()}{RESET} to "
    #       f"{YELLOW}{policy_details[1].upper()}{RESET} {group_name} "
    #       f"{YELLOW}{policy_details[2]}{RESET} in "
    #       f"{YELLOW}{policy_details[3].upper()}{RESET} {ConfigState.target_compartment_credentials['cmp_ocid'])} where "
    #       f"{YELLOW}{policy_details[4]}{RESET}'"
    # )

    resources = ",".join(policy_details[2])
    return (f"Allow "
          f"{policy_details[0].upper()} {config_class.domain_data.display_name}/{group_name} to "
          f"{policy_details[1].upper()} "
          f"{resources} in "
          f"{policy_details[3].upper()} {config_class.get_compartment_id()}"
          f"{f' where {policy_details[4]}' if policy_details[4] else ''}"
    )

def creat_new_policy_response(identity_client, group_name, config_class: ConfigState) -> None:
    name = inquirer.text(
        message="enter new policy name: ",
        style=STYLE,
        default="",
    ).execute()
    policy_name = f"P-{group_name}-{name}"
    statement = build_policy_statement(group_name)
    description = inquirer.text(
        message="enter description: ",
        style=STYLE,
        default=""
    ).execute()
    identity_client.create_policy(
        create_policy_details=oci.identity.models.CreatePolicyDetails(
            compartment_id=config_class.get_compartment_id(),
            name=policy_name,
            statements=[statement],
            description=description,
            version_date=datetime.datetime.now().strftime("%Y-%m-%d")
        )
    )

def policy_handler(identity_client, config_class: ConfigState) -> None:
    try:
        structured_groupe_dict = get_groups_list(config_class.get_groups("list"), config_class)
        if not structured_groupe_dict:
            raise ValueError(f"{RED}groups not created or not found{RESET}")

        selected_group_name = inquire_display_dict(
            structured_groupe_dict,
            "Which group do you need ?")
        # listing_policies(identity_client, selected_group_name)
        creat_new_policy_response(identity_client, selected_group_name, config_class)
    except Exception as e:
        print(f"Exception in policy handler: {e}")
