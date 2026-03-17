from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class ConfigState:
    """Application configuration state."""

    config_file_entries: Dict[str, Any] = field(default_factory=dict),

    iam_user_resources_access: Optional[Dict[str, Any]] = field(default=dict),

    domain_data: Optional[Dict[str, Any]] = field(default=dict),

    target_compartment_credentials: Optional[Dict[str, Any]] = field(default=dict),

    compartment_id: Optional[str] = '',
    compartment_name: Optional[str] = '',

    parent_compartment_id: Optional[str] = '',
    parent_compartment_name: Optional[str] = '',

    target_user_credentials: Optional[Dict[str, Any]] = field(default=dict),
