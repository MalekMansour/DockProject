import jwt
import datetime
from functools import wraps
from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure key

# ---------------------------------
# JWT Authentication Setup
# ---------------------------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Expect the token in the Authorization header as "Bearer <token>"
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            parts = auth_header.split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except Exception as e:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
def login():
    auth = request.json
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Missing credentials'}), 401

    # For demonstration, we use hardcoded credentials. Replace this with a proper user check.
    if auth['username'] != 'admin' or auth['password'] != 'admin':
        return jsonify({'message': 'Invalid credentials'}), 401

    token = jwt.encode({
        'user': auth['username'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({'token': token})

# ---------------------------------
# Database Setup & Helper Functions
# ---------------------------------
def create_database():
    conn = mysql.connector.connect(
        host="localhost",
        port=3307,
        user="root",
        password="password"
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS StudentDB")
    conn.commit()
    cursor.close()
    conn.close()

create_database()

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # If using Docker, consider "host.docker.internal" for host MySQL connections
        port=3307,
        user="root",
        password="password",
        database="StudentDB"
    )

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

# ---------------------------------
# API Endpoints (Protected by JWT)
# ---------------------------------
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Student API!"})

@app.route('/student', methods=['POST'])
@token_required
def create_student():
    data = request.json
    studentID = data.get('studentID')
    studentName = data.get('studentName')
    course = data.get('course')
    presentDate = data.get('presentDate')

    if not studentID or not studentName or not course or not presentDate:
        return jsonify({"error": "Missing data"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE studentID = %s", (studentID,))
    existing_student = cursor.fetchone()

    if existing_student:
        cursor.close()
        conn.close()
        return jsonify({"error": "Student already exists"}), 409

    cursor.execute(
        "INSERT INTO students (studentID, studentName, course, presentDate) VALUES (%s, %s, %s, %s)",
        (studentID, studentName, course, presentDate)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Student added successfully"}), 201

@app.route('/students', methods=['GET'])
@token_required
def get_students():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT studentID, studentName, course, presentDate FROM students"
        cursor.execute(query)
        students = cursor.fetchall()
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    finally:
        cursor.close()
        conn.close()
    return jsonify(students), 200

@app.route('/student/<int:studentID>', methods=['GET'])
@token_required
def get_student(studentID):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT studentID, studentName, course, presentDate FROM students WHERE studentID = %s"
        cursor.execute(query, (studentID,))
        student = cursor.fetchone()
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    finally:
        cursor.close()
        conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(student), 200

@app.route('/student', methods=['PUT'])
@token_required
def update_student():
    data = request.json
    studentID = data.get('studentID')
    studentName = data.get('studentName')
    course = data.get('course')
    presentDate = data.get('presentDate')

    if not studentID or not studentName or not course or not presentDate:
        return jsonify({"error": "Missing data"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE studentID = %s", (studentID,))
    existing_student = cursor.fetchone()

    if not existing_student:
        cursor.close()
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    cursor.execute(
        "UPDATE students SET studentName = %s, course = %s, presentDate = %s WHERE studentID = %s",
        (studentName, course, presentDate, studentID)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Student updated successfully"}), 200

@app.route('/student/<int:studentID>', methods=['DELETE'])
@token_required
def delete_student(studentID):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE studentID = %s", (studentID,))
    existing_student = cursor.fetchone()

    if not existing_student:
        cursor.close()
        conn.close()
        return jsonify({"error": "Student does not exist"}), 404

    cursor.execute("DELETE FROM students WHERE studentID = %s", (studentID,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Student deleted successfully"}), 200

# ---------------------------------
# Run the Flask App
# ---------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
