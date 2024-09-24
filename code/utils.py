import numpy as np
import pandas as pd

import numpy as np

def getThicknesses(depths: np.ndarray) -> np.ndarray:
    """
    Calculate the thicknesses of soil layers based on depth values.

    Parameters:
    - depths: NumPy array of depth values.

    Returns:
    - thicknesses: NumPy array of calculated soil layer thicknesses.
    """
    thicknesses = []
    L_prev = 0  # Top layer starts at the surface
    for i in range(len(depths) - 1):
        L = (depths[i] + depths[i + 1]) / 2.0
        thicknesses.append(L - L_prev)
        L_prev = L
    L = depths[-1] + depths[-1] / 2.0  # Add the thickness of layer surrounding the last depth
    thicknesses.append(L - L_prev)
    
    return np.array(thicknesses)

def get_weights_for_soildepths(depths: np.ndarray) -> np.ndarray:
    """
    Calculate normalized weights for soil depths based on their thicknesses.

    Parameters:
    - depths: NumPy array of depth values.

    Returns:
    - soil_thickness_weight: Normalized weights for soil thicknesses as a NumPy array.
    """
    soil_thickness = getThicknesses(depths)  # Get the thicknesses
    soil_thickness_weight = soil_thickness / np.sum(soil_thickness)  # Normalize the weights
    
    return soil_thickness_weight



def calculate_weighted_averages(data_array: np.ndarray, 
                                 weights: np.ndarray) -> np.ndarray:
    """
    Calculate weighted averages for a given data array.

    Parameters:
    - data_array: NumPy array of values (e.g., soil moisture or soil temperature).
    - soil_thickness_weight: NumPy array of weights corresponding to soil thickness.

    Returns:
    - weighted_avg: Weighted average of the input data array as a NumPy array.
    """
    # Calculate weighted sum
    weighted_sum = np.sum(data_array * weights, axis=1)
    # Calculate weighted average
    weighted_avg = weighted_sum / np.sum(weights)

    return weighted_avg



def calculate_psychrometric_constant(pressure_kpa: np.ndarray) -> np.ndarray:
    """
    Calculate the psychrometric constant (gamma) in kPa/°C based on atmospheric pressure.

    Parameters:
    pressure_kpa (np.ndarray): Atmospheric pressure in kilopascals (kPa).

    Returns:
    np.ndarray: Psychrometric constant (gamma) in kPa/°C for each pressure value.
    
    The formula used for the calculation is:
        γ = (c_p * P) / (λ * R_v)
    where:
        c_p = Specific heat capacity of dry air at constant pressure (MJ/kg·°C)
        P = Atmospheric pressure (kPa)
        λ = Latent heat of vaporization of water (MJ/kg)
        R_v = Ratio of molecular weights of water vapor to dry air.
    """
    # Constants
    specific_heat_air: float = 1.013 * 1e-3  # Specific heat capacity of dry air (MJ/kg·°C)
    latent_heat_vaporization: float = 2.45     # Latent heat of vaporization of water (MJ/kg)
    ratio_vapor_to_air: float = 0.622          # Ratio of molecular weights of water vapor to dry air

    # Calculate psychrometric constant (gamma) for each pressure value
    gamma: np.ndarray = (specific_heat_air * pressure_kpa) / (ratio_vapor_to_air * latent_heat_vaporization)

    return gamma


def calculate_slope_saturation_vapor_pressure_curve(T: np.ndarray) -> np.ndarray:
    """
    Calculate the slope of the saturation vapor pressure curve (Delta) in kPa/°C
    based on temperature using an empirical formula.

    Parameters:
    T (float or numpy array): Temperature in degrees Celsius.

    Returns:
    numpy array: Slope of saturation vapor pressure curve (Delta) in kPa/°C.
    """
    # Constants
    a = 17.27
    b = 237.3

    # Calculate the slope (Delta)
    delta = (4098 * 0.6108 * np.exp(a * T / (T + b))) / np.power(T + b, 2)

    return delta


def W_sqm_to_MJ_sq_m(radiation: np.ndarray, accumulation_time: int) -> np.ndarray:
    """
    Convert solar radiation from watts per square meter (W/m²) to megajoules per square meter (MJ/m²)
    over a specified accumulation time.

    Parameters:
    radiation (np.ndarray): Solar radiation in W/m².
    accumulation_time (int): Accumulation time in seconds.

    Returns:
    np.ndarray: Solar radiation in MJ/m².
    """
    # Convert from W/m² to MJ/m²
    radiation_mj_per_m2 = (radiation * accumulation_time) / 1e6 # Convert to MJ/m²
    return radiation_mj_per_m2

def calculate_Makkink_ET( T: np.ndarray, 
                          pressure_kpa: np.ndarray, 
                          radiation: np.ndarray,
                          constant_a: float = 0.63,
                          accumulation_time:int = 1800) -> np.ndarray:
    """
    Calculate Makkink reference evapotranspiration (ET0).

    Parameters:
    constant_a (float): Coefficient for radiation effect.
    T (np.ndarray): Temperature in degrees Celsius (array).
    pressure_kpa (np.ndarray): Atmospheric pressure in kilopascals (array).
    radiation (np.ndarray): Solar radiation in W/m2 (array).

    Returns:
    np.ndarray: Makkink ET0 in mm/day.
    """
    latent_heat_vaporization: float = 2.45  # Latent heat of vaporization of water (MJ/kg)
    gamma = calculate_psychrometric_constant(pressure_kpa=pressure_kpa)  # Psychrometric constant
    delta = calculate_slope_saturation_vapor_pressure_curve(T=T)  # Slope of saturation vapor pressure curve
    radiation_mj_per_m2 = W_sqm_to_MJ_sq_m(radiation,accumulation_time=1800)

    # Calculate Makkink ET
    makkink_ET = (constant_a * radiation_mj_per_m2 * delta) / (latent_heat_vaporization * (delta / (delta + gamma)))

    return makkink_ET




