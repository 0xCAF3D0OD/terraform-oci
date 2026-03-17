# Terraform - Oracle Cloud Infrastructure

## Contenu du Repository

Ce repertoire contient la configuration pour la mise en place d'une infrastructure Oracle Cloud Infrastructure (OCI) 
sécurisée avec Terraform, suivant le principe du **Moindre Privilège**.

### Structure du Projet

- **`terraform/`** - Configuration Terraform IaC pour OCI
  - Compartiments et organisation des ressources

- **`oci-python/`** - Outils Python pour la gestion d'OCI
  - CLI interactif pour la manipulation de la structure OCI (compartiment, utilisateur, politiques, etc.)
  - Utilisation de la librairie `inquirer` pour l'interface utilisateur
  - Script d'aide pour automatiser les tâches courantes

- **`.github/workflows/`** - Pipelines CI/CD (GitHub Actions)
  - Automatisation des builds et deployments du script oci-python

- **`img/`** - Assets et schémas architecturaux
  
## Philosophie et Architecture de Sécurité

### C'est quoi le principe du "Moindre Privilège" ?

![what_is_principle_of_least_privilege.png](img/what_is_principle_of_least_privilege.png)

Le principe du moindre privilège implique de n'accorder aux utilisateurs que l'accès proche du minimum dont ils ont besoin pour 
leur tâche spécifique. Cette stratégie permet de limiter les conséquences d'une potentielle compromission de compte.

Le principe du moindre privilège adopte une approche plus granulaire du contrôle d'accès. 
Chaque utilisateur peut avoir un niveau d'accès différent, en fonction des tâches qu'il doit accomplir.

Le but est donc de passer d'un système qui utilise un seul compte (Admin) à un système cloisonné, sécurisé.

### Pourquoi on utilise ce principe ?

Le principe du moindre privilège est l'un des concepts fondamentaux de la sécurité Zero Trust. Un réseau de confiance 
zéro établit les connexions une par une et les réauthentifie régulièrement. 
Il ne donne aux utilisateurs et aux dispositifs que l'accès dont ils ont absolument besoin, 
ce qui permet de mieux contenir les menaces potentielles à l'intérieur du réseau.

**Problème initial :**
- On utilise un compte Admin pour tout
- **Risque :** Une erreur de frappe ou une clé volée = toute la Tenancy (compte Oracle) compromise

**En gros**: Un grand pouvoir implique de grandes responsabilités, plus tu as du pouvoir plus ton erreur à d'impact sur l'infra.


### C'est quoi la philosophie du Zero Trust ?

La sécurité Zero Trust est une philosophie de sécurité émergente qui part du principe que tout utilisateur ou dispositif
peut présenter une menace. Elle contraste avec les anciens modèles de sécurité qui considèrent que toutes les connexions 
provenant de l'intérieur d'un réseau interne sont dignes de confiance.

---

### La Chaîne de Confiance (4 maillons) (Le "Quoi")

| Objet              | Emplacement dans la console | Son rôle actuel |
|--------------------|----------------------------|-----------------|
| **X (User)**       | Identity > Domains > Users | son identité de travail |
| **X (Group)**      | Identity > Domains > Groups | Le "porte-clés" (X est dedans) |
| **X policy**       | Identity > Policies | L'autorisation qui nomme le groupe DevOps |
| **X compartiment** | Identity > Compartments | La zone où le groupe a le droit d'agir |

---

```
1. Utilisateur (X@dev.com)
   ↓ Compte vide, sans aucun droit par défaut
   
2. Groupe (X)
   ↓ Un "contenant" qui porte les droits (scalable : facile d'ajouter 10 nouveaux employés)
   
3. Policy (X policy)
   ↓ Le contrat juridique : "Le groupe X a le droit de gérer les serveurs, mais rien d'autre"
   
4. Profil CLI ([X])
   ↓ Identité numérique (clés .pem) pour prouver à Oracle qui tu es
```

---

### Les 3 Piliers de la Sécurité

#### La Cloison : Le Compartiment

**Concept :** On arrête de tout mettre dans la "pièce principale" (Root)

- **Action :** Création d'un espace nommé `X...`
- **Métaphore :** Une pièce sécurisée dans une maison dont on a donné les clés à quelqu'un d'autre
- **Bénéfice :** Isolation complète des ressources de test/dev

#### Le Verrou : La Policy

**Concept :** Le document juridique qui définit les droits

