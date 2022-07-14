#import dependencies 
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np

from flask import Flask, jsonify

#database setup 
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station

#flask setup 
app = Flask(__name__)


#routes 
@app.route("/")
def homepage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"----------------------------------------------------------------------------------<br/>"
        f"Precipitation data: /api/v1.0/precipitation<br/>"
        f"Station info: /api/v1.0/stations<br/>"
        f"TOBS from previous year, most active station only: /api/v1.0/tobs<br/>"
        f"Temperature data for a given start date: /api/v1.0/YYYY-MM-DD<br/>"
        f"Temperature data for a given start and end date: /api/v1.0/YYYY-MM-DD/YYYY-MM-DD"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return JSON list of precipitation/date data"""

     # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query 
    prcpdata = session.query(measurement.date, measurement.prcp).order_by(measurement.date).all()
    #Close session
    session.close()

    prcpdata_cleaned = list(np.ravel(prcpdata))

    return (jsonify(prcpdata_cleaned))

@app.route("/api/v1.0/stations")
def stations():
    """Return JSON list of station data"""
    session = Session(engine)
    station_data = session.query(station.station, station.name, station.latitude, station.longitude, station.elevation).group_by(station.station).all() 
    session.close()
    station_data_cleaned = list(np.ravel(station_data))

    return (jsonify(station_data_cleaned))

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations (TOBS) for the previous year"""
    last_12_date = "2016-08-23"

    session = Session(engine)
    tobs_data = session.query(measurement.date, measurement.tobs).filter(measurement.date >= last_12_date).filter(measurement.station == 'USC00519281').order_by(measurement.date).all() 
    session.close()

    tobs_data_cleaned = list(np.ravel(tobs_data))
    return (jsonify(tobs_data_cleaned))

@app.route("/api/v1.0/<start_date>")
def start_date_temp_data(start_date):
    """Return a JSON list of the min temp, avg temp, and max temp for a given start date"""
    start_date_query = start_date 
    session = Session(engine)
    start_data = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start_date_query).all()
    session.close()

    start_data_cleaned = list(np.ravel(start_data))
    
    return (jsonify(start_data_cleaned))

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end_date_temp_data(start_date, end_date):
    """Return a JSON list of the min temp, avg temp, and max temp for a given start date"""
    start_date_query = start_date 
    end_date_query = end_date 
    session = Session(engine)
    start_end_data = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start_date_query).filter(measurement.date <= end_date_query).all()
    session.close()

    start_end_data_cleaned = list(np.ravel(start_end_data))
    return (jsonify(start_end_data_cleaned))

if __name__ == '__main__':
    app.run(debug=True)