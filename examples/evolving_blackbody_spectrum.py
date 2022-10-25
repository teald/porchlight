"""This example runs through a blackbody spectrum evolving through time.
Although this is not strictly a physical model based off reality, one could
modify this to evolve along the H-R diagram, for example.
"""
import matplotlib.pyplot as plt
import numpy as np
import porchlight
import astropy.constants as const
import astropy.units as u
from typing import Callable


@porchlight.Door
def blackbody(temperature: u.Quantity) -> Callable:
    """Defines a "spectrum", a blackbody function that takes wavelength and
    returns intensity. All units are in SI.
    """

    def bb_fxn(wl):
        """Blackbody function initialized at some temperature"""
        wl = wl * u.m if not isinstance(wl, u.Quantity) else wl

        term1 = 2 * const.h * const.c / wl ** 5

        exponent = const.h * const.c / (wl * u.k_B * temperature)
        term2 = np.power(np.exp(exponent) - 1, -1)

        return term1 * term2

    return bb_fxn


@porchlight.Door
def blackbody_peak(temperature: u.Quantity) -> u.Quantity:
    """Wien's displacement law for peak wavelength"""
    peak_wl = 2.879e-3 * u.m * u.K / temperature
    return peak_wl


@porchlight.Door
def temp_evolution(time: u.Quantity) -> u.Quantity:
    """Evolve the temperature over time as a logarithmic curve."""
    k = 1e-6 * u.s ** -1
    t_inflect = 1e6 * u.s

    temperature = 1000.0 * u.K / (1 + np.exp(k * (time - t_inflect)))

    return temperature


@porchlight.Door
def gen_spectrum(bb_fxn: Callable, wavelengths: u.Quantity):
    spectrum = bb_fxn(wavelengths)

    return spectrum


def main():
    """Executes the example."""
    nbr = porchlight.Neighborhood()

    # Adding the Doors we've defined above
    nbr.add_door(blackbody)
    nbr.add_door(blackbody_peak)
    nbr.add_door(temp_evolution)
    nbr.add_door(gen_spectrum)

    # List out the parameters in our system to the terminal.
    print("Neighborhood object contains the following parameters:")
    for pname, param in nbr.params.items():
        print(f"\t{pname}: {param.value} ({param.type})")

    print("\nThe parameters are required by the following Doors:")
    for dname, door in nbr.doors.items():
        argstr = ", ".join([pname for pname in door.required_arguments])
        print(f"\t{dname}({argstr})")

    # Need to set the values for our required parameters. In this case, that's
    # just temperature!
    nbr.set_param("temperature", 500.0 * u.K)

    nbr.run_step()


if __name__ == "__main__":
    main()

    filename = __file__.split("/")[-1]
    print(f"\n\nExample {filename} has completed.")
