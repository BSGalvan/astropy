# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
Handles the "Console" unit format.
"""


from . import base, core, utils


class Console(base.Base):
    """
    Output-only format for to display pretty formatting at the
    console.

    For example::

      >>> import astropy.units as u
      >>> print(u.Ry.decompose().to_string('console'))  # doctest: +FLOAT_CMP
                       m^2 kg
      2.1798721*10^-18 ------
                        s^2
    """

    _times = "*"
    _line = "-"

    @classmethod
    def _get_unit_name(cls, unit):
        return unit.get_format_name('console')

    @classmethod
    def _format_superscript(cls, number):
        return f'^{number}'

    @classmethod
    def _format_unit_list(cls, units):
        out = []
        for base_, power in units:
            if power == 1:
                out.append(cls._get_unit_name(base_))
            else:
                out.append('{}{}'.format(
                    cls._get_unit_name(base_),
                    cls._format_superscript(
                            utils.format_power(power))))
        return ' '.join(out)

    @classmethod
    def format_exponential_notation(cls, val):
        m, ex = utils.split_mantissa_exponent(val)

        parts = []
        if m:
            parts.append(m)

        if ex:
            parts.append(f"10{cls._format_superscript(ex)}")

        return cls._times.join(parts)

    @classmethod
    def to_string(cls, unit):
        if isinstance(unit, core.CompositeUnit):
            if unit.scale == 1:
                s = ''
            else:
                s = cls.format_exponential_notation(unit.scale)

            if len(unit.bases):
                positives, negatives = utils.get_grouped_by_powers(
                    unit.bases, unit.powers)
                if len(negatives):
                    if len(positives):
                        positives = cls._format_unit_list(positives)
                    else:
                        positives = '1'
                    negatives = cls._format_unit_list(negatives)
                    l = len(s)
                    r = max(len(positives), len(negatives))
                    f = f"{{0:^{l}s}} {{1:^{r}s}}"

                    lines = [
                        f.format('', positives),
                        f.format(s, cls._line * r),
                        f.format('', negatives)
                    ]

                    s = '\n'.join(lines)
                else:
                    positives = cls._format_unit_list(positives)
                    s += positives
        elif isinstance(unit, core.NamedUnit):
            s = cls._get_unit_name(unit)

        return s
