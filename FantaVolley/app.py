from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fanta.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
    points_per_game = db.Column(db.Integer, default=0)
    total_points = db.Column(db.Integer, default=0)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    points = db.Column(db.Integer, default=0)
    played = db.Column(db.Boolean, default=False)

# Home route to view students and squads
@app.route('/')
def dashboard():
    squads = Squad.query.all()
    students = Student.query.all()
    return render_template('dashboard.html', squads=squads, students=students)


@app.route('/add_game', methods=['GET', 'POST'])
def add_game():
    if request.method == 'POST':
        student_id = request.form['student_id']
        points = int(request.form['points'])
        played = request.form['played'] == 'yes'

        # Get student and update game details
        student = Student.query.get(student_id)
        student.played = played
        student.points_per_game = points if played else 0
        student.total_points += points if played else -7

        # Update squad's total points
        squad = Squad.query.get(student.squad_id)
        squad.total_points = sum([s.total_points for s in Student.query.filter_by(squad_id=squad.id)])

        # Add new game to the Games table
        new_game = Game(student_id=student_id, points=points, played=played)
        db.session.add(new_game)
        db.session.commit()

        return redirect(url_for('dashboard'))

    students = Student.query.all()
    return render_template('add_game.html', students=students)


# Initialize the database
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
