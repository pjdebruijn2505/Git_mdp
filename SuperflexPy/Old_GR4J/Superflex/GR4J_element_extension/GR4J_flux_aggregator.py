class FluxAggregator(BaseElement):

    _num_downstream = 1
    _num_upstream = 1

    def set_input(self, input):

        self.input = {}
        self.input['Qr'] = input[0]
        self.input['F'] = input[1]
        self.input['Q2_out'] = input[2]

    def get_output(self, solve=True):

        return [self.input['Qr']
                + np.maximum(0, self.input['Q2_out'] - self.input['F'])]