import numpy as np

from .constraint import Constraint
from .constraint import ConstraintType
from .._CythonUtils import _create_velocity_constraint


class CanonicalLinearConstraint(Constraint):

    def get_constraint_type(self):
        return ConstraintType.CanonicalLinear

    def get_constraint_params(self, path, ss):
        """ Return constraint parameter for Canonical Linear Constraints.

        Parameters
        ----------
        path: `Interpolator`
            The geometric path.
        ss: array
            The path discretization.

        Returns
        -------
        a: array
            Shape (N, m). See notes.
        b: array
            Shape (N, m). See notes.
        c: array
            Shape (N, m). See notes.
        F: array
            Shape (N, k, m). See notes.
        b: array
            Shape (N, k,). See notes
        ubound: array, or None
            Shape (N, 2). See notes.
        xbound: array, or None
            Shape (N, 2). See notes.

        Notes
        -----
        The general canonical linear constraint has this form

        .. math::
        a[i] u + b[i] x + c[i] = v,
        F[i] v \leq b[i],
        xbound[i, 0] \leq x \leq xbound[i, 1],
        ubound[i, 0] \leq u \leq ubound[i, 1].
        """
        raise NotImplementedError


class JointVelocityConstraint(CanonicalLinearConstraint):
    """ A Joint Velocity Constraint class.

    Parameters
    ----------
    vlim: array
        Shape (dof, 2). The lower and upper velocity bounds of the j-th joint
        is vlim[j, 0] and vlim[j, 1] respectively.

    """

    def __init__(self, vlim):
        self.vlim = np.array(vlim)
        assert self.vlim.shape[1] == 2, "Wrong input shape."
        self._format_string = "    Velocity limit: \n" + str(self.vlim)

    def get_constraint_params(self, path, ss):
        qs = path.evald(ss)
        # Return resulti from cython version
        _, _, xbound_ = _create_velocity_constraint(qs, self.vlim)
        xbound = np.array(xbound_)
        xbound[:, 0] = xbound_[:, 1]
        xbound[:, 1] = - xbound_[:, 0]
        return None, None, None, None, None, xbound, None