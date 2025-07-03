__doc__ = """ Joint between rods test module """

# System imports
from elastica.joint import (
    FreeJoint,
    HingeJoint,
    FixedJoint,
)
from numpy.testing import assert_allclose
from elastica._rotations import _inv_rotate
from elastica.rod.cosserat_rod import CosseratRod
from elastica.utils import Tolerance
import numpy as np
import pytest
from scipy.spatial.transform import Rotation
from elastica.joint import ExternalContact, SelfContact


# TODO: change tests and made them independent of rod, at least assigin hardcoded values for forces and torques


# seed random number generator
rng = np.random.default_rng(0)


def test_freejoint():
    # Some rod properties. We need them for constructer, they are not used.
    normal = np.array([0.0, 1.0, 0.0])
    direction = np.array([0.0, 0.0, 1.0])
    base_length = 1
    base_radius = 0.2
    density = 1
    nu = 0.1

    # Youngs Modulus [Pa]
    youngs_modulus = 1e6
    # poisson ratio
    poisson_ratio = 0.5
    shear_modulus = youngs_modulus / (poisson_ratio + 1.0)

    # Origin of the rod
    origin1 = np.array([0.0, 0.0, 0.0])
    origin2 = np.array([1.0, 0.0, 0.0])

    # Number of elements
    n = 4

    # create rod classes
    rod1 = CosseratRod.straight_rod(
        n,
        origin1,
        direction,
        normal,
        base_length,
        base_radius,
        density,
        youngs_modulus=youngs_modulus,
        shear_modulus=shear_modulus,
    )
    rod2 = CosseratRod.straight_rod(
        n,
        origin2,
        direction,
        normal,
        base_length,
        base_radius,
        density,
        youngs_modulus=youngs_modulus,
        shear_modulus=shear_modulus,
    )

    # Stiffness between points
    k = 1e8

    # Damping between two points
    nu = 1

    # Rod indexes
    rod1_index = -1
    rod2_index = 0

    # Rod velocity
    v1 = np.array([-1, 0, 0]).reshape(3, 1)
    v2 = v1 * -1

    rod1.velocity_collection = np.tile(v1, (1, n + 1))
    rod2.velocity_collection = np.tile(v2, (1, n + 1))

    # Compute the free joint forces
    distance = (
        rod2.position_collection[..., rod2_index]
        - rod1.position_collection[..., rod1_index]
    )
    elasticforce = k * distance
    relative_vel = (
        rod2.velocity_collection[..., rod2_index]
        - rod1.velocity_collection[..., rod1_index]
    )
    dampingforce = nu * relative_vel
    contactforce = elasticforce + dampingforce

    frjt = FreeJoint(k, nu)
    frjt.apply_forces(rod1, rod1_index, rod2, rod2_index)
    frjt.apply_torques(rod1, rod1_index, rod2, rod2_index)

    assert_allclose(
        rod1.external_forces[..., rod1_index], contactforce, atol=Tolerance.atol()
    )
    assert_allclose(
        rod2.external_forces[..., rod2_index], -1 * contactforce, atol=Tolerance.atol()
    )


