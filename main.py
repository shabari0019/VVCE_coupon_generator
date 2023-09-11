import csv
import threading
from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

coupon_lock = threading.Lock()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Update with your database URI
db = SQLAlchemy(app)

class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    number = db.Column(db.String(15), nullable=False)
    usn = db.Column(db.String(15), unique=True, nullable=False)
    code_genarated = db.Column(db.String(20), nullable=False)

db.create_all()


@app.route('/reset/VVCE_2023')
def add():
    Coupon.query.delete()
    db.session.commit()
    with open('data2.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Create a Coupon object and insert it into the database
            coupon = Coupon(
                name=row['name'],
                usn=row['usn'],
                number=row['number'],
                code_genarated=str(0)
            )
            db.session.add(coupon)

    # Commit the changes to the database
    db.session.commit()

    return "Reset successfull "


def find_coupon_by_number(number):
    coupon = Coupon.query.filter_by(number=number, code_genarated='0').first()

    if coupon:
        name = coupon.name
        usn = coupon.usn
        coupon.code_genarated = '1'
        db.session.commit()

        return name+" - "+usn
    else:
        return None


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        number = str(request.form['number'])
        coupon_code = find_coupon_by_number(number)

        if coupon_code:
            TIME = datetime.now().strftime("%H:%M")
            DATE= date.today().strftime("%B %d, %Y")
            return render_template('index.html', coupon=coupon_code,D=(TIME,DATE))
        else:
            flash('Number not found in the database or Coupon Generated already.', 'error')
    return render_template('index.html')

if __name__ == '__main__':
    app.secret_key = 'qwertyuiop'
    app.run(debug=True)
