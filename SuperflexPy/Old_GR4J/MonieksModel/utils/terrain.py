# This file contains the three main types of terrain used by the FlexTopo model and
# How runoff and discharge behave in these types of cells.

import numpy as np

def plateau(timestep, Par, forcing, Fluxes, States):
    Imax, Ce, Sumax, beta, Pmax, Kf, k = Par

    # Imax=Par[0]
    # Ce=Par[1]
    # Sumax=Par[2]
    # beta=Par[3]
    # Pmax=Par[4] ## Anders is bij ons D
    # Kf=Par[5]
    # k=Par[6]

    Qo = forcing[:, 0]
    Prec = forcing[:, 1]
    Etp = forcing[:, 2]

    tmax = len(Prec)
    Si = States[:, 0]
    Su = States[:, 1]
    Sf = States[:, 2]

    Eidt = Fluxes[:, 0]
    Eadt = Fluxes[:, 1]
    Qfdt = Fluxes[:, 2]
    Qusdt = Fluxes[:, 3]

    dt = 1
    t = timestep

    Pdt = Prec[t] * dt
    Epdt = Etp[t] * dt

    # Interception Reservoir
    if Pdt > 0:
        Si[t] = Si[t] + Pdt
        Pedt = max(0, Si[t] - Imax)
        Si[t] = Si[t] - Pedt
        Eidt[t] = 0
    else:
        # Evaporation only when there is no rainfall
        Pedt = 0
        Eidt[t] = min(Epdt, Si[t])
        Si[t] = Si[t] - Eidt[t]

    if t < tmax - 1:
        Si[t + 1] = Si[t]

    # Unsaturated Reservoir
    if Pedt > 0:
        rho = (Su[t] / Sumax) ** beta
        Su[t] = Su[t] + (1 - rho) * Pedt
        Qufdt = rho * Pedt
    else:
        Qufdt = 0

    # Transpiration
    Epdt = max(0, Epdt - Eidt[t])
    Eadt[t] = Epdt * (Su[t] / (Sumax * Ce))
    Eadt[t] = min(Eadt[t], Su[t])
    Su[t] = Su[t] - Eadt[t]

    # Percolation
    Qusdt = (Su[t] / Sumax) * Pmax * dt
    Su[t] = Su[t] - min(Qusdt, Su[t])
    if t < tmax - 1:
        Su[t + 1] = Su[t]

    # Fast Reservoir
    Sf[t] = Sf[t] + Qufdt
    Qfdt[t] = dt * Kf * Sf[t]
    Sf[t] = Sf[t] - min(Qfdt[t], Sf[t])

    if t < tmax - 1:
        Sf[t + 1] = Sf[t]

    # save output
    States[:, 0] = Si
    States[:, 1] = Su
    States[:, 2] = Sf

    Fluxes[:, 0] = Eidt
    Fluxes[:, 1] = Eadt
    Fluxes[:, 2] = Qfdt
    Fluxes[:, 3] = Qusdt

    return (Fluxes, States)