def test_hingejoint():
    # Define the rod for testing
    # Some rod properties. We need them for constructer, they are not used.
    normal1 = np.array([0.0, 1.0, 0.0])
    direction = np.array([1.0, 0.0, 0.0])
    normal2 = np.array([0.0, 0.0, 1.0])
    direction2 = np.array([1.0 / np.sqrt(2), 1.0 / np.sqrt(2), 0.0])
    # direction2 = np.array([0.,1.0,0.])
    base_length = 1
    base_radius = 0.2
    density = 1
    nu = 0.1

    # Youngs Modulus [Pa]
    youngs_modulus = 1e6
    # poisson ratio
    poisson_ratio = 0.5
    shear_modulus = youngs_modulus / (poisson_ratio + 1.0)

    # Origin of the rod
    origin1 = np.array([0.0, 0.0, 0.0])
    origin2 = np.array([1.0, 0.0, 0.0])

    # Number of elements
    n = 2

    # create rod classes
    rod1 = CosseratRod.straight_rod(
        n,
        origin1,
        direction,
        normal1,
        base_length,
        base_radius,
        density,
        youngs_modulus=youngs_modulus,
        shear_modulus=shear_modulus,
    )
    rod2 = CosseratRod.straight_rod(
        n,
        origin2,
        direction2,
        normal2,
        base_length,
        base_radius,
        density,
        youngs_modulus=youngs_modulus,
        shear_modulus=shear_modulus,
    )

    # Rod velocity
    v1 = np.array([-1, 0, 0]).reshape(3, 1)
    v2 = v1 * -1

    rod1.velocity_collection = np.tile(v1, (1, n + 1))
    rod2.velocity_collection = np.tile(v2, (1, n + 1))

    # Stiffness between points
    k = 1e8
    kt = 1e6
    # Damping between two points
    nu = 1

    # Rod indexes
    rod1_index = -1
    rod2_index = 0

    # Compute the free joint forces
    distance = (
        rod2.position_collection[..., rod2_index]
        - rod1.position_collection[..., rod1_index]
    )
    elasticforce = k * distance
    relative_vel = (
        rod2.velocity_collection[..., rod2_index]
        - rod1.velocity_collection[..., rod1_index]
    )
    dampingforce = nu * relative_vel
    contactforce = elasticforce + dampingforce

    hgjt = HingeJoint(k, nu, kt, normal1)

    hgjt.apply_forces(rod1, rod1_index, rod2, rod2_index)
    hgjt.apply_torques(rod1, rod1_index, rod2, rod2_index)

    assert_allclose(
        rod1.external_forces[..., rod1_index], contactforce, atol=Tolerance.atol()
    )
    assert_allclose(
        rod2.external_forces[..., rod2_index], -1 * contactforce, atol=Tolerance.atol()
    )

    system_two_tangent = rod2.director_collection[2, :, rod2_index]
    force_direction = np.dot(system_two_tangent, normal1) * normal1
    torque = -kt * np.cross(system_two_tangent, force_direction)

    torque_rod1 = -rod1.director_collection[..., rod1_index] @ torque
    torque_rod2 = rod2.director_collection[..., rod2_index] @ torque

    assert_allclose(
        rod1.external_torques[..., rod1_index], torque_rod1, atol=Tolerance.atol()
    )
    assert_allclose(
        rod2.external_torques[..., rod2_index], torque_rod2, atol=Tolerance.atol()
    )


rest_euler_angles = [
    np.array([0.0, 0.0, 0.0]),
    np.array([np.pi / 2, 0.0, 0.0]),
    np.array([0.0, np.pi / 2, 0.0]),
    np.array([0.0, 0.0, np.pi / 2]),
    2 * np.pi * rng.random(size=3),
]


