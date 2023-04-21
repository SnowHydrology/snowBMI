"""Temperature index snow model"""

import numpy as np
import yaml


def solve_snow(temp, precip, doy, swe, melt, rain_snow, rs_thresh, snow_thresh_max, rain_thresh_min,
               ddf_max, ddf_min, tair_melt_thresh):
    """Run the snow model for one time step to update the states and fluxes.

    Parameters
    ----------
    temp : ndarray
        Air temperature (input from forcing data).
    precip : ndarray
        Precipitation (input from forcing data).
    doy : int
        Day of year (incremented from model start)
    swe: ndarray
        Snow water equivalent (state that gets updated).
    melt: ndarray
        Snowmelt + rainfall per time step (flux that gets updated).
    rain_snow: int
        Rain-snow partitioning method (parameter).
    rs_thresh: float
        Rain-snow air temperature threshold (parameter, for rain_snow == 1).
    snow_thresh_max: float
        Maximum air temperature threshold for snow (parameter, for rain_snow == 2).
    rain_thresh_min: float
        Minimum air temperature threshold for rain (parameter, for rain_snow == 2).
    ddf_max: float
        Maximum annual degree day factor (parameter).
    ddf_min: float
        Minimum annual degree day factor (parameter).
    tair_melt_thresh: float
        Air temperature threshold above which snowmelt can occur (parameter).

    Returns
    -------
    TODO
    result : ndarray
        The temperatures after time *time_step*.

    Examples
    --------
    TODO
    """

    # Assign precipitation phase
    # 0 = snow, 1 = rain
    if rain_snow == 1:
        if temp <= rs_thresh:
            ppt_phase = 0
        else:
            ppt_phase = 1
    elif rain_snow == 2:
        if temp <= snow_thresh_max:
            ppt_phase = 0
        elif temp >= rain_thresh_min:
            ppt_phase = 1
        else:
            ppt_phase = (temp - snow_thresh_max) / (rain_thresh_min - snow_thresh_max)
    else:
        raise RuntimeError("Invalid rain-snow partitioning method")

    # Compute snowfall and rainfall
    snowfall_mm = (1 - ppt_phase) * precip
    rainfall_mm = precip - snowfall_mm

    # Add new snowfall to swe
    np.add(swe, snowfall_mm, out=swe)

    # Compute degree day factor for melt calcs
    ddf = ((ddf_max + ddf_min) / 2) + (np.sin((doy - 81) / 58.09) * ((ddf_max - ddf_min) / 2))

    # Compute potential melt
    if temp > tair_melt_thresh:
        melt_pot_mm = (temp - tair_melt_thresh) * ddf
    else:
        melt_pot_mm = 0

    # Compute total melt knowing melt can't exceed SWE
    melt = np.add(0, min(swe, melt_pot_mm), out=melt)

    # Compute SWE taking melt into account
    swe = np.subtract(swe, melt, swe)

    # Add rainfall to melt
    # Yes, rainfall != melt, but this simple model assumes all rain is a land surface water flux
    melt = np.add(melt, rainfall_mm, out=melt)

    return swe, melt


