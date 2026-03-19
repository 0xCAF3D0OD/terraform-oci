##  Complete Flowchart

<img src="../img/oci-python-workflow.png" alt="schemas" width="600">

<img src="../img/oci-global-workflow.png" alt="schemas" width="600">


## Phase 1: Authentification & Configuration
```doctest
# config.py + inquire_handler.py

config_file = oci.config.from_file()  # Lit ~/.oci/config [DEFAULT]
config_class = ConfigState()           # Create the tool box"
```
#### Workflow:
1. OCI CLI automatically detects ~/.oci/config 
2. Loads the [DEFAULT] profile (admin) 
3. Creates a ConfigState object to store the data

```doctest
# inquire_handler.py → inquirer_oci_domains()

1. Read the environment variables: EDUCHAT_DOMAIN, DK_COMPANY_DOMAIN, etc.
2. Display a selection menu
3. Create an IdentityDomainsClient
4. Return the URL of the selected domain
```
#### result:
```doctest
ConfigState.domain_data = Domain(
    id="...",
    url="https://...",
    display_name="educhat"
)
```

<img src="../img/oci-user-selection.png" alt="schemas" width="600">

---

## Workflow 2A: Create a Compartment:

### Step 1: Selecting the Parent Compartment
**Function:** `compartment_selection()`
```doctest
# 1. Recursion to list ALL compartments
all_compartments = get_compartment_list(
    identity_client,
    tenancy_id="ocid1.tenancy.oc1...",
    parent_name="dk_company"
)

# 2. Result = hierarchical dictionary
{
    “cmp_dev (parent: dk_company)”: {
        “cmp_name”: “cmp_dev”,
        “cmp_parent”: “dk_company”,
        “cmp_ocid”: “ocid1.compartment.oc1..xxx”
    },
    “cmp_test (parent: cmp_dev)”: {
        “cmp_name”: “cmp_test”,
        “cmp_parent”: “cmp_dev”,
        “cmp_ocid”: “ocid1.compartment.oc1..yyy”
    },
    ...
}

# 3. Selection menu
selected = inquire_display_dict(compartments, “Which compartment do you need?”)
ConfigState.target_compartment = compartments[selected]
```
### Result:
```doctest
ConfigState.target_compartment = {
    “cmp_name”: “cmp_dev”,
    “cmp_ocid”: “ocid1.compartment.oc1..xxx”
}
```

### Step 2: User Inputs with Validation

**Function:** `compartment_requirements()`

### Step 3: Automatic Tag Generation

**Function:** `define_tags(name, “compartment”, config_class)`

```python
# Input: “cmp-educhat-dev”
# Parsing: split(“-”) → [“cmp”, ‘educhat’, “dev”]

freeform_tags = {
    ‘env’: ‘dev’,                          # ← Extracted from the name
    ‘team’: ‘devops’,                      # ← Fixed
    'project': ‘educhat’,                  # ← Extracted from the name
    ‘created_by’: ‘vincentRevole’,         # ← User configuration
    ‘backup-required’: ‘false’             # ← Logic: dev=false
}
defined_tags = {
    ‘Oracle-Tags’: {
        ‘CreatedBy’: ‘vincentRevole’,      # ← Timestamp
        ‘CreatedOn’: ‘2026-03-18 14:32’
    }
}
```

### Step 4: Summary & Validation

**Function:** `resume_compartment_data()` + `user_validation_by_y_n()`

### Step 5: Create or Modify

```python
if choice == “Y”:
    # CREATE
    
elif choice == “n”:
    # MODIFY
    field = input(“What to modify? (name/description)”)
    if field == “name”:
        new_name = input(“New name: ”)
        # Regenerate tags with the new name
    elif field == “description”:
        new_description = input(“New description: ”)
    # Display the summary with the new values
    # Infinite loop → Y/n
else:
    exit()
```

---

## Workflow 4A: Create a User

### Step 1: Select the Domain & Existing Users

**Function:** `inquirer_oci_users()`

```python
# 1. Select the domain
domain_url = inquirer_oci_domains(config_file, config_class)

# 2. Create a domain-specific client
identity_domains_client = IdentityDomainsClient(config_file, domain_url)

# 3. List existing users
response = identity_domains_client.list_users(
    attributes="userName,groups,ocid"
)

# 4. Parse the users and their groups
users_list = {
    “vincentRevole”: {
        “user_name”: “vincentRevole”,
        “user_id”: “c00cae...”,
        “user_ocid”: “ocid1.user.oc1...”,
        “groups”: [
            {
                “group_name”: “Grp-DevOps-Admin”,
                “group_id”: “83038...f”,
                “ocid”: “ocid1.group.oc1...”
            }
        ]
    },
    ...
}

# 5. Selection Menu
selected_user = inquire_display_dict(users_list, “Which user do you want?”)
ConfigState.target_user_credentials = users_list[selected_user]
```

### Step 2: Group Selection

**Function:** `groups_handler()`

