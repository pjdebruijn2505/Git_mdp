import numpy as np
import matplotlib.pyplot as plt

def seasonal_trend(n, offset):

    t = np.linspace(0, n / 365 * np.pi, n)
    sin_disc = abs(np.sin(t)) + offset  #offset to keep some evaporation or precipitation in simulation
    cos_disc = abs(np.cos(t)) + offset

    return sin_disc, cos_disc

def Visualize_precipitation_evaporation(evaporation, precipitation):
    net_flux = precipitation - evaporation
    plt.figure(figsize=(10, 5))

    bar_width = 0.4
    index = np.arange(len(precipitation))

    plt.bar(index, precipitation, color='blue', width=bar_width, label='Precipitation [mm/day]')
    plt.bar(index + bar_width, evaporation, color='red', width=bar_width, label='Evaporation [mm/day]')
    plt.ylim(0, max(np.max(precipitation), np.max(evaporation)))
    plt.xlabel('Day')
    plt.ylabel('Amount [mm/day]')
    plt.title('Daily Precipitation and Evaporation')
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Plotting net flux (precipitation - evaporation)
    plt.figure(figsize=(10, 5))

    plt.bar(index, net_flux, color='orange', label='Net Flux [mm/day]')
    plt.ylim(np.min(net_flux), np.max(net_flux))
    plt.xlabel('Day')
    plt.ylabel('Amount [mm/day]')
    plt.title('Daily Net Flux (Precipitation - Evaporation)')
    plt.legend()
    plt.tight_layout()
    plt.show()
    return

def precipitation_evaporation(years, offset, season = True, plot = True):
# We create a precipitation time series of years *365 time steps and predict the output of the reservoir

    #reproducibility
    np.random.seed(42)
    n = years * 365  # daily data

    if (season == True):
        sin_disc, cos_disc = seasonal_trend(n,offset)
    else:
        sin_disc, cos_disc = 1, 1
    # Generate a synthetic dataset of 200 precipitation values
    precipitation = np.random.normal(loc=2.5, scale=2, size=n)*cos_disc
    precipitation[precipitation < 0] = 0  # Ensure values are non-negative

    evaporation = np.random.normal(loc=2.5, scale=2, size=n)* sin_disc #Slightly smaller values for evaporation
    evaporation[evaporation < 0] = 0  # Ensure values are non-negative

    # Round values to two decimal places
    evaporation = np.round(evaporation, 1)
    precipitation = np.round(precipitation, 1)

    if(plot == True):
        Visualize_precipitation_evaporation(evaporation, precipitation)

    return evaporation, precipitation