@pytest.mark.parametrize("rest_euler_angle", rest_euler_angles)
def test_fixedjoint(rest_euler_angle):
    # Define the rod for testing
    # Some rod properties. We need them for constructor, they are not used.
    normal1 = np.array([0.0, 1.0, 0.0])
    direction = np.array([1.0, 0.0, 0.0])
    normal2 = np.array([0.0, 0.0, 1.0])
    direction2 = np.array([1.0 / np.sqrt(2), 1.0 / np.sqrt(2), 0.0])
    # direction2 = np.array([0.,1.0,0.])
    base_length = 1
    base_radius = 0.2
    density = 1
    nu = 0.1

    # Youngs Modulus [Pa]
    youngs_modulus = 1e6
    # poisson ratio
    poisson_ratio = 0.5
    shear_modulus = youngs_modulus / (poisson_ratio + 1.0)

    # Origin of the rod
    origin1 = np.array([0.0, 0.0, 0.0])
    origin2 = np.array([1.0, 0.0, 0.0])

    # Number of elements
    n = 2

    # create rod classes
    rod1 = CosseratRod.straight_rod(
        n,
        origin1,
        direction,
        normal1,
        base_length,
        base_radius,
        density,
        youngs_modulus=youngs_modulus,
        shear_modulus=shear_modulus,
    )
    rod2 = CosseratRod.straight_rod(
        n,
        origin2,
        direction2,
        normal2,
        base_length,
        base_radius,
        density,
        youngs_modulus=youngs_modulus,
        shear_modulus=shear_modulus,
    )

    # Rod velocity
    v1 = np.array([-1, 0, 0]).reshape(3, 1)
    v2 = v1 * -1

    rod1.velocity_collection = np.tile(v1, (1, n + 1))
    rod2.velocity_collection = np.tile(v2, (1, n + 1))

    # Rod angular velocity
    omega1 = 1 / 180 * np.pi * np.array([0, 0, 1]).reshape(3, 1)
    omega2 = -omega1
    rod1.omega_collection = np.tile(omega1, (1, n + 1))
    rod2.omega_collection = np.tile(omega2, (1, n + 1))

    # Positional and rotational stiffness between systems
    k = 1e8
    kt = 1e6
    # Positional and rotational damping between systems
    nu = 1
    nut = 1e2

    # Rod indexes
    rod1_index = -1
    rod2_index = 0

    # Compute the free joint forces
    distance = (
        rod2.position_collection[..., rod2_index]
        - rod1.position_collection[..., rod1_index]
    )
    elasticforce = k * distance
    relative_vel = (
        rod2.velocity_collection[..., rod2_index]
        - rod1.velocity_collection[..., rod1_index]
    )
    dampingforce = nu * relative_vel
    contactforce = elasticforce + dampingforce

    rest_rotation_matrix = Rotation.from_euler(
        "xyz", rest_euler_angle, degrees=False
    ).as_matrix()
    fxjt = FixedJoint(k, nu, kt, nut, rest_rotation_matrix=rest_rotation_matrix)

    fxjt.apply_forces(rod1, rod1_index, rod2, rod2_index)
    fxjt.apply_torques(rod1, rod1_index, rod2, rod2_index)

    assert_allclose(
        rod1.external_forces[..., rod1_index], contactforce, atol=Tolerance.atol()
    )
    assert_allclose(
        rod2.external_forces[..., rod2_index], -1 * contactforce, atol=Tolerance.atol()
    )

    # collect directors of systems one and two
    # note that systems can be either rods or rigid bodies
    rod1_director = rod1.director_collection[..., rod1_index]
    rod2_director = rod2.director_collection[..., rod2_index]

    # rel_rot: C_12 = C_1I @ C_I2
    # C_12 is relative rotation matrix from system 1 to system 2
    # C_1I is the rotation from system 1 to the inertial frame (i.e. the world frame)
    # C_I2 is the rotation from the inertial frame to system 2 frame (inverse of system_two_director)
    rel_rot = rod1_director @ rod2_director.T
    # error_rot: C_22* = C_21 @ C_12*
    # C_22* is rotation matrix from current orientation of system 2 to desired orientation of system 2
    # C_21 is the inverse of C_12, which describes the relative (current) rotation from system 1 to system 2
    # C_12* is the desired rotation between systems one and two, which is saved in the static_rotation attribute
    dev_rot = rel_rot.T @ rest_rotation_matrix

    # compute rotation vectors based on C_22*
    # scipy implementation
    rot_vec = _inv_rotate(np.dstack([np.eye(3), dev_rot.T])).squeeze()

    # rotate rotation vector into inertial frame
    rot_vec_inertial_frame = rod2_director.T @ rot_vec

    # deviation in rotation velocity between system 1 and system 2
    # first convert to inertial frame, then take differences
    dev_omega = (
        rod2_director.T @ rod2.omega_collection[..., rod2_index]
        - rod1_director.T @ rod1.omega_collection[..., rod1_index]
    )

    # we compute the constraining torque using a rotational spring - damper system in the inertial frame
    torque = kt * rot_vec_inertial_frame - nut * dev_omega

    # The opposite torques will be applied to system one and two after rotating the torques into the local frame
    torque_rod1 = -rod1_director @ torque
    torque_rod2 = rod2_director @ torque

    assert_allclose(
        rod1.external_torques[..., rod1_index], torque_rod1, atol=Tolerance.atol()
    )
    assert_allclose(
        rod2.external_torques[..., rod2_index], torque_rod2, atol=Tolerance.atol()
    )


from elastica.joint import (
    _dot_product,
    _norm,
    _clip,
    _out_of_bounds,
    _find_min_dist,
    _aabbs_not_intersecting,
)


@pytest.mark.parametrize("ndim", [2, 3, 5, 10, 20])
def test_dot_product_error_message(ndim):
    vector1 = np.random.randn(ndim)
    vector2 = np.random.randn(ndim)
    error_message = (
        "This function is removed in v0.3.2. Please use\n"
        "elastica.contact_utils._dot_product()\n"
        "instead for find the dot product between a and b."
    )
    with pytest.raises(NotImplementedError) as error_info:
        dot_product = _dot_product(vector1, vector2)
    assert error_info.value.args[0] == error_message


@pytest.mark.parametrize("ndim", [2, 3, 5, 10, 20])
def test_norm_error_message(ndim):
    vec1 = np.random.randn(ndim)
    error_message = (
        "This function is removed in v0.3.2. Please use\n"
        "elastica.contact_utils._norm()\n"
        "instead for finding the norm of a."
    )
    with pytest.raises(NotImplementedError) as error_info:
        norm = _norm(vec1)
    assert error_info.value.args[0] == error_message


