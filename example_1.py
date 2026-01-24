from enum import StrEnum

class Goal(StrEnum): # Creates an Enum whose members are also valid strings
    MAXIMIZE_PROGRESS = "maximize_progress"
    MINIMIZE_COST = "minimize_cost"
    BALANCE_TIME_AND_MONEY = "balance_time_and_money"

val = str(Goal.MAXIMIZE_PROGRESS)  # 'maximize_progress'
print(val)  # 'minimize_cost'
print(Goal.MINIMIZE_COST == "minimize_cost")  # True
print(Goal("balance_time_and_money"))  # Goal.BALANCE_TIME_AND_MONEY
