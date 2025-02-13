import mysql.connector
import datetime
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

# Updated Student table schema to match JSON format
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS students (
            studentID INT AUTO_INCREMENT PRIMARY KEY,  
            studentName VARCHAR(200) NOT NULL,  
            course VARCHAR(100) NOT NULL,  
            presentDate DATE NOT NULL  
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Call create_table() at startup
create_table()

# **Welcome Route**
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Student API!"})

# **Route to create a student**
@app.route('/student', methods=['POST'])
def create_student():
    data = request.json
    studentID = data.get('studentID')  # Not used since it's auto-incremented
    studentName = data.get('studentName')
    course = data.get('course')
    presentDate = data.get('presentDate')

    # Ensure all required fields are provided
    if not studentName or not course or not presentDate:
        return jsonify({"error": "Missing data"}), 400

    # Validate date format
    try:
        datetime.datetime.strptime(presentDate, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format, expected YYYY-MM-DD"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (studentName, course, presentDate) VALUES (%s, %s, %s)",
                   (studentName, course, presentDate))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Student added successfully"}), 201

# **Route to get all students**
@app.route('/student', methods=['GET'])
def get_students():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT studentID, studentName, course, presentDate FROM students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(students)

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
