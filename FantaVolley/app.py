from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fanta.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate

# Models for Students, Squads, and Games
class Squad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    total_points = db.Column(db.Integer, default=0)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    squad_id = db.Column(db.Integer, db.ForeignKey('squad.id'), nullable=False)
    played = db.Column(db.Boolean, default=False)
    total_points = db.Column(db.Integer, default=0)

    # Define relationship to access related Squad directly
    squad = db.relationship('Squad', backref='students')

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50))
    squad_id = db.Column(db.Integer, db.ForeignKey('squad.id'))
    points = db.Column(db.Integer, default=0)
    played = db.Column(db.Boolean, default=False)

    # Relationship to access related Squad directly
    squad = db.relationship('Squad', backref='games')

# Initialize the database and add students
@app.before_first_request
def initialize_data():
    db.create_all()

    # Create Squads
    if not Squad.query.first():  # Check if squads are already created
        squad1 = Squad(name="Squadra Gumiero")
        squad2 = Squad(name="Squadra Salvo")
        db.session.add(squad1)
        db.session.add(squad2)
        db.session.commit()

    # Create Students
    squad1 = Squad.query.filter_by(name="Squadra Gumiero").first()
    squad2 = Squad.query.filter_by(name="Squadra Salvo").first()

    students_squad1 = [
        "Alessandro Gumiero", "Matteo Bodlli", "Jabir Ali", 
        "Daniele Locatelli", "Lorenzo Ricali", 
        "Andrea Umer Rigamonti", "Martina Mascheroni"
    ]
    students_squad2 = [
        "Manuel Barindelli", "Laura Bramani", "Andrea Ghisolfi", 
        "Nicolo Narciso", "David Palazzo", "Gabriele Salvo", 
        "Matteo Tonet", "Yassin Yachou", "Sara Zorzan"
    ]

    if not Student.query.first():  # Only add students if not already in the database
        for student_name in students_squad1:
            student = Student(name=student_name, squad_id=squad1.id)
            db.session.add(student)

        for student_name in students_squad2:
            student = Student(name=student_name, squad_id=squad2.id)
            db.session.add(student)

        db.session.commit()

# Home route to view students, squads, and game history
@app.route('/')
def dashboard():
    squads = Squad.query.all()
    students = Student.query.all()
    games = Game.query.order_by(Game.id.desc()).limit(10).all()  # Fetch last 10 games
    return render_template('dashboard.html', squads=squads, students=students, games=games)

@app.route('/add_game', methods=['GET', 'POST'])
def add_game():
    if request.method == 'POST':
        date = request.form['date']
        gumiero_points = int(request.form['gumiero_points'])
        salvo_points = int(request.form['salvo_points'])
        gumiero_not_played = int(request.form['gumiero_not_played'])
        salvo_not_played = int(request.form['salvo_not_played'])

        # Validate the number of players who did not play
        if not (0 <= gumiero_not_played <= 7):
            return "Invalid input for Squadra Gumiero!", 400
        if not (0 <= salvo_not_played <= 9):
            return "Invalid input for Squadra Salvo!", 400

        # Calculate total points with penalties
        gumiero_total = gumiero_points - (gumiero_not_played * 7)
        salvo_total = salvo_points - (salvo_not_played * 7)

        # Update squad points
        gumiero_squad = Squad.query.filter_by(name="Squadra Gumiero").first()
        salvo_squad = Squad.query.filter_by(name="Squadra Salvo").first()

        gumiero_squad.total_points += gumiero_total
        salvo_squad.total_points += salvo_total

        # Add the game to the database
        new_game_gumiero = Game(date=date, squad_id=gumiero_squad.id, points=gumiero_points, played=True)
        new_game_salvo = Game(date=date, squad_id=salvo_squad.id, points=salvo_points, played=True)

        db.session.add(new_game_gumiero)
        db.session.add(new_game_salvo)
        db.session.commit()

        return redirect(url_for('dashboard'))

    squads = Squad.query.all()
    students = Student.query.all()
    return render_template('add_game.html', squads=squads, students=students)

if __name__ == '__main__':
    app.run(debug=True)
