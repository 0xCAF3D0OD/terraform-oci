from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class ConfigState:
    """Application configuration state."""


    config_file_entries: Dict[str, Any] = field(default_factory=dict)

    domain_data: Optional[Dict[str, Any]] = field(default_factory=dict)

    iam_user_resources_access: Optional[Dict[str, Any]] = field(default_factory=dict)

    target_compartment_credentials: Optional[Dict[str, Any]] = field(default_factory=dict)
    target_user_credentials: Optional[Dict[str, Any]] = field(default_factory=dict)

    compartment_id: Optional[str] = ''
    compartment_name: Optional[str] = ''
    parent_compartment_id: Optional[str] = ''
    parent_compartment_name: Optional[str] = ''

    target_compartment: Optional[Dict[str, Any]] = field(default_factory=dict)
    target_group: Optional[Dict[str, Any]] = field(default_factory=dict)
    target_user: Optional[Dict[str, Any]] = field(default_factory=dict)
    target_policy: Optional[Dict[str, Any]] = field(default_factory=dict)


    def get_compartment(self) -> Dict[str, Any]:
        return self.iam_user_resources_access["compartment"]["data"]

    def get_groups(self, type_data: str) -> Dict[str, Any] | list[Dict[str, Any]]:
        if type_data == "list":
            return self.iam_user_resources_access["groups"]["data"].resources
        elif type_data == "name":
            return self.target_group["group_name"]
        elif type_data == "ocid":
            return self.target_group["group_ocid"]
        elif type_data == "id":
            return self.target_group["group_id"]
        return self.iam_user_resources_access["groups"]["data"]


    def get_policies(self) -> Dict[str, Any]:
        return self.iam_user_resources_access["policies"]["data"]

    def get_policies_status(self) -> Dict[str, Any]:
        return self.iam_user_resources_access["policies"]["status"]

    def get_users(self) -> Dict[str, Any]:
        return self.iam_user_resources_access["users"]["data"]

    def get_tenancy(self) -> str:
        return self.config_file_entries["tenancy"]

    def get_username(self) -> Dict[str, Any]:
        return self.target_user_credentials["user_name"]

    def get_compartment_status(self) -> Dict[str, Any]:
        return self.iam_user_resources_access["compartments"]["status"]

    def get_compartment_id(self) -> Dict[str, Any]:
        return self.target_compartment['cmp_ocid']

    def get_compartment_name(self) -> Dict[str, Any]:
        return self.target_compartment["cmp_name"]