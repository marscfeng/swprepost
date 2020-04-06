# This file is part of swipp, a Python package for surface-wave
# inversion pre- and post-processing.
# Copyright (C) 2019-2020 Joseph P. Vantassel (jvantassel@utexas.edu)
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https: //www.gnu.org/licenses/>.

"""DispersionSuite class definition."""

import logging

from swipp import DispersionSet, Suite, regex

logger = logging.getLogger(name=__name__)

__all__ = ["DispersionSuite"]

class DispersionSuite(Suite):
    """Container for instantiated `DispersionSet` objects.

    Attributes
    ----------
    sets : list
        Container for instantiated `DispersionSet` objects.

    """
    @staticmethod
    def check_input(curveset, set_type):
        """Check inputs comply with the required format.

        Specifically:
        1. `curveset` is of type `set_type`.

        """
        if not isinstance(curveset, set_type):
            msg = f"Must be instance of {type(set_type)}, not {type(curveset)}."
            raise TypeError(msg)

    def __init__(self, dispersionset):
        """Initialize a `DispersionSuite`, from a `DispersionSet`.

        Parameters
        ----------
        dispersionset : DispersionSet
            Initialized `DispersionSet` object.

        Returns
        -------
        DispersionSuite
            Instantiated `DispersionSuite` object.

        Raises
        ------
        TypeError
            If `dispersionset` is not of type `DispersionSet`.

        """
        self.check_input(dispersionset, DispersionSet)
        self.sets = [dispersionset]

    def append(self, dispersionset):
        """Append `DispersionSet` object to `DispersionSuite`.

        Parameters
        ----------
            Refer to :meth: `__init__ <DispersionSuite.__init__>`.

        Returns
        -------
        None
            Updates the attribute `sets`.

        Raises
        ------
        TypeError
            If `dispersionset` is not of type `DispersionSet`.

        """
        self.check_input(dispersionset, DispersionSet)
        self.sets.append(dispersionset)

    @property
    def size(self):
        return len(self.sets)

    @property
    def ids(self):
        """Return the ids corresponding to `sets`."""
        return [cset.identifer for cset in self.sets]

    @property
    def misfits(self):
        """Return the misfits corresponding to `sets`."""
        return [cset.misfit for cset in self.sets]

    @classmethod
    def from_geopsy(cls, fname, nsets="all", nrayleigh="all", nlove="all"):
        """Instantiate from a text file following the Geopsy format.

        Parameters
        ----------
        fname : str
            Name of file, may be a relative or full path.
        nsets : int, optional
            Number of sets to extract, default is "all" so all 
            available sets will be extracted.
        nrayleigh, nlove : int, optional
            Number of Rayleigh and Love modes respectively, default
            is "all" so all available modes will be extracted.

        Returns
        -------
        DispersionSuite
            Instantiated `DispersionSuite` object.

        """
        with open(fname, "r") as f:
            lines = f.read()

        dc_sets = []
        previous_id, previous_misfit = "start", "0"
        rayleigh, love = None, None
        model_count = 0
        for model_info in regex.dcset.finditer(lines):
            identifier, misfit, wave_type, data = model_info.groups()

            if identifier != previous_id and previous_id != "start":
                dc_sets.append(cls._dcset()(previous_id,
                                            float(previous_misfit),
                                            rayleigh=rayleigh, love=love))
                model_count += 1
                rayleigh, love = None, None

            if wave_type == "Rayleigh":
                rayleigh = cls._dcset()._parse_dcs(data, nmodes=nrayleigh)
            elif wave_type == "Love":
                love = cls._dcset()._parse_dcs(data, nmodes=nlove)
            else:
                raise NotImplementedError

            previous_id = identifier
            previous_misfit = misfit

            if model_count + 1 == nsets:
                break

        dc_sets.append(cls._dcset()(previous_id,
                                    float(previous_misfit),
                                    rayleigh=rayleigh, love=love))
        return cls.from_list(dc_sets)

    @classmethod
    def _dcset(cls):
        """Convenient `DispersionSet` to allow subclassing."""
        return DispersionSet

    @classmethod
    def from_list(cls, dc_sets):
        """Instantiate from a list of `DispersionSet` objects.

        Parameters
        ----------
        dc_sets : list
            List of `DispersionSet` objects.

        Returns
        -------
        DipsersionSuite
            Instatiated `DispersionSuite` object.

        """
        obj = cls(dc_sets[0])
        if len(dc_sets) > 1:
            for dc_set in dc_sets[1:]:
                obj.append(dc_set)
        return obj
    
    def write_to_txt(self, fname, nbest="all"):
        """Write to text file, following the Geopsy format.

        Parameters
        ----------
        fname : str
            Name of file, may be a relative or the full path.
        nbest : {int, 'all'}, optional
            Number of best models to write to file, default is 'all'
            indicating all models will be written.

        Returns
        -------
        None
            Writes file to disk.

        """
        nbest = self._handle_nbest(nbest)
        with open(fname, "w") as f:
            f.write("# File written by swipp")
            for cid, cmf, cit in zip(self.ids[:nbest], self.misfits[:nbest], self._items[:nbest]):
                cit.write_set(f, cid, cmf)

    def __eq__(self, other):
        """Define when two DispersionCurve objects are equal."""
        if self.size != other.size:
            return False
        for my, ur in zip(self.sets, other.sets):
            if my != ur:
                return False
        return True

    def __getitem__(self, slce):
        """Define slicing behavior"""
        return self.sets[slce]

    def __str__(self):
        """Human-readable representation of the object."""
        return f"DispersionSuite with {len(self.sets)} DispersionSets."
