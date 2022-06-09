from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

import random

# from flask_sqlalchemy
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
    has_toilet = db.Column(db.Boolean, default=False, nullable=False)
    # the database input for the boolean is either 1 or 0
    has_wifi = db.Column(db.Boolean, default=False, nullable=False)
    has_sockets = db.Column(db.Boolean, default=False, nullable=False)
    can_take_calls = db.Column(db.Boolean, default=False, nullable=False)
    coffee_price = db.Column(db.String(250), default=False, nullable=True)

    #  alternative method
    def to_dict(self):
        dictionary = {}
        for column in self._table_.columns:
            # column.name = key
            # and the value is the value or the getattribute of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


@app.route("/")
def home():
    return render_template("index.html")


#   in this casee we want our server to act as an api for a developer looking for a random coffee shop to give to his application user.
# to do this we do serialisation
@app.route("/random", methods=['GET'])
def random_cafe():
    coffee_place = db.session.query(Cafe).all()
    print(random.randint(1, 6))
    choice = random.choice(coffee_place)
    return jsonify(coffee_place={
        "id": choice.id,
        "name": choice.name,
        "map_url": choice.map_url,
        "img_url": choice.img_url,
        "location": choice.location,
        "has_sockets": choice.has_sockets,
        "has_toilet": choice.has_toilet,
        "has_wifi": choice.has_wifi,
        "can_take_calls": choice.can_take_calls,
        "seats": choice.seats,
        "coffee_price": choice.coffee_price, })


records = {}


@app.route("/all")
def all_cafe():
    coffee = db.session.query(Cafe).all()
    list_1 = []
    for shops in coffee:
        coffee = {
            "id": shops.id,
            "name": shops.name,
            "map_url": shops.map_url,
            "img_url": shops.img_url,
            "location": shops.location,
            "has_sockets": shops.has_sockets,
            "has_toilet": shops.has_toilet,
            "has_wifi": shops.has_wifi,
            "can_take_calls": shops.can_take_calls,
            "seats": shops.seats,
            "coffee_price": shops.coffee_price
        }
        list_1.append(coffee)
    return jsonify(list_1)


## HTTP GET - Read Record
# we use <> to collect form html page and send to url
# but we pass to url using if no html ?

@app.route("/search/<location>")
def search(location):
    # alternatively we could send a query not through passing the url.

    cafe = db.session.query(Cafe).all()
    list_2 = []
    for cof in cafe:
        if location in cof.location:
            coffee = {
                "id": cof.id,
                "name": cof.name,
                "map_url": cof.map_url,
                "img_url": cof.img_url,
                "location": cof.location,
                "has_sockets": cof.has_sockets,
                "has_toilet": cof.has_toilet,
                "has_wifi": cof.has_wifi,
                "can_take_calls": cof.can_take_calls,
                "seats": cof.seats,
                "coffee_price": cof.coffee_price
            }
            list_2.append(coffee)
        # elif location not in cof.location:
        #     failed = {'error': {
        #         "Not found": " sorry we dont have cafe data on this location"
        #     }}
        #     return jsonify(failed)

    return jsonify(list_2)


# ALternatively we dont have to pass the <location> we just pass it in
# http://127.0.0.1:5000/search?loc=Clerkenwell

@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafe:
        return jsonify(cafe.location)
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


# API to post and add to our database using the postman to test.
# we are to collect the key,value pair using the syntac request.args.get("keyword")
# This is an alternative to using a url with <> to pass variables. very good option.

## HTTP POST - Create Record
@app.route("/add", methods=['POST'])
def post_new():
    dictionary = Cafe(
        # this is how to get from a url without adding the <> in the url
        name=request.args.get("name"),
        map_url=request.args.get("map_url"),
        img_url=request.args.get("img_url"),
        location=request.args.get("location"),
        has_sockets=bool(request.args.get("has_socket")),
        # we change the request.get to a boolean data type.
        has_toilet=bool(request.args.get("has_toilet")),
        has_wifi=bool(request.args.get("has_wifi")),
        can_take_calls=bool(request.args.get("can_take_calls")),
        coffee_price=request.args.get("coffee_price"),
    )
    db.session.add(dictionary)
    print(Cafe.coffee_price)
    db.session.commit()

    answer = {
        "response": {
            "success": "successfully added new cafe"
        }
    }

    return jsonify(answer)


## HTTP PUT/PATCH - Update Record
# Patch, to handle patch requests
@app.route("/update-price/<int:cafe_id>", methods=['PATCH'])
def change_price(cafe_id):
    #     step1: we get the entry with the cafe.id.
    #  step2: we get the entry passed as a  key,value pair to the url like so()
    entry = db.session.query(Cafe).get(cafe_id)
    new_price = request.args.get("price")
    # print(entry.coffee_price)
    if entry is not None:
        entry.coffee_price = new_price
        # if we are just updating there is no need to do session.add just commit after declaring new values
        db.session.commit()

        ## HTTP DELETE - Delete Record
        return jsonify({
            "reply": {
                "done": "you have successfully updated the price"
            }
        })

    elif entry is None:
        return jsonify(
            {
                'answer': {
                    "sorry": "We couldn't find this id number in our entries"
                }
            }
        ), 404


entry_key = "TopSecretAPIKey"


@app.route("/delete/<api_key>", methods=["DELETE"])
def delete(api_key):
    if api_key == entry_key:
        cafe_id = request.args.get("entry_number")
        required = db.session.query(Cafe).get(cafe_id)
        if required is not None:
            db.session.delete(required)
            db.session.commit()
            return jsonify(
                {
                    "data": {
                        "name": required.name,
                        "location": required.location,

                    },
                    "Action": {
                        "Action": f"This entry for {required.name} has been deleted"
                    }
                }
            ), 404
        elif required is None:
            return jsonify({
                "reply": {
                    "Error": "Sorry no entry has this Id"
                }
            })

    elif api_key != entry_key:
        return jsonify({
            "Error": {
                "Error": "You don't have access to this administrative role"
            }
        }), 401


if __name__ == '__main__':
    app.run(debug=True)
