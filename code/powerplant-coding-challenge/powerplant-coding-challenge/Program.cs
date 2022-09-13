//-----------------------------------
// Imports
//-----------------------------------

using Newtonsoft.Json.Linq;

using powerplant_coding_challenge;

//-----------------------------------
// Fields
//-----------------------------------

/// <summary>
/// This is the builder that allows to instanciate the application launhcer.
/// </summary>
var builder = WebApplication.CreateBuilder(args);

/// <summary>
/// This is the application.
/// </summary>
var app = builder.Build();

/// <summary>
/// This is the input file used as an input.
/// </summary>
const String INPUT_FILE_NAME = "payload1.json";

/// <summary>
/// This is the output file used as an output.
/// </summary>
const String OUTPUT_FILE_NAME = "example_response.json";

//-----------------------------------
// Functions
//-----------------------------------
/// <summary>
/// This si the method used to read the production data, compute the activation of the prodctuors and export the data.
/// </summary>
String ProductionplanMethod (String fileName)
{
    // FCTN 01 - read data
    if (!File.Exists(fileName))
    {
        return "Input file not found";
    }
    String fileDataReaded = File.ReadAllText(fileName);
    JToken? jsonReaded = null;
    try
    {
        jsonReaded = JValue.Parse(fileDataReaded);
    }
    catch (Exception ex)
    {
        return "Exception while parsing file : " + ex.Message;
    }

    if (jsonReaded == null)
    {
        return "Impossible to parse input file";
    }

    // FCTN 02 - parsing data
    // Fuels
    JToken fuelsData = jsonReaded["fuels"];

    if (fuelsData == null)
    {
        return "Fuels not found in input file";
    }

    JValue gas = (JValue) fuelsData["gas(euro/MWh)"];
    JValue kerosine = (JValue) fuelsData["kerosine(euro/MWh)"];
    JValue co2 = (JValue) fuelsData["co2(euro/ton)"];
    JValue wind = (JValue) fuelsData["wind(%)"];

    InputFuels fuels = new InputFuels(
        Convert.ToDouble(gas.Value),
        Convert.ToDouble(kerosine.Value),
        Convert.ToDouble(co2.Value),
        Convert.ToDouble(wind.Value)
    );

    // Power plants
    JToken powerPlantsData = jsonReaded["powerplants"];
    IList<InputProductor> productors = new List<InputProductor>();

    if (powerPlantsData == null)
    {
        return "Power plants not found in input file";
    }

    foreach (var powerPlant in powerPlantsData)
    {
        JValue nameValue = (JValue)(powerPlant["name"]);
        JValue typeValue = (JValue)(powerPlant["type"]);
        JValue efficiencyValue = (JValue)(powerPlant["efficiency"]);
        JValue pminValue = (JValue)(powerPlant["pmin"]);
        JValue pmaxValue = (JValue)(powerPlant["pmax"]);

        productors.Add(new InputProductor(
            nameValue.ToString(),
            typeValue.ToString(),
            Convert.ToDouble(efficiencyValue.Value),
            Convert.ToDouble(pminValue.Value),
            Convert.ToDouble(pmaxValue.Value)
        ));
    }

    Input inputData = new Input(Convert.ToDouble(((JValue)jsonReaded["load"]).Value), fuels, productors);
    
    // FCTN 03 - activate productors

    // FCTN 04 - jsonify data

    // FCTN 05 - write data

    return "SUCCESS";
}

/// <summary>
/// This is the method used to test the classes and the functionnalities.
/// </summary>
String UnitTest ( )
{
    // TEST 01
    Productor p1 = new Productor("gasfiredbig1", "gasfired", 0.53, 100, 460);
    p1.Activation = 1;

    Double expectedP1Power = 243.8;
    Double actualP1Power = p1.OutputPower;

    Double errorP1 = expectedP1Power - actualP1Power;

    if (errorP1 != 0)
    {
        return "The power computed for p1 is different than the expected one !";
    }

    // TEST 02
    List<IPhysicFactor> windFactor = new List<IPhysicFactor>()
    {
        new WindFactor(0.60)
    };

    Productor p2 = new Productor("windpark1", "windturbine", 1, 0, 150, true, windFactor);
    p2.Activation = 1;

    Double expectedP2Power = 90;
    Double actualP2Power = p2.OutputPower;

    Double errorP2 = expectedP2Power - actualP2Power;

    if (errorP2 != 0)
    {
        return "The power computed for p2 is different than the expected one !";
    }


    return "Tests passed !";
}

//-----------------------------------
// Routes
//-----------------------------------

/// <summary>
/// This is the required first route.
/// </summary>
app.MapGet("/productionplan", () => ProductionplanMethod(INPUT_FILE_NAME));

/// <summary>
/// This is the route used to test the classes created.
/// </summary>
app.MapGet("/test", () => UnitTest());

/// <summary>
/// This is the route in order to know that everything work.
/// </summary>
app.MapGet("/", () => "Hello World !");

//-----------------------------------
// Main
//-----------------------------------

/// <summary>
/// This is the launching of the application.
/// </summary>
app.Run();
