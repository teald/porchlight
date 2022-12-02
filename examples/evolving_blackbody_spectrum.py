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

        term1 = 2 * const.h * const.c ** 2 / wl ** 5

        exponent = const.h * const.c / (wl * const.k_B * temperature)

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
    k = 2e-5 * u.s ** -1
    t_inflect = 2e5 * u.s
    t_start = 5000.0 * u.K

    temperature = t_start / (1 + np.exp(k * (time - t_inflect))) + 500.0 * u.K

    return temperature


@porchlight.Door
def gen_spectrum(bb_fxn: Callable, wavelengths: u.Quantity):
    "Updates the blackbody spectrum."
    spectrum = bb_fxn(wavelengths)

    return spectrum


@porchlight.Door
def step_time_forward(time, dt=1e4 * u.s):
    """Applies the only real change in this model, stepping forward."""
    time = time + dt
    return time


def main():
    """Executes the example."""
    nbr = porchlight.Neighborhood()

    # Adding the Doors we've defined above
    nbr.add_door(temp_evolution)  # This will initialize the temperature
    nbr.add_door(blackbody)
    nbr.add_door(blackbody_peak)
    nbr.add_door(gen_spectrum)
    nbr.add_door(step_time_forward)

    # List out the parameters in our system to the terminal.
    print("Neighborhood object contains the following parameters:")
    for pname, param in nbr.params.items():
        print(f"\t{pname}: {param.value} ({param.type})")

    print("\nThe parameters are required by the following Doors:")
    for dname, door in nbr.doors.items():
        argstr = ", ".join([pname for pname in door.required_arguments])
        print(f"\t{dname}({argstr})")

    # Need to set the values for our required parameters. In this case, that's
    # just wavelength grid and time!
    nbr.set_param("time", 0.0 * u.s)
    nbr.set_param(
        "wavelengths", np.logspace(-1, np.log10(30), 10000) * u.micron
    )

    # Let's run the model a number of times and collect data as the model
    # evolves.
    data = {}

    N_STEPS = 50
    for i in range(N_STEPS):
        nbr.run_step()

        # Since temperature, time, and spectrum are the only parameters really
        # updating every step, just track those.
        cur_temp = nbr.params["temperature"]
        cur_time = nbr.params["time"]
        cur_spectrum = nbr.params["spectrum"]

        cur_data = {
            "temperature": cur_temp.value,
            "time": cur_time.value,
            "cur_spectrum": cur_spectrum.value,
        }

        data[f"{cur_time.value:1.5e}"] = cur_data

        # Print out info to the terminal during evolution.
        print(
            f"{i:4d}) Temperature: {cur_temp.value:6.1f} Kelvin "
            f"|| Time: {cur_time.value:.3e} seconds"
        )

    ######################################
    #                                    #
    # EVERYTHING BELOW HERE IS PLOTTING! #
    #                                    #
    ######################################

    # We now have our coupled blackbody/temperature evolution model ready, and
    # we can use it as we'd like. Let's plot it to see if it worked out.
    fig, axes = plt.subplots(2, 1)

    ax = axes[0]

    ax.set(
        xscale="log",
        # yscale="log",
        xlabel="Wavelength (micron)",
        ylabel="Flux (W/m^2/m)",
    )

    times = list(data.keys())

    N_SAMPLES = 10

    cmap = plt.get_cmap("gist_rainbow")
    colors = [cmap(i / N_SAMPLES) for i in range(N_SAMPLES)]

    # Just reversing the colors to add hint of physicality.
    colors = colors[::-1]

    itimes = [i * len(times) // (N_SAMPLES - 1) for i in range(N_SAMPLES - 1)]
    itimes += [len(times) - 1]

    for i, itime in enumerate(itimes):
        time = times[itime]

        wl = nbr.params["wavelengths"].value.to(u.micron).value
        spectrum = data[time]["cur_spectrum"].si.value

        ax.plot(wl, spectrum, color=colors[i])

    # Plot the temperature evolution with time for the run.
    ax = axes[1]

    ax.set(xlabel="Time (seconds)", ylabel="Temperature (Kelvin)")

    temperatures = [d["temperature"].value for d in data.values()]
    times = [d["time"].value for d in data.values()]
    sample_times = [times[i] for i in itimes]
    sample_temps = [temperatures[i] for i in itimes]

    ax.plot(times, temperatures, "k-")

    # Add in the points sampled for the spectra.
    for i, (time, temp) in enumerate(zip(sample_times, sample_temps)):
        time = float(time)
        ax.plot(time, temp, marker="o", color=colors[i])

    plt.show()


if __name__ == "__main__":
    main()

    filename = __file__.split("/")[-1]
    print(f"\n\nExample {filename} has completed.")