- **Action :** Statement précis
```
  Allow group X to manage instance-family in compartment compartiment_Dev
```
- **Mot-clé magique :** `in compartment` = la limite de sécurité
- **Résultat :** En dehors de ce compartiment, le groupe DevOps n'existe pas pour Oracle

#### Le Garde-fou : Le Profil [X]

**Concept :** Configuration du terminal pour être prudent par défaut

- **Action :** Identité de X (droits limités) en tant que profil par défaut
- **Protection :** Pour une action "dangereuse", tu dois consciemment ajouter `--profile ADMIN`
- **Bénéfice :** Protection contre toi-même (erreurs de manipulation)

---

### Comment ca été fait ? (Le "Comment")

#### 1. Sécurisation de l'accès

Au lieu d'un simple mot de passe, il faut utiliser une **paire de clés API (RSA)** :
```
Clé privée (.pem)  →  Reste sur son Mac (jamais partagée)
       ↓
Signature numérique
       ↓
Clé publique  →  Donnée à Oracle (peut être publique)
       ↓
Oracle vérifie la signature
```

**Analogie :** C'est comme un badge magnétique. Oracle reconnaît la signature de la clé de l'utilisateur.

#### 2. Organisation des droits

**Liaison User → Groupe :**
```bash
oci iam group add-user --user-id <X_OCID> --group-id <DEVOPS_GROUP_OCID>
```

**Liaison Groupe → Ressources :**
```
Allow group X to manage instance-family in compartment X
```

---

### Le Résultat Final : Deux "Casquettes"

Tu as maintenant deux identités distinctes sur son ordinateur :

| Profil | Casquette | Rôle | Utilisation |
|--------|-----------|------|-------------|
| **[DEFAULT]** (ou **[ADMIN]**) | 👑 Admin | Propriétaire : créer/supprimer des utilisateurs, payer les factures | Actions rares et sensibles |
| **[X]** | 👷 DevOps | Technicien : créer des serveurs, gérer le réseau dans compartiment_Dev | Travail quotidien |

**Commandes au quotidien :**
```bash
# Travail normal (utilise automatiquement [X])
tf_files plan

# Action administrative (doit être explicite)
oci iam user create --name "nouveau-dev" --profile ADMIN
```

---

### État Final de son Infrastructure

| Élément               | État | Rôle |
|-----------------------|------|------|
| **Utilisateur Admin** | Caché derrière `--profile ADMIN` | Le propriétaire, ne touche à rien au quotidien |
| **Utilisateur X**     | Profil par défaut | Le technicien qui travaille dans son compartiment |
| **Compartiment X**    | Actif | Zone de test isolée et sécurisée |
| **Policy**            | Restrictive | Lie X à son compartiment uniquement |

---

## Phase 1 : Configuration de l'authentification Oracle Cloud

### 1. Génération d'une clé de signature d'API (paire publique/privée)
- Commande : `openssl genrsa -out ~/.oci/oci_api_key.pem 2048`
- Génère la clé publique : `openssl rsa -pubout -in ~/.oci/oci_api_key.pem -out ~/.oci/oci_api_key_public.pem`
- Documentation : https://docs.oracle.com/fr-fr/iaas/Content/API/Concepts/apisigningkey.htm

### 2. Installation de la CLI OCI
- Installation : `bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"`
- Documentation : https://docs.oracle.com/fr-fr/iaas/Content/API/SDKDocs/cliinstall.htm

### 3. Configuration du compte ADMIN (profil DEFAULT)
- Création du fichier `~/.oci/config` avec les credentials du compte admin
- Upload de la clé publique dans la console Oracle Cloud (User Settings → API Keys)
- Documentation : https://docs.oracle.com/fr-fr/iaas/Content/API/Concepts/sdkconfig.htm

Exemple de fichier config :
```
[DEFAULT]
user=<USER_OCID>
fingerprint=xx:xx:xx:xx:xx:xx:xx:xx
tenancy=<TENANCY_OCID>
region=us-ashburn-1
key_file=~/.oci/oci_api_key.pem
```

---

## Phase 2 : Organisation des ressources Oracle Cloud

### 4. Création du compartiment "X"
- But : Organiser les ressources par environnement
- Commande : `oci iam compartment create --name "X" --description "Compartiment de développement" --compartment-id <TENANCY_OCID>`
- OCID obtenu : `<COMPARTMENT_OCID>`

### 5. Création de l'utilisateur DevOps "X@dev.com"
- Console Oracle Cloud → Identity → Users → Create User
- Génération de ses clés API (via la console)
- Configuration du profil [X] dans `~/.oci/config`

