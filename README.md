# OCI Policy Statements Utilities

Small Python scripts for reporting Oracle Cloud Infrastructure (OCI) IAM policy statement counts across a tenancy and its compartment hierarchy.

## What This Repository Contains

- `policy-statements.py`
  Lists policies in each accessible active compartment and prints the number of statements in each policy.
- `compartment-hierarchy-statements.py`
  Calculates the total number of policy statements in each accessible active compartment, including statements inherited from all child compartments in that subtree.

## Requirements

- Python 3.9+
- OCI Python SDK
- An OCI CLI or SDK config file available at the default location used by `oci.config.from_file()`
  Usually `~/.oci/config`
- OCI IAM permissions that allow reading compartments and policies in the tenancy

Install the dependency with:

```bash
pip install oci
```

## Required OCI IAM Policy

To run these scripts across the tenancy, grant the executing user or group at least:

```text
Allow group <group_name> to inspect compartments in tenancy
Allow group <group_name> to inspect policies in tenancy
```

These permissions allow the scripts to:

- List compartments in the tenancy subtree
- Read root and child compartment metadata
- List policies attached to the tenancy and compartments
- Count policy statements in each policy and aggregate totals through the hierarchy

If you run the scripts from an OCI compute instance, function, or another resource principal instead of a user group, apply the equivalent policy to the appropriate principal type.

## Authentication

Both scripts use the default OCI SDK config:

```python
config = oci.config.from_file()
```

Make sure your active profile in `~/.oci/config` points at the tenancy you want to inspect and that the credentials are valid before running the scripts.

If you need a non-default profile or config path, update the scripts accordingly.

## Scripts

### `policy-statements.py`

This script does not calculate the number of IAM policies. It calculates the number of statements in each policy.

This script:

- Loads the OCI config and creates an Identity client
- Lists all accessible compartments in the tenancy subtree
- Adds the root compartment explicitly
- Skips inactive compartments
- Lists policies in each compartment
- Prints one row per policy with the number of statements in that policy

Example output:

```text
Compartment Name               | Policy Name                    | Statements
---------------------------------------------------------------------------
Root                           | tenancy-admins                 | 4
Networking                     | netops-read                    | 2
Security                       | security-admins                | 7
```

Run it with:

```bash
python3 policy-statements.py
```

### `compartment-hierarchy-statements.py`

This script:

- Loads the OCI config and creates an Identity client
- Lists all accessible compartments in the tenancy subtree
- Builds a parent-child compartment map
- Counts policy statements local to each active compartment
- Recursively aggregates those counts through child compartments
- Prints one row per compartment with the total statements in that compartment subtree

This is useful when you want to understand the total policy statement footprint for a compartment and everything beneath it.

Example output:

```text
Compartment Name               | Total Statements (Inc. Children)
----------------------------------------------------------------------
Root                           | 128
SharedServices                 | 41
Security                       | 19
```

Run it with:

```bash
python3 compartment-hierarchy-statements.py
```

## Notes and Behavior

- Only compartments returned with `access_level="ACCESSIBLE"` are included.
- Only compartments in `ACTIVE` lifecycle state are processed.
- Root compartment policies are included in both reports.
- The hierarchy report totals policy statements in a compartment plus all descendant compartments.
- The scripts print tabular output to stdout and do not write files.

## Typical Use Cases

- Estimate IAM policy sprawl in a tenancy
- Find compartments with large numbers of policy statements
- Compare local policy counts versus subtree totals
- Support governance or cleanup efforts before compartment reorganization

## License

Add a license file if you plan to publish this repository publicly.
