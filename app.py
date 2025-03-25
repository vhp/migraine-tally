#!/usr/bin/env python3
"""
Migraine Tally - A simple Flask application to log and track migraines
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_wtf.csrf import CSRFProtect
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///headaches.db"
app.config["SECRET_KEY"] = os.environ.get('FLASK_SECRET_KEY') or os.urandom(24)
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

class Migraine(db.Model):
    """
    Migraine model to store migraine episodes and their characteristics
    """
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(
        db.DateTime, default=datetime.now(ZoneInfo("UTC"))
    )
    aura = db.Column(db.Boolean, default=False)
    headache = db.Column(db.Boolean, default=False)
    haze = db.Column(db.Boolean, default=False)
    abortive_medicine = db.Column(db.Boolean, default=False)
#    severity = db.Column(db.Integer, default=0)  # 0-10 scale
#    notes = db.Column(db.Text, default="")

@app.route("/")
def index():
    """
    Main page showing the form to add migraines and a list of recorded migraines
    """
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of entries per page
    migraines = Migraine.query.order_by(Migraine.timestamp.desc()).paginate(page=page, per_page=per_page)
    return render_template("index.html", migraines=migraines)

@app.route("/add", methods=["POST"])
def add_migraines():
    """
    Add a new migraine record
    """
    # At least one symptom should be selected
    if not any([
        request.form.get("aura") == "on",
        request.form.get("headache") == "on",
        request.form.get("haze") == "on"
    ]):
        flash('Please select at least one symptom', 'error')
        return redirect(url_for("index"))

    new_migraines = Migraine(
        aura=request.form.get("aura") == "on",
        headache=request.form.get("headache") == "on",
        haze=request.form.get("haze") == "on",
        abortive_medicine=request.form.get("abortive_medicine") == "on",
    )
    try:
        db.session.add(new_migraines)
        db.session.commit()
        flash('Migraine log added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding migraine: {str(e)}', 'error')

    return redirect(url_for("index"))

@app.route("/delete/<int:id>", methods=["POST"])
def delete_migraine(id):
    """
    Delete a migraine record
    """
    migraine = Migraine.query.get_or_404(id)
    db.session.delete(migraine)
    db.session.commit()
    flash('Migraine log deleted.', 'success')
    return redirect(url_for("index"))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_migraine(id):
    """
    Edit an existing migraine record
    """
    migraine = Migraine.query.get_or_404(id)
    if request.method == "POST":
        # Add validation - at least one symptom should be selected
        if not any([
            request.form.get("aura") == "on",
            request.form.get("headache") == "on",
            request.form.get("haze") == "on"
        ]):
            flash('Please select at least one symptom', 'error')
            return render_template("edit.html", migraine=migraine)

        migraine.aura = request.form.get("aura") == "on"
        migraine.headache = request.form.get("headache") == "on"
        migraine.haze = request.form.get("haze") == "on"
        migraine.abortive_medicine = request.form.get("abortive_medicine") == "on"
        db.session.commit()
        flash('Migraine log updated successfully!', 'success')
        return redirect(url_for("index"))
    return render_template("edit.html", migraine=migraine)

def calculate_stats(view_type, ranges):
    """
    Calculate migraine statistics across different time ranges

    Args:
        view_type: Either 'events' or 'days'
        ranges: List of day ranges to calculate stats for

    Returns:
        Dictionary with stats for each time range
    """
    today = datetime.now(ZoneInfo("UTC")).date()
    stats = {}

    for days in ranges:
        start_date = today - timedelta(days=days)

        if view_type == "events":
            query = Migraine.query.filter(Migraine.timestamp >= start_date)
            total_count = query.count()
            aura_count = query.filter(Migraine.aura == True).count()
            headache_count = query.filter(Migraine.headache == True).count()
            haze_count = query.filter(Migraine.haze == True).count()
            medicine_count = query.filter(Migraine.abortive_medicine == True).count()
        else:  # 'days' view
            base_query = (
                db.session.query(func.date(Migraine.timestamp).label("date"))
                .filter(Migraine.timestamp >= start_date)
                .distinct()
            )
            total_count = base_query.count()
            aura_count = base_query.filter(Migraine.aura == True).count()
            headache_count = base_query.filter(Migraine.headache == True).count()
            haze_count = base_query.filter(Migraine.haze == True).count()
            medicine_count = base_query.filter(
                Migraine.abortive_medicine == True
            ).count()

        stats[days] = {
            "total": total_count,
            "aura": aura_count,
            "headache": headache_count,
            "haze": haze_count,
            "medicine": medicine_count,
        }

    return stats

@app.route("/stats")
def stats():
    """
    Display statistics about migraine frequency over different time periods
    """
    view_type = request.args.get("view", "events")
    ranges = [30, 60, 90, 180, 365]
    stats = calculate_stats(view_type, ranges)
    return render_template("stats.html", stats=stats, view_type=view_type)

@app.route("/chart")
def chart_view():
    """
    Display visual charts of migraine statistics
    """
    view_type = request.args.get("view", "events")
    ranges = [30, 60, 90, 180, 365]
    stats = calculate_stats(view_type, ranges)
    return render_template("chart.html", stats=stats, view_type=view_type)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=False)
