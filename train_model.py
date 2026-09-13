import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
import numpy as np
import json

df = pd.read_csv("dataset.csv")
X = df.drop(columns=["Price"])
y = df["Price"]

cat = X.select_dtypes(include="object").columns.tolist()
num = [c for c in X.columns if c not in cat]

preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
    ("num", StandardScaler(), num)
])

models = {
    "Linear Regression": LinearRegression(),
    "Decision Tree": DecisionTreeRegressor(max_depth=14, random_state=42),
    "Random Forest": RandomForestRegressor(n_estimators=180, max_depth=18, random_state=42, n_jobs=-1),
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=180, random_state=42),
    "Extra Trees": ExtraTreesRegressor(n_estimators=180, max_depth=18, random_state=42, n_jobs=-1)
}

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
results = {}
best_name, best_pipe, best_r2 = None, None, -1

for name, model in models.items():
    pipe = Pipeline([("preprocessor", preprocessor), ("model", model)])
    pipe.fit(X_train, y_train)
    pred = pipe.predict(X_test)
    mae = mean_absolute_error(y_test, pred)
    mse = mean_squared_error(y_test, pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, pred)
    results[name] = {"MAE": mae, "MSE": mse, "RMSE": rmse, "R2": r2}
    if r2 > best_r2:
        best_name, best_pipe, best_r2 = name, pipe, r2

joblib.dump(best_pipe, "model.pkl")
joblib.dump({"test_actual": y_test.tolist(), "test_predicted": best_pipe.predict(X_test).tolist()}, "evaluation.pkl")

with open("model_metrics.json","w") as f:
    json.dump({"best_model":best_name, "results":results}, f, indent=2)

print("Best model:", best_name)
print("R2:", best_r2)
print("model.pkl, evaluation.pkl and model_metrics.json created.")
