# Import the dependencies.
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import numpy as np
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )
@app.route("/api/v1.0/precipitation<br/>")
def precipitation ():
    """ Return precipitation data for the las 12 months"""
    recent_date = session.query(func.max(Measurement.date)).first()
    last_date = dt.datetime.strptime(recent_date[0], "%Y-%m-%d")
    one_year_ago = last_date - dt.timedelta(days=365)
    
    # Perform a query to retrieve the data and precipitation scores
    preci_data = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date >= one_year_ago).all()
    # convert the query results to a dictionary
    preci_dict = {date: preci for date, preci in preci_data}
    return jasonify(preci_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    # Query all stations
    results = session.query(Station.station).all()

    # Convert the list of tuples into a normal list
    stations = list(np.ravel(results))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature observations for the last 12 months."""
    # Calculate the date one year ago from the last data point
    recent_date = session.query(func.max(Measurement.date)).first()[0]
    last_date = dt.datetime.strptime(recent_date, "%Y-%m-%d")
    one_year_ago = last_date - dt.timedelta(days=365)

    # Identify the most active station
    most_active_station = session.query(Measurement.station).\
                          group_by(Measurement.station).\
                          order_by(func.count(Measurement.station).desc()).first()[0]

    # Query for the last 12 months of temperature observations for the most active station
    temp_data = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.station == most_active_station).\
                filter(Measurement.date >= one_year_ago).all()

    # Convert the list of tuples into a normal list
    temps = list(np.ravel(temp_data))
    return jsonify(temps)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX for a given start or start-end range."""
    # Select statement to calculate TMIN, TAVG, TMAX
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*sel).filter(Measurement.date >= start).all()
    else:
        results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert the results into a list
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == "__main__":
    app.run(debug=True)