def hillslope(timestep, Par, forcing, Fluxes, States, conc):
    '''
    A.1: interception reservoir   [Si]
    A.2: unsaturated reservoir    [Su]
    A.3: fast reservoir           [Sf]
    A.4: saturated reservoir      [Ss]

    B.1: Interception evaporation [Eidt]
    B.2: Transpiration            [Eadt]
    B.3: Fast reservoir to water  [Qfdt]
    B.4: Unsaturated to fast flow [Qufdt]
    B.5: Unsaturated to saturated [Qusdt]

    Returns: Fluxes(4) and States(3)
    '''

    # HBVpareto Calculates values of 3 objective functions for HBV model
    tmax = len(forcing[:, 0])

    Imax = Par[0]
    Ce = Par[1]
    Sumax = Par[2]
    beta = Par[3]
    D = Par[4]
    Kf = Par[5]
    k = Par[6]  # degradation factor for the fertiliser

    Qo = forcing[:, 0]
    Prec = forcing[:, 1]
    Etp = forcing[:, 2]
    W = forcing[:, 3]  # fertilizer injection

    Si = States[:, 0]
    Su = States[:, 1]
    Sf = States[:, 2]

    Eidt = Fluxes[:, 0]
    Eadt = Fluxes[:, 1]
    Qfdt = Fluxes[:, 2]
    Qusdt = Fluxes[:, 3]

    ci = np.zeros(tmax)
    cu = np.zeros(tmax)
    cf = np.zeros(tmax)

    # concentrations with decay factor
    Ci = conc[:, 0]
    Cu = conc[:, 1]
    Cf = conc[:, 2]

    dt = 1
    t = timestep

    Pdt = Prec[t] * dt
    Epdt = Etp[t] * dt

    # Interception Reservoir
    if Pdt > 0:
        Si[t] = Si[t] + Pdt
        Pedt = max(0, Si[t] - Imax)
        Si[t] = Si[t] - Pedt
        Eidt[t] = 0

    else:
        Pedt = 0
        Eidt[t] = min(Epdt, Si[t])
        Si[t] = Si[t] - Eidt[t]

    if Si[t] > 0:
        ci[t] = W[t] / Si[t]

    else:
        ci[t] = 0

    if t == 1:
        Ci[t] = ci[t] * np.exp(-k)

    else:
        Ci[t] = (ci[t] + Ci[t - 1]) * np.exp(-k)

    if t < tmax - 1:
        Si[t + 1] = Si[t]
        ci[t + 1] = ci[t]
        Ci[t + 1] = Ci[t]

    # Unsaturated Reservoir
    if Pedt > 0:
        rho = (Su[t] / Sumax) ** beta
        Su[t] = Su[t] + (1 - rho) * Pedt
        Qufdt = rho * Pedt

        cu[t] = Ci[t] * Pedt / Su[t]
    else:
        Qufdt = 0
        cu[t] = 0

    if t == 1:
        Cu[t] = cu[t] * np.exp(-k)

    else:
        Cu[t] = (cu[t] + Cu[t - 1]) * np.exp(-k)

    # Transpiration
    Epdt = max(0, Epdt - Eidt[t])
    Eadt[t] = Epdt * (Su[t] / (Sumax * Ce))
    Eadt[t] = min(Eadt[t], Su[t])
    Su[t] = Su[t] - Eadt[t]

    if t < tmax - 1:
        Su[t + 1] = Su[t]
        cu[t + 1] = cu[t]
        Cu[t + 1] = Cu[t]

    # Preferential Percolation
    Qusdt = D * Qufdt
    Su[t] = Su[t] - min(Qusdt, Su[t])

    if t < tmax - 1:
        Su[t + 1] = Su[t]

    # Fast Reservoir
    Sf[t] = Sf[t] + (1 - D) * Qufdt
    Qfdt[t] = dt * Kf * Sf[t]
    Sf[t] = Sf[t] - min(Qfdt[t], Sf[t])

    if Sf[t] > 0:
        cf[t] = Ci[t] * Qufdt / Sf[t]

    else:
        cf[t] = 0

    if t == 1:
        Cf[t] = cf[t] * np.exp(-k)

    else:
        Cf[t] = (cf[t] + Cf[t - 1]) * np.exp(-k)

    if t < tmax - 1:
        Sf[t + 1] = Sf[t]
        cf[t + 1] = cf[t]
        Cf[t + 1] = Cf[t]

    # concentration in the fast reservoir
    # if Sf[t] > 0:
    #     Cf[t] = ((1 - D) * Qufdt * Cu[t] - Qfdt[t] * Cf[t] - k * Cf[t] * Sf[t]) / Sf[t] + Cf[t]
    # else:
    #     Cf[t] = 0

    # save output
    States[:, 0] = Si
    States[:, 1] = Su
    States[:, 2] = Sf

    Fluxes[:, 0] = Eidt
    Fluxes[:, 1] = Eadt
    Fluxes[:, 2] = Qfdt
    Fluxes[:, 3] = Qusdt

    conc[:, 0] = Ci
    conc[:, 1] = Cu
    conc[:, 2] = Cf

    return (Fluxes, States, conc)  # , Qfdt, Qufdt)


