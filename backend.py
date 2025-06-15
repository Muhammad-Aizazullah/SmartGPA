
import http.server
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer

DATABASE = 'gpa_calculator.db'
grade_mapping = {
    "A+": 4.0, "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D+": 1.3, "D": 1.0, "F": 0.0
}

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gpa_courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            credit_hours INTEGER NOT NULL,
            grade TEXT NOT NULL,
            grade_point REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


class GPAHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(open('index.html', 'rb').read())
        elif self.path == '/gpa':
            self.calculate_gpa()
        else:
            self.respond_error(404, "Not Found")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        if self.path == '/':
            self.add_course(data)
        else:
            self.respond_error(404, "Not Found")

    def calculate_gpa(self):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT credit_hours, grade_point FROM gpa_courses")
        rows = cursor.fetchall()

        total_points = 0
        total_credits = 0
        for credit, grade_point in rows:
            total_points += grade_point * credit
            total_credits += credit

        gpa = (total_points / total_credits) if total_credits else 0.0

        self._set_headers()
        self.wfile.write(json.dumps({"gpa": round(gpa, 2)}).encode())

    def add_course(self, data):
        try:
            course_name = data.get('course')
            credit_hours = int(data.get('credit'))
            grade = data.get('grade')

            if not course_name or not credit_hours or not grade:
                raise ValueError("Missing data")

            grade_point = grade_mapping.get(grade, 0)

            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO gpa_courses (course_name, credit_hours, grade, grade_point) VALUES (?, ?, ?, ?)",
                (course_name, credit_hours, grade, grade_point)
            )
            conn.commit()
            conn.close()

            self._set_headers()
            self.wfile.write(json.dumps({"message": "Course added successfully."}).encode())

        except Exception as e:
            self.respond_error(400, f"Invalid data: {str(e)}")

    def respond_error(self, status, message):
        self._set_headers(status)
        self.wfile.write(json.dumps({"error": message}).encode())

if __name__ == "__main__":
    init_db()
    server_address = ('', 8000)
    print("🚀 Server running at http://127.0.0.1:8000")
    httpd = HTTPServer(server_address, GPAHandler)
    httpd.serve_forever()
