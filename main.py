from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


@app.route("/")
def home():
    return render_template("index.html")
    
@app.route("/random")
def random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)

    return jsonify(cafe={
        "id": random_cafe.id,
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        "seats": random_cafe.seats,
        "has_toilet": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "has_sockets": random_cafe.has_sockets,
        "can_take_calls": random_cafe.can_take_calls,
        "coffee_price": random_cafe.coffee_price,
    })


@app.route("/all")
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    #This uses a List Comprehension but you could also split it into 3 lines.
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


@app.route("/add", methods=['POST'])
def add():
    cafe_to_insert = Cafe()

    cafe_to_insert.name = request.form.get("name")
    cafe_to_insert.location = request.form.get("location")
    cafe_to_insert.seats = request.form.get("seats")
    cafe_to_insert.img_url = request.form.get("img_url")
    cafe_to_insert.can_take_calls = bool(request.form.get("can_take_calls"))
    cafe_to_insert.coffee_price = request.form.get("coffee_price")
    cafe_to_insert.has_sockets = bool(request.form.get("has_sockets"))
    cafe_to_insert.has_wifi = bool(request.form.get("has_wifi"))
    cafe_to_insert.has_toilet = bool(request.form.get("has_toilet"))
    cafe_to_insert.map_url = request.form.get("map_url")
    db.session.add(cafe_to_insert)
    db.session.commit()
    return jsonify(response={"Success": "Successfully added the cafe."})


@app.route("/update-price/<cafe_id>", methods=['PATCH'])
def update_price(cafe_id):

    cafe_selected = Cafe.query.get(cafe_id)
    if cafe_selected:
        cafe_selected.coffee_price = request.form.get("new_price")
        db.session.commit()

        return jsonify(response={"Success": "Successfully changed the price."}),200
    else:
        return jsonify(response={"Error": "Babayı buldun."}),404


@app.route("/report-closed/<int:cafe_id>", methods=['DELETE'])
def report_closed(cafe_id):
    cafe_selected = Cafe.query.get(cafe_id)
    key = request.args.get("api-key")
    if  key == "yarak":

        if cafe_selected:
            db.session.delete(cafe_selected)
            db.session.commit()
            return jsonify(response={"Success": "Successfully deleted the cafe."}),200
        else:
            return jsonify(response={"Error": "Coffee does not found."}),404
    else:
        return jsonify(response={"Error": "You have no permission to delete."}), 403


if __name__ == '__main__':
    app.run(debug=True)
