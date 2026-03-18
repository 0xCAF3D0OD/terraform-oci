from __future__ import annotations

import sys

import oci
from dotenv import load_dotenv
from InquirerPy import inquirer
from classes import ConfigState
from utils.config import GREEN, YELLOW, RED, RESET, STYLE
from utils.config import define_tags
from utils.inquire_handler import inquire_display_dict, user_validation_by_y_n

load_dotenv()

EXIT_OPTION = "exit"

def get_compartment_list(
        identity_client: oci.identity.IdentityClient,
        current_id: str,
        parent_name: str,
        list_compartments: dict[str, dict[str, str]]
) -> dict:
    try:
        # Appel API
        list_compartments_response = identity_client.list_compartments(
            compartment_id=current_id,
            sort_by="NAME",
            sort_order="ASC",
            lifecycle_state="ACTIVE"
        )

        for compartment in list_compartments_response.data:
            # On crée un label unique pour éviter d'écraser des doublons (Nom + Parent)
            display_label = f"{compartment.name} (parent: {parent_name})"
            list_compartments[display_label] = {
                "cmp_name": compartment.name,
                "cmp_parent": parent_name,
                "cmp_ocid": compartment.id,
            }
            get_compartment_list(identity_client, compartment.id, compartment.name, list_compartments)

        return list_compartments

    except oci.exceptions.ServiceError as e:
        # Erreur côté OCI (ex: 403 Forbidden si tu n'as pas accès à un sous-compartiment)
        print(f"⚠️  Skipping sub-compartments of {parent_name}: {e.message}")
        return list_compartments
    except Exception as e:
        # Erreur critique (ex: Coupure réseau)
        print(f"❌ Critical error fetching compartments: {e}")
        return list_compartments


def resume_compartment_data(
        new_compartment_name: str,
        description: str,
        freeform_tags,
        defined_tags,
        config_class: ConfigState
) -> None:
    print(f"\n{YELLOW}=== Compartment Configuration ==={RESET}\n"
          f"{YELLOW}Parent compartment:{RESET} {GREEN}{config_class.get_compartment_name()}{RESET} → "
          f"{GREEN}{config_class.get_compartment_id()}{RESET}\n"
          f"{YELLOW}Compartment name:{RESET} {GREEN}{new_compartment_name}{RESET}\n"
          f"{YELLOW}Description:{RESET} {GREEN}{description}{RESET}\n"
          f"{YELLOW}Freeform tags:{RESET} {GREEN}{freeform_tags}{RESET}\n"
          f"{YELLOW}Defined tags:{RESET} {GREEN}{defined_tags}{RESET}\n"
          f"{YELLOW}{'='*35}{RESET}\n")

def validate_compartment_name(new_compartment_name: str, config_class: ConfigState) -> str:
    while new_compartment_name == config_class.get_compartment_name():
        print(f"❌ '{new_compartment_name}' is the same as parent. Please use a different name.")
        new_compartment_name = inquirer.text(
            message="Enter a NEW compartment name:",
            style=STYLE
        ).execute()

    return new_compartment_name

def compartment_requirements(config_class: ConfigState) -> tuple[str | None, str]:
    # Name validation
    new_compartment_name = inquirer.text(
        message="Enter the compartment name:",
        style=STYLE,
        validate=lambda result: len(result.split("-")) == 3,
        invalid_message="Invalid format, use 'cmp-name-env' (ex: cmp-educhat-dev)",
    ).execute()

    # Parent compartment verification (retry loop)
    new_compartment_name = validate_compartment_name(new_compartment_name, config_class)

    # Description Validation
    new_compartment_description = inquirer.text(
        message="Enter the compartment description:",
        style=STYLE,
        validate=lambda result: 0 < len(result) <= 400,
        invalid_message="Description must be between 1 and 400 chars"
    ).execute()

    return new_compartment_name, new_compartment_description