```python
# 1. Structure the list of groups
groups_list = config_class.get_groups(“list”)

structured_groups = {
    “Grp-DevOps-Admin-xxx”: {
        “group_ocid”: “ocid1.group.oc1...”,
        “group_id”: “xxx”,
        “group_name”: “Grp-DevOps-Admin-xxx”
    },
    ...
}
# 2. Selection Menu
selected_group = inquire_display_dict(structured_groups, “Which group?”)
ConfigState.target_group = structured_groups[selected_group]
```

### Step 3: Building Credentials

**Function:** `build_credentials()`

```python
# User input
name = input(“Enter name (firstname-lastname): ”)   # “jean-dupont”

# Parse the selected group
group_name = “Grp-DevOps-Admin”
_, team, role, grp_id = group_name.split(“-”) # [“Grp”, “DevOps”, ‘Admin’, “xxx”]

# Automatic construction
user_name = f“U-{team}{role}-{name}”          # “U-DevOpsAdmin-jean-dupont”
email = f“{name}@{team}{role}.ch”             # “jean-dupont@DevopsAdmin.ch”
description = input(“Description: ”)

return {
    “name”: “jean-dupont”,
    “user_name”: “U-DevOpsAdmin-jean-dupont”,
    “email”: “jean-dupont@devopsadmin.ch”,
    “group_name”: “Grp-DevOps-Admin”,
    “group_ocid”: “ocid1.group.oc1.....”
}
```
### Étape 4 : Résumé & Validation

### Step 5: Creating the User

**Function:** `create_new_user()`

```python
if user_validation == “Y”:
    identity_domains_client.create_user(
        user=User(
            schemas=[“urn:ietf:params:scim:schemas:core:2.0:User”],
            user_name=“U-DevOpsAdmin-jean-dupont”,
            name={
                “givenName”: “jean”,
                “familyName”: “dupont”
            },
            emails=[{
                “value”: “jean-dupont@devopsadmin.ch”,
                “type”: “work”,
                “primary”: True
            }],
            groups=[{
                “value”: “ocid1.group.oc1...”,     # Group OCID
                “name”: “Grp-DevOps-Admin”,
                “type”: “direct”
            }],
            display_name="U-DevOpsAdmin-jean-dupont"
        )
    )
    print(“✅ User created successfully!”)
else:
    print(“❌ Exit program...”)
    sys.exit(0)
```

---

## Workflow 3A: Create a Policy

### Step 1: Select the Group

```python
# Same logic as Workflow 4A, Step 2
structured_groups = get_groups_list(...)
selected_group = inquire_display_dict(structured_groups, “Which group?”)
```

### Step 2: Constructing the Policy Statement

**Function:** `build_policy_statement()`

The policy follows this **OCI template:**
```
Allow <subject> to <verb> <resource-type> in <location> where <conditions>
```

**Interactive Workflow:**

<img src="../img/oci-policy-workflow.png" alt="schemas" height="600">

### Practical Example

```python
POLICY_SUBJECT = [“group”]
POLICY_VERB = [“inspect”, “read”, ‘use’, “manage”]
POLICY_RES_TYPE = [
    “all-resources”,
    “instance-family”,
    “virtual-network-family”,
    “database-family”,
    ...
]
POLICY_LOCA = [“compartment id”, “tenancy id”]

# User selections:
subject = “group”
verb = “manage”
resource_types = [“instance-family”, “virtual-network-family”]
location = “compartment id”
condition = “”

# Built statement:
"Allow group educhat/Grp-DevOps-Admin to manage 
 instance-family,virtual-network-family in 
 compartment id ocid1.compartment.oc1..."
```

### Step 3: Policy Settings

```python
name = input(“Enter policy name: ”)     # “dev-perms”
policy_name = f“P-{group_name}-{name}”  # “P-Grp-DevOps-Admin-dev-perms”
description = input(“Description: ”)
```

### Step 4: Creation

```python
identity_client.create_policy(
    create_policy_details=CreatePolicyDetails(
        compartment_id="ocid1.compartment.oc1...",
        name="P-Grp-DevOps-Admin-dev-perms",
        statements=[“Allow group educhat/...”],
        description="Allows DevOps to manage compute resources",
        version_date="2026-03-18"
    )
)
```

---

## Data Classes: ConfigState

**File:** `classes.py`

```python
@dataclass
class ConfigState:
    “”“The global state of the application”“”
    
    # Authentication
    config_file_entries: Dict[str, Any]   # ~/.oci/config parsed
    
    # User selections
    domain_data: Optional[Dict]           # Selected OCI Domain
    target_compartment: Optional[Dict]    # Selected parent compartment
    target_user: Optional[Dict]           # Selected user
    target_group: Optional [Dict]         # Selected group
    target_policy: Optional[Dict]         # Created policy
    
    # Access data (IAM resources)
    iam_user_resources_access: Dict[str, Any]  # {
        “compartments”: {“data”: [...], ‘status’: “ok”},
        “users”: {“data”: [...], ‘status’: “ok”},
        “groups”: {“data”: [...], ‘status’: “ok”},
        “policies”: {“data”: [...], ‘status’: “ok”}
    }
    
    # Helper methods
    def get_compartment(self) -> Dict:
        return self.iam_user_resources_access[“compartment”][“data”]
    
    def get_groups(self, type_data: str) -> Dict:
        ...
```

