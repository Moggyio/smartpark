from flask import Flask, render_template, request, redirect, url_for
import pymysql
from datetime import datetime

# Flask app
app = Flask(__name__)

# Database config
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Bo92mloboa$',
    'database': 'car_park_db'
}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

# ---------------- ROUTES ---------------- #

@app.route("/")
def dashboard():
    """Dashboard showing all number plates and parking info"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM number_plates ORDER BY id DESC")
    plates = cursor.fetchall()

    # Calculate parking spaces
    cursor.execute("SELECT COUNT(*) AS total FROM space_status")
    total_spaces = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS occupied FROM number_plates WHERE time_out IS NULL")
    occupied = cursor.fetchone()["occupied"]
    free_spaces = total_spaces - occupied

    conn.close()
    return render_template("dashboard.html", plates=plates, total=total_spaces, free=free_spaces)

@app.route("/edit/<int:plate_id>", methods=["GET", "POST"])
def edit_plate(plate_id):
    """Edit time_in and time_out for a plate"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == "POST":
        time_in = request.form["time_in"]
        time_out = request.form["time_out"]
        cursor.execute(
            "UPDATE number_plates SET time_in=%s, time_out=%s WHERE id=%s",
            (time_in, time_out, plate_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))

    cursor.execute("SELECT * FROM number_plates WHERE id=%s", (plate_id,))
    plate = cursor.fetchone()
    conn.close()
    return render_template("edit.html", plate=plate)

if __name__ == "__main__":
    app.run(debug=True)
