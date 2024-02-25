import numpy as np
from utils.terrain import plateau, hillslope, wetland
from utils.utils import Weigfun

def FLEXtopo(ParPlateau, ParHillslope_crop, ParHillslope_forest, ParWetland, ParCatchment, forcing, landscapes, frac1):
    # parameters and constants
    Ks = ParCatchment[0]
    Tlag = ParCatchment[1]
    k = ParPlateau[6]
    dt = 1
    tmax = len(forcing[:, 0])

    # initialize states
    States_plateau, States_hillslope, States_hillslope_crop, States_hillslope_forest,
    States_wetland = np.zeros((tmax, 3))


    # initialize fluxes
    Fluxes_plateau, Fluxes_hillslope, Fluxes_hillslope_crop, Fluxes_hillslope_forest,
    Fluxes_wetland= np.zeros((tmax, 4))

    # initialize concentration
    conc_hillslope, conc_hillslope_crop, conc_hillslope_forest = np.zeros((tmax, 3))
    conc_wetland = np.zeros((tmax, 4))

    Qsdt, Qfdt, Qtotdt, Ctot, Ea, cs, Cs, Ctot,  Ctot_fin = np.zeros(tmax)

    frac = 0.7
    A_basin = 1274215423 / 1000

    Def = np.zeros(tmax)  # initial deficit

    # loop over time
    for t in range(0, tmax):

        # plateau
        Fluxes_plateau, States_plateau = plateau(
            t, ParPlateau, forcing, Fluxes_plateau, States_plateau)

        # hillslope
        Fluxes_hillslope_crop, States_hillslope_crop, conc_hillslope_crop = hillslope(
            t, ParHillslope_crop, forcing, Fluxes_hillslope_crop, States_hillslope_crop, conc_hillslope_crop)
        Fluxes_hillslope_forest, States_hillslope_forest, conc_hillslope_forest = hillslope(
            t, ParHillslope_forest, forcing, Fluxes_hillslope_forest, States_hillslope_forest, conc_hillslope_forest)
        # wetland
        Fluxes_wetland, States_wetland, Ss, conc_wetland = wetland(
            t, ParWetland, forcing, Fluxes_wetland, States_wetland, conc_wetland, Ss, landscapes[2])

        # Slow Reservoir
        # Ss[t]=Ss[t]+ Fluxes_plateau[t,3] * landscapes[0] + (1-frac) * Fluxes_hillslope_forest[t,3]*landscapes[1] + frac * Fluxes_hillslope_crop[t,3]*landscapes[1] + Fluxes_wetland[t,3]*landscapes[2]
        Ss[t] = Ss[t] + Fluxes_plateau[t, 3] * landscapes[0] + 0.7 * Fluxes_hillslope_crop[t, 3] * landscapes[1] + 0.3 * \
                Fluxes_hillslope_forest[t, 3] * landscapes[1] + Fluxes_wetland[t, 3] * landscapes[2]

        Ea[t] = ((1 - frac) * Fluxes_hillslope_forest[t, 1] + frac * Fluxes_hillslope_crop[t, 1]) * landscapes[1] + \
                Fluxes_wetland[t, 1] * landscapes[2] + Fluxes_plateau[t, 1] * landscapes[0]
        Ea_w = Fluxes_wetland[t, 1] * landscapes[2]
        Def[t] = min(Ss[t], frac1 * (forcing[t, 2] - Ea_w))

        Ss[t] = Ss[t] - Def[t]
        Ea[t] = Ea[t] + frac1 * Def[t]

        Qsdt = dt * Ks * Ss[t]
        Ss[t] = Ss[t] - min(Qsdt, Ss[t])

        if t < tmax - 1:
            Ss[t + 1] = Ss[t]

        if Ss[t] > 0:  # [t,2] = Cs
            cs[t] = ((conc_hillslope_crop[t, 2] + conc_hillslope_crop[t, 1] + conc_wetland[t, 1] + conc_wetland[
                t, 2]) / 2 * Qsdt) / Ss[t]
            # cs[t] = ((conc_wetland[t,1] * Fluxes_wetland[t,2] + conc_wetland[t, 2] * Qsdt + conc_hillslope_crop[t,1] * Fluxes_hillslope_crop[t,2] + conc_hillslope_crop[t,2] * Qsdt))/ Ss[t]
            # cs[t] = (0.7*Fluxes_hillslope_crop[t, 3]*landscapes[1]*conc_hillslope_crop[t,0] + Fluxes_wetland[t,3]*landscapes[2]*conc_wetland[t,0]  -k * Ss[t]*conc_wetland[t,2]) / Ss[t] + conc_wetland[t,2]
            # cs[t] = (0.7 *Fluxes_hillslope_crop[t,3] * dt * landscapes[1] * A_basin * (conc_hillslope_crop[t,1] + conc_hillslope_crop[t,2]) + Fluxes_wetland[t,3] * dt * A_basin * landscapes[2] * (conc_wetland[t,1] + conc_wetland[t,2])) / Ss[t]
        else:
            cs[t] = 0

        if t == 0:
            Cs[t] = cs[t] * np.exp(-k)
        else:
            Cs[t] = (cs[t] + Cs[t - 1]) * np.exp(-k)

        if t < tmax - 1:
            cs[t + 1] = cs[t]
            Cs[t + 1] = Cs[t]

        Qtotdt[t] = Qsdt + (0.3 * Fluxes_hillslope_forest[t, 2] + 0.7 * Fluxes_hillslope_crop[t, 2]) * landscapes[1] + \
                    Fluxes_plateau[t, 2] * landscapes[0] + Fluxes_wetland[t, 2] * landscapes[2]

        if Qtotdt[t] > 0:
            # Ctot[t] = (Cs[t] * Qsdt + conc_hillslope_crop[t,2] * Fluxes_hillslope[t,2] + conc_wetland[t,2] * Fluxes_wetland[t,2]) / Qtotdt[t] / (1000000)
            Ctot[t] = (Qsdt * Cs[t] + 0.7 * Fluxes_hillslope_crop[t, 2] * conc_hillslope_crop[t, 2] + Fluxes_wetland[
                t, 2] * conc_wetland[t, 2]) / Qtotdt[t] / 1000000

        else:
            Ctot[t] = 0

        if t == 1:
            Ctot_fin[t] = Ctot[t] * np.exp(-k)
        else:
            Ctot_fin[t] = (Ctot[t] + Ctot_fin[t - 1]) * np.exp(-k)

    # Offset Q
    Weigths = Weigfun(Tlag)
    Qm = np.convolve(Qtotdt, Weigths)
    Qm = Qm[0:tmax]

    # plt.plot(Qm)
    # plt.plot(Fluxes_hillslope_forest[:,2])

    return (Qm, Ea, Ctot_fin, Def)
