import os
from InquirerPy import inquirer
import oci

def get_groups_list(groups_list: list[dict[str, str]]) -> dict:
    try:
        print(f"get_groups_list {groups_list}")
        structured_groups_dict= {}
        for group in groups_list:
            display_label = f"{group.display_name}-{group.id}"

            structured_groups_dict[display_label] = {
                "tenancy_id": group.tenancy_ocid,
                "dmn_id": group.domain_ocid,
                "gp_cmp_id": group.compartment_ocid,
                "gp_ocid": group.id
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

def groupes_management(identifier):
    return None