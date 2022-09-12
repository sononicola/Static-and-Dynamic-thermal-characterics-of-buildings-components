from .wall_compound import Wall
import pandas as pd
import matplotlib.pyplot as plt


def plot_bar_chart_comparasion(structures: list[Wall], latex: bool = False) -> plt.Axes:
    """
    Make a bar plot comparasion. Resulting data are a little scaled due to very different values

    https://stackoverflow.com/questions/14270391/python-matplotlib-multiple-bars
    """
    names = [struct.name for struct in structures]
    data = [struct.create_dict_valuable_properties() for struct in structures]

    df = pd.DataFrame(data, index=names)

    # since numbers to compare are very different, we "scale" values a bit
    df["massa superficiale"] = df["massa superficiale"] / 100
    df["trasmittanza termica periodica"] = df["trasmittanza termica periodica"] * 100
    df["fattore attenuazione"] = df["fattore attenuazione"] * 10
    df["capacità termica areica interna"] = df["capacità termica areica interna"] / 10

    ax = df.plot(
        kind="bar", rot=0, xlabel="Pareti", title="Comparazione", figsize=(6, 4)
    )

    # add some labels
    for c in ax.containers:
        # set the bar label
        ax.bar_label(c, fmt="%.2f", label_type="edge")

    # add a little space at the top of the plot for the annotation
    ax.margins(y=0.5)

    if latex:
        custom_labels = [
            "Spessore [m]",
            "Resistenza [m$^2$ K W$^{-1}$]",
            "Massa superficiale [$\\times10^2$ kg m$^{-2}$]",
            "Trasmittanza termica periodica $Y_{12}$ [$\\times10^{-2}$ W m$^{-2}$ K$^{-1}$]",
            "Sfasamento [h]",
            "Fattore di attenuazione [$\\times10^{-1}$]",
            "Capacità termica periodica interna $k_1$ [$\\times10^{1}$ kJ m$^{-2}$ K$^{-1}$]",
        ]
    else:
        custom_labels = [
            "Spessore [m]",
            "Resistenza [m2 K W-1]",
            "Massa superficiale [100 * kg m-1]",
            "Trasmittanza termica periodica Y12 [0.01 *  W m-2 K-1]",
            "Sfasamento [h]",
            "Fattore di attenuazione [* 0.1]",
            "Capacità termica periodica interna k1 [10 * kJ m-2 K-1]",
        ]
    ax.legend(loc="upper center", labels=custom_labels, frameon=True, ncol=2)

    return ax
