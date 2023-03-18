from api import create_app
from api.config.config import config_dict

# Create app
app = create_app(config=config_dict['dev'])

if __name__=="__main__":
    # Run app in debug mode
    app.run(debug=True)