Exemple profil X :
```
[X]
user=<USER_OCID>
fingerprint=dc:62:87:d0:20:f6:4f:20
tenancy=<TENANCY_OCID>
region=us-ashburn-1
key_file=path/to/.oci/pem_file
```

---

## Phase 3 : Configuration IAM (Identity & Access Management)

### 6. Compte ADMIN crée le groupe "X"
```bash
oci iam group create \
  --name DevOps \
  --description "Groupe pour l'équipe X" \
  --profile DEFAULT
```

### 7. Compte ADMIN ajoute l'utilisateur X au groupe X
```bash
oci iam group add-user \
  --user-id ocid1.user.oc1..xxxxxxxxxxxxxx \
  --group-id <DEVOPS_GROUP_OCID> \
  --profile DEFAULT
```

### 8. Compte ADMIN crée les policies IAM
```bash
oci iam policy create \
  --compartment-id <COMPARTMENT_OCID> \
  --name "devops-compartment-dev-policy" \
  --description "Permissions pour le groupe DevOps" \
  --statements '[
    "Allow group X to manage virtual-network-family in compartment id <COMPARTMENT_OCID>",
    "Allow group X to manage instance-family in compartment id <COMPARTMENT_OCID>"
  ]' \
  --profile DEFAULT
```

---

### For the Terraform configuration see in the [terraform](tf_files/README.terraform.md)

## Schéma récapitulatif
```
Tenancy Oracle Cloud
│
├── Utilisateur ADMIN (x@protonmail.com)
│   └── Profil [DEFAULT] dans ~/.oci/config
│
├── Utilisateur X (X@dev.com)
│   └── Profil [X] dans ~/.oci/config
│
├── Groupe DevOps
│   └── Contient : X
│
├── Policy "devops-compartment-dev-policy"
│   └── "Allow group DevOps to manage virtual-network-family..."
│   └── "Allow group DevOps to manage instance-family..."
│
└── Compartiment "compartiment_Dev"
    └── VCN "internal" (créé par Terraform avec profil X)
```

### Concepts Clés Oracle Cloud

| Concept OCI | Analogie | Équivalent AWS | Rôle |
|-------------|----------|----------------|------|
| **Tenancy** | L'immeuble entier | AWS Account | Compte root, contient tout |
| **Compartment** | Les étages/pièces | Organizational Units (OU) | Organiser et isoler les ressources |
| **User** | Une personne | IAM User | Identité individuelle |
| **Group** | Une équipe | IAM Group | Regrouper des utilisateurs |
| **Policy** | Le contrat d'accès | IAM Policy | Définir les permissions |
| **VCN** | Réseau virtuel | VPC | Réseau isolé dans le cloud |
| **Subnet** | Sous-réseau | Subnet | Segment du réseau |
| **Instance** | Serveur virtuel | EC2 Instance | Machine virtuelle |

---

![schema](img/infra-oci.png)

---

## Commandes Utiles

### Vérification de la configuration
```bash
# tester l'authentification (profil X)
oci iam user get --user-id ocid1.user.oc1..aaaaaaaaxjkpmkqfklpkzq --profile X

# lester l'authentification (profil ADMIN)
oci iam user get --user-id ocid1.user.oc1..aaaaaaaa7guzlrtcmsqgwwsx72tlllc6rq --profile DEFAULT

# Lister les compartiments accessibles
oci iam compartment list --all --profile X

# Lister les groupes (nécessite permissions)
oci iam group list --all --profile DEFAULT

# Vérifier l'appartenance au groupe
oci iam group list-users --group-id <GROUP_OCID> --profile DEFAULT

# Lister les policies
oci iam policy list --compartment-id <TENANCY_OCID> --all --profile DEFAULT

# Voir le contenu d'une policy
oci iam policy get --policy-id <POLICY_OCID> --profile DEFAULT
```

### Gestion des ressources réseau
```bash
# Lister les VCNs
oci network vcn list --compartment-id <COMPARTMENT_OCID> --profile X

# Détails d'un VCN
oci network vcn get --vcn-id <VCN_OCID> --profile X

# Lister les subnets
oci network subnet list --compartment-id <COMPARTMENT_OCID> --profile X

# Supprimer un VCN (avec Terraform c'est mieux)
# oci network vcn delete --vcn-id <VCN_OCID> --profile X --force
```

