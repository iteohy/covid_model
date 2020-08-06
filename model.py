from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector


class SchellingAgent(Agent):
    """
    Schelling segregation agent
    """

    def __init__(self, pos, model, agent_type):
        """
         Create a new Schelling agent.

         Args:
            unique_id: Unique identifier for the agent.
            x, y: Agent initial location.
            agent_type: Indicator for the agent's type (minority=1, majority=0)
        """
        super().__init__(pos, model)
        self.pos = pos
        self.type = agent_type
        self.contact = set()

    def step(self):
        similar = 0
        for neighbor in self.model.grid.neighbor_iter(self.pos, moore=True):
            if neighbor.type == self.type:
                similar += 1
                self.contact.add(neighbor.unique_id)

        # If unhappy, move:
        if similar < self.model.homophily:
            # move to random adjacent cell
            x, y = self.pos
            r = self.random.random()
            if r < 0.3:
                x = x+1
            elif r < 0.6:
                x = x-1

            r = self.random.random()
            if r < 0.3:
                y = y+1
            elif r<0.6:
                y = y-1


            self.model.grid.move_agent(self, (x,y))
        else:
            self.model.happy += 1


class Schelling(Model):
    """
    Model class for the Schelling segregation model.
    """

    def __init__(self, height=20, width=20, density=0.8, minority_pc=0.2, homophily=3):
        """
        """

        self.height = height
        self.width = width
        self.density = density
        self.minority_pc = minority_pc
        self.homophily = homophily

        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, torus=True)

        self.happy = 0
        self.contact = 0
        self.datacollector = DataCollector(
            {"happy": "happy"},  # Model-level count of happy agents
            # For testing purposes, agent's individual x and y
            {"x": lambda a: a.pos[0], "y": lambda a: a.pos[1]}            
        )

        # Set up agents
        # We use a grid iterator that returns
        # the coordinates of a cell as well as
        # its contents. (coord_iter)
        for cell in self.grid.coord_iter():
            x = cell[1]
            y = cell[2]
            if self.random.random() < self.density:
                if self.random.random() < self.minority_pc:
                    agent_type = 1
                else:
                    agent_type = 0

                agent = SchellingAgent((x, y), self, agent_type)
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        """
        Run one step of the model. If All agents are happy, halt the model.
        """
        self.happy = 0  # Reset counter of happy agents
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

        if self.happy == self.schedule.get_agent_count():
            self.running = False

        # compute average contact per agent
        total = 0
        for cell in self.grid.coord_iter():
            content, x, y = cell
            if content:
                for c in content:
                    total+=len(c.contact)
        self.contact = total/self.schedule.get_agent_count()

