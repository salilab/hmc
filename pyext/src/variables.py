import numpy as np

import IMP.isd
import IMP.core
import IMP.hmc

from .julia import HMCUtilities


def _get_nuis_bounds(m, pi):
    n = IMP.isd.Nuisance(m, pi)
    return n.get_lower(), n.get_upper()


class OptimizedVariables(object):
    key_constraints = [
        # sphere (coords/radius)
        (
            (
                IMP.core.XYZ.get_xyz_keys()[0],
                IMP.core.XYZ.get_xyz_keys()[1],
                IMP.core.XYZ.get_xyz_keys()[2],
            ),
            lambda m, pi: HMCUtilities.IdentityConstraint(3),
        ),
        # local coordinates
        (
            (IMP.FloatKey(4), IMP.FloatKey(5), IMP.FloatKey(6)),
            lambda m, pi: HMCUtilities.IdentityConstraint(3),
        ),
        (
            (IMP.core.XYZR.get_radius_key(),),
            lambda m, pi: HMCUtilities.LowerBoundedConstraint(0.0),
        ),
        # rigid body quaternion
        (
            (
                IMP.FloatKey("rigid_body_quaternion_0"),
                IMP.FloatKey("rigid_body_quaternion_1"),
                IMP.FloatKey("rigid_body_quaternion_2"),
                IMP.FloatKey("rigid_body_quaternion_3"),
            ),
            lambda m, pi: HMCUtilities.UnitVectorConstraint(4),
        ),
        # local rigid body quaternion
        (
            (
                IMP.FloatKey("rigid_body_local_quaternion_0"),
                IMP.FloatKey("rigid_body_local_quaternion_1"),
                IMP.FloatKey("rigid_body_local_quaternion_2"),
                IMP.FloatKey("rigid_body_local_quaternion_3"),
            ),
            lambda m, pi: HMCUtilities.UnitVectorConstraint(4),
        ),
        # direction
        (
            (
                IMP.core.Direction.get_direction_key(0),
                IMP.core.Direction.get_direction_key(1),
                IMP.core.Direction.get_direction_key(2),
            ),
            lambda m, pi: HMCUtilities.DirectionConstraint(4),
        ),
        # nuisance
        (
            (IMP.isd.Nuisance.get_nuisance_key(),),
            lambda m, pi: HMCUtilities.TransformConstraint(
                *_get_nuis_bounds(m, pi)
            ),
        ),
    ]

    def __init__(self, m):
        self.m = m
        self.optimized_key_index_pairs = []
        self.joint_constraint = None
        self.interface = None
        self.update_variables()

    def update_variables(self):
        self.optimized_key_index_pairs.clear()
        constraints = []
        pis = self.m.get_particle_indexes()
        ps = [self.m.get_particle(pi) for pi in pis]
        for fks, f in self.key_constraints:
            for p in ps:
                if all(p.get_is_optimized(fk) for fk in fks):
                    c = f(self.m, p.get_index())
                    constraints.append(c)
                    for fk in fks:
                        self.optimized_key_index_pairs.append(
                            (fk, p.get_index())
                        )
        self.joint_constraint = HMCUtilities.JointConstraint(*constraints)
        self.interface = IMP.hmc.ValueGradientInterface(
            self.m, *list(zip(*self.optimized_key_index_pairs))[:2]
        )

    def shuffle(self, sigma=1):
        ny = HMCUtilities.free_dimension(self.joint_constraint)
        y = np.random.normal(0, 1, size=ny)
        x = HMCUtilities.constrain(self.joint_constraint, y)
        self.interface.set_values(x)
        self.m.update()

    def get_transformation(self):
        return self.joint_constraint

    def get_interface(self):
        return self.interface

    def get_names(self):
        return [
            "{0}_{1}".format(
                self.m.get_particle(pi).get_name(), fk.get_string()
            )
            for fk, pi in self.optimized_key_index_pairs
        ]
