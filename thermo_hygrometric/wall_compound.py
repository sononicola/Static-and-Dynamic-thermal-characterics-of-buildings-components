from dataclasses import dataclass
from typing import Optional
import numpy as np
from numpy.testing import assert_almost_equal
from .wall_layer import Layer


@dataclass
class Wall:
    name: str
    layers: list[Layer]
    # int = internal, ext = external :
    temp_int: float = 20.0  # Temperature in celsius
    temp_ext: float = -5.0
    relative_humidity_int: float = 0.65  # URi
    relative_humidity_ext: float = 0.9  # URe
    surface_thermal_resistance_int: float = 0.130  # Rsi
    surface_thermal_resistance_ext: float = 0.040  # Rse
    time: float = 24  # time of the analysis in hour

    def thicknesses(self) -> np.ndarray:
        "np.array with thickness of each Layer"
        return np.array([layer.thickness for layer in self.layers])

    def thickness_cumsum(self) -> np.ndarray:
        "cumulative sum of thickness of each Layer. Starting from 0"
        s = np.cumsum(self.thicknesses(), dtype=float)
        s = np.insert(s, 0, 0.0)
        return s

    def thermal_conductivities(self) -> np.ndarray:
        "np.array with thermal conductivitiy of each Layer"
        return np.array([layer.thermal_conductivity for layer in self.layers])

    def vapor_permeabilities(self) -> np.ndarray:
        "np.array with vapor permeability of each Layer"
        return np.array([layer.vapor_permeability for layer in self.layers])

    def densities(self) -> np.ndarray:
        "np.array with density of each Layer"
        return np.array([layer.density for layer in self.layers])

    def specific_heats(self) -> np.ndarray:
        "np.array with specific_heat of each Layer"
        return np.array([layer.specific_heat for layer in self.layers])

    def equivalent_thicknesses(self) -> np.ndarray:
        "np.array with Sd of each Layer"
        return np.array([layer.equivalent_thickness for layer in self.layers])

    def equivalent_thickness_tot(self) -> float:
        "sum of Sd of each Layer"
        return np.sum(self.equivalent_thicknesses())

    def equivalent_thickness_cumsum(self) -> np.ndarray:
        "cumulative sum of Sd of each Layer. Starting from 0"
        cum_sum = np.cumsum(self.equivalent_thicknesses(), dtype=float)
        cum_sum = np.insert(cum_sum, 0, 0.0)
        return cum_sum

    def thermal_resistances(self) -> np.ndarray:
        "np.array with the thermal resistance of each Layer, with addition of the internal and external surface thermal resistance"
        res = np.array([layer.thermal_resistance for layer in self.layers])
        res = np.insert(res, 0, self.surface_thermal_resistance_int)
        res = np.append(res, self.surface_thermal_resistance_ext)

        return res

    def thermal_resistance_tot(self) -> float:
        "sum of the thermal resistances. Starting from the surface internal' one"
        return np.sum(self.thermal_resistances())

    def thermal_resistance_cumsum(self) -> np.ndarray:
        "cumulative sum of the thermal resistances"
        cum_sum = np.cumsum(self.thermal_resistances(), dtype=float)
        return cum_sum

    def thermal_transmittance(self) -> float:
        "U = 1/R_tot"
        return 1 / self.thermal_resistance_tot()

    def calc_surface_temperatures(self) -> np.ndarray:
        delta_temp = self.temp_int - self.temp_ext
        temp = self.temp_int - (
            (self.thermal_resistance_cumsum() * delta_temp)
            / self.thermal_resistance_tot()
        )
        temp = np.insert(temp, 0, self.temp_int)

        # last term of temp array should be equal to temp_ext
        assert_almost_equal(temp[-1], self.temp_ext)

        return temp

    def calc_saturation_pressures(self) -> np.ndarray:
        return np.array(
            [
                610.5 * np.exp(17.269 * temp / (237.3 + temp))
                if temp >= 0
                else 610.5 * np.exp(21.875 * temp / (265.5 + temp))
                for temp in self.calc_surface_temperatures()
            ]
        )

    def calc_internal_pressures(self) -> np.ndarray:
        p_int = self.relative_humidity_int * self.calc_saturation_pressures()[0]
        p_ext = self.relative_humidity_ext * self.calc_saturation_pressures()[-1]
        delta_p = p_int - p_ext

        # 1:lenght-2 because we already know pressure at the boundaries
        press = p_int - (
            (
                self.equivalent_thickness_cumsum()[
                    1 : len(self.calc_saturation_pressures() - 2)
                ]
                * delta_p
            )
            / self.equivalent_thickness_tot()
        )
        press = np.insert(press, 0, p_int)

        # last term of press array should be equal to p_ext
        assert_almost_equal(press[-1], p_ext)

        return press

    def draw_graph(self):
        ...

    # TODO cambiare il nome
    def calc_profondità_penetrazione(self) -> np.ndarray:
        "delta"
        # TIME: hour to seconds
        return np.sqrt(
            (self.thermal_conductivities() * self.time * 3600)
            / (np.pi * self.densities() * self.specific_heats())
        )

    def xi(self) -> np.ndarray:
        return self.thicknesses() / self.calc_profondità_penetrazione()

    def calc_matrice_trasferimento_layer(self) -> list[np.ndarray]:
        # TODO cambiare nome a delta e xi
        xi = self.xi()
        delta = self.calc_profondità_penetrazione()
        thermal_conductivity = self.thermal_conductivities()

        zz: list[np.ndarray] = []  # zz : lista di matrici z
        for i in range(0, len(xi)):
            # z : matrice per ogni strato
            z = np.zeros((2, 2), dtype=np.complex128)  # matrice complex float
            z[0][0] = complex(
                (np.cosh(xi[i]) * np.cos(xi[i])), (np.sinh(xi[i]) * np.sin(xi[i]))
            )
            z[1][1] = z[0][0]
            z[0][1] = -(delta[i] / (2 * thermal_conductivity[i])) * complex(
                (np.sinh(xi[i]) * np.cos(xi[i]) + np.cosh(xi[i]) * np.sin(xi[i])),
                (np.cosh(xi[i]) * np.sin(xi[i]) - np.sinh(xi[i]) * np.cos(xi[i])),
            )
            z[1][0] = -(thermal_conductivity[i] / (delta[i])) * complex(
                (np.sinh(xi[i]) * np.cos(xi[i]) - np.cosh(xi[i]) * np.sin(xi[i])),
                (np.sinh(xi[i]) * np.cos(xi[i]) + np.cosh(xi[i]) * np.sin(xi[i])),
            )
            # aggiunge alla lista zz
            zz.append(z)
        return zz

    def calc_matrice_trasferimento_tot(self) -> np.ndarray:
        "Z"
        "matrice di trasferimento totale  del componente edilizio = Z_N * Z_n-1 * ... * Z_1"
        zz = self.calc_matrice_trasferimento_layer()

        Z = np.zeros((2, 2), dtype=np.complex128)
        Z = zz[-1]  # Z_N
        for i in range(1, len(zz)):  # [1  2 ... N  N+1)
            Z = Z.dot(zz[-1 - i])  # prodotto scalare
        return Z

    def calc_matrice_trasferimento_tot_ambiente_ambiente(self) -> np.ndarray:
        "Zee"
        Z = self.calc_matrice_trasferimento_tot()

        # Strato d'aria interno
        Zsi = np.array(
            [
                [complex(1, 0), complex(-self.surface_thermal_resistance_int)],
                [complex(0, 0), complex(1, 0)],
            ],
            dtype=np.complex128,
        )

        # Strato d'aria esterno
        Zse = np.array(
            [
                [complex(1, 0), complex(-self.surface_thermal_resistance_ext)],
                [complex(0, 0), complex(1, 0)],
            ],
            dtype=np.complex128,
        )

        Zee = Zse.dot(Z)
        Zee = Zee.dot(Zsi)

        return Zee

    # TODO verdere come migliroare i -> ndarray per le matrici complesse

    def calc_trasmittanza_termica_periodica(self) -> float:
        "Y12"
        Y12 = -1 / self.calc_matrice_trasferimento_tot_ambiente_ambiente()[0][1]
        Y12 = np.sqrt((Y12.real) ** 2 + (Y12.imag) ** 2)

        return Y12

    def calc_attenuazione(self) -> float:
        "fd"
        return (
            -self.calc_trasmittanza_termica_periodica() / self.thermal_transmittance()
        )

    def calc_phase(self) -> float:
        Zee = self.calc_matrice_trasferimento_tot_ambiente_ambiente()
        # time in hour
        return (
            (np.arctan2(Zee[0][1].imag, Zee[0][1].real)) * self.time / (2 * np.pi)
        )  # tempo in ore

    def calc_sfasamento(self) -> float:
        return self.calc_phase() + self.time / 2

    def calc_ammettanza_termica_interna(self) -> float:
        "Y11"
        Zee = self.calc_matrice_trasferimento_tot_ambiente_ambiente()

        Y11 = -Zee[0][0] / Zee[0][1]
        Y11 = np.sqrt((Y11.real) ** 2 + (Y11.imag) ** 2)  # the module

        return Y11

    def calc_ammettanza_termica_esterna(self) -> float:
        "Y22"
        Zee = self.calc_matrice_trasferimento_tot_ambiente_ambiente()

        Y22 = -Zee[1][1] / Zee[0][1]
        Y22 = np.sqrt((Y22.real) ** 2 + (Y22.imag) ** 2)  # the module

        return Y22

    def run_analysis(self) -> str:
        "Return all results as a string"
        # TODO
        res = ""
        res += str(self.thickness_cumsum())
        res += str(self.equivalent_thicknesses())
        res += str(self.equivalent_thickness_tot())
        res += str(self.equivalent_thickness_cumsum())
        res += str(self.thermal_resistances())
        res += str(self.thermal_resistance_tot())
        res += str(self.thermal_resistance_cumsum())
        res += str(self.thermal_transmittance())
        res += str(self.calc_surface_temperatures())
        res += str(self.calc_saturation_pressures())
        res += str(self.calc_internal_pressures())
        res += str(self.calc_profondità_penetrazione())
        res += str(self.xi())
        res += str(self.calc_matrice_trasferimento_layer())
        res += str(self.calc_matrice_trasferimento_tot())
        res += str(self.calc_matrice_trasferimento_tot_ambiente_ambiente())
        res += str(self.calc_trasmittanza_termica_periodica())
        res += str(self.calc_attenuazione())
        res += str(self.calc_phase())
        res += str(self.calc_sfasamento())
        res += str(self.calc_ammettanza_termica_interna())
        res += str(self.calc_ammettanza_termica_esterna())
        return res