---


## Utilities: Validation

### config.py

```python

# OCI IAM constants
POLICY_SUBJECT = [Choice(value=None, name="Exit"), “group”]
POLICY_VERB = [“inspect”, “read”, ‘use’, “manage”]
POLICY_LOCA = [“compartment id”, “tenancy id”]
POLICY_RES_TYPE = [
    “all-resources”,
    “instance-family”,
    “virtual-network-family”,
    “database-family”,
    ...
]
```

### inquire_handler.py

```python
def inquire_display_dict(dictionary: dict, key_phrase: str):
    “”“Displays a selection menu for a dictionary”“”
    choices = [EXIT_OPTION] + list(dictionary.keys())
    user_selection = inquirer.select(
        message=key_phrase,
        choices=choices,
        style=STYLE
    ).execute()
    return user_selection

def user_validation_by_y_n(message: str) -> str:
    “”“Y/n validation”“”
    return inquirer.text(
        message=message,
        validate=lambda r: r in [“Y”, “n”]
    ).execute()
```

---

## Recursive Flow: Compartment Hierarchy

```
Tenancy (root)
├── dk_company
│   ├── cmp_dev
│   │   ├── cmp_educhat_dev
│   │   └── cmp_test_dev
│   └── cmp_prod
├── external
└── sandbox
```

**Code:** `get_compartment_list()` = **recursion**

```python
def get_compartment_list(
    identity_client,
    current_id,           # Current OCID
    parent_name,          # Parent name (for display)
    list_compartments
):
    # 1. Retrieve child compartments
    response = identity_client.list_compartments(
        compartment_id=current_id,
        lifecycle_state="ACTIVE"
    )
    
    # 2. For each child compartment
    for compartment in response.data:
        display_label = f“{compartment.name} (parent: {parent_name})”
        list_compartments[display_label] = {
            “cmp_name”: compartment.name,
            “cmp_parent”: parent_name,
            “cmp_ocid”: compartment.id
        }
        
        # 3. 🔄 RECURSION: explore children
        get_compartment_list(
            identity_client,
            compartment.id,      # ← Go down one level
            compartment.name,
            list_compartments
        )
    
    return list_compartments
```

**Result:**
```python
{
    “dk_company (parent: Tenancy)”: {...},
    “cmp_dev (parent: dk_company)”: {...},
    “cmp_educhat_dev (parent: cmp_dev)”: {...},
    “cmp_test_dev (parent: cmp_dev)”: {...},
    “cmp_prod (parent: dk_company)”: {...},
    ...
}
```

---

## Use Case: Create a Complete Infrastructure

### Scenario: New DevOps Team

```
1.️  Create Compartment
    - Parent: dk_company
    - Name: cmp-newteam-dev
    - Tags: project=newteam, env=dev

2.  Create Group
    - Name: Grp-NewTeam-Admin
    - Domain: educhat

3.  Create Users
    - user1: U-NewTeamAdmin-alice-martin
    - user2: U-NewTeamAdmin-bob-dupont
    
4.  Create Policy
    - Allow group educhat/Grp-NewTeam-Admin
    - to manage instance-family,virtual-network-family
    - in compartment id <cmp-newteam-dev>

5.  Validate
    - Alice can access the compartment
    - Alice cannot leave the compartment
    - Alice cannot delete the group
```

---

## Technology & Dependencies

| Package | Role |
|---------|------|
| **oci** | Oracle Cloud SDK (API calls) |
| **InquirerPy** | Interactive menus (select, text, checkbox) |
| **python-dotenv** | Load environment variables (.env) |

```bash
# Installation
pip install oci InquirerPy python-dotenv

# Usage
python3 main.py
```

---

## Real-World Execution Example

```bash
$ python3 main.py

Select domain: [1] Exit
               [2] educhat
               [3] dk_company
                ↓
                Select: educhat ✓

=== Main Menu ===
[1] Exit
[2A] New Compartment
[3A] New Policy
[4A] New User
↓
Select: 2A ✓

Which compartment do you need?
[1] dk_company (parent: Tenancy)
[2] cmp_dev (parent: dk_company)
[3] cmp_test (parent: cmp_dev)
↓
Select: cmp_dev ✓

Enter the compartment name: cmp-educhat-prod
Enter description: Production environment for educhat

=== Compartment Configuration ===
Parent: cmp_dev → ocid1.compartment.oc1...
Name: cmp-educhat-prod
Description: Production environment
Tags:
  - env: prod
  - project: educhat
  - created_by: vincentRevole
  - backup-required: true
=== ===

Do you confirm? (Y/n): Y ✓

✅ Compartment management has been created
```

---

**💡 This is a production-ready tool that trades flexibility for security and traceability!**