@pytest.mark.parametrize(
    "x, result",
    [(0.5, 1), (1.5, 1.5), (2.5, 2)],
)
def test_clip_error_message(x, result):
    low = 1.0
    high = 2.0
    error_message = (
        "This function is removed in v0.3.2. Please use\n"
        "elastica.contact_utils._clip()\n"
        "instead for clipping x."
    )
    with pytest.raises(NotImplementedError) as error_info:
        _clip(x, low, high)
    assert error_info.value.args[0] == error_message


@pytest.mark.parametrize(
    "x, result",
    [(0.5, 1), (1.5, 1.5), (2.5, 2)],
)
def test_out_of_bounds_error_message(x, result):
    low = 1.0
    high = 2.0
    error_message = (
        "This function is removed in v0.3.2. Please use\n"
        "elastica.contact_utils._out_of_bounds()\n"
        "instead for checking if x is out of bounds."
    )
    with pytest.raises(NotImplementedError) as error_info:
        _out_of_bounds(x, low, high)
    assert error_info.value.args[0] == error_message


def test_find_min_dist_error_message():
    x1 = np.array([0, 0, 0])
    e1 = np.array([1, 1, 1])
    x2 = np.array([0, 1, 0])
    e2 = np.array([1, 0, 1])

    error_message = (
        "This function is removed in v0.3.2. Please use\n"
        "elastica.contact_utils._find_min_dist()\n"
        "instead for finding minimum distance between contact points."
    )
    with pytest.raises(NotImplementedError) as error_info:
        (
            min_dist_vec,
            contact_point_of_system2,
            contact_point_of_system1,
        ) = _find_min_dist(x1, e1, x2, e2)
    assert error_info.value.args[0] == error_message


def test_aabbs_not_intersecting_error_message():
    aabb_one = np.array([[0, 0], [0, 0], [0, 0]])
    aabb_two = np.array([[0, 0], [0, 0], [0, 0]])
    error_message = (
        "This function is removed in v0.3.2. Please use\n"
        "elastica.contact_utils._aabbs_not_intersecting()\n"
        "instead for checking aabbs intersection."
    )
    with pytest.raises(NotImplementedError) as error_info:
        _aabbs_not_intersecting(aabb_one, aabb_two)
    assert error_info.value.args[0] == error_message


from elastica.typing import RodBase, RigidBodyBase
from elastica.joint import (
    _prune_using_aabbs_rod_rigid_body,
    _prune_using_aabbs_rod_rod,
    _calculate_contact_forces_rod_rigid_body,
    _calculate_contact_forces_rod_rod,
    _calculate_contact_forces_self_rod,
)


