

def create_path_by_name(name: str, team_id: int, count: int):
    if count > 0:
        path = f"src/people/{name}-{count + 1}_team_{team_id}.jpg"
    else:
        path = f"src/people/{name}_team_{team_id}.jpg"
    return path
