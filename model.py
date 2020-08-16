from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector


class DiseaseState():
    def __init__(self, state, color, stroke_color):
        """
        Create a disease state

        Args:
            state: Indicator for SEIR
            color: color of agent for Portrayal
            stroke_color: stroke color of agent for Portrayal
        """
        self.state = state
        self.setColors(color, stroke_color)
        self.setShape("circle", 0.5, "true", 0)
        self.lifespan = -1
        self.assigned_lifespan = -1

    def setColors(self, color, stroke_color):
        #portrayal["Color"] = ["#FF0000"]
        #portrayal["stroke_color"] = "#000000"
        self.color = color
        self.stroke_color = stroke_color

    def setShape(self, shape, radius, filled, layer):
        #portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 0}
        self.shape = shape
        self.radius = radius
        self.layer = layer
        self.filled = filled

    def decrementLifespan(self):
        if self.lifespan > -1:
            self.lifespan -= 1

    def setLifespan(self, lifespan):
        self.lifespan = int(lifespan)
        self.assigned_lifespan = int(lifespan)
        
        #print(str(self)+': '+str(self.lifespan))


class Susceptible(DiseaseState):
    def __init__(self):
        # init disease state Susceptible, color Green, stroke Black
        super().__init__("S", "#00FF00", "#000000")

class Exposed(DiseaseState):
    def __init__(self):
        # init disease state Exposed, color Blue, stroke Black
        super().__init__("E", "#0000FF", "#000000")

class Infected(DiseaseState):
    def __init__(self):
        # init disease state Infected, color Red, stroke Black
        super().__init__("I", "#FF0000", "#000000")

class Removed(DiseaseState):
    def __init__(self):
        # init disease state Removed, color Grey, stroke Black
        super().__init__("R", "#CCCCCC", "#000000")


class CovidAgent(Agent):
    """
    Agent simulating covid-19 spread
    """

    def __init__(self, pos, model, d_state, move=True, isolate_duration=14):
        """
         Create a new covid agent.

         Args:
            unique_id: Unique identifier for the agent.
            x, y: Agent initial location.
            d_state: disease state of the agent (S,E,I,R)
        """
        super().__init__(pos, model)
        self.pos = pos
        self.contact = set()
        self.d_state = d_state
        self.move = move
        self.isolate_duration = isolate_duration


    def step(self):
        # increment lifespan
        #self.d_state.incrementLife()
        self.d_state.decrementLifespan()
        self.isolate_duration -= 1 # decrease isolation duration

        if isinstance(self.d_state, Exposed):
            if self.d_state.lifespan == 0 :
                self.d_state = Infected()
                ls = self.random.uniform(self.model.min_infected, self.model.max_infected)*self.model.day_steps
                self.d_state.setLifespan(ls)

        elif isinstance(self.d_state, Infected):
            if self.d_state.lifespan == 0:
                self.d_state = Removed()

            if (self.d_state.assigned_lifespan - self.d_state.lifespan) == self.model.day_isolation:
                self.move = False

        # if agent not moving, stop here.
        if not self.move:
            # if isolation complete, move again
            if self.isolate_duration==0:
                self.move = True
            else:
                return

        # track agents in contact
        contents = self.model.grid.get_cell_list_contents(self.pos)      

        if len(contents)>1:
            contents.remove(self)
            for c in contents:
                if c.move:
                    self.contact.add(c.unique_id)

                # what to do to agent(s) in cell

                if isinstance(self.d_state, Infected): # infected
                    if isinstance(c.d_state, Susceptible) and c.move:
                        if self.random.random()<self.model.infection_rate: # probability of infection
                            c.d_state = Exposed()
                            ls = self.random.uniform(self.model.min_exposed, self.model.max_exposed)*self.model.day_steps
                            c.d_state.setLifespan(ls)

        # move to random adjacent cell
        x, y = self.pos
        r = self.random.random()
        if r < 0.33:
            x = x+1
        elif r < 0.66:
            x = x-1

        r = self.random.random()
        if r < 0.33:
            y = y+1
        elif r<0.66:
            y = y-1


        self.model.grid.move_agent(self, (x,y))
        

class Covid(Model):
    """
    Model class for the Covid infection model.
    """

    def __init__(self, density, minority_pc, infection_rate, min_infected, max_infected, min_exposed, 
        max_exposed, day_steps, day_isolation, height=20, width=20):
        """
        """

        self.height = height
        self.width = width
        self.density = density
        self.minority_pc = minority_pc
        self.infection_rate = infection_rate

        self.min_exposed = min_exposed
        self.max_exposed = max_exposed
        self.min_infected = min_infected
        self.max_infected = max_infected

        self.day_steps = day_steps
        self.day_isolation = day_isolation

        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, torus=True)

        self.infected = 0
        self.exposed = 0
        self.susceptible = 0
        self.removed = 0

        self.contact = 0

        self.datacollector = DataCollector(
            # Model-level count 
            {"contact": "contact", "infected": "infected", 
            "exposed":"exposed", "susceptible": "susceptible", "removed": "removed"}, 
            
            # For testing purposes, agent's individual x and y
            {"x": lambda a: a.pos[0], "y": lambda a: a.pos[1]}
        )

        # Set up agents
        # We use a grid iterator that returns
        # the coordinates of a cell as well as
        # its contents. (coord_iter)

        num_agents = 0
        num_infected = 0
        for cell in self.grid.coord_iter():
            x = cell[1]
            y = cell[2]
            if num_agents < self.density and self.random.random()>0.3:

                num_agents += 1

                if num_infected < self.minority_pc and self.random.random()>0.3:
                    agent_type = Infected()
                    num_infected += 1

                    # generate typical infected lifespan from normal distribution
                    ls = self.random.uniform(self.min_infected, self.max_infected)
                    agent_type.setLifespan(ls*self.day_steps)
                else:
                    agent_type = Susceptible()

                agent = CovidAgent((x, y), self, agent_type)
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)

        self.running = True
        #self.datacollector.collect(self)

    def step(self):
        """
        Run one step of the model. If All agents are happy, halt the model.
        """
        # Reset counters
        self.infected = 0  
        self.exposed = 0
        self.susceptible = 0
        self.removed = 0

        self.schedule.step()
               
        # compute average contact per agent
        total = 0
        for cell in self.grid.coord_iter():
            content, x, y = cell
            if content:
                for c in content:
                    total+=len(c.contact)

                    if isinstance(c.d_state, Infected):
                        self.infected += 1
                    elif isinstance(c.d_state, Exposed):
                        self.exposed += 1
                    elif isinstance(c.d_state, Susceptible):
                        self.susceptible += 1
                    elif isinstance(c.d_state, Removed):
                        self.removed += 1

        self.contact = total/self.schedule.get_agent_count()

         # collect data
        self.datacollector.collect(self)

        if self.infected+self.exposed == 0:
            self.running = False


