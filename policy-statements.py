import oci

# Initialize service client
config = oci.config.from_file()
identity_client = oci.identity.IdentityClient(config)
tenancy_id = config["tenancy"]

# Get all compartments
print("Fetching compartments...")
compartments = oci.pagination.list_call_get_all_results(
    identity_client.list_compartments,
    tenancy_id,
    compartment_id_in_subtree=True,
    access_level="ACCESSIBLE"
).data

# Add root compartment
root_compartment = identity_client.get_compartment(tenancy_id).data
all_compartments = compartments + [root_compartment]

# Iterate and count
print(f"{'Compartment Name':<30} | {'Policy Name':<30} | {'Statements'}")
print("-" * 75)

for comp in all_compartments:
    if comp.lifecycle_state != 'ACTIVE':
        continue
        
    policies = oci.pagination.list_call_get_all_results(
        identity_client.list_policies,
        comp.id
    ).data
    
    for policy in policies:
        statement_count = len(policy.statements)
        print(f"{comp.name:<30} | {policy.name:<30} | {statement_count}")


