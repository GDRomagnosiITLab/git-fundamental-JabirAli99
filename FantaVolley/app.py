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
    total_points = db.Column(db.Integer, default=0)

    # Define relationship to access related Squad directly
    squad = db.relationship('Squad', backref='students')

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50))
    squad_id = db.Column(db.Integer, db.ForeignKey('squad.id'))
    points = db.Column(db.Integer, default=0)
    played = db.Column(db.Boolean, default=False)

# Initialize the database and add students
@app.before_first_request
def create_tables():
    db.create_all()

    # Create Squads
    if not Squad.query.first():  # Check if squads are already created
        squad1 = Squad(name="Squadra Gumiero")
        squad2 = Squad(name="Squadra Salvo")
        db.session.add(squad1)
        db.session.add(squad2)
        db.session.commit()

    # Create Students
    students = [
        "Manuel Barindelli", "Matteo Bodlli", "Laura Bramani", "Michele Fontana", 
        "Andrea Ghisolfi", "Alessandro Gumiero", "Jabir Ali", "Daniele Locatelli", 
        "Martina Mascheroni", "Nicolo Narciso", "David Palazzo", "Lorenzo Ricali", 
        "Andrea Umer Rigamonti", "Gabriele Salvo", "Matteo Tonet", "Yassin Yachou", 
        "Sara Zorzan"
    ]
    
    # Assign students to squads, assuming squad 1 for first half and squad 2 for the second half
    squad1 = Squad.query.filter_by(name="Squadra Gumiero").first()
    squad2 = Squad.query.filter_by(name="Squadra Salvo").first()

    if not Student.query.first():  # Only add students if not already in the database
        for i, student_name in enumerate(students):
            squad_id = squad1.id if i < len(students) // 2 else squad2.id
            student = Student(name=student_name, squad_id=squad_id)
            db.session.add(student)

        db.session.commit()

# Home route to view students and squads
@app.route('/')
def dashboard():
    squads = Squad.query.all()
    students = Student.query.all()
    return render_template('dashboard.html', squads=squads, students=students)

@app.route('/add_game', methods=['GET', 'POST'])
def add_game():
    if request.method == 'POST':
        # Get the game data
        date = request.form['date']
        squad_id = request.form['squad']
        points = int(request.form['points'])
        played_students_count = 0
        not_played_students_count = 0
        
        # Count the number of players who didn't play
        for student in Student.query.filter_by(squad_id=squad_id).all():
            played = request.form.get(f'played_{student.id}') == 'yes'
            if played:
                played_students_count += 1
            else:
                not_played_students_count += 1
                student.total_points -= 7  # Apply penalty of -7 for players who didn't play
            student.played = played  # Update played status
        
        # Subtract the penalty for not played players
        squad = Squad.query.get(squad_id)
        squad.total_points = points - (not_played_students_count * 7)  # Total points minus penalty

        # Add the game to the Game table
        new_game = Game(squad_id=squad_id, points=points, date=date)
        db.session.add(new_game)
        db.session.commit()

        # Update the total points for the squad
        squad.total_points = sum(student.total_points for student in Student.query.filter_by(squad_id=squad_id))
        db.session.commit()

        return redirect(url_for('dashboard'))

    squads = Squad.query.all()
    students = Student.query.all()
    return render_template('add_game.html', squads=squads, students=students)

if __name__ == '__main__':
    app.run(debug=True)