def create_new_compartment(identity_client: oci.identity.IdentityClient, config_class: ConfigState) -> None:
    try:
        new_compartment_name, description = compartment_requirements(config_class)
        freeform_tags, defined_tags = define_tags(new_compartment_name, "compartment", config_class)
        while True:
            resume_compartment_data(
                new_compartment_name,
                description,
                freeform_tags,
                defined_tags,
                config_class
            )
            choice = user_validation_by_y_n("do you want to create this new compartment: Y/n")
            if choice == "Y":
                identity_client.create_compartment(
                    create_compartment_details=oci.identity.models.CreateCompartmentDetails(
                        compartment_id=config_class.get_compartment_id(),
                        name=new_compartment_name,
                        description=description,
                        freeform_tags=freeform_tags,
                        defined_tags=defined_tags
                    ))

                print(f"{GREEN}compartment management has been created{RESET}")
                break
            elif choice == "n":
                field = inquirer.text(
                    message="What to modify? (name/description) or nothing for exit: ",
                    style=STYLE,
                    validate=lambda result: result == "name" or result == "description" or result == "",
                    invalid_message="Please fill: name or description if want to exit touch enter",
                ).execute()
                if field == "name":
                    new_compartment_name = input("New name: ").strip()
                    freeform_tags, defined_tags = define_tags(new_compartment_name, "compartment", config_class)
                elif field == "description":
                    description = input(f"\n{YELLOW}New description: {RESET}").strip()
                else:
                    print(f"\n{RED}exit the programme{RESET}")
                    return
            else:
                print("❌ Choix invalide")
    except oci.exceptions.ConfigFileNotFound as e:
        raise
    except oci.exceptions.ClientError as e:
        raise
    except oci.exceptions.ConnectTimeout as e:
        raise
    except Exception as e:
        print(f"Error in create_compartment: {e}")

def compartment_selection(identity_client: oci.identity.IdentityClient, config_class: ConfigState) -> None:
    all_compartments = {}

    list_compartments = get_compartment_list(
        identity_client,
        config_class.get_tenancy(),
        "dk_company",
        all_compartments
    )
    if not list_compartments:
        raise ValueError(f"{RED}compartment not created or not found{RESET}")

    selected_compartment_name = inquire_display_dict(
        list_compartments,
        "Which compartment do you need ?")
    if selected_compartment_name == EXIT_OPTION:
        print(f"{RED}exit program ... {RESET}")
        sys.exit(0)
    selected_compartment_credential = list_compartments[selected_compartment_name]
    config_class.target_compartment = selected_compartment_credential
    return None

#{
#   'user_name': 'vincentRevole@admindev.com',
#   'user_id': 'c00cae...',
#   'user_ocid': 'ocid1.user.oc1..aaaaaaaa...',
#   'groups': [{
#       'group_name': 'Grp-DevOps-Admin',
#       'group_id': '83038...f',
#       'ocid': 'ocid1.group.oc1..aaaaaaaa...'
#    }]
#}
def compartment_handler(identity_client, config_class: ConfigState) -> None:
    try:
        compartment_selection(identity_client, config_class)
        create_new_compartment(identity_client, config_class)

    except oci.exceptions.ServiceError as e:
        # Erreurs retournées par l'API Oracle (ex: 403 Forbidden, 404 Not Found)
        print(f"❌ OCI Service Error: status={e.status}, code={e.code}, message={e.message}")

    except oci.exceptions.RequestException as e:
        # Erreurs de connexion (ex: Timeout, pas d'internet)
        print(f"📡 Network Error: Impossible de contacter les serveurs OCI. Vérifiez votre connexion.")

    except KeyError as e:
        # Erreur si le fichier config ou le dictionnaire est mal formé
        print(f"🔑 Configuration Error: La clé {e} est manquante dans les credentials ou la config.")

    except ValueError as e:
        # Pour ton raise ValueError personnalisé (ex: compartiment non trouvé)
        print(f"⚠️ Validation Error: {e}")

    except Exception as e:
        # Le filet de sécurité pour tout le reste
        print(f"🔥 Unexpected Error [{type(e).__name__}]: {e}")
