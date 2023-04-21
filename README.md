# snowBMI

**Description**:  This simple, temperature index snow model includes an implementation of the [Basic Model Interface](https://csdms.colorado.edu/wiki/BMI) (BMI). It's meant for demonstration purposes, but feel free to use it however you like. I'd recommend it mostly for snow modeling, but you do you.

BMI is developed by the [CSDMS](https://csdms.colorado.edu/wiki/Main_Page) group at CU Boulder. Much of the BMI code here is from their [heat](https://github.com/csdms/bmi-example-python) example. 

## Dependencies

This is a simple bit of Python code developed with Python 3.9. The `snowBMI` module requires:

* The [BMI Python bindings](https://github.com/csdms/bmi-python) from CSDMS
* `numpy`
* `yaml`

The example also requires:

* [Jupyter Notebook](https://jupyter.org/)
* `pandas`
* `Matplotlib`

## Installation

First install the BMI Python bindings using the CSDMS instructions. Next, build the model by going to the main level of the `snowBMI` directory and running:

`pip install -e .`

## Usage

This model comes with an example Jupyter Notebook so you can see how the BMI functions work to control model execution and the handling of data.

`examples/run-model-from-bmi.ipynb`

## Known issues

This is but a simple model that makes several assumptions. They are:

* Snow hydrology is ignored (if melt is produced then it immediately disappears from the snowpack)
* Rainfall is added to snowmelt so that the melt term represents a land surface water flux
* The model is configured for a daily timestep
* Date handling is only done by a day of year tracker in the code (i.e., there is no explicit handling of POSIX-formatted datetimes)

## Reporting issues, getting help

If you see any bugs, errors, etc., please use this repo's Issue Tracker. You can also make any requests for help there.

## Open source licensing info
[LICENSE](LICENSE)

----

## Credits and references

1. [BMI](https://csdms.colorado.edu/wiki/BMI) from CSDMS
2. The BMI Python [heat](https://github.com/csdms/bmi-example-python) example
3. Temperature index snow models like Snow-17 and the equations in DeWalle and Rango (2008)
    - _Anderson, E. A. "Snow accumulation and ablation model–SNOW-17." US National Weather Service, Silver Spring, MD 61 (2006)._
    - _DeWalle, David R., and Albert Rango. Principles of Snow Hydrology. Cambridge University Press, 2008._
4. The Next Generation Water Prediction Capability project at the NOAA-NWS Office of Water Prediction
   - GitHub repo for the [NextGen Framework](https://github.com/NOAA-OWP/ngen)
   - BMI implementation of the [LSTM](https://github.com/NOAA-OWP/lstm/) machine learning model
