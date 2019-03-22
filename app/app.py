from flask import Flask
from .routes import main_routes, eos_routes, tt1_routes, page_not_found, internal_server_error
from flask_navigation import Navigation

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

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

app.register_error_handler(404, page_not_found)
app.register_error_handler(500, internal_server_error)

