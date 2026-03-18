import os
import oci

from utils.config import RED, RESET
from utils.inquire_handler import inquire_display_dict

def get_groups_list(groups_list: list[dict[str, str]]) -> dict:
    try:
        structured_groups_dict= {}
        for group in groups_list:
            display_label = f"{group.display_name}-{group.id}"
            structured_groups_dict[display_label] = {
                "tenancy_id": group.tenancy_ocid,
                "domain_id": group.domain_ocid,
                "group_cmp_id": group.compartment_ocid,
                "group_ocid": group.ocid,
                "group_id": group.id,
                "group_name": display_label
            }

        return structured_groups_dict

    except oci.exceptions.ServiceError as e:
        # Erreur côté OCI (ex: 403 Forbidden si tu n'as pas accès à un sous-compartiment)
        print(f"⚠️  Service error on {display_label}: {e.message}")
        return {}
    except Exception as e:
        # Erreur critique (ex: Coupure réseau)
        print(f"❌ Critical error fetching compartments: {e}")
        return {}

def groups_handler(identity_domains_client, config_class) -> None:
    structured_groupe_dict = get_groups_list(config_class.get_groups("list"))
    if not structured_groupe_dict:
        raise ValueError(f"{RED}groups not created or not found{RESET}")

    selected_group_name = inquire_display_dict(
        structured_groupe_dict,
        "Which group do you need ?")
    if selected_group_name:
        config_class.target_group = structured_groupe_dict[selected_group_name]
        print(f"{config_class.target_group}")
    return None