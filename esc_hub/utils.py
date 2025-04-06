from .models import Hub, Route, MST, MSTPath

def build_mst():
    """Computes and stores the MST using Kruskal's algorithm with debug prints."""
    print("=== Starting MST Construction ===")
    
    # Fetch all hubs and routes
    hubs = Hub.objects.all()
    routes = Route.objects.all()
    print(f"Found {hubs.count()} hubs and {routes.count()} routes")

    # Prepare edges with distances
    edges = [(route.distance, route) for route in routes]
    edges.sort()  # Sort edges by distance
    print(f"Sorted edges by distance. First edge: {edges[0][1].source.id}-{edges[0][1].destination.id} ({edges[0][0]}km)")

    # Initialize Union-Find
    parent = {hub.id: hub.id for hub in hubs}
    print("Initialized Union-Find structure")

    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]  # Path compression
            node = parent[node]
        return node

    def union(node1, node2):
        root1 = find(node1)
        root2 = find(node2)
        if root1 != root2:
            parent[root2] = root1
            print(f"  Union: Connected {node1} and {node2} (roots: {root1}, {root2})")

    # Kruskal's algorithm
    mst_routes = []
    print("\nProcessing edges:")
    for dist, route in edges:
        src = route.source.id
        dest = route.destination.id
        print(f"\nEdge: {route.source.id}-{route.destination.id} ({dist}km)")
        print(f"  Find({src}) = {find(src)}, Find({dest}) = {find(dest)}")
        
        if find(src) != find(dest):
            union(src, dest)
            mst_routes.append(route)
            print(f"  ADDED TO MST (Current MST edges: {len(mst_routes)})")
        else:
            print("  SKIPPED (Would create cycle)")

    # Clear old MST
    print("\nClearing old MST data...")
    deleted_paths, _ = MSTPath.objects.all().delete()
    deleted_msts, _ = MST.objects.all().delete()
    print(f"Deleted {deleted_paths} paths and {deleted_msts} MST instances")

    # Store new MST
    print("\nCreating new MST...")
    mst_instance = MST.objects.create()
    print(f"Created MST instance (ID: {mst_instance.id})")
    
    print("Adding paths to MST:")
    for i, route in enumerate(mst_routes, start=1):
        path = MSTPath.objects.create(route=route, number=i)
        mst_instance.path.add(path)
        print(f"  {i}. {route.source.id}-{route.destination.id} ({route.distance}km)")

    print("\n=== MST Construction Complete ===")
    print(f"Total MST edges: {len(mst_routes)}")
    print(f"Total MST cost: {sum(route.distance for route in mst_routes)} km")
    
    return mst_instance