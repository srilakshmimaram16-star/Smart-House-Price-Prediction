import numpy as np
import pandas as pd

np.random.seed(42)

locations = ["Guntur","Vijayawada","Visakhapatnam","Tirupati","Nellore","Kurnool",
"Anantapur","Rajahmundry","Kakinada","Ongole","Kadapa","Srikakulam","Hyderabad",
"Chennai","Bengaluru","Mumbai","Pune","Delhi"]

location_factor = {
"Guntur":1.00,"Vijayawada":1.15,"Visakhapatnam":1.25,"Tirupati":1.10,
"Nellore":0.95,"Kurnool":0.85,"Anantapur":0.82,"Rajahmundry":0.92,
"Kakinada":0.98,"Ongole":0.88,"Kadapa":0.80,"Srikakulam":0.78,
"Hyderabad":1.55,"Chennai":1.50,"Bengaluru":1.75,"Mumbai":2.30,
"Pune":1.60,"Delhi":1.90}

n = 3000
df = pd.DataFrame({
    "Location": np.random.choice(locations, n),
    "Area": np.random.randint(500, 5001, n),
    "Bedrooms": np.random.randint(1, 6, n),
    "Bathrooms": np.random.randint(1, 5, n),
    "Floors": np.random.randint(1, 5, n),
    "Property_Age": np.random.randint(0, 31, n),
    "Parking": np.random.choice(["Yes","No"], n, p=[0.7,0.3]),
    "Kitchen": np.random.choice(["Yes","No"], n, p=[0.95,0.05]),
    "Balcony": np.random.randint(0, 4, n),
    "Furnishing": np.random.choice(["Unfurnished","Semi Furnished","Fully Furnished"], n),
    "Property_Type": np.random.choice(["Apartment","Independent House","Villa","Plot"], n),
    "Construction_Quality": np.random.choice(["Low","Medium","High"], n)
})

base = df["Location"].map(location_factor)
quality = df["Construction_Quality"].map({"Low":0.90,"Medium":1.0,"High":1.18})
furn = df["Furnishing"].map({"Unfurnished":0.90,"Semi Furnished":1.0,"Fully Furnished":1.12})
ptype = df["Property_Type"].map({"Apartment":1.0,"Independent House":1.08,"Villa":1.35,"Plot":0.72})
parking = (df["Parking"]=="Yes").astype(int)*250000
kitchen = (df["Kitchen"]=="Yes").astype(int)*100000

price = (
    df["Area"] * 6500 * base * quality * furn * ptype
    + df["Bedrooms"]*350000
    + df["Bathrooms"]*250000
    + df["Floors"]*120000
    - df["Property_Age"]*90000
    + df["Balcony"]*100000
    + parking + kitchen
    + np.random.normal(0, 350000, n)
)
df["Price"] = np.maximum(price, 500000).round(-3)
df.to_csv("dataset.csv", index=False)
print("dataset.csv created:", df.shape)
