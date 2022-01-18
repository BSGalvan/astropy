# Licensed under a 3-clause BSD style license - see LICENSE.rst

# STDLIB
import pathlib
import sys
from types import MappingProxyType

# LOCAL
from astropy import units as u
from astropy.utils.decorators import deprecated
from astropy.utils.data import get_pkg_data_path
from astropy.utils.state import ScienceState

from . import parameters
from .core import _COSMOLOGY_CLASSES, Cosmology

__all__ = ["default_cosmology"]

__doctest_requires__ = {"*": ["scipy"]}


# Pre-defined cosmologies. This loops over the data directory and creates a
# corresponding cosmology instance.
data_dir = pathlib.Path(get_pkg_data_path("cosmology", "data", package="astropy"))
for path in data_dir.glob("*.ecsv"):
    cosmo = Cosmology.read(path, format="ascii.ecsv")
    cosmo.__doc__ = (f"{path.stem} instance of {cosmo.__class__.__qualname__} "
                     f"cosmology\n(from {cosmo.meta['reference']})")

    # Put in this namespace
    setattr(sys.modules[__name__], path.stem, cosmo)
    __all__.append(path.stem)

    # And add to parameters.py
    m = cosmo.to_format("mapping")
    m["cosmology"] = m["cosmology"].__qualname__
    m.update(m.pop("meta"))
    setattr(parameters, path.stem, MappingProxyType(m))
    parameters.available += (path.stem, )

del data_dir, path, cosmo, m  # clean the namespace
parameters.available = tuple(sorted(parameters.available))

#########################################################################
# The science state below contains the current cosmology.
#########################################################################


class default_cosmology(ScienceState):
    """The default cosmology to use.

    To change it::

        >>> from astropy.cosmology import default_cosmology, WMAP7
        >>> with default_cosmology.set(WMAP7):
        ...     # WMAP7 cosmology in effect
        ...     pass

    Or, you may use a string::

        >>> with default_cosmology.set('WMAP7'):
        ...     # WMAP7 cosmology in effect
        ...     pass

    To get the default cosmology:

        >>> default_cosmology.get()
        FlatLambdaCDM(name="Planck18", H0=67.66 km / (Mpc s), Om0=0.30966, ...

    To get a specific cosmology:

        >>> default_cosmology.get("Planck13")
        FlatLambdaCDM(name="Planck13", H0=67.77 km / (Mpc s), Om0=0.30712, ...
    """

    _default_value = "Planck18"
    _value = "Planck18"

    @classmethod
    def get(cls, key=None):
        """Get the science state value of ``key``.

        Parameters
        ----------
        key : str or None
            The built-in |Cosmology| realization to retrieve.
            If None (default) get the current value.

        Returns
        -------
        `astropy.cosmology.Cosmology` or None
            `None` only if ``key`` is "no_default"

        Raises
        ------
        TypeError
            If ``key`` is not a str, |Cosmology|, or None.
        ValueError
            If ``key`` is a str, but not for a built-in Cosmology

        Examples
        --------
        To get the default cosmology:

        >>> default_cosmology.get()
        FlatLambdaCDM(name="Planck18", H0=67.66 km / (Mpc s), Om0=0.30966, ...

        To get a specific cosmology:

        >>> default_cosmology.get("Planck13")
        FlatLambdaCDM(name="Planck13", H0=67.77 km / (Mpc s), Om0=0.30712, ...
        """
        if key is None:
            key = cls._value

        if isinstance(key, str):
            # special-case one string
            if key == "no_default":
                return None
            # all other options should be built-in realizations
            try:
                value = getattr(sys.modules[__name__], key)
            except AttributeError:
                raise ValueError(f"Unknown cosmology {key!r}. "
                                 f"Valid cosmologies:\n{parameters.available}")
        elif isinstance(key, Cosmology):
            value = key
        else:
            raise TypeError("'key' must be must be None, a string, "
                            f"or Cosmology instance, not {type(key)}.")

        # validate value to `Cosmology`, if not already
        return cls.validate(value)

    @deprecated("5.0", alternative="get")
    @classmethod
    def get_cosmology_from_string(cls, arg):
        """Return a cosmology instance from a string."""
        return cls.get(arg)

    @classmethod
    def validate(cls, value):
        """Return a Cosmology given a value.

        Parameters
        ----------
        value : None, str, or `~astropy.cosmology.Cosmology`

        Returns
        -------
        `~astropy.cosmology.Cosmology` instance

        Raises
        ------
        TypeError
            If ``value`` is not a string or |Cosmology|.
        """
        # None -> default
        if value is None:
            value = cls._default_value

        # Parse to Cosmology. Error if cannot.
        if isinstance(value, str):
            value = cls.get(value)
        elif not isinstance(value, Cosmology):
            raise TypeError("default_cosmology must be a string or Cosmology instance, "
                            f"not {value}.")

        return value
