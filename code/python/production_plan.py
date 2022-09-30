#-----------------------------------
# Imports
#-----------------------------------

from pydantic import BaseModel

#-----------------------------------
# Class
#-----------------------------------

class ProductionPlan (BaseModel) :
    """This is the model used to receive the data from the client."""

    load: float
    """This is the load to aim for the power plant production."""

    fuels: object
    """These are the price or the data about the different fuels or emissions."""

    powerplants: list
    """These are the available power plants."""