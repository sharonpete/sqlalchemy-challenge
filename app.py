import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save the reference to the tables
station = Base.classes.station
measurement = Base.classes.measurement


# Flask Setup
app = Flask(__name__)

@app.route("/")
def home():
    print("Server received request for 'Home page")
    return ( 
        f"Welcome to my 'Home' page!<br/>"
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>Precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>Stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>TOBS - Temperature Observations</a><br/>"
        f"<a href='/api/v1.0/start'>Start</a><br/>"
        f"<a href='/api/v1.0/start/end'>Start - End</a><br/>"
       
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session link from Python to the DB
    session = Session(engine)

    # Find the most recent date in the data set, convert string format to date.
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    most_recent_date = (dt.datetime.strptime(most_recent_date, '%Y-%m-%d')).date()

    # Calculate the date one year prior to the most recent date in dataset
    analysis_start_date = most_recent_date - dt.timedelta(days=365)

    # query for prcp
    prcp_data = session.query(measurement.date, measurement.prcp).\
    filter((measurement.date <= most_recent_date) & (measurement.date >= analysis_start_date)).all()
    session.close()

    # create a list of dictionaries, including the station just because
    prcp_values = []
    for row in prcp_data:
        dict = {}
        dict['date'] = row.date
        dict['prcp'] = row.prcp
        prcp_values.append(dict)

    print("Server received request for /api/v1.0/precipitation")
    return jsonify(prcp_values)

@app.route("/api/v1.0/stations")
def stations():
     # Create our session link from Python to the DB
    session = Session(engine)
    # query for stations
    results = session.query(station.station, station.name).all()
    session.close()

    # create a list of dictionaries
    stations = []
    for row in results:
        stations.append(row.station)

    print("Server received request for /api/v1.0/stations")
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
     # Create our session link from Python to the DB
    session = Session(engine)
    
    # Design a query to find the most active station (i.e. what station has the most rows?)
    results = session.query(measurement.station, func.count(measurement.station), station.name, station.id).\
        order_by(func.count(measurement.station).desc()).\
        group_by(measurement.station).all()
    most_active = results[0][0]

    # Return a JSON list of temperature observations (TOBS) for the previous year
    # Find the most recent date in the data set, convert string format to date.
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    most_recent_date = (dt.datetime.strptime(most_recent_date, '%Y-%m-%d')).date()

    # Calculate the date one year prior to the most recent date in dataset
    analysis_start_date = most_recent_date - dt.timedelta(days=365)
    
    results = session.query(measurement.tobs).\
        filter((measurement.station == most_active) \
        & (measurement.date <= most_recent_date) \
        & (measurement.date >= analysis_start_date)).all()

    session.close()

    # create a list of dictionaries
    tobs = []
    for row in results:
        tobs.append(row.tobs)

    print("Server received request for /api/v1.0/tobs")
    return jsonify(tobs)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def tobs_summary(start=None, end=None):
    # Create our session link from Python to the DB
    session = Session(engine)
    
    print("Start date:"+start)
    if end:
        print("End date: "+end)
    
    # query for stations
    if not end:
        results = session.query(func.min(measurement.tobs),func.max(measurement.tobs),\
            func.avg(measurement.tobs)).filter(measurement.date >= start)\
            .filter(measurement.tobs != 'None').all()
    else:
        results = session.query(func.min(measurement.tobs),func.max(measurement.tobs),\
            func.avg(measurement.tobs))\
            .filter((measurement.date >= start) & (measurement.date <= end))\
            .filter(measurement.tobs != 'None').all()
   

    session.close()

    summary = []
    for row in results:
        dict = {}
        dict['start date'] = start
        if end:
            dict['end date'] = end

        dict['tobs min'] = row[0]
        dict['tobs max'] = row[1]
        dict['tobs avg'] = row[2]
        summary.append(dict)


    print("Server received request for /api/v1.0/<start>")
    return jsonify(summary)




if __name__ == "__main__":
    app.run(debug=True)