#Two extensions of the LagElement as implemented in Superflex by to facilitate the
# GR4J implementation. Difference in calculate_lag_area method

class UnitHydrograph1(LagElement):

    def __init__(self, parameters, states, id):

        LagElement.__init__(self, parameters, states, id)

    def _build_weight(self, lag_time):

        weight = []

        for t in lag_time:
            array_length = np.ceil(t)
            w_i = []
            for i in range(int(array_length)):
                w_i.append(self._calculate_lag_area(i + 1, t)
                           - self._calculate_lag_area(i, t))
            weight.append(np.array(w_i))

        return weight

    @staticmethod
    def _calculate_lag_area(bin, len):
        if bin <= 0:
            value = 0
        elif bin < len:
            value = (bin / len)**2.5
        else:
            value = 1
        return value

class UnitHydrograph2(LagElement):

    def __init__(self, parameters, states, id):

        LagElement.__init__(self, parameters, states, id)

    def _build_weight(self, lag_time):

        weight = []

        for t in lag_time:
            array_length = np.ceil(t)
            w_i = []
            for i in range(int(array_length)):
                w_i.append(self._calculate_lag_area(i + 1, t)
                           - self._calculate_lag_area(i, t))
            weight.append(np.array(w_i))

        return weight

    @staticmethod
    def _calculate_lag_area(bin, len):
        half_len = len / 2
        if bin <= 0:
            value = 0
        elif bin < half_len:
            value = 0.5 * (bin / half_len)**2.5
        elif bin < len:
            value = 1 - 0.5 * (2 - bin / half_len)**2.5
        else:
            value = 1
        return value