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

    # Fixed total spaces
    total_spaces = 80  

    # Count occupied spaces (cars currently parked)
    cursor.execute("SELECT COUNT(*) AS occupied FROM number_plates WHERE time_out IS NULL")
    occupied = cursor.fetchone()["occupied"]

    free_spaces = total_spaces - occupied

    conn.close()
    return render_template("dashboard.html", plates=plates, total=total_spaces, free=free_spaces, occupied=occupied)

@app.route("/edit/<int:plate_id>", methods=["GET", "POST"])
def edit_plate(plate_id):
    """Edit time_in and time_out for a plate, calculate fee server-side"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM number_plates WHERE id=%s", (plate_id,))
    plate = cursor.fetchone()

    if request.method == "POST":
        time_in_str = request.form["time_in"]
        time_out_str = request.form["time_out"]

        # Convert string to datetime objects if provided
        time_in = datetime.strptime(time_in_str, "%Y-%m-%dT%H:%M") if time_in_str else None
        time_out = datetime.strptime(time_out_str, "%Y-%m-%dT%H:%M") if time_out_str else None

        # Calculate parking fee
        parking_fee = None
        if time_in and time_out:
            diff_hours = (time_out - time_in).total_seconds() / 3600
            if diff_hours > 0:
                parking_fee = round(diff_hours * 2.5, 2)  # $2.5/hour
            else:
                parking_fee = 0

        # Update database with new times and fee
        cursor.execute(
            "UPDATE number_plates SET time_in=%s, time_out=%s, parking_fee=%s WHERE id=%s",
            (time_in, time_out, parking_fee, plate_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))

    conn.close()
    return render_template("edit.html", plate=plate)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

