from dataclasses import dataclass
from typing import Optional

@dataclass
class Layer:
    name: str
    thickness: float #in meters
    thermal_conductivity: float # lambda
    vapor_permeability: float # mu
    density: float
    specific_heat: float
    color: Optional[str] = "white" 
    
    #TODO add is_air 

    @property
    def equivalent_thickness(self):
        "Sd"
        return self.thickness * self.vapor_permeability

    @property
    def thermal_resistance(self):
        "R"
        return self. thickness / self.thermal_conductivity



