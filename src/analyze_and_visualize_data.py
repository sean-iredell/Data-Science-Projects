import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

# Save images
images_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'images')
os.makedirs(images_path, exist_ok=True)
def save_plot_as_png(fig, filename):
    file_path = os.path.join(images_path, filename)
    fig.savefig(file_path, format='png')
    print(f"Saved plot as {file_path}")

# Ridge model
def train_ridge_model(df, predictors, target):
    X = df[predictors]
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    ridge_model = Ridge(alpha=1.0)
    ridge_model.fit(X_train_scaled, y_train)
    
    return ridge_model, scaler, X_train_scaled, X_test_scaled, y_train, y_test  # Ensure return of X_train, X_test, y_train, y_test

# Evaluation metrics
def evaluate_model(ridge_model, scaler, X_train_scaled, y_train, X_test_scaled, y_test):
    y_train_pred = ridge_model.predict(X_train_scaled)
    y_test_pred = ridge_model.predict(X_test_scaled)
    
    metrics = {
        "train_r2": r2_score(y_train, y_train_pred),
        "test_r2": r2_score(y_test, y_test_pred),
        "train_mse": mean_squared_error(y_train, y_train_pred),
        "test_mse": mean_squared_error(y_test, y_test_pred),
        "train_mae": mean_absolute_error(y_train, y_train_pred),
        "test_mae": mean_absolute_error(y_test, y_test_pred),
    }
    return metrics

# MTE vs. Non-MTE Teams
def calculate_overall_efficiency(df, ridge_model, scaler, predictors, mte_teams, non_mte_teams):
    df["Predicted Points Scored"] = ridge_model.predict(scaler.transform(df[predictors]))
    df_grouped = df.groupby('Team').agg({'Predicted Points Scored': 'mean'}).reset_index()
    average_points_scored = df_grouped["Predicted Points Scored"].mean()
    
    df_grouped["Offensive Efficiency"] = (df_grouped["Predicted Points Scored"] / average_points_scored) * 100
    df_grouped["Event Type"] = df_grouped["Team"].apply(
        lambda x: 'MTE' if x in mte_teams else 'Non-MTE'
    )
    mte_avg = df_grouped[df_grouped["Event Type"] == "MTE"]["Offensive Efficiency"].mean()
    non_mte_avg = df_grouped[df_grouped["Event Type"] == "Non-MTE"]["Offensive Efficiency"].mean()
    
    return df_grouped, mte_avg, non_mte_avg

# Before, During, After
def calculate_period_efficiency(MTE, ridge_model, scaler, predictors, mte_teams):
    MTE["Predicted Points Scored"] = ridge_model.predict(scaler.transform(MTE[predictors]))
    
    MTE_filtered = MTE[MTE['Team'].isin(mte_teams)]
    before_df = MTE_filtered[MTE_filtered['Period'] == 'Before']
    during_df = MTE_filtered[MTE_filtered['Period'] == 'During']
    after_df = MTE_filtered[MTE_filtered['Period'] == 'After']
    
    before_eff = before_df.groupby('Team').agg(Offensive_Efficiency_Before=('Predicted Points Scored', 'mean'))
    during_eff = during_df.groupby('Team').agg(Offensive_Efficiency_During=('Predicted Points Scored', 'mean'))
    after_eff = after_df.groupby('Team').agg(Offensive_Efficiency_After=('Predicted Points Scored', 'mean'))
    
    efficiency_data = before_eff.merge(during_eff, on="Team").merge(after_eff, on="Team")
    efficiency_data["Percent Change (Before to During)"] = (
        (efficiency_data["Offensive_Efficiency_During"] - efficiency_data["Offensive_Efficiency_Before"]) 
        / efficiency_data["Offensive_Efficiency_Before"]
    ) * 100
    efficiency_data["Percent Change (During to After)"] = (
        (efficiency_data["Offensive_Efficiency_After"] - efficiency_data["Offensive_Efficiency_During"]) 
        / efficiency_data["Offensive_Efficiency_During"]
    ) * 100
    
    return efficiency_data

# Load data
data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed.csv')
try:
    df = pd.read_csv(data_path)
