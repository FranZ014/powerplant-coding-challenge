## How to launch the app

console -> python -m main

## TODO List

Architecture :

1. Create http server
2. Create 'interface' class IPhysicFactor : used to edit the output power of power plants.
3. Create class WindFactor : used to edit the ouptput power of power plants with the wind pourcentage.
4. Create class PowerPlant : used to collect the data of power plant and compute the output power.

Fonctions : 

On request "productionplan"
1. Read input json from client
2. Parse data into PowerPlants and IPhysicsFactor
3. Compute which power plant to activate
4. Fill up data into nameless objects
5. Write output json to client