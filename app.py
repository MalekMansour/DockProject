import mysql.connector
import datetime  # Add this line
from flask import Flask, request, jsonify

app = Flask(__name__)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost", 
        port=3307,         # PORT FOR DOCKER
        user="root",
        password="password",
        database="student"
    )

# student table (updated schema)
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS students (
            studentID VARCHAR(20) PRIMARY KEY,  -- Allowing up to 20 characters for studentID
            studentName VARCHAR(255) NOT NULL,  -- Allowing long names (up to 255 chars)
            course VARCHAR(255) NOT NULL,      -- Course name can be long
            presentDate DATE NOT NULL          -- Date format YYYY-MM-DD is standard for MySQL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Call create_table() at startup
create_table()

# Route to create a student (with new data format)
@app.route('/student', methods=['POST'])
def create_student():
    data = request.json
    studentID = data.get('studentID')
    studentName = data.get('studentName')
    course = data.get('course')
    presentDate = data.get('presentDate')

    # Ensure all fields are provided in the request
    if not studentID or not studentName or not course or not presentDate:
        return jsonify({"error": "Missing data"}), 400

    try:
        datetime.datetime.strptime(presentDate, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format, expected YYYY-MM-DD"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (studentID, studentName, course, presentDate) VALUES (%s, %s, %s, %s)",
                   (studentID, studentName, course, presentDate))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Student added successfully"}), 201

# Route to get all students
@app.route('/student', methods=['GET'])
def get_students():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(students)

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)

