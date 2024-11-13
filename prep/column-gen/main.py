#https://towardsdatascience.com/column-generation-in-linear-programming-and-the-cutting-stock-problem-3c697caf4e2b
#https://github.com/bruscalia/optimization-demo-files/blob/c711c97e7bea736c23d0fa39500000fd52366117/mip/cutting_stock/cutting_stock.ipynb

import numpy as np
import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt

dataset = pd.read_csv("data.txt", sep=" ")

def solve_knapsack(W, w, duals):
    return linprog(
        -duals, A_ub=np.atleast_2d(w), b_ub=np.atleast_1d(W),
        bounds=(0, np.inf), integrality=1,
    )

# Total width
W = 100.0

# Width and amount associated with each demand
w = dataset.w.values
d = dataset.d.values

# LP parameters
A = np.eye(dataset.shape[0]) * (W // w)
c = np.ones_like(w)

# Initial solution
sol = linprog(c, A_ub=-A, b_ub=-d, bounds=(0, None))
sol_dual = linprog(-d, A_ub=A.T, b_ub=c, bounds=(0, None))
diff = np.abs(sol_dual.x + sol.ineqlin.marginals).sum()
print(f"Compare duality difference: {diff}")

# Iterate
for _ in range(1000):
    duals = -sol.ineqlin.marginals
    price_sol = solve_knapsack(W, w, duals)
    y = price_sol.x
    if 1 + price_sol.fun < -1e-4:
        print(f"Iteration: {_}; Reduced cost: {(1 + price_sol.fun):.3f}")
        A = np.hstack((A, y.reshape((-1, 1))))
        c = np.append(c, 1)
        sol = linprog(c, A_ub=-A, b_ub=-d, bounds=(0, None))
    else:
        break

sol_round = linprog(c, A_ub=-A, b_ub=-d, bounds=(0, np.inf), integrality=0)
print(f"Rounding solution {np.ceil(sol_round.x).sum()}")
sol = linprog(c, A_ub=-A, b_ub=-d, bounds=(0, np.inf), integrality=1)
print(f"Integer solution: {sol.x.sum()}")



fig, ax = plt.subplots(figsize=[7, 3], dpi=100)
hmap = ax.imshow(A > 1e-6, cmap="Blues")
plt.axis('off')
fig.tight_layout()
plt.show()








