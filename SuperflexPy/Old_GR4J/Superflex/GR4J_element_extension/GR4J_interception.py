class InterceptionFilter(BaseElement):

     _num_upstream = 1
     _num_downstream = 1

     def set_input(self, input):

         self.input = {}
         self.input['PET'] = input[0]
        self.input['P'] = input[1]

    def get_output(self, solve=True):

        remove = np.minimum(self.input['PET'], self.input['P'])

        return [self.input['PET'] - remove, self.input['P'] - remove]