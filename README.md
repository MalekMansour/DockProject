# Docker Project

This project is a simple Flask-based API for managing student records. It uses MySQL as the database to store student information.

It connects to a MySQL database and provides endpoints to create and retrieve student information. The database connection is established using mysql.connector, and a students table is created if it does not exist. The API includes a welcome route (/) that returns a welcome message, a route to create a new student (/student with POST method) that adds a student to the database, and a route to get all students (/student with GET method) that retrieves all student records from the database. The application runs on localhost at port 8080.
