class RoutingStore(ODEsElement):
    def __init__(self, parameters, states, approximation, id):

        ODEsElement.__init__(self,
                             parameters=parameters,
                             states=states,
                             approximation=approximation,
                             id=id)

        self._fluxes_python = [self._flux_function_python]

        if approximation.architecture == 'numba':
            self._fluxes = [self._flux_function_numba]
        elif approximation.architecture == 'python':
            self._fluxes = [self._flux_function_python]

    def set_input(self, input):

        self.input = {}
        self.input['P'] = input[0]

    def get_output(self, solve=True):

        if solve:
            # Solve the differential equation
            self._solver_states = [self._states[self._prefix_states + 'S0']]
            self._solve_differential_equation()

            # Update the states
            self.set_states({self._prefix_states + 'S0': self.state_array[-1, 0]})

        fluxes = self._num_app.get_fluxes(fluxes=self._fluxes_python,
                                          S=self.state_array,
                                          S0=self._solver_states,
                                          dt=self._dt,
                                          **self.input,
                                          **{k[len(self._prefix_parameters):]: self._parameters[k] for k in self._parameters},
                                          )

        Qr = - fluxes[0][1]
        F = -fluxes[0][2]

        return [Qr, F]

    @staticmethod
    def _flux_function_python(S, S0, ind, P, x2, x3, gamma, omega, dt):

        if ind is None:
            return(
                [
                    P,  # P
                    - ((x3**(1 - gamma)) / ((gamma - 1))) * (S**gamma),  # Qr
                    - (x2 * (S / x3)**omega),  # F
                ],
                0.0,
                S0 + P * dt
            )
        else:
            return(
                [
                    P[ind],  # P
                    - ((x3[ind]**(1 - gamma[ind])) / ((gamma[ind] - 1))) * (S**gamma[ind]),  # Qr
                    - (x2[ind] * (S / x3[ind])**omega[ind]),  # F
                ],
                0.0,
                S0 + P[ind] * dt[ind],
                [
                    0.0,
                    - ((x3[ind]**(1 - gamma[ind])) / ((gamma[ind] - 1) * dt[ind])) * (S**(gamma[ind] - 1)) * gamma[ind],
                    - (omega[ind] * x2[ind] * ((S / x3[ind])**(omega[ind] - 1)))
                ]
            )

    @staticmethod
    @nb.jit('Tuple((UniTuple(f8, 3), f8, f8, UniTuple(f8, 3)))(optional(f8), f8, i4, f8[:], f8[:], f8[:], f8[:], f8[:], f8[:])',
            nopython=True)
    def _flux_function_numba(S, S0, ind, P, x2, x3, gamma, omega, dt):

        return(
            (
                P[ind],  # P
                - ((x3[ind]**(1 - gamma[ind])) / ((gamma[ind] - 1))) * (S**gamma[ind]),  # Qr
                - (x2[ind] * (S / x3[ind])**omega[ind]),  # F
            ),
            0.0,
            S0 + P[ind] * dt[ind],
            (
                0.0,
                - ((x3[ind]**(1 - gamma[ind])) / ((gamma[ind] - 1) * dt[ind])) * (S**(gamma[ind] - 1)) * gamma[ind],
                - (omega[ind] * x2[ind] * ((S / x3[ind])**(omega[ind] - 1)))
            )
        )