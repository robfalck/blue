"""
Stress calculation component.

Simple calculation of beam bending stress assuming small angular displacments.
Vectorized for multiple load cases.
"""

from __future__ import division
from six.moves import range

import numpy as np

from openmdao.api import ExplicitComponent


class MultiStressComp(ExplicitComponent):

    def initialize(self):
        self.metadata.declare('num_elements', types=int)
        self.metadata.declare('num_rhs', types=int)
        self.metadata.declare('E')

    def setup(self):
        num_elements = self.metadata['num_elements']
        num_nodes = num_elements + 1
        num_rhs = self.metadata['num_rhs']

        self.add_input('h', shape=num_elements)

        for j in range(num_rhs):
            self.add_input('displacements_%d' % j, shape=2 * num_nodes)
            self.add_output('stress_%d' % j, shape=num_elements)

            self.declare_partials(of='stress_%d' % j, wrt='displacements_%d' % j)
            self.declare_partials(of='stress_%d' % j, wrt='h')

    def compute(self, inputs, outputs):
        num_rhs = self.metadata['num_rhs']
        tk = inputs['h'] * 0.5
        E = self.metadata['E']

        for j in range(num_rhs):
            ang = inputs['displacements_%d' % j][1::2]
            d_ang = ang[1:] - ang[0:-1]
            outputs['stress_%d' % j] = tk * E * d_ang

    def compute_partials(self, inputs, partials):
        num_elements = self.metadata['num_elements']
        num_nodes = num_elements + 1
        num_states = num_nodes * 2
        num_rhs = self.metadata['num_rhs']
        tk = inputs['h'] * 0.5
        E = self.metadata['E']

        for j in range(num_rhs):
            ang = inputs['displacements_%d' % j][1::2]
            d_ang = ang[1:] - ang[0:-1]
            partials['stress_%d' % j, 'h'] = np.diag(0.5 * E * d_ang)

            J = np.zeros((num_elements, num_states))
            J[:, 1:-1:2] = -np.diag(tk * E)
            J[:, 3::2] += np.diag(tk * E)
            partials['stress_%d' % j, 'displacements_%d' % j] = J