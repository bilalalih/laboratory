goals: list[str] = []

if not goals:
    print("No goals exist")
    input = input("Your goals: ")
    goals = [g.strip() for g in input.split(",") if g.strip()]
    goals.extend(["Wake up early", "Exercise", "Read a book"])
if goals:
    print("Current goals:")
    for i, goal in enumerate(goals, start=1):
        print(f"{i}. {goal}")