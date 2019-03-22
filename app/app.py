from flask import Flask
from .routes import main_routes, eos_routes, tt1_routes
from flask_navigation import Navigation

app = Flask(__name__)


nav = Navigation(app)
nav.Bar('top', [
    nav.Item('Home', 'main.home'),
    nav.Item('tt1', 'tt1.tt1'),
    nav.Item('EoS', 'eos.eos', items=[
        nav.Item('Equation of State', 'eos.eos'),
        nav.Item('T-S-Diagram', 'eos.ts'),
    ]),
])

app.register_blueprint(main_routes)
app.register_blueprint(eos_routes)
app.register_blueprint(tt1_routes)

