from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random

app = Flask(__name__)

## CREATE DB
class Base(DeclarativeBase):
    pass
## Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


## Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)


    def to_dict(self):
        dictionary={}
        for column in self.__table__.columns:
            #Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
## Get a random cafe to Visit:
@app.route("/random")
def get_random_cafe():
        result = db.session.execute(db.select(Cafe))
        all_cafes = result.scalars().all()
        random_cafe = random.choice(all_cafes)
        return jsonify(cafe=random_cafe.to_dict())

## Get all the Cafes in our database:
@app.route("/all")
def get_all_cafes():
    result = db.session.execute(db.select(Cafe))
    all_cafe = result.scalars().all()
    all_cafes = [cafe.to_dict() for cafe in all_cafe]
    return jsonify(all=all_cafes)

## Search the cafes on Specific Location:
@app.route("/search")
def search_cafe():
    query_location = request.args.get("loc")
    query = db.select(Cafe).where(Cafe.location==query_location)
    result = db.session.execute(query)
    located_cafes = result.scalars().all()
    if not located_cafes:
        return jsonify({"error":
                        {
                            "Not Found": "We donot have cafe at this location."
                        }})
    else:
        located_cafes = [cafe.to_dict() for cafe in located_cafes]
        return jsonify(cafes=located_cafes)


    


# HTTP POST - Create Record
## Add a Cafe to the Database:

@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})

# HTTP PUT/PATCH - Update Record
## Update Price of Specific Cafe:

@app.route("/update-price/<int:id>",methods=["PATCH"])
def update_price(id):
    updated_price = request.args.get("new-price")
    cafe = Cafe.query.get(id)
    if cafe:
        cafe.coffee_price = updated_price
        db.session.commit()
        return jsonify({
            "message":"Price Updated Successfully",
        })
    else:
        return jsonify({
            "message":"Cafe with that id not found"
        })

# HTTP DELETE - Delete Record
## Delete a Cafe Record from Database:
@app.route("/report-closed/<int:id>", methods=["DELETE"])
def delete_cafe(id):
    key = request.get.args("api-key")
    if key == "SECRETAPIKEY":
        cafe = Cafe.query.get(id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify({
                "message":"Cafe deleted successfully",
            })
        else:
            return jsonify({
                "message":"Cafe with that id not found"
            })
    else:
        return jsonify({
            "message":"Make sure to add correct key"
        })


if __name__ == '__main__':
    app.run(debug=True)
