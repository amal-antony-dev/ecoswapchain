import heapq
from .models import Hub, Route

def build_mst():
    """Rebuilds the optimized hub network using Kruskal's MST Algorithm."""
    
    hubs = Hub.objects.all()
    routes = Route.objects.all()

    edges = [(route.distance, route.source.id, route.destination.id) for route in routes]
    edges.sort()  # Sort edges by distance (smallest first)

    parent = {hub.id: hub.id for hub in hubs}  # Disjoint Set for Union-Find

    def find(node):
        while parent[node] != node:
            node = parent[node]
        return node

    def union(node1, node2):
        root1 = find(node1)
        root2 = find(node2)
        if root1 != root2:
            parent[root2] = root1

    mst_routes = []
    for dist, src, dest in edges:
        if find(src) != find(dest):
            union(src, dest)
            mst_routes.append((src, dest, dist))

    # Clear old routes and update database
    Route.objects.all().delete()
    for src, dest, dist in mst_routes:
        Route.objects.create(
            source=Hub.objects.get(id=src),
            destination=Hub.objects.get(id=dest),
            distance=dist,
            time=dist / 50,  # Example: Assuming avg speed of 50 km/h
            cost=dist * 0.5  # Example: Cost per km
        )

    print("Routes updated successfully!")
