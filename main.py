import pickle
def imgPro(images):
  images=images/255.0
#Jinja2==3.0.3

def load_model():
    with open('model.pkl', 'rb') as file:
        loaded_model = pickle.load(file)
    return loaded_model