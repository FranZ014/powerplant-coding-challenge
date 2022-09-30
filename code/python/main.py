#-----------------------------------
# Imports
#-----------------------------------

import json
from typing import Optional
import uvicorn
from fastapi import FastAPI
from production_plan import ProductionPlan
from windfactor import WindFactor
from iphysicfactor import IPhysicFactor
from powerplant import PowerPlant

#-----------------------------------
# Methods
#-----------------------------------

def parse_data (productionPlan: ProductionPlan) -> Optional[object] :
    """This method is used to parse the raw data of the json file into power plants, physic factor and load. Take the raw data as parameter."""

    try: 
        power_plants = []

        load: float = productionPlan.load
        gas_price: float = 0.0
        kerosine_price: float = 0.0
        co2_price: float = 0.0
        wind_power: float = 0.0

        if 'gas(euro/MWh)' in productionPlan.fuels :
            gas_price = productionPlan.fuels['gas(euro/MWh)']
        else:
            print("ERROR : the gas price has not been found in the data - aborting.")
            return None

        if 'kerosine(euro/MWh)' in productionPlan.fuels :
            kerosine_price = productionPlan.fuels['kerosine(euro/MWh)']
        else:
            print("ERROR : the kerosine price has not been found in the data - aborting.")
            return None

        if 'co2(euro/ton)' in productionPlan.fuels :
            co2_price = productionPlan.fuels['co2(euro/ton)']
        else:
            print("WARNING : the co2 emission price has not been found in the data. - passed because not used.")

        if 'wind(%)' in productionPlan.fuels :
            wind_power = productionPlan.fuels['wind(%)']
        else:
            print("ERROR : the wind power has not been found in the data - aborting.")
        
        wind_physic_factor = WindFactor(wind_power/100)
        pp_index = -1

        for power_plant_data in productionPlan.powerplants: 

            pp_index += 1

            pp_name: str = ""
            pp_type: str = ""
            pp_efficiency: float = 1.0
            pp_pmin: float = 0.0
            pp_pmax: float = 0.0
            pp_price: float = 0.0
            pp_physic_factors: list[IPhysicFactor] = list()
            pp_aon: bool = False

            if 'name' in power_plant_data :
                pp_name: str = power_plant_data['name']
            else:
                print("ERROR : powerplant #", pp_index, "does not have a name - powerplant not imported.")
                continue

            if 'type' in power_plant_data :
                pp_type: str = power_plant_data['type']
            else:
                print("ERROR : the", pp_name, "powerplant does not have a type - powerplant not imported.")
                continue
            
            if 'efficiency' in power_plant_data :
                pp_efficiency = power_plant_data['efficiency']
            else:
                print("WARNING : the", pp_name, "powerplant does not have an efficiency factor - 1.0 has been used")

            if 'pmin' in power_plant_data :
                pp_pmin = power_plant_data['pmin']
            else:
                print("ERROR : the", pp_name, "powerplant does not have a minimum power - powerplant not imported.")
                continue

            if 'pmax' in power_plant_data:
                pp_pmax = power_plant_data['pmax']
            else:
                print("ERROR : the", pp_name, "powerplant does not have a maximum power - powerplant not imported.")
                continue

            if pp_type == "gasfired" :
                pp_physic_factors = None
                pp_price = gas_price
            
            elif pp_type == "turbojet" :
                pp_physic_factors = None
                pp_price = kerosine_price
            
            elif pp_type == "windturbine":
                pp_physic_factors.append(wind_physic_factor)
                pp_aon = True

            else:
                print("ERROR : the", pp_name, "powerplant of the type \"", pp_type,"\" has not been recognized - powerplant not imported.")
                continue

            power_plants.append(PowerPlant(pp_index, pp_name, pp_type, pp_efficiency, pp_pmin, pp_pmax, pp_price, pp_aon, pp_physic_factors))
            del pp_physic_factors

        if len(power_plants) == 0 :
            print("ERROR : no power plants imported ...")
            return None

        return [load, power_plants]

    except:
        return None

def compute_powerplants (load: float, power_plants: list[PowerPlant]) -> None :
    """This method is used to edit the power plant activation. Take the load aimed and the power plants and returns nothing."""

    load_left: float = load

    # Sort by computed price
    power_plants.sort(key= lambda power_plant: (power_plant.compute_price_rate(), power_plant.get_index()))

    # Activate the lower price firsts
    for power_plant in power_plants:

        if load_left == 0 :
            break
        
        if power_plant.compute_price_rate() == 0 :

            load_left -= power_plant.compute_activation(load_left)

        else:
            break

    
    # If power left -> activate higher price
    if load_left > 0 :

        for power_plant in power_plants :

            if load_left == 0 :
                break
            
            if power_plant.compute_price_rate() == 0 :
                continue

            load_left -= power_plant.compute_activation(load_left)

    # If power left -> it's due to pmin, deactivate last AON (expensive one, or just index wise) and activate low price linear producer
    if load_left > 0 :
        
        nothing_changed = False

        while load_left > 0 and not(nothing_changed):

            nothing_changed = True

            power_plants.reverse()
            
            for power_plant in power_plants :

                if power_plant.is_all_or_nothing() and power_plant.get_activation() == 1 :
                    load_left += power_plant.compute_output_power()
                    power_plant.set_activation(0)
                    break

            power_plants.reverse()

            for power_plant in power_plants :
                
                if load_left == 0 :
                    break

                if power_plant.is_all_or_nothing() :
                    continue

                if power_plant.get_activation() == 1 :
                    continue

                else :
                    nothing_changed = True
                    load_left -= power_plant.compute_activation(load_left)

    # If power left -> reactivate aon until negative power left
    if load_left > 0 :

        for power_plant in power_plants :
            
            if load_left <= 0 :
                break

            if power_plant.is_all_or_nothing() and power_plant.get_activation() == 0 :
                load_left -= power_plant.compute_activation(load_left)

        print("WARNING : load left after activation of every power plant : ", load_left)

    # Sort by indices
    power_plants.sort(key= lambda power_plant: power_plant.get_index())

def create_exportable_data (power_plants: list[PowerPlant]) -> Optional[list[object]] :
    """This method is used to parse the power plant into a writable nameless object."""
    
    data: list[object] = []

    for power_plant in power_plants:
        pp_data = {'name': power_plant.get_name(), 'p': "{:.1f}".format(power_plant.compute_output_power())}
        data.append(pp_data)
    
    return data

#-----------------------------------
# Main
#-----------------------------------

if __name__ == "__main__" :

    app = FastAPI()
    """This is the fast api object."""

    @app.post("/productionplan")
    def productionplan(productionPlan: ProductionPlan) :
        """This method is called by the user when he wants to use the api."""

        # Parsing the data received from the user.
        parsed_data = parse_data(productionPlan)

        if not(parsed_data is None) :
                    
            power_plants: list[PowerPlant] = parsed_data[1]
            """Are the power plants."""

            load: float = parsed_data[0]
            """Is the load of the network."""

            # Compute the ouput power of each power plants.
            compute_powerplants(load, power_plants)

            # Export the data
            return create_exportable_data(power_plants)

        else :
            print("An error occured while parsing the received data")
            print("data received : ")
            print(productionPlan)
            print("")
            print("------------------")

            return {}

    uvicorn.run(app, host="0.0.0.0", port=8888)