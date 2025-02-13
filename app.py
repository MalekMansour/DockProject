import mysql.connector
from flask import Flask, request, jsonify

app = Flask(__name__)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost", 
        port=3307,  # PORT FOR DOCKER
        user="root",
        password="password",
        database="student"
    )

# Student table (updated schema without presentDate)
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS students (
            studentID INT AUTO_INCREMENT PRIMARY KEY,  -- Auto-incrementing studentID
            first_name VARCHAR(100) NOT NULL,  -- First name
            last_name VARCHAR(100) NOT NULL,  -- Last name
            course VARCHAR(100) NOT NULL  -- Course name up to 100 chars
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Call create_table() at startup
create_table()

# Root route
@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Student API! Use /student for POST and GET requests."})

# Route to create a student
@app.route('/student', methods=['POST'])
def create_student():
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    course = data.get('course')

    # Ensure all fields are provided in the request
    if not first_name or not last_name or not course:
        return jsonify({"error": "Missing data"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (first_name, last_name, course) VALUES (%s, %s, %s)",
                   (first_name, last_name, course))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Student added successfully"}), 201

# Route to get all students
@app.route('/student', methods=['GET'])
def get_students():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT studentID, first_name, last_name, course FROM students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(students)

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
