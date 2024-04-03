# Import the dependencies.
import numpy as np

import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
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
Measurement = Base.classes.measurement
Station = Base.classes.station

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
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/r>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    recent_datapoint = dt.date(2017, 8, 23)
    oneyear = recent_datapoint - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= oneyear).order_by(Measurement.date).all()
    precip_dict = dict(results)
    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    hawaii_stations = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    results = session.query(*hawaii_stations).all()
    session.close()

    stations = []
    for station, name, latitude, longitude, elevation in results:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = latitude
        station_dict["Lon"] = longitude
        station_dict["Elevation"] = elevation
        stations.append(station_dict)
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    recent_datapoint = dt.date(2017, 8, 23)
    oneyear = recent_datapoint - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station=="USC00519281").\
    filter(Measurement.date>=oneyear).all()

    tempobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["TOBS"] = tobs
        tempobs.append(tobs_dict)
    return jsonify(tempobs)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    session = Session(engine)
    recent_datapoint = dt.date(2017, 8, 23)
    oneyear = recent_datapoint - dt.timedelta(days=365)
    start = oneyear-recent_datapoint
    results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
    session.close()

    temperature = []
    for min_temp, max_temp, avg_temp in results:
        temp_dict = {}
        temp_dict["Minimum Temperature"] = min_temp
        temp_dict["Maximum Temperature"] = max_temp
        temp_dict["Average Temperature"] = avg_temp
        temperature.append(temp_dict)
    return jsonify(temperature)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
              filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temperature = []
    for min_temp, max_temp, avg_temp in results:
        temp_dict = {}
        temp_dict["Minimum Temperature"] = min_temp
        temp_dict["Maximum Temperature"] = max_temp
        temp_dict["Average Temperature"] = avg_temp
        temperature.append(temp_dict)
    return jsonify(temperature)



if __name__ == "__main__":
    app.run(debug=True)