def mock_rod_init(self):
    "Initializing Rod"
    "Details of initialization are given in test_contact_specific_functions.py"

    self.n_elems = 2
    self.position_collection = np.array([[1, 2, 3], [0, 0, 0], [0, 0, 0]])
    self.radius = np.array([1, 1])
    self.lengths = np.array([1, 1])
    self.tangents = np.array([[1.0, 1.0], [0.0, 0.0], [0.0, 0.0]])
    self.internal_forces = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
    self.external_forces = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
    self.velocity_collection = np.array(
        [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    )


def mock_rigid_body_init(self):
    "Initializing Rigid Body"
    "Details of initialization are given in test_contact_specific_functions.py"

    self.n_elems = 1
    self.position_collection = np.array([[0], [0], [0]])
    self.director_collection = np.array(
        [[[1.0], [0.0], [0.0]], [[0.0], [1.0], [0.0]], [[0.0], [0.0], [1.0]]]
    )
    self.radius = np.array([1.0])
    self.length = np.array([2.0])
    self.external_forces = np.array([[0.0], [0.0], [0.0]])
    self.external_torques = np.array([[0.0], [0.0], [0.0]])
    self.velocity_collection = np.array([[0.0], [0.0], [0.0]])


MockRod = type("MockRod", (RodBase,), {"__init__": mock_rod_init})

MockRigidBody = type(
    "MockRigidBody", (RigidBodyBase,), {"__init__": mock_rigid_body_init}
)


def test_prune_using_aabbs_rod_rigid_body_error_message():
    rod = MockRod()
    cylinder = MockRigidBody()
    error_message = (
        "This function is removed in v0.3.2. Please use\n"
        "elastica.contact_utils._prune_using_aabbs_rod_cylinder()\n"
        "instead for checking rod cylinder intersection."
    )
    with pytest.raises(NotImplementedError) as error_info:
        _prune_using_aabbs_rod_rigid_body(
            rod.position_collection,
            rod.radius,
            rod.lengths,
            cylinder.position_collection,
            cylinder.director_collection,
            cylinder.radius,
            cylinder.length,
        )
    assert error_info.value.args[0] == error_message


def test_prune_using_aabbs_rod_rod_error_message():
    rod_one = MockRod()
    rod_two = MockRod()
    error_message = (
        "This function is removed in v0.3.2. Please use\n"
        "elastica.contact_utils._prune_using_aabbs_rod_rod()\n"
        "instead for checking rod rod intersection."
    )
    with pytest.raises(NotImplementedError) as error_info:
        _prune_using_aabbs_rod_rod(
            rod_one.position_collection,
            rod_one.radius,
            rod_one.lengths,
            rod_two.position_collection,
            rod_two.radius,
            rod_two.lengths,
        )
    assert error_info.value.args[0] == error_message


def test_calculate_contact_forces_rod_rigid_body_error_message():
    "initializing rod parameters"
    rod = MockRod()
    rod_element_position = 0.5 * (
        rod.position_collection[..., 1:] + rod.position_collection[..., :-1]
    )

    "initializing cylinder parameters"
    cylinder = MockRigidBody()
    x_cyl = (
        cylinder.position_collection[..., 0]
        - 0.5 * cylinder.length * cylinder.director_collection[2, :, 0]
    )

    "initializing constants"
    """
        Setting contact_k = 1 and other parameters to 0,
        so the net forces becomes a function of contact forces only.
        """
    k = 1.0
    nu = 0
    velocity_damping_coefficient = 0
    friction_coefficient = 0

    error_message = (
        "This function is removed in v0.3.2. Please use\n"
        "elastica._contact_functions._calculate_contact_forces_rod_cylinder()\n"
        "instead for calculating rod cylinder contact forces."
    )

    "Function call"
    with pytest.raises(NotImplementedError) as error_info:
        _calculate_contact_forces_rod_rigid_body(
            rod_element_position,
            rod.lengths * rod.tangents,
            cylinder.position_collection[..., 0],
            x_cyl,
            cylinder.length * cylinder.director_collection[2, :, 0],
            rod.radius + cylinder.radius,
            rod.lengths + cylinder.length,
            rod.internal_forces,
            rod.external_forces,
            cylinder.external_forces,
            cylinder.external_torques,
            cylinder.director_collection[:, :, 0],
            rod.velocity_collection,
            cylinder.velocity_collection,
            k,
            nu,
            velocity_damping_coefficient,
            friction_coefficient,
        )
    assert error_info.value.args[0] == error_message


def test_calculate_contact_forces_rod_rod_error_message():
    rod_one = MockRod()
    rod_two = MockRod()
    """Placing rod two such that its first element just touches the last element of rod one."""
    rod_two.position_collection = np.array([[4, 5, 6], [0, 0, 0], [0, 0, 0]])

    "initializing constants"
    """
    Setting contact_k = 1 and nu to 0,
    so the net forces becomes a function of contact forces only.
    """
    k = 1.0
    nu = 0.0

    error_message = (
        "This function is removed in v0.3.2. Please use\n"
        "elastica._contact_functions._calculate_contact_forces_rod_rod()\n"
        "instead for calculating rod rod contact forces."
    )

    "Function call"
    with pytest.raises(NotImplementedError) as error_info:
        _calculate_contact_forces_rod_rod(
            rod_one.position_collection[..., :-1],
            rod_one.radius,
            rod_one.lengths,
            rod_one.tangents,
            rod_one.velocity_collection,
            rod_one.internal_forces,
            rod_one.external_forces,
            rod_two.position_collection[..., :-1],
            rod_two.radius,
            rod_two.lengths,
            rod_two.tangents,
            rod_two.velocity_collection,
            rod_two.internal_forces,
            rod_two.external_forces,
            k,
            nu,
        )
    assert error_info.value.args[0] == error_message


def test_calculate_contact_forces_self_rod_error_message():
    "Function to test the calculate contact forces self rod function"

    "Testing function with handcrafted/calculated values"

    rod = MockRod()

    "initializing constants"
    k = 1.0
    nu = 1.0

    error_message = (
        "This function is removed in v0.3.2. Please use\n"
        "elastica._contact_functions._calculate_contact_forces_self_rod()\n"
        "instead for calculating rod self-contact forces."
    )

    "Function call"
    with pytest.raises(NotImplementedError) as error_info:
        _calculate_contact_forces_self_rod(
            rod.position_collection[..., :-1],
            rod.radius,
            rod.lengths,
            rod.tangents,
            rod.velocity_collection,
            rod.external_forces,
            k,
            nu,
        )
    assert error_info.value.args[0] == error_message


class TestExternalContact:
    def test_external_contact_rod_rigid_body_with_collision_with_k_without_nu_and_friction(
        self,
    ):
        "Testing External Contact wrapper with Collision with analytical verified values"

        mock_rod = MockRod()
        mock_rigid_body = MockRigidBody()
        ext_contact = ExternalContact(k=1.0, nu=0.0)
        ext_contact.apply_forces(mock_rod, 0, mock_rigid_body, 1)

        """Details and reasoning about the values are given in 'test_contact_specific_functions.py/test_claculate_contact_forces_rod_rigid_body()'"""
        assert_allclose(
            mock_rod.external_forces,
            np.array([[0.166666, 0.333333, 0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]),
            atol=1e-6,
        )

        assert_allclose(
            mock_rigid_body.external_forces, np.array([[-0.5], [0.0], [0.0]]), atol=1e-6
        )

        assert_allclose(
            mock_rigid_body.external_torques, np.array([[0.0], [0.0], [0.0]]), atol=1e-6
        )

    def test_external_contact_rod_rigid_body_with_collision_with_nu_without_k_and_friction(
        self,
    ):
        "Testing External Contact wrapper with Collision with analytical verified values"

        mock_rod = MockRod()
        "Moving rod towards the cylinder with a velocity of -1 in x-axis"
        mock_rod.velocity_collection = np.array([[-1, 0, 0], [-1, 0, 0], [-1, 0, 0]])
        mock_rigid_body = MockRigidBody()
        "Moving cylinder towards the rod with a velocity of 1 in x-axis"
        mock_rigid_body.velocity_collection = np.array([[1], [0], [0]])
        ext_contact = ExternalContact(k=0.0, nu=1.0)
        ext_contact.apply_forces(mock_rod, 0, mock_rigid_body, 1)

        """Details and reasoning about the values are given in 'test_contact_specific_functions.py/test_claculate_contact_forces_rod_rigid_body()'"""
        assert_allclose(
            mock_rod.external_forces,
            np.array([[0.5, 1, 0], [0, 0, 0], [0, 0, 0]]),
            atol=1e-6,
        )

        assert_allclose(
            mock_rigid_body.external_forces, np.array([[-1.5], [0], [0]]), atol=1e-6
        )

        assert_allclose(
            mock_rigid_body.external_torques, np.array([[0.0], [0.0], [0.0]]), atol=1e-6
        )

    def test_external_contact_rod_rigid_body_with_collision_with_k_and_nu_without_friction(
        self,
    ):
        "Testing External Contact wrapper with Collision with analytical verified values"

        mock_rod = MockRod()
        "Moving rod towards the cylinder with a velocity of -1 in x-axis"
        mock_rod.velocity_collection = np.array([[-1, 0, 0], [-1, 0, 0], [-1, 0, 0]])
        mock_rigid_body = MockRigidBody()
        "Moving cylinder towards the rod with a velocity of 1 in x-axis"
        mock_rigid_body.velocity_collection = np.array([[1], [0], [0]])
        ext_contact = ExternalContact(k=1.0, nu=1.0)
        ext_contact.apply_forces(mock_rod, 0, mock_rigid_body, 1)

        """Details and reasoning about the values are given in 'test_contact_specific_functions.py/test_claculate_contact_forces_rod_rigid_body()'"""
        assert_allclose(
            mock_rod.external_forces,
            np.array([[0.666666, 1.333333, 0], [0, 0, 0], [0, 0, 0]]),
            atol=1e-6,
        )

        assert_allclose(
            mock_rigid_body.external_forces, np.array([[-2], [0], [0]]), atol=1e-6
        )

        assert_allclose(
            mock_rigid_body.external_torques, np.array([[0.0], [0.0], [0.0]]), atol=1e-6
        )

    def test_external_contact_rod_rigid_body_with_collision_with_k_and_nu_and_friction(
        self,
    ):
        "Testing External Contact wrapper with Collision with analytical verified values"

        mock_rod = MockRod()
        "Moving rod towards the cylinder with a velocity of -1 in x-axis"
        mock_rod.velocity_collection = np.array([[-1, 0, 0], [-1, 0, 0], [-1, 0, 0]])
        mock_rigid_body = MockRigidBody()
        "Moving cylinder towards the rod with a velocity of 1 in x-axis"
        mock_rigid_body.velocity_collection = np.array([[1], [0], [0]])
        ext_contact = ExternalContact(
            k=1.0, nu=1.0, velocity_damping_coefficient=0.1, friction_coefficient=0.1
        )
        ext_contact.apply_forces(mock_rod, 0, mock_rigid_body, 1)

        """Details and reasoning about the values are given in 'test_contact_specific_functions.py/test_claculate_contact_forces_rod_rigid_body()'"""
        assert_allclose(
            mock_rod.external_forces,
            np.array(
                [
                    [0.666666, 1.333333, 0],
                    [0.033333, 0.066666, 0],
                    [0.033333, 0.066666, 0],
                ]
            ),
            atol=1e-6,
        )

        assert_allclose(
            mock_rigid_body.external_forces, np.array([[-2], [-0.1], [-0.1]]), atol=1e-6
        )

        assert_allclose(
            mock_rigid_body.external_torques, np.array([[0.0], [0.0], [0.0]]), atol=1e-6
        )

    def test_external_contact_rod_rigid_body_without_collision(self):
        "Testing External Contact wrapper without Collision with analytical verified values"

        mock_rod = MockRod()
        mock_rigid_body = MockRigidBody()
        ext_contact = ExternalContact(k=1.0, nu=0.5)

        """Setting rigid body position such that there is no collision"""
        mock_rigid_body.position_collection = np.array([[400], [500], [600]])
        mock_rod_external_forces_before_execution = mock_rod.external_forces.copy()
        mock_rigid_body_external_forces_before_execution = (
            mock_rigid_body.external_forces.copy()
        )
        mock_rigid_body_external_torques_before_execution = (
            mock_rigid_body.external_torques.copy()
        )
        ext_contact.apply_forces(mock_rod, 0, mock_rigid_body, 1)

        assert_allclose(
            mock_rod.external_forces, mock_rod_external_forces_before_execution
        )
        assert_allclose(
            mock_rigid_body.external_forces,
            mock_rigid_body_external_forces_before_execution,
        )
        assert_allclose(
            mock_rigid_body.external_torques,
            mock_rigid_body_external_torques_before_execution,
        )

    def test_external_contact_with_two_rods_with_collision_with_k_without_nu(self):
        "Testing External Contact wrapper with two rods with analytical verified values"
        "Test values have been copied from 'test_contact_specific_functions.py/test_calculate_contact_forces_rod_rod()'"

        mock_rod_one = MockRod()
        mock_rod_two = MockRod()
        mock_rod_two.position_collection = np.array([[4, 5, 6], [0, 0, 0], [0, 0, 0]])
        ext_contact = ExternalContact(k=1.0, nu=0.0)
        ext_contact.apply_forces(mock_rod_one, 0, mock_rod_two, 0)

        assert_allclose(
            mock_rod_one.external_forces,
            np.array([[0, -0.666666, -0.333333], [0, 0, 0], [0, 0, 0]]),
            atol=1e-6,
        )
        assert_allclose(
            mock_rod_two.external_forces,
            np.array([[0.333333, 0.666666, 0], [0, 0, 0], [0, 0, 0]]),
            atol=1e-6,
        )

    def test_external_contact_with_two_rods_with_collision_without_k_with_nu(self):
        "Testing External Contact wrapper with two rods with analytical verified values"
        "Test values have been copied from 'test_contact_specific_functions.py/test_calculate_contact_forces_rod_rod()'"

        mock_rod_one = MockRod()
        mock_rod_two = MockRod()

        """Moving the rods towards each other with a velocity of 1 along the x-axis."""
        mock_rod_one.velocity_collection = np.array([[1, 0, 0], [1, 0, 0], [1, 0, 0]])
        mock_rod_two.velocity_collection = np.array(
            [[-1, 0, 0], [-1, 0, 0], [-1, 0, 0]]
        )
        mock_rod_two.position_collection = np.array([[4, 5, 6], [0, 0, 0], [0, 0, 0]])
        ext_contact = ExternalContact(k=0.0, nu=1.0)
        ext_contact.apply_forces(mock_rod_one, 0, mock_rod_two, 0)

        assert_allclose(
            mock_rod_one.external_forces,
            np.array(
                [[0, -0.333333, -0.166666], [0, 0, 0], [0, 0, 0]],
            ),
            atol=1e-6,
        )
        assert_allclose(
            mock_rod_two.external_forces,
            np.array([[0.166666, 0.333333, 0], [0, 0, 0], [0, 0, 0]]),
            atol=1e-6,
        )

    def test_external_contact_with_two_rods_with_collision_with_k_and_nu(self):
        "Testing External Contact wrapper with two rods with analytical verified values"
        "Test values have been copied from 'test_contact_specific_functions.py/test_calculate_contact_forces_rod_rod()'"

        mock_rod_one = MockRod()
        mock_rod_two = MockRod()

        """Moving the rods towards each other with a velocity of 1 along the x-axis."""
        mock_rod_one.velocity_collection = np.array([[1, 0, 0], [1, 0, 0], [1, 0, 0]])
        mock_rod_two.velocity_collection = np.array(
            [[-1, 0, 0], [-1, 0, 0], [-1, 0, 0]]
        )
        mock_rod_two.position_collection = np.array([[4, 5, 6], [0, 0, 0], [0, 0, 0]])
        ext_contact = ExternalContact(k=1.0, nu=1.0)
        ext_contact.apply_forces(mock_rod_one, 0, mock_rod_two, 0)

        assert_allclose(
            mock_rod_one.external_forces,
            np.array(
                [[0, -1, -0.5], [0, 0, 0], [0, 0, 0]],
            ),
            atol=1e-6,
        )
        assert_allclose(
            mock_rod_two.external_forces,
            np.array([[0.5, 1, 0], [0, 0, 0], [0, 0, 0]]),
            atol=1e-6,
        )

    def test_external_contact_with_two_rods_without_collision(self):
        "Testing External Contact wrapper with two rods with analytical verified values"

        mock_rod_one = MockRod()
        mock_rod_two = MockRod()

        "Setting rod two position such that there is no collision"
        mock_rod_two.position_collection = np.array(
            [[100, 101, 102], [0, 0, 0], [0, 0, 0]]
        )
        ext_contact = ExternalContact(k=1.0, nu=1.0)
        mock_rod_one_external_forces_before_execution = (
            mock_rod_one.external_forces.copy()
        )
        mock_rod_two_external_forces_before_execution = (
            mock_rod_two.external_forces.copy()
        )
        ext_contact.apply_forces(mock_rod_one, 0, mock_rod_two, 0)

        assert_allclose(
            mock_rod_one.external_forces, mock_rod_one_external_forces_before_execution
        )
        assert_allclose(
            mock_rod_two.external_forces, mock_rod_two_external_forces_before_execution
        )


class TestSelfContact:
    def test_self_contact_with_rod_self_collision(self):
        "Testing Self Contact wrapper rod self collision with analytical verified values"

        mock_rod = MockRod()

        "Test values have been copied from 'test_contact_specific_functions.py/test_calculate_contact_forces_self_rod()'"
        mock_rod.n_elems = 3
        mock_rod.position_collection = np.array(
            [[1, 4, 4, 1], [0, 0, 1, 1], [0, 0, 0, 0]]
        )
        mock_rod.radius = np.array([1, 1, 1])
        mock_rod.lengths = np.array([3, 1, 3])
        mock_rod.tangents = np.array(
            [[1.0, 0.0, -1.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]]
        )
        mock_rod.velocity_collection = np.array(
            [[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]]
        )
        mock_rod.internal_forces = np.array(
            [[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]]
        )
        mock_rod.external_forces = np.array(
            [[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]]
        )
        sel_contact = SelfContact(k=1.0, nu=0.0)
        sel_contact.apply_forces(mock_rod, 0, mock_rod, 0)

        assert_allclose(
            mock_rod.external_forces,
            np.array(
                [[0, 0, 0, 0], [-0.333333, -0.666666, 0.666666, 0.333333], [0, 0, 0, 0]]
            ),
            atol=1e-6,
        )

    def test_self_contact_with_rod_no_self_collision(self):
        "Testing Self Contact wrapper rod no self collision with analytical verified values"

        mock_rod = MockRod()

        "the initially set rod does not have self collision"
        mock_rod_external_forces_before_execution = mock_rod.external_forces.copy()
        sel_contact = SelfContact(k=1.0, nu=1.0)
        sel_contact.apply_forces(mock_rod, 0, mock_rod, 0)

        assert_allclose(
            mock_rod.external_forces, mock_rod_external_forces_before_execution
        )
