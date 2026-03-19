# Infrastructure Management Tool (still in developpment)

The `oci-python` CLI is an **interactive assistant** that automates administrative tasks for Oracle Cloud Infrastructure (OCI). It is an IAM management tool that guides users step-by-step through the creation of compartments, users, groups, and policies with **automatic validation and standardization**.

**In short:** An interactive interface that ensures you do things in a secure and traceable way.

## 1. System Architecture Overview

```
oci-python/
├── srcs/
│   ├── classes.py                          (Data models = “Toolkit”)
│   │
│   ├── governance_resources/               (Governance resources)
│   │   └── compartment_handler.py          (Compartment management)
│   │
│   ├── management_resources/               (IAM “management” resources)
│   │   ├── users_handler.py                (User management)
│   │   ├── groups_handler.py              (Group management)
│   │   └── policy_handler.py               (Policy management)
│   │
│   └── utils/                              (Utilities)
│       ├── config.py                       (Tags, styles, constants)
│       └── inquire_handler.py              (Interactive interface)
│
├── requirements.txt                        (Dependencies)
├── build.sh & install.sh                  (Deployment scripts)
└── .env                                    (OCI environment variables)
```

<img src="../img/oci-python-workflow.png" alt="schemas" width="600">

## 2. How It Works

**see in workflow README md file**

## 3. Getting Started

### Prerequisites

* OCI CLI configured: A valid `~/.oci/config` file with your API keys (see on [README.md](../README.md)).
* `.env` file: Must contain your OCI domains (ex: `EDUCHAT_DOMAIN=https://...`).

## Installation

### Option 1 : Download Binary (Easiest)
```bash
# Download the latest release from GitHub Releases
https://github.com/0xCAF3D0OD/terraform-oci/releases/tag/v1.0.0
chmod +x oci-resource-ctl.os_version
./oci-resource-ctl
```

### Option 2 : Build from Source
```bash
git clone https://github.com/0xCAF3D0OD/terraform-oci.git
cd oci-python
pip install -r requirements.txt
pyinstaller oci-resource-ctl.spec
./dist/oci-resource-ctl
```

### Commands

To launch the tool:

```bash
./oci-resourc-ctl
```

### Simple Example: Creating a Test Compartment

1. **Launch:** Select `2A. -- new compartment`.
2. **User:** Select your profile (ex: `vincentRevole`).
3. **Target:** Choose the parent from the list: `dk_company (parent: Tenancy)`.
4. **Input:**
   * Name: `cmp-educhat-test`
   * Description: `Temporary test environment`.
5. **Validation:** The script displays a summary. You type `Y`.
   * **Result:** The compartment is created with the tags `project: educhat` and `env: test` automatically extracted from the name.