class Snow(object):
    """Snow model class.

    Examples
    --------
    TODO

    """

    def __init__(
        self, rs_method=1, rs_thresh=2.5, snow_thresh_max=1.5, rain_thresh_min=4.5,
            ddf_max=1, ddf_min=0, tair_melt_thresh=1, swe_init=0, dayofyear=274, year=2016,
    ):
        """Create a new heat model.

        Parameters
        ---------
        swe_init : float
            Alpha parameter in the heat equation.
            :param rs_method:
            :param rs_thresh:
            :param snow_thresh_max:
            :param rain_thresh_min:
            :param ddf_max:
            :param ddf_min:
            :param tair_melt_thresh:
        """
        self._rs_method = rs_method
        self._rs_thresh = rs_thresh
        self._snow_thresh_max = snow_thresh_max
        self._rain_thresh_min = rain_thresh_min
        self._ddf_max = ddf_max
        self._ddf_min = ddf_min
        self._tair_melt_thresh = tair_melt_thresh

        self._time = 0.0
        self._time_step = 86400
        self._dayofyear = dayofyear
        self._year = year

        self._tair_c = np.zeros(1, dtype=float)
        self._ppt_mm = np.zeros(1, dtype=float)
        self._swe_mm = np.zeros(1, dtype=float)
        swe_tmp = np.zeros(1, dtype=float)
        swe_tmp[0, ] = swe_init
        self._swe_mm = swe_tmp
        self._melt_mm = np.zeros(1, dtype=float)

    @property
    def rs_method(self):
        """Rain-snow partitioning method."""
        return self._rs_method

    @property
    def rs_thresh(self):
        """Rain-snow air temperature threshold when rs_method = 1."""
        return self._rs_thresh

    @property
    def snow_thresh_max(self):
        """Maximum snow air temperature threshold when rs_method = 2."""
        return self._snow_thresh_max

    @property
    def rain_thresh_min(self):
        """Maximum rain air temperature threshold when rs_method = 2."""
        return self._rain_thresh_min

    @property
    def ddf_max(self):
        """Maximum annual degree day factor."""
        return self._ddf_max

    def ddf_min(self):
        """Minimum annual degree day factor."""
        return self._ddf_min

    def tair_melt_thresh(self):
        """Minimum annual degree day factor."""
        return self._tair_melt_thresh

    @property
    def time(self):
        """Current model time."""
        return self._time

    @property
    def time_step(self):
        """Model time step."""
        return self._time_step

    @property
    def dayofyear(self):
        """Current model day of year."""
        return self._dayofyear

    @dayofyear.setter
    def dayofyear(self, dayofyear):
        """Set model day of year."""
        self._dayofyear = dayofyear

    @property
    def year(self):
        """Current model year."""
        return self._year

    @year.setter
    def year(self, year):
        """Set model year."""
        self._year = year

    @property
    def tair_c(self):
        """Current air temperature."""
        return self._tair_c

    @tair_c.setter
    def tair_c(self, new_tair_c):
        """Set air temperature."""
        self._tair_c[:] = new_tair_c

    @property
    def ppt_mm(self):
        """Current precipitation."""
        return self._ppt_mm

    @ppt_mm.setter
    def ppt_mm(self, ppt_mm):
        """Set precipitation."""
        self._ppt_mm[:] = ppt_mm

    @property
    def swe_mm(self):
        """Current snow water equivalent."""
        return self._swe_mm

    @swe_mm.setter
    def swe_mm(self, swe_mm):
        """Set swe."""
        self._swe_mm[:] = swe_mm

    @property
    def melt_mm(self):
        """Current snowmelt."""
        return self._melt_mm

    @melt_mm.setter
    def melt_mm(self, melt_mm):
        """Set melt."""
        self._melt_mm[:] = melt_mm

    @classmethod
    def from_file_like(cls, file_like):
        """Create a Snow object from a file-like object.

        Parameters
        ----------
        file_like : file_like
            Input parameter file.

        Returns
        -------
        Snow
            A new instance of a Snow object.
        """
        config = yaml.safe_load(file_like)
        return cls(**config)

    def advance_in_time(self):
        """Calculate new temperatures for the next time step."""
        solve_snow(
            self._tair_c,
            self._ppt_mm,
            self._dayofyear,
            self._swe_mm,
            self._melt_mm,
            self._rs_method,
            self._rs_thresh,
            self._snow_thresh_max,
            self._rain_thresh_min,
            self._ddf_max,
            self._ddf_min,
            self._tair_melt_thresh,
        )

        self._time += self._time_step
        if self._dayofyear == 365:    # check if day of year == 365
            if self._year % 4 != 0:   # if not leap year then increment to next year
                self._dayofyear = 1
                self._year += 1
            else:                     # otherwise (ie, it's a leap year) add 1 day
                self._dayofyear += 1
        elif self._dayofyear == 366:  # check if end of a leap year and increment to next year
            self._dayofyear = 1
            self._year += 1
        else:                         # otherwise add one day to clock
            self._dayofyear += 1