### Debugging
```bash
# CLI OCI avec debug
oci network vcn list --compartment-id <OCID> --debug --profile X

# Désactiver les logs
unset TF_LOG

# Vérifier les fingerprints des clés
openssl rsa -pubout -outform DER -in ~/.oci/X_keys/oci_api_key.pem | openssl md5 -c
```

---

## Ressources et Documentation

### Documentation Officielle Oracle
- **Oracle Cloud Documentation :** https://docs.oracle.com/en-us/iaas/
- **OCI CLI Reference :** https://docs.oracle.com/en-us/iaas/tools/oci-cli/latest/
- **API Reference :** https://docs.oracle.com/iaas/api/
- **Policy Reference :** https://docs.oracle.com/en-us/iaas/Content/Identity/Reference/policyreference.htm

### Free Tier et Pricing
- **OCI Free Tier :** https://www.oracle.com/cloud/free/
- **OCI Pricing Calculator :** https://www.oracle.com/cloud/cost-estimator.html
- **Networking Pricing :** https://www.oracle.com/cloud/networking/pricing/

### Tutoriels et exemples
- **OCI Tutorials :** https://docs.oracle.com/en-us/iaas/Content/GSG/Concepts/baremetalintro.htm
- **Terraform Examples (GitHub) :** https://github.com/oracle/terraform-provider-oci/tree/master/examples

---

## Troubleshooting : Erreurs Courantes

### Erreur : "NotAuthorizedOrNotFound"

**Symptôme :**
```
Error: 404-NotAuthorizedOrNotFound
Authorization failed or requested resource not found.
```

**Causes possibles :**
1. L'utilisateur n'a pas les permissions nécessaires
2. La ressource n'existe pas
3. L'utilisateur n'est pas dans le bon groupe
4. La policy n'est pas correctement configurée

**Solutions :**
```bash
# Vérifier l'appartenance au groupe
oci iam group list-users --group-id <GROUP_OCID> --profile DEFAULT

# Vérifier les policies
oci iam policy list --compartment-id <TENANCY_OCID> --all --profile DEFAULT

# Vérifier que la ressource existe
oci iam compartment get --compartment-id <COMPARTMENT_OCID> --profile DEFAULT
```

### Erreur : "InvalidParameter - Compartment does not exist"

**Symptôme :**
```
Error: InvalidParameter
Compartment {Compartment_Dev} does not exist or is not part of the policy compartment subtree
```

**Cause :** Nom du compartiment incorrect ou sensible à la casse

**Solution :** Utiliser l'OCID du compartiment plutôt que le nom
```
# Au lieu de :
Allow group DevOps to manage ... in compartment Compartment_Dev

# Utiliser :
Allow group DevOps to manage ... in compartment id ocid1.compartment.oc1..xxx
```

### Erreur : Fingerprint mismatch

**Symptôme :**
```
Error: authorization failed or requested resource not found
```

**Cause :** Le fingerprint dans le fichier config ne correspond pas à la clé uploadée

**Solution :**
```bash
# Calculer le fingerprint de ta clé locale
openssl rsa -pubout -outform DER -in ~/.oci/X_keys/oci_api_key.pem | openssl md5 -c

# Comparer avec celui dans la console Oracle Cloud
# User Settings → API Keys → Voir le fingerprint

# Si différent, re-upload la clé publique
```

---

## Checklist de Sécurité

### Avant de commencer

- [ ] Activer MFA (Multi-Factor Authentication) sur le compte Admin
- [ ] Créer des clés API séparées pour chaque utilisateur
- [ ] Ne jamais partager les clés privées (.pem)
- [ ] Stocker les clés privées avec permissions restrictives (`chmod 600`)

### Configuration des droits

- [ ] Principe du moindre privilège : donner uniquement les droits nécessaires
- [ ] Utiliser des groupes plutôt que des permissions directes sur utilisateurs
- [ ] Limiter les policies aux compartiments spécifiques (pas `in tenancy`)
- [ ] Documenter chaque policy créée

### Gestion du code Terraform

- [ ] Ne jamais commiter `terraform.tfvars` avec des secrets
- [ ] Utiliser un `.gitignore` approprié
- [ ] Versionner le code dans Git
- [ ] Utiliser Terraform State en remote (S3, OCI Object Storage)
- [ ] Activer le chiffrement du state file

### Monitoring et audit

- [ ] Activer Cloud Guard (détection de menaces)
- [ ] Configurer des alerles de coûts
- [ ] Réviser régulièrement les permissions IAM
- [ ] Utiliser des tags pour tracer les ressources

---
