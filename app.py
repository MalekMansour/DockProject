import mysql.connector
from flask import Flask, request, jsonify

app = Flask(__name__)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # HOST for container
        port=3307,  # PORT for container
        user="root",
        password="password",
        database="student"
    )

# Create students table if not exists
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            studentID INT PRIMARY KEY,  
            studentName VARCHAR(100) NOT NULL,  
            course VARCHAR(100) NOT NULL,  
            presentDate DATE NOT NULL  
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

create_table()

# Welcome route
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Student API!"})

# Route to create a student
@app.route('/student', methods=['POST'])
def create_student():
    data = request.json
    studentID = data.get('studentID')  
    studentName = data.get('studentName')
    course = data.get('course')
    presentDate = data.get('presentDate')

    # Ensure all fields are provided
    if not studentID or not studentName or not course or not presentDate:
        return jsonify({"error": "Missing data"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if student exists
    cursor.execute("SELECT * FROM students WHERE studentID = %s", (studentID,))
    existing_student = cursor.fetchone()
    
    if existing_student:
        cursor.close()
        conn.close()
        return jsonify({"error": "Student already exists"}), 409  # HTTP 409 Conflict

    # Insert new student
    cursor.execute(
        "INSERT INTO students (studentID, studentName, course, presentDate) VALUES (%s, %s, %s, %s)",
        (studentID, studentName, course, presentDate)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Student added successfully"}), 201

# Route to get all students (always /student and not /students)
@app.route('/student', methods=['GET'])
def get_students():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT studentID, studentName, course, presentDate FROM students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(students)

# Route to update a student's record
@app.route('/student', methods=['PUT'])
def update_student():
    data = request.json
    studentID = data.get('studentID')
    studentName = data.get('studentName')
    course = data.get('course')
    presentDate = data.get('presentDate')

    # Ensure all fields are provided
    if not studentID or not studentName or not course or not presentDate:
        return jsonify({"error": "Missing data"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if student exists
    cursor.execute("SELECT * FROM students WHERE studentID = %s", (studentID,))
    existing_student = cursor.fetchone()

    if not existing_student:
        cursor.close()
        conn.close()
        return jsonify({"error": "Student not found"}), 404  # HTTP 404 Not Found

    # Update student record
    cursor.execute(
        "UPDATE students SET studentName = %s, course = %s, presentDate = %s WHERE studentID = %s",
        (studentName, course, presentDate, studentID)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Student updated successfully"}), 200

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
