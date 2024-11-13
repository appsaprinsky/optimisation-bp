import pulp as pl
import numpy as np
import matplotlib.pyplot as plt
import random

# Example data: Assume we have some generated pairings
pairings = {
    "Pairing1": {"flights": ["Flight1", "Flight2"], "cost": 300, "duration": 3},
    "Pairing2": {"flights": ["Flight3", "Flight4"], "cost": 250, "duration": 4},
    "Pairing3": {"flights": ["Flight1", "Flight4"], "cost": 280, "duration": 5},
    "Pairing4": {"flights": ["Flight2", "Flight3"], "cost": 270, "duration": 2.5},
}

# Crew data (crew members and availability)
crew_members = ["Crew1", "Crew2", "Crew3"]
max_duty_hours = 10  # Max duty hours per crew member per schedule
min_rest_hours = 8   # Minimum rest period between pairings

# Set up the crew rostering master problem
rostering_prob = pl.LpProblem("Crew_Rostering", pl.LpMinimize)

# Decision variables for assigning pairings to crew members
assignment_vars = {
    (crew, pairing): pl.LpVariable(f"assign_{crew}_{pairing}", 0, 1, pl.LpBinary)
    for crew in crew_members for pairing in pairings
}

# Objective function: Minimize the total cost across all pairings and crew assignments
rostering_prob += pl.lpSum(
    assignment_vars[(crew, pairing)] * pairings[pairing]["cost"]
    for crew in crew_members for pairing in pairings
)

# Constraint 1: Ensure each flight is covered by at least one pairing
flights = {flight for pairing in pairings.values() for flight in pairing["flights"]}
for flight in flights:
    rostering_prob += pl.lpSum(
        assignment_vars[(crew, pairing)]
        for crew in crew_members for pairing in pairings
        if flight in pairings[pairing]["flights"]
    ) >= 1, f"Cover_{flight}"

# Constraint 2: Duty hours limit per crew member
for crew in crew_members:
    rostering_prob += pl.lpSum(
        assignment_vars[(crew, pairing)] * pairings[pairing]["duration"]
        for pairing in pairings
    ) <= max_duty_hours, f"DutyHours_{crew}"

# Constraint 3: Minimum rest period between consecutive pairings
# Assumes some scheduling structure; here we use arbitrary rest periods
# Example: If Crew1 is assigned Pairing1 and Pairing3, ensure sufficient rest
rest_constraints = {
    ("Pairing1", "Pairing3"): min_rest_hours,  # Example rest requirement
    ("Pairing2", "Pairing4"): min_rest_hours,
}
for (pair1, pair2), rest in rest_constraints.items():
    for crew in crew_members:
        rostering_prob += (
            assignment_vars[(crew, pair1)] + assignment_vars[(crew, pair2)] <= 1
        ), f"Rest_{crew}_{pair1}_{pair2}"

# Constraint 4: Crew preferences (e.g., Crew2 prefers not to work Pairing4)
rostering_prob += assignment_vars[("Crew2", "Pairing4")] == 0, "Preference_Crew2_Pairing4"

# Constraint 5: Min/Max shifts per crew
min_shifts = 1
max_shifts = 2
for crew in crew_members:
    rostering_prob += pl.lpSum(
        assignment_vars[(crew, pairing)] for pairing in pairings
    ) >= min_shifts, f"MinShifts_{crew}"
    rostering_prob += pl.lpSum(
        assignment_vars[(crew, pairing)] for pairing in pairings
    ) <= max_shifts, f"MaxShifts_{crew}"

# Solve the problem
rostering_prob.solve()

# Output results
print("Roster Assignments:")
for crew in crew_members:
    assigned_pairings = [
        pairing for pairing in pairings if pl.value(assignment_vars[(crew, pairing)]) == 1
    ]
    print(f"{crew}: {assigned_pairings}")

# Visualization
def visualize_roster(assignment_vars):
    fig, ax = plt.subplots()
    crew_schedule = {crew: [] for crew in crew_members}
    for crew, pairing in assignment_vars:
        if pl.value(assignment_vars[(crew, pairing)]) == 1:
            crew_schedule[crew].append(pairing)

    for idx, (crew, pairings) in enumerate(crew_schedule.items()):
        ax.broken_barh(
            [(i, 1) for i in range(len(pairings))],
            (idx - 0.4, 0.8),
            facecolors=["#3498db" if "Flight1" in pair else "#e74c3c" for pair in pairings],
        )
        ax.text(-1, idx, crew, va="center", ha="right")

    ax.set_xlabel("Pairings")
    ax.set_yticks(range(len(crew_members)))
    ax.set_yticklabels(crew_members)
    ax.set_xticks(range(len(pairings)))
    ax.set_xticklabels(pairings)
    plt.title("Crew Rostering Schedule")
    plt.show()

# Call visualization function
visualize_roster(assignment_vars)
