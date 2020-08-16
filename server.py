from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter

from model import Covid


class HappyElement(TextElement):
    """
    Display a text count of how many happy agents there are.
    """

    def __init__(self):
        pass

    def render(self, model):
        return "Number agents: " + str(model.schedule.get_agent_count()) + "; Day: " + str(int(model.schedule.steps/model.day_steps))


def covid_draw(agent):
    """
    Portrayal Method for canvas
    """
    if agent is None:
        return
    
    #portrayal = {"Shape": dstate.shape, "r": dstate.radius, "Filled": dstate.filled, "Layer": dstate.layer}
    portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 0}
    
    dstate = agent.d_state
    portrayal["Color"] = [dstate.color]
    portrayal["stroke_color"] = dstate.stroke_color
    #portrayal["Color"] = ["#FF0000"]
    #portrayal["stroke_color"] = "#000000"
    
    return portrayal


happy_element = HappyElement()
canvas_element = CanvasGrid(covid_draw, 20, 20, 500, 500)
seir_chart = ChartModule([
    {"Label": "infected", "Color": "Red"},
    {"Label": "exposed", "Color": "Blue"},
    {"Label": "removed", "Color": "Grey"},
    {"Label": "susceptible", "Color": "Green"}])

contact_chart = ChartModule([{"Label": "contact", "Color": "Black"}])

model_params = {
    "height": 20,
    "width": 20,
    "density": UserSettableParameter("number", "number of agents", value=100),
    "minority_pc": UserSettableParameter("number", "number Infected", value=10),
    "infection_rate": UserSettableParameter("slider", "Infectiousness", 0.7, 0.1, 1.0, 0.05),
    "min_infected": UserSettableParameter('number', 'min Infected duration (days)', value=7),
    "max_infected": UserSettableParameter('number', 'max Infected duration (days)', value=14),
    "min_exposed": UserSettableParameter('number', 'min Exposed duration (days)', value=1),
    "max_exposed": UserSettableParameter('number', 'max Exposed duration (days)', value=5),
    "day_steps": UserSettableParameter('number', 'Number of steps in a day', value=5),
    "day_isolation": UserSettableParameter('number', 'Number of days to isolation', value=6)
    
}

server = ModularServer(
    Covid, [canvas_element, happy_element, seir_chart, contact_chart], "COVID-19", model_params
)