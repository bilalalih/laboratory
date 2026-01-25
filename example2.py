names: dict[int, str] = {
    1: "James Goldfield",
    2: "Linda Park",
    3: "Robert Chen",
}

titles: dict[str, list[str]] = {
    "Engineer": ["Software Engineer", "DevOps Engineer", "QA Engineer"],
    "Manager": ["Project Manager", "Product Manager", "Team Lead"],
    "Designer": ["UI/UX Designer", "Graphic Designer", "Product Designer"],
}

def get_name_by_id(user_id: int) -> str:
    return names.get(user_id, "Unknown User")

for id, name in names.items():
    print(f"ID: {id}, Name: {name}")

def get_titles_by_role(role: str) -> list[str]:
    return titles.get(role, [])

for role, t_list in titles.items():
    print(f"Role: {role}, Titles: {', '.join(t_list)}")
# for n in names.keys():
#     name = get_name_by_id(n)
#     print(name)

students: dict[str, str] = {
    "S001": "Alice Johnson",
    "S002": "Bob Smith",
    "S003": "Charlie Davis",
}

print(f"Student: {students.get('S002', 'Unknown Student')}")