def wetland(timestep, Par, forcing, Fluxes, States, conc, Ss, landscape):
    tmax = len(forcing[:, 0])

    Imax = Par[0]
    Ce = Par[1]
    Sumax = Par[2]
    beta = Par[3]
    Cmax = Par[4]
    Kf = Par[5]
    k = Par[6]

    Qo = forcing[:, 0]
    Prec = forcing[:, 1]
    Etp = forcing[:, 2]
    W = forcing[:, 3]

    tmax = len(Prec)
    Si = States[:, 0]
    Su = States[:, 1]
    Sf = States[:, 2]

    Eidt = Fluxes[:, 0]
    Eadt = Fluxes[:, 1]
    Qfdt = Fluxes[:, 2]

    # No percolation, everything ends up in river!

    # concentrations without decay factor
    ci = np.zeros(tmax)
    cu = np.zeros(tmax)
    cf = np.zeros(tmax)
    cs = np.zeros(tmax)

    # concentrations with decay factor
    Ci = conc[:, 0]
    Cu = conc[:, 1]
    Cf = conc[:, 2]
    Cs = conc[:, 3]

    dt = 1
    t = timestep

    Pdt = Prec[t] * dt
    Epdt = Etp[t] * dt

    if Pdt > 0:
        Si[t] = Si[t] + Pdt
        Pedt = max(0, Si[t] - Imax)
        Si[t] = Si[t] - Pedt
        Eidt[t] = 0
    else:
        # Evaporation only when there is no rainfall
        Pedt = 0
        Eidt[t] = min(Epdt, Si[t])
        Si[t] = Si[t] - Eidt[t]

    if Si[t] > 0:
        ci[t] = W[t] / Si[t]

    else:
        ci[t] = 0

    if t == 1:
        Ci[t] = ci[t] * np.exp(-k)

    else:
        Ci[t] = (ci[t] + Ci[t - 1] * np.exp(-k))

    if t < tmax - 1:
        Si[t + 1] = Si[t]
        ci[t + 1] = ci[t]
        Ci[t + 1] = Ci[t]

    # Unsaturated Reservoir
    if Pedt > 0:
        rho = (Su[t] / Sumax) ** beta
        Su[t] = Su[t] + (1 - rho) * Pedt
        Qufdt = rho * Pedt

        cu[t] = Ci[t] * Pedt / Su[t]

    else:
        Qufdt = 0
        cu[t] = 0

    if t == 1:
        Cu[t] = cu[t] * np.exp(-k)

    else:
        Cu[t] = (cu[t] + Cu[t - 1]) * np.exp(-k)

    # Transpiration
    Epdt = max(0, Epdt - Eidt[t])
    Eadt[t] = Epdt * (Su[t] / (Sumax * Ce))
    Eadt[t] = min(Eadt[t], Su[t])
    Su[t] = Su[t] - Eadt[t]

    # Capillary rise
    Qrdt = (1 - Su[t] / Sumax) * Cmax * dt;

    # check if the groundwater has enough water (note: you need to use the landscape
    # percentage!!!)
    Qrdt = min(Qrdt, Ss[t] / landscape);

    # su cannot be more than sumax
    if ((Su[t] + Qrdt) > Sumax):
        Qrdt = Sumax - Su[t]

        Su[t] = Su[t] + Qrdt
        Ss[t] = Ss[t] - Qrdt * landscape

    if t < tmax - 1:
        Su[t + 1] = Su[t]
        cu[t + 1] = cu[t]
        Cu[t + 1] = Cu[t]

    # concentration in the unsaturated reservoir
    # if Su[t] > 0:
    #     Cu[t] = (Qrdt * Cs[t] + fert[t] - Qufdt * Cu[t-1] - k * Cu[t-1] * Su[t]) / Su[t] + Cu[t-1]
    # else:
    #     Cu[t] = 0

    # Fast Reservoir
    Sf[t] = Sf[t] + Qufdt
    Qfdt[t] = dt * Kf * Sf[t]
    Sf[t] = Sf[t] - min(Qfdt[t], Sf[t])

    # concentration in the fast reservoir
    if Sf[t] > 0:
        cf[t] = Ci[t] * Qufdt / Sf[t]

    else:
        cf[t] = 0

    if t == 1:
        Cf[t] = cf[t] * np.exp(-k)

    else:
        Cf[t] = (cf[t] + Cf[t - 1]) * np.exp(-k)

    if t < tmax - 1:
        Sf[t + 1] = Sf[t]
        cf[t + 1] = cf[t]
        Cf[t + 1] = Cf[t]

    # save output
    States[:, 0] = Si
    States[:, 1] = Su
    States[:, 2] = Sf

    Fluxes[:, 0] = Eidt
    Fluxes[:, 1] = Eadt
    Fluxes[:, 2] = Qfdt

    conc[:, 0] = Ci
    conc[:, 1] = Cu
    conc[:, 2] = Cf
    conc[:, 3] = Cs

    return (Fluxes, States, Ss, conc)