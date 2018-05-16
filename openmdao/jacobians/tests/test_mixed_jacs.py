import unittest
import numpy as np
from numpy.testing import assert_almost_equal

from openmdao.api import Problem, Group, IndepVarComp, DirectSolver, NewtonSolver, \
    ScipyKrylov, LinearRunOnce, LinearBlockGS

from openmdao.test_suite.components.double_sellar import DoubleSellar


def _baseline(mode):
    p = Problem()

    dv = p.model.add_subsystem('dv', IndepVarComp(), promotes=['*'])
    dv.add_output('z', [1.,1.])

    p.model.add_subsystem('double_sellar', DoubleSellar())
    p.model.connect('z', ['double_sellar.g1.z', 'double_sellar.g2.z'])

    p.model.add_design_var('z', lower=-10, upper=10)
    p.model.add_objective('double_sellar.g1.y1')

    p.setup(mode=mode)

    p.model.nonlinear_solver = NewtonSolver()

    p.run_model()

    objective = p['double_sellar.g1.y1']
    jac = p.compute_totals()

    return objective, jac


def _mixed_case(mode):
    p = Problem()

    dv = p.model.add_subsystem('dv', IndepVarComp(), promotes=['*'])
    dv.add_output('z', [1.,1.])

    p.model.add_subsystem('double_sellar', DoubleSellar())
    p.model.connect('z', ['double_sellar.g1.z', 'double_sellar.g2.z'])

    p.model.add_design_var('z', lower=-10, upper=10)
    p.model.add_objective('double_sellar.g1.y1')

    p.setup(mode=mode)

    p.model.double_sellar.g1.linear_solver = DirectSolver(assembled_jac='csc')
    p.model.double_sellar.g1.nonlinear_solver = NewtonSolver()

    p.model.double_sellar.g2.linear_solver = DirectSolver(assembled_jac='csc')
    p.model.double_sellar.g2.nonlinear_solver = NewtonSolver()

    newton = p.model.nonlinear_solver = NewtonSolver()
    newton.linear_solver = ScipyKrylov()
    newton.linear_solver.precon = LinearBlockGS()

    p.model.linear_solver = ScipyKrylov(assembled_jac='dense')
    p.model.linear_solver.precon = DirectSolver()

    p.run_model()

    objective = p['double_sellar.g1.y1']
    jac = p.compute_totals()

    return objective, jac


class MixingJacsTestCase(unittest.TestCase):
    def test_mixed_fwd(self):
        base_objective, base_jac = _baseline('fwd')
        obj, jac = _mixed_case('fwd')

        assert_almost_equal(base_objective, obj, decimal=7)

        for key in jac:
            assert_almost_equal(base_jac[key], jac[key], decimal=7)

    def test_mixed_rev(self):
        base_objective, base_jac = _baseline('rev')
        obj, jac = _mixed_case('rev')

        assert_almost_equal(base_objective, obj, decimal=7)

        for key in jac:
            assert_almost_equal(base_jac[key], jac[key], decimal=7)

if __name__ == '__main__':
    unittest.main()
