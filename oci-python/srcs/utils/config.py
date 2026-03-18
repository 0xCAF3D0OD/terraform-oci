from InquirerPy import inquirer
from InquirerPy.utils import get_style
from InquirerPy.base.control import Choice
from classes import ConfigState
import datetime
from functools import wraps
import oci

# Codes ANSI
GREEN = "\033[1;32m"  # Bold Green (valeurs)
YELLOW = "\033[1;33m"  # Bold Yellow (labels)
RED = "\033[1;31m"  # Bold Yellow (labels)
RESET = "\033[0m"  # Reset

STYLE = get_style({
        "questionmark": "#e5c07b",
        "message": "#e5c07b bold",
        "pointer": "#61afef bold",
        "answermark": "#98c379",
        "answer": "#98c379 bold",
    },
    style_override=False) # style_override=False permet de garder les couleurs de base pour le reste

# oci_config: {
#   'log_requests': False,
#   'additional_user_agent': '',
#   'pass_phrase': None,
#   'user': 'ocid1.user.oc1..aaaaa...',
#   'fingerprint': '2a:dd:87:...',
#   'tenancy': 'ocid1.tenancy.oc1..aaaa...',
#   'region': 'us-ashburn-1',
#   'key_file': '~/.oci/vrevol_keys/oci_api_key.pem'
# }

def define_tags(new_compartment_name: str) -> tuple[dict, dict]:
    cmp_tag, project_tag, env_tag = new_compartment_name.split("-")
    freeform_tags = {
        'env': env_tag,
        'team': 'devops',
        'project': project_tag,
        'created_by': ConfigState.target_user_credentials["user_name"],
        'backup-required': "false" if env_tag == "dev" else "true"
    }

    defined_tags = {
        'Oracle-Tags': {
            'CreatedBy': ConfigState.target_user_credentials["user_name"],
            'CreatedOn': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    }

    return freeform_tags, defined_tags

# Allow <subject> to <verb> <resource-type> in <location> where <conditions>

POLICY_SUBJECT = [Choice(value=None, name="Exit"), "group"]
POLICY_VERB = [Choice(value=None, name="Exit"), "inspect", "read", "use", "manage"]
POLICY_LOCA = [Choice(value=None, name="Exit"), "compartment id", "tenancy id"]
POLICY_RES_TYPE = [
    Choice(value=None, name="Exit"),
    "all-resources",
    "cluster-family",
    "compute-management-family",
    "data-catalog-family",
    "data-science-family",
    "autonomous-database-family",
    "database-family",
    "dns",
    "email-family",
    "file-family",
    "instance-agent-command-family",
    "instance-agent-family",
    "instance-family",
    "key-family",
    "load-balancers",
    "network-security-group",
    "object-family",
    "optimizer-api-family",
    "osms-family",
    "osmh-family",
    "secret-family",
    "virtual-network-family",
    "recovery-service-family",
    "volume-family",
    "network-load-balancers",
    "leaf-certificate-family",
    "certificate-authority-family",
    "nosql-family"
]
