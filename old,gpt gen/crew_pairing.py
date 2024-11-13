import pulp as pl
import numpy as np
import matplotlib.pyplot as plt
import random

# Step 1: Define data structures for flights and initial feasible pairings
flights = ["Flight1", "Flight2", "Flight3", "Flight4"]
flight_durations = [1, 1.5, 2, 1.25]  # Example durations in hours

# Step 2: Define the master problem (restricted master problem, RMP)
master_prob = pl.LpProblem("Crew_Pairing", pl.LpMinimize)

# Variables representing initial feasible pairings
pairing_vars = {
    "Pairing1": pl.LpVariable("x_Pairing1", lowBound=0, cat="Continuous"),
    "Pairing2": pl.LpVariable("x_Pairing2", lowBound=0, cat="Continuous"),
}

# Add objective function to minimize total cost (using arbitrary cost for each pairing)
master_prob += pairing_vars["Pairing1"] * 300 + pairing_vars["Pairing2"] * 250

# Add constraints to cover all flights (initially arbitrary pairings)
# Example: Pairing1 covers Flight1 and Flight2, Pairing2 covers Flight3 and Flight4
flight_coverage = {
    "Flight1": [pairing_vars["Pairing1"]],
    "Flight2": [pairing_vars["Pairing1"]],
    "Flight3": [pairing_vars["Pairing2"]],
    "Flight4": [pairing_vars["Pairing2"]],
}

for flight, pairings in flight_coverage.items():
    master_prob += pl.lpSum(pairings) >= 1, f"Cover_{flight}"

# Step 3: Define subproblem for column generation (generating new pairings)
def column_generation(master_prob, flight_durations, duals):
    """Solves subproblem to generate new feasible pairing (column) based on duals."""
    sub_prob = pl.LpProblem("Subproblem", pl.LpMaximize)
    new_pairing = pl.LpVariable.dicts("Flight", range(len(flights)), cat="Binary")

    # Objective: Maximize profit based on duals to find pairing with lowest reduced cost
    sub_prob += pl.lpSum(duals[i] * new_pairing[i] for i in range(len(flights)))
    sub_prob += pl.lpSum(flight_durations[i] * new_pairing[i] for i in range(len(flights))) <= 5, "Duty_Time"

    # Solve subproblem
    sub_prob.solve()
    objective_value = pl.value(sub_prob.objective)
    if objective_value is not None and objective_value > 1e-5:
        return [new_pairing[i].varValue for i in range(len(flights))]
    return None

# Step 4: Solve the master problem iteratively (branch-and-price framework)
def branch_and_price(master_prob):
    """Main loop for branch-and-price algorithm."""
    while True:
        # Solve master problem to obtain duals
        master_prob.solve()
        duals = {i: master_prob.constraints[f"Cover_Flight{i+1}"].pi for i in range(len(flights))}

        # Column generation step: generate new feasible pairing
        new_pairing = column_generation(master_prob, flight_durations, duals)

        if new_pairing is None:
            break  # Stop if no improving column is found

        # Add new pairing to the master problem as a new column
        col_name = f"Pairing{len(pairing_vars) + 1}"
        pairing_vars[col_name] = pl.LpVariable(f"x_{col_name}", lowBound=0, cat="Continuous")
        master_prob += pairing_vars[col_name] * random.randint(200, 400)  # Random cost for example

        # Update coverage for new pairing
        for i, flight in enumerate(flights):
            if new_pairing[i] > 0:
                if flight in flight_coverage:
                    flight_coverage[flight].append(pairing_vars[col_name])
                else:
                    flight_coverage[flight] = [pairing_vars[col_name]]

        for flight, pairings in flight_coverage.items():
            master_prob.constraints[f"Cover_{flight}"] = pl.lpSum(pairings) >= 1

    return pairing_vars, master_prob

# Step 5: Visualize results
def visualize_solution(pairing_vars):
    fig, ax = plt.subplots()
    bars = []
    for pairing, var in pairing_vars.items():
        bars.append(var.value())
    ax.bar(pairing_vars.keys(), bars)
    ax.set_ylabel("Pairing Usage")
    ax.set_title("Optimized Crew Pairing Solution")
    plt.show()

# Run branch-and-price algorithm and visualize the solution
pairing_vars, master_prob = branch_and_price(master_prob)
visualize_solution(pairing_vars)
