import oci

config = oci.config.from_file()
identity = oci.identity.IdentityClient(config)
tenancy_id = config["tenancy"]

def get_hierarchy_data():
    """Builds a map of parent IDs to child IDs and a map of local statement counts."""
    all_comps = oci.pagination.list_call_get_all_results(
        identity.list_compartments,
        tenancy_id,
        compartment_id_in_subtree=True,
        access_level="ACCESSIBLE"
    ).data

    hierarchy = {tenancy_id: []}
    local_counts = {}
    names = {tenancy_id: "Root"}

    # Initialize Root local count
    root_policies = identity.list_policies(tenancy_id).data
    local_counts[tenancy_id] = sum(len(p.statements) for p in root_policies)

    for c in all_comps:
        if c.lifecycle_state == "ACTIVE":
            # Map children to parents
            hierarchy.setdefault(c.compartment_id, []).append(c.id)
            names[c.id] = c.name
            
            # Get local statements for this specific compartment
            policies = identity.list_policies(c.id).data
            local_counts[c.id] = sum(len(p.statements) for p in policies)
            
    return hierarchy, local_counts, names

def aggregate_totals(comp_id, hierarchy, local_counts, totals):
    """Recursively sums local counts and child totals."""
    current_total = local_counts.get(comp_id, 0)
    
    for child_id in hierarchy.get(comp_id, []):
        current_total += aggregate_totals(child_id, hierarchy, local_counts, totals)
    
    totals[comp_id] = current_total
    return current_total

if __name__ == "__main__":
    hier_map, local_map, name_map = get_hierarchy_data()
    total_map = {}
    
    # Calculate totals starting from the root
    aggregate_totals(tenancy_id, hier_map, local_map, total_map)

    print(f"{'Compartment Name':<30} | {'Total Statements (Inc. Children)':<35}")
    print("-" * 70)
    for cid, total in total_map.items():
        print(f"{name_map[cid]:<30} | {total:<35}")

