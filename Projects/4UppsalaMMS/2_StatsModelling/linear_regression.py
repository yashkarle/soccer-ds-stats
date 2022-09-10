#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 10 23:12:36 2022

@author: yashkarle
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf


epl_df = pd.read_csv("2_StatsModelling/playerstats.csv", delimiter=",")

num_obs = 546
minutes_model = pd.DataFrame()
minutes_model = minutes_model.assign(minutes=epl_df["Min"][0:num_obs])
minutes_model = minutes_model.assign(age=epl_df["Age"][0:num_obs])

# Make an age squared column so we can fit polynomial model.
minutes_model = minutes_model.assign(age_squared=np.power(epl_df["Age"][0:num_obs], 2))
minutes_model = minutes_model.assign(age_cubic=np.power(epl_df["Age"][0:num_obs], 3))


fig, ax = plt.subplots(num=1)
ax.plot(
    minutes_model["age"],
    minutes_model["minutes"],
    linestyle="none",
    marker=".",
    markersize=10,
    color="blue",
)
ax.set_ylabel("Minutes played")
ax.set_xlabel("Age")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.xlim((15, 40))
plt.ylim((0, 3000))
plt.show()


model_fit = smf.ols(formula="minutes  ~ age", data=minutes_model).fit()
print(model_fit.summary())
b = model_fit.params


# First plot the data as previously
fig, ax = plt.subplots(num=1)
ax.plot(
    minutes_model["age"],
    minutes_model["minutes"],
    linestyle="none",
    marker=".",
    markersize=10,
    color="blue",
)
ax.set_ylabel("Minutes played")
ax.set_xlabel("Age")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.xlim((15, 40))
plt.ylim((0, 3000))

# Now create the line through the data
x = np.arange(40, step=1)
y = b[0] + b[1] * x
ax.plot(x, y, color="black")

# Show distances to line for each point
for i, a in enumerate(minutes_model["age"]):
    ax.plot(
        [a, a],
        [minutes_model["minutes"][i], b[0] + b[1] * a],
        color="red",
    )
plt.show()


# First fit the model
model_fit = smf.ols(formula="minutes  ~ age + age_squared", data=minutes_model).fit()
print(model_fit.summary())
b = model_fit.params

# Compare the fit
fig, ax = plt.subplots(num=1)
ax.plot(
    minutes_model["age"],
    minutes_model["minutes"],
    linestyle="none",
    marker=".",
    markersize=10,
    color="blue",
)
ax.set_ylabel("Minutes played")
ax.set_xlabel("Age")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.xlim((15, 40))
plt.ylim((0, 3000))
x = np.arange(40, step=1)
y = b[0] + b[1] * x + b[2] * x * x
ax.plot(x, y, color="black")

# for i, a in enumerate(minutes_model["age"]):
#     ax.plot(
#         [a, a],
#         [minutes_model["minutes"][i], b[0] + b[1] * a + b[2] * a * a],
#         color="red",
#     )
plt.show()


# First fit the model
model_fit = smf.ols(
    formula="minutes ~ age + age_squared + age_cubic", data=minutes_model
).fit()
print(model_fit.summary())
b = model_fit.params

# Compare the fit
fig, ax = plt.subplots(num=1)
ax.plot(
    minutes_model["age"],
    minutes_model["minutes"],
    linestyle="none",
    marker=".",
    markersize=10,
    color="blue",
)
ax.set_ylabel("Minutes played")
ax.set_xlabel("Age")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.xlim((15, 40))
plt.ylim((0, 3000))
x = np.arange(40, step=1)
y = b[0] + b[1] * x + b[2] * x * x + b[3] * x * x * x
ax.plot(x, y, color="black")

# for i, a in enumerate(minutes_model["age"]):
#     ax.plot(
#         [a, a],
#         [minutes_model["minutes"][i], b[0] + b[1] * a + b[2] * a * a],
#         color="red",
#     )
plt.show()
