import os
import numpy as np
import pandas as pd

def generate_northeast_landslide_dataset(n_samples: int = 6000, random_state: int = 42) -> pd.DataFrame:
    """
    Generate realistic synthetic landslide hazard training data
    modeled on Northeast Indian Himalayan & Indo-Burma terrain (Assam, Meghalaya, Sikkim, etc.).
    Incorporates empirical rainfall thresholds, slope factor of safety concepts, and geology.
    """
    np.random.seed(random_state)

    # 1. Slope (degrees) - NE India ranges from gentle valleys (5-15°) to steep slopes (30-65°)
    slope = np.random.triangular(5.0, 32.0, 65.0, n_samples)

    # 2. Elevation (meters above sea level) - 50m (Brahmaputra valley) to 4000m (Sikkim/Arunachal)
    elevation = np.random.exponential(scale=900, size=n_samples) + 80.0
    elevation = np.clip(elevation, 50.0, 4200.0)

    # 3. Rainfall triggers (mm)
    # Heavy monsoonal bursts common in Cherrapunji/Mawsynram/Sub-Himalayan belt
    rainfall_24h = np.random.gamma(shape=2.5, scale=35.0, size=n_samples)
    rainfall_24h = np.clip(rainfall_24h, 0.0, 350.0)

    rainfall_12h = rainfall_24h * np.random.uniform(0.55, 0.85, n_samples)
    rainfall_6h = rainfall_12h * np.random.uniform(0.45, 0.75, n_samples)
    rainfall_1h = rainfall_6h * np.random.uniform(0.20, 0.50, n_samples)
    rainfall_total = rainfall_24h

    # 4. Soil moisture (0.10 to 0.98 saturation)
    # Heavily correlated with antecedent rainfall
    soil_moisture = 0.25 + 0.65 * (rainfall_24h / 350.0) + np.random.normal(0, 0.05, n_samples)
    soil_moisture = np.clip(soil_moisture, 0.10, 0.98)

    # 5. Soil Type (0: Clayey, 1: Loamy, 2: Sandy Loam, 3: Gravelly/Debris)
    soil_type = np.random.choice([0, 1, 2, 3], size=n_samples, p=[0.25, 0.35, 0.25, 0.15])

    # 6. Geology / Lithology (0: Weathered Shale/Sandstone (Tertiary), 1: Phyllite/Schist, 2: Gneiss/Granite, 3: Alluvium)
    geology = np.random.choice([0, 1, 2, 3], size=n_samples, p=[0.40, 0.30, 0.15, 0.15])

    # 7. Vegetation (NDVI: 0.1 bare/roadcut to 0.85 dense subtropical forest)
    vegetation_ndvi = np.random.uniform(0.12, 0.88, n_samples)

    # 8. Land Use (0: Dense Forest, 1: Road Cut/Active Excavation, 2: Jhum/Cultivation, 3: Rural Settlement)
    land_use = np.random.choice([0, 1, 2, 3], size=n_samples, p=[0.35, 0.30, 0.20, 0.15])

    # 9. Historical Landslide Density (0.0 to 1.0)
    historical_density = np.random.beta(a=1.5, b=4.0, size=n_samples)

    # =========================================================================
    # Physical Landslide Susceptibility Index (Empirical proxy for Factor of Safety)
    # =========================================================================
    # Slope effect (steep slopes > 28 deg have high destabilizing shear stress)
    slope_factor = np.clip((slope - 15.0) / 35.0, 0.0, 1.3) ** 1.4

    # Rainfall trigger factor (24h rain > 90mm or 1h intense rain > 25mm increases pore pressure)
    rain_factor = np.clip(rainfall_24h / 140.0, 0.0, 1.4) + np.clip(rainfall_1h / 30.0, 0.0, 0.6)

    # Soil moisture saturation effect
    moisture_factor = (soil_moisture ** 2.2) * 1.2

    # Lithology weakness (Tertiary shales in Assam/Meghalaya are notoriously friable)
    geo_weakness = np.array([1.2, 1.0, 0.4, 0.3])[geology]

    # Land use: Road cuts destabilize toe of slopes
    land_use_factor = np.array([0.5, 1.4, 1.1, 0.9])[land_use]

    # Lack of vegetation root reinforcement
    veg_vulnerability = (1.0 - vegetation_ndvi) * 1.1

    # Historical recurrence density
    hist_factor = historical_density * 1.2

    # Calculate raw susceptibility logit
    hazard_score = (
        0.30 * slope_factor +
        0.32 * rain_factor +
        0.18 * moisture_factor +
        0.10 * geo_weakness +
        0.08 * land_use_factor +
        0.08 * veg_vulnerability +
        0.08 * hist_factor -
        0.45  # baseline offset
    )

    # Sigmoid to probability
    prob = 1.0 / (1.0 + np.exp(-3.2 * (hazard_score - 0.55)))
    prob = np.clip(prob, 0.01, 0.99)

    # Determine risk classes according to Section 12
    # 0 - 25%   LOW
    # 25 - 50%  MEDIUM
    # 50 - 75%  HIGH
    # 75 - 100% VERY HIGH
    risk_level = []
    for p in prob:
        if p < 0.25:
            risk_level.append("LOW")
        elif p < 0.50:
            risk_level.append("MEDIUM")
        elif p < 0.75:
            risk_level.append("HIGH")
        else:
            risk_level.append("VERY HIGH")

    df = pd.DataFrame({
        "slope": slope.round(1),
        "elevation": elevation.round(1),
        "rainfall_total": rainfall_total.round(1),
        "rainfall_1h": rainfall_1h.round(1),
        "rainfall_6h": rainfall_6h.round(1),
        "rainfall_12h": rainfall_12h.round(1),
        "rainfall_24h": rainfall_24h.round(1),
        "soil_moisture": soil_moisture.round(3),
        "soil_type": soil_type,
        "geology": geology,
        "vegetation_ndvi": vegetation_ndvi.round(3),
        "land_use": land_use,
        "historical_landslide_density": historical_density.round(3),
        "risk_probability": prob.round(4),
        "risk_level": risk_level,
        "source_type": "DEMO"
    })

    return df

if __name__ == "__main__":
    os.makedirs("ai/datasets", exist_ok=True)
    df = generate_northeast_landslide_dataset()
    output_path = "ai/datasets/northeast_landslide_training_data.csv"
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} samples saved to {output_path}")
    print(df["risk_level"].value_counts())
