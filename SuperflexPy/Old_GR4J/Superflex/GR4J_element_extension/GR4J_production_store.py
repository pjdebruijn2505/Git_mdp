class ProductionStore(ODEsElement):

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
        self.input['PET'] = input[0]
        self.input['P'] = input[1]

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

        Pn_minus_Ps = self.input['P'] - fluxes[0][0]
        Perc = - fluxes[0][2]
        return [Pn_minus_Ps + Perc]

    def get_aet(self):

        try:
            S = self.state_array
        except AttributeError:
            message = '{}get_aet method has to be run after running '.format(self._error_message)
            message += 'the model using the method get_output'
            raise AttributeError(message)

        fluxes = self._num_app.get_fluxes(fluxes=self._fluxes_python,
                                          S=S,
                                          S0=self._solver_states,
                                          dt=self._dt,
                                          **self.input,
                                          **{k[len(self._prefix_parameters):]: self._parameters[k] for k in self._parameters},
                                          )

        return [- fluxes[0][1]]

    @staticmethod
    def _flux_function_python(S, S0, ind, P, x1, alpha, beta, ni, PET, dt):

        if ind is None:
            return(
                [
                    P * (1 - (S / x1)**alpha),  # Ps
                    - PET * (2 * (S / x1) - (S / x1)**alpha),  # Evaporation
                    - ((x1**(1 - beta)) / ((beta - 1))) * (ni**(beta - 1)) * (S**beta)  # Perc
                ],
                0.0,
                S0 + P * (1 - (S / x1)**alpha) * dt
            )
        else:
            return(
                [
                    P[ind] * (1 - (S / x1[ind])**alpha[ind]),  # Ps
                    - PET[ind] * (2 * (S / x1[ind]) - (S / x1[ind])**alpha[ind]),  # Evaporation
                    - ((x1[ind]**(1 - beta[ind])) / ((beta[ind] - 1))) * (ni[ind]**(beta[ind] - 1)) * (S**beta[ind])  # Perc
                ],
                0.0,
                S0 + P[ind] * (1 - (S / x1[ind])**alpha[ind]) * dt[ind],
                [
                    - (P[ind] * alpha[ind] / x1[ind]) * ((S / x1[ind])**(alpha[ind] - 1)),
                    - (PET[ind] / x1[ind]) * (2 - alpha[ind] * ((S / x1[ind])**(alpha[ind] - 1))),
                    - beta[ind] * ((x1[ind]**(1 - beta[ind])) / ((beta[ind] - 1) * dt[ind])) * (ni[ind]**(beta[ind] - 1)) * (S**(beta[ind] - 1))
                ]
            )

    @staticmethod
    @nb.jit('Tuple((UniTuple(f8, 3), f8, f8, UniTuple(f8, 3)))(optional(f8), f8, i4, f8[:], f8[:], f8[:], f8[:], f8[:], f8[:], f8[:])',
            nopython=True)
    def _flux_function_numba(S, S0, ind, P, x1, alpha, beta, ni, PET, dt):

        return(
            (
                P[ind] * (1 - (S / x1[ind])**alpha[ind]),  # Ps
                - PET[ind] * (2 * (S / x1[ind]) - (S / x1[ind])**alpha[ind]),  # Evaporation
                - ((x1[ind]**(1 - beta[ind])) / ((beta[ind] - 1))) * (ni[ind]**(beta[ind] - 1)) * (S**beta[ind])  # Perc
            ),
            0.0,
            S0 + P[ind] * (1 - (S / x1[ind])**alpha[ind]) * dt[ind],
            (
                - (P[ind] * alpha[ind] / x1[ind]) * ((S / x1[ind])**(alpha[ind] - 1)),
                - (PET[ind] / x1[ind]) * (2 - alpha[ind] * ((S / x1[ind])**(alpha[ind] - 1))),
                - beta[ind] * ((x1[ind]**(1 - beta[ind])) / ((beta[ind] - 1) * dt[ind])) * (ni[ind]**(beta[ind] - 1)) * (S**(beta[ind] - 1))
            )
        )