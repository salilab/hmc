import numpy as np

import IMP.isd
import IMP.core
import IMP.hmc

from .julia import HMCUtilities


class TransformationBuilder(object):

    """
    Check if variables are set up and create the necessary transformations.
    """

    def build(self, m, pi):
        """Build the transformation.

        If the transformation applies, return a list of
        `(FloatKey, ParticleIndex)` tuples for optimized attributes to which
        the transformation is applied, and an `HMCUtilities.VariableConstraint`
        transformation object.
        """
        raise NotImplementedError


class UnconstrainedTransformationBuilder(TransformationBuilder):
    def __init__(self, fks):
        self.fks = fks

    def build(self, m, pi):
        p = m.get_particle(pi)
        kp_pairs = []
        for fk in self.fks:
            if m.get_has_attribute(fk, pi) and p.get_is_optimized(fk):
                kp_pairs.append((fk, pi))
        n = len(kp_pairs)
        if n > 0:
            return kp_pairs, HMCUtilities.IdentityConstraint(n)
        else:
            return


class UnitVectorTransformationBuilder(TransformationBuilder):
    def __init__(self, fks):
        self.fks = fks

    def build(self, m, pi):
        p = m.get_particle(pi)
        kp_pairs = []
        for fk in self.fks:
            if not (m.get_has_attribute(fk, pi) and p.get_is_optimized(fk)):
                return
            kp_pairs.append((fk, pi))
        n = len(kp_pairs)
        return kp_pairs, HMCUtilities.UnitVectorConstraint(n)


class UnitVectorScaledTransformationBuilder(TransformationBuilder):
    def __init__(self, fks):
        self.fks = fks

    def compute_scaling(self, m, pi):
        if self.fks[0] in (
            IMP.FloatKey("rigid_body_quaternion_0"),
            IMP.FloatKey("rigid_body_local_quaternion_0")
        ): # rigid body
            rb = IMP.core.RigidBody(m, pi)
            center = rb.get_coordinates()
            vs = np.array([list(IMP.core.XYZ(p).get_coordinates() - center) for p in rb.get_rigid_members()])
            sigma = np.std(vs, ddof = 0)
            # upper bound on the scaling from pulling back the Euclidean metric on the rigid body members
            # to the quaternion of the rigid body
            # metric is equivalent to 4G, where G is the moment of inertia tensor
            # bound corresponds to worst-case scenario of co-linear members
            # TODO: recurse through nested rigid bodies
            r = 2 * sigma
        else: # fallback
            r = 1.0
        return r

    def build(self, m, pi):
        p = m.get_particle(pi)
        kp_pairs = []
        for fk in self.fks:
            if not (m.get_has_attribute(fk, pi) and p.get_is_optimized(fk)):
                return
            kp_pairs.append((fk, pi))
        n = len(kp_pairs)
        r = self.compute_scaling(m, pi)
        return kp_pairs, HMCUtilities.UnitVectorScaledConstraint(n, r)


class WeightTransformationBuilder(TransformationBuilder):
    def build(self, m, pi):
        if not IMP.isd.Weight.get_is_setup(m, pi):
            return
        w = IMP.isd.Weight(m, pi)
        if not w.get_weights_are_optimized():
            return
        kp_pairs = [(fk, pi) for fk in w.get_weight_keys()]
        n = len(kp_pairs)
        return kp_pairs, HMCUtilities.UnitSimplexConstraint(n)


class RadiusTransformationBuilder(TransformationBuilder):
    def build(self, m, pi):
        p = m.get_particle(pi)
        fk = IMP.core.XYZR.get_radius_key()
        if not (m.get_has_attribute(fk, pi) and p.get_is_optimized(fk)):
            return
        return [(fk, pi)], HMCUtilities.LowerBoundedConstraint(0.0)


class NuisanceTransformationBuilder(TransformationBuilder):
    def build(self, m, pi):
        p = m.get_particle(pi)
        fk = IMP.isd.Nuisance.get_nuisance_key()
        if not (m.get_has_attribute(fk, pi) and p.get_is_optimized(fk)):
            return
        n = IMP.isd.Nuisance(m, pi)
        return (
            [(fk, pi)],
            HMCUtilities.TransformConstraint(n.get_lower(), n.get_upper()),
        )


class BoundingBoxTransformationBuilder(TransformationBuilder):
    
    """
    Transformation that smoothly constrains the variables within the provided bounding box
    """

    def __init__(self, fks, bbox):
        self.bbox = bbox
        self.fks = fks

    def build(self, m, pi):
        lb = self.bbox.get_corner(0)
        ub = self.bbox.get_corner(1)
        p = m.get_particle(pi)
        kp_pairs = []
        constraints = []
        for i, fk in enumerate(self.fks):
            if not (m.get_has_attribute(fk, pi) and p.get_is_optimized(fk)):
                return
            c = HMCUtilities.BoundedConstraint(lb[i], ub[i])
            constraints.append(c)
            kp_pairs.append((fk, pi))
        joint_constraint = HMCUtilities.JointConstraint(*constraints)
        return kp_pairs, joint_constraint


class OptimizedVariables(object):

    transform_builders = [
        UnconstrainedTransformationBuilder(
            # XYZ/RigidBody coordinates
            list(IMP.core.XYZ.get_xyz_keys())
            # NonRigidMember local coordinates
            + [IMP.FloatKey(4), IMP.FloatKey(5), IMP.FloatKey(6)]
        ),
        # XYZR radius
        RadiusTransformationBuilder(),
        # RigidBody quaternion
        UnitVectorScaledTransformationBuilder(
            [
                IMP.FloatKey("rigid_body_quaternion_{0}".format(i))
                for i in range(4)
            ]
        ),
        # NonRigidMember local quaternion
        UnitVectorScaledTransformationBuilder(
            [
                IMP.FloatKey("rigid_body_local_quaternion_{0}".format(i))
                for i in range(4)
            ]
        ),
        # Direction
        UnitVectorTransformationBuilder(
            [IMP.core.Direction.get_direction_key(i) for i in range(3)]
        ),
        # Nuisance
        NuisanceTransformationBuilder(),
        WeightTransformationBuilder(),
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
        for tb in self.transform_builders:
            for pi in pis:
                result = tb.build(self.m, pi)
                if result is None:
                    continue
                kp_pairs, c = result
                self.optimized_key_index_pairs.extend(kp_pairs)
                constraints.append(c)

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
