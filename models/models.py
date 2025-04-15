import pickle


with open('models/sleep_quality_model.pkl', 'rb') as file:  
    SLEEP_QUALITY_MODEL = pickle.load(file)

with open('models/sleep_stage_model.pkl', 'rb') as file:  
    SLEEP_STAGE_MODEL = pickle.load(file)
