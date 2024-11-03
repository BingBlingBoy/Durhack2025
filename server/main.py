from flask import Flask, render_template, jsonify
from dataclasses import dataclass
from flask_htmx import HTMX, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
htmx = HTMX(app)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

@dataclass
class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f"<Region {self.name}>"

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/regions")
def regions_list():
    regions = db.session.execute(db.select(Region)).scalars().all()
    regions = [{"name": region.name, "description": region.description} for region in regions]
    return jsonify(regions)

@app.route("/hola-mundo")
def hola_mundo():
    body = "Hola Mundo!"
    return make_response(
        body,
        push_url=False,
        trigger={"event1": "A message", "event2": "Another message"},
    )

# TODO change this line of code
current = []

@app.route("/pins/<int:pin_id>", methods=['GET'])
def find_pin(pin_id):
    global current
    
    regions_response = requests.get("http://localhost:5000/regions")
    regions = regions_response.json()

    if pin_id in current:
        current.remove(pin_id)
        return make_response(
            ""
        )
    else:
        current.append(pin_id)
        response = f""" 
            <div class="bg-white">
                <p class="text-xl text-black">{regions[pin_id]["name"]}</p>
                <p class="text-sm text-black">{regions[pin_id]["description"]}</p>
            </div>

        """
        return make_response(
            response,
            push_url=False,
            trigger={"event1": "A message", "event2": "Another message"},
    )




app.run(debug=True)