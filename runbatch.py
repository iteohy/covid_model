from model import Covid
from mesa.batchrunner import BatchRunner
import time

def getInfected(model):
    return model.cuminfected

def getDays(model):
    return model.schedule.steps/model.day_steps

def getStats(model):
    return model.stats

# comm params
comm_model_params = {
    #"width": 600,
    "density": 50000,
    "infection_rate": 0.7,
    "min_infected": 17,
    "max_infected": 24,
    "mean_infected": 20,
    "min_exposed": 3.78,
    "max_exposed": 6.78,
    "mean_exposed": 5.2,
    "day_steps": 3,
    "initial_infected": 2,
    "day_isolation": 5,
    "detection_rate": 0.7
}
comm_variable_params = {
    #"infection_rate": [0.3, 0.5, 0.7, 0.9],
    #"detection_rate": [0.3, 0.5, 0.7, 0.9],
    #"day_isolation": [3, 5, 7, 9, 11, 13, 15]
    "width": [300]
}

# dorm params
dorm_model_params = {

    #"width": 200,
    #"density": 5000,
    "initial_infected": 5,

    "infection_rate": 0.3,

    "min_infected": 17,
    "max_infected": 24,
    "mean_infected": 20,
    "min_exposed": 3.78,
    "max_exposed": 6.78,
    "mean_exposed": 5.2,
    
    "day_steps": 5,
    "day_isolation": 5,
    "detection_rate": 0.7
}
dorm_variable_params = {
    #"initial_infected": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    #"infection_rate": [0.3, 0.5, 0.7, 0.9]
    #"day_isolation": [3, 5, 7, 9, 11, 13, 15]
   	
   	# grid size
   	#"width": [100, 200, 300, 400, 500]
   	
   	# number of agents
   	#"density": [1000, 2000, 3000, 4000, 5000]
   	
   	# density
   	"width": [100]
   	"density": [1000]
}

# assign active params
model_params = dorm_model_params
variable_params = dorm_variable_params

batch_run = BatchRunner(Covid, variable_params, model_params, iterations=5, max_steps=200*dorm_model_params['day_steps'], 
                        model_reporters={"infected": getInfected, "days":getDays, "stats":getStats})
batch_run.run_all()

data = batch_run.get_model_vars_dataframe()

data['total_infected'] = data['infected']+data['initial_infected']
data['%'] = 100*data['total_infected']/model_params['density']
data.to_csv("agents_%d.csv"%int(time.time()), index=False)

#
#sdata = data[["initial_infected", "width", "days", "total_infected", "%"]]
#sdata = sdata.groupby(['initial_infected', 'width']).mean()
#sdata.to_csv("width_grouped_%d.csv"%int(time.time()), index=True)

