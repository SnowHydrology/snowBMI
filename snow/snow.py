"""Temperature index snow model"""

import numpy as np
import yaml
from scipy import ndimage


def solve_snow(temp, precip, swe, melt, rain_snow, alpha=1.0, time_step=1.0):
    """Solve the 2D Heat Equation on a uniform mesh.

    Parameters
    ----------
    temp : ndarray
        Temperature.
    spacing : array_like
        Grid spacing in the row and column directions.
    out : ndarray (optional)
        Output array.
    alpha : float (optional)
        Thermal diffusivity.
    time_step : float (optional)
        Time step.

    Returns
    -------
    result : ndarray
        The temperatures after time *time_step*.

    Examples
    --------

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

    # Compute degree day factor
    ddf = ((ddf_max + ddf_min) / 2) + (sin((yday(date) - 81) / 58.09) * ((ddf_max - ddf_min) / 2))

    # Compute potential melt
    if temp > tair_melt_thresh:
        melt_pot_mm = (tair_c - tair_melt_thresh) * ddf
    else:
        melt_pot_mm = 0

    # Compute SWE taking snowfall and melt into account
    swe = max(0, swe + snowfall_mm - melt_pot_mm)


return np.add(temp, out, out=out)


class Snow(object):

    """Solve the Heat equation on a grid.

    Examples
    --------
    >>> heat = Snow()
    >>> heat.time
    0.0
    >>> heat.time_step
    0.25
    >>> heat.advance_in_time()
    >>> heat.time
    0.25

    >>> heat = Snow(shape=(5, 5))
    >>> heat.temperature = np.zeros_like(heat.temperature)
    >>> heat.temperature[2, 2] = 1.
    >>> heat.advance_in_time()

    >>> heat = Snow(alpha=.5)
    >>> heat.time_step
    0.5
    >>> heat = Snow(alpha=.5, spacing=(2., 3.))
    >>> heat.time_step
    2.0
    """

    def __init__(
        self, shape=(10, 20), spacing=(1.0, 1.0), origin=(0.0, 0.0), alpha=1.0
    ):
        """Create a new heat model.

        Parameters
        ---------
        shape : array_like, optional
            The shape of the solution grid as (*rows*, *columns*).
        spacing : array_like, optional
            Spacing of grid rows and columns.
        origin : array_like, optional
            Coordinates of lower left corner of grid.
        alpha : float
            Alpha parameter in the heat equation.
        """
        self._shape = shape
        self._spacing = spacing
        self._origin = origin
        self._time = 0.0
        self._alpha = alpha
        self._time_step = min(spacing) ** 2 / (4.0 * self._alpha)

        self._temperature = np.random.random(self._shape)
        self._next_temperature = np.empty_like(self._temperature)

    @property
    def time(self):
        """Current model time."""
        return self._time

    @property
    def temperature(self):
        """Temperature of the plate."""
        return self._temperature

    @temperature.setter
    def temperature(self, new_temp):
        """Set the temperature of the plate.

        Parameters
        ----------
        new_temp : array_like
            The new temperatures.
        """
        self._temperature[:] = new_temp

    @property
    def time_step(self):
        """Model time step."""
        return self._time_step

    @time_step.setter
    def time_step(self, time_step):
        """Set model time step."""
        self._time_step = time_step

    @property
    def shape(self):
        """Shape of the model grid."""
        return self._shape

    @property
    def spacing(self):
        """Spacing between nodes of the model grid."""
        return self._spacing

    @property
    def origin(self):
        """Origin coordinates of the model grid."""
        return self._origin

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
            self._swe_mm,
            self._melt_mm
            alpha=self._alpha,
            time_step=self._time_step,
        )
        np.copyto(self._temperature, self._next_temperature)

        self._time += self._time_step