except FileNotFoundError:
    print(f"Error: The file at {data_path} does not exist.")
    raise

# Define MTE teams
mte_teams = ["Auburn", "Tennessee", "Iowa St.", "Gonzaga", "Oklahoma"]

MTE = df[df["Team"].isin(mte_teams)]      
Non_MTE = df[~df["Team"].isin(mte_teams)] 

print("MTE DataFrame:")
print(MTE)

print("\nNon-MTE DataFrame:")
print(Non_MTE)

# Training model
predictors = ["ORebs", "AST", "TO", "FGA", "3FGA", "FTA"]
target = "Points Scored"
ridge_model, scaler, X_train_scaled, X_test_scaled, y_train, y_test = train_ridge_model(df, predictors, target)
metrics = evaluate_model(ridge_model, scaler, X_train_scaled, y_train, X_test_scaled, y_test)
print("Model Evaluation Metrics:", metrics)

# Calculate MTE vs. Non-MTE
df_grouped, mte_avg, non_mte_avg = calculate_overall_efficiency(df, ridge_model, scaler, predictors, mte_teams, Non_MTE)
print(f"MTE Avg Efficiency: {mte_avg}, Non-MTE Avg Efficiency: {non_mte_avg}")

# Calculate Before, During, After
efficiency_data = calculate_period_efficiency(MTE, ridge_model, scaler, predictors, mte_teams)

# Plot for percent changes
teams = efficiency_data.index
before_during = efficiency_data["Percent Change (Before to During)"]
during_after = efficiency_data["Percent Change (During to After)"]
bar_width = 0.35
x = np.arange(len(teams))
fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(x - bar_width / 2, before_during, bar_width, label="Before to During", color="blue")
ax.bar(x + bar_width / 2, during_after, bar_width, label="During to After", color="green")
ax.set_title("Percent Change in Offensive Efficiency", fontsize=16)
ax.set_xlabel("Team", fontsize=14)
ax.set_ylabel("Percent Change (%)", fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels(teams, rotation=45, fontsize=12)
ax.legend(fontsize=12)
ax.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
save_plot_as_png(fig, 'percent_change_efficiency.png')
plt.show()

# Actual vs. Predicted calculation
def plot_predictions(df, predictors, target):
    ridge_model, scaler, X_train_scaled, X_test_scaled, y_train, y_test = train_ridge_model(df, predictors, target)
    y_pred = ridge_model.predict(X_test_scaled)
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, y_pred, alpha=0.7, color='b')
    plt.xlabel('Actual Points Scored', fontsize=12)
    plt.ylabel('Predicted Points Scored', fontsize=12)
    plt.title('Actual vs Predicted Points Scored', fontsize=14)
    plt.grid(True)
    plt.show()


# Ranking vs. Offensive Efficency
grouped_df = df.groupby('Ranking').agg(
    {'Offensive Efficiency': 'mean'}  # Calculate the mean offensive efficiency per ranking
).reset_index()
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(grouped_df['Ranking'], grouped_df['Offensive Efficiency'], color='b', label='Team')
slope, intercept = np.polyfit(grouped_df['Ranking'], grouped_df['Offensive Efficiency'], 1)  # Linear fit
best_fit_line = slope * grouped_df['Ranking'] + intercept
ax.plot(grouped_df['Ranking'], best_fit_line, color='r', label=f'Best Fit (y={slope:.2f}x + {intercept:.2f})')
ax.set_title('Ranking vs Offensive Efficiency', fontsize=16)
ax.set_xlabel('Ranking', fontsize=14)
ax.set_ylabel('Offensive Efficiency', fontsize=14)
ax.grid(True)
ax.legend()
save_plot_as_png(fig, 'ranking_vs_efficiency.png')

# Actual vs. Predicted Plot
y_pred = ridge_model.predict(X_test_scaled)
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(y_test, y_pred, alpha=0.7, color='b')
ax.set_xlabel('Actual Points Scored', fontsize=12)
ax.set_ylabel('Predicted Points Scored', fontsize=12)
ax.set_title('Actual vs Predicted Points Scored', fontsize=14)
ax.grid(True)
save_plot_as_png(fig, 'predicted_vs_actual.png')
plt.show()
