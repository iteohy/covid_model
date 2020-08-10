from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter

from model import Schelling


class HappyElement(TextElement):
    """
    Display a text count of how many happy agents there are.
    """

    def __init__(self):
        pass

    def render(self, model):
        return "Number agents: " + str(model.schedule.get_agent_count()) + "; Infected:" + str(model.infected)


def schelling_draw(agent):
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
canvas_element = CanvasGrid(schelling_draw, 20, 20, 500, 500)
seir_chart = ChartModule([
    {"Label": "infected", "Color": "Red"},
    {"Label": "exposed", "Color": "Blue"},
    {"Label": "removed", "Color": "Grey"},
    {"Label": "susceptible", "Color": "Green"}])

contact_chart = ChartModule([{"Label": "contact", "Color": "Black"}])

model_params = {
    "height": 20,
    "width": 20,
    "density": UserSettableParameter("slider", "Agent density", 0.1, 0.1, 1.0, 0.1),
    "minority_pc": UserSettableParameter("slider", "Init Infected", 0.8, 0.05, 1.0, 0.05),
    "homophily": UserSettableParameter("slider", "Homophily", 3, 0, 8, 1),
}

server = ModularServer(
    Schelling, [canvas_element, happy_element, seir_chart, contact_chart], "Schelling", model_params
)