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
        f"<a href='/jsonified'>JSON</a><br/>"

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
    # results = session.query(Measurement.station, Measurement.date, Measurement.prcp)\
    #     .filter(Measurement.date > '2016-08-23').order_by(Measurement.date.desc()).all()
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
        # dict = {}
        # dict['name'] = row.name
        # dict['station'] = row.station
        stations.append(row.station)

    print("Server received request for /api/v1.0/stations")
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
     # Create our session link from Python to the DB
    session = Session(engine)
    # query for stations
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00516128').\
            filter(Measurement.date > '2016-08-23').order_by(Measurement.date.desc()).\
            filter(Measurement.tobs != 'None').all()
    session.close()

    
    # create a list of dictionaries
    tobs = []
    for row in results:
        dict = {}
        dict['date'] = row.date
        dict['tobs'] = row.tobs
        tobs.append(dict)

    print("Server received request for /api/v1.0/tobs")
    return jsonify(tobs)


@app.route("/api/v1.0/<start>")
def tobs_summary(start):

    # Create our session link from Python to the DB
    session = Session(engine)
    # query for stations
    results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),\
        func.avg(Measurement.tobs)).filter(Measurement.date >= start)\
            .filter(Measurement.tobs != 'None').all()
   

    session.close()

    # convert list of tuples into normal list
    #summary = list(np.ravel(results))
    summary = []
    for row in results:
        dict = {}
        dict['start date'] = start
        dict['tobs min'] = row[0]
        dict['tobs max'] = row[1]
        dict['tobs avg'] = row[2]
        summary.append(dict)


    print("Server received request for /api/v1.0/<start>")
    return jsonify(summary)


@app.route("/api/v1.0/<start>/<end>")
def other_tobs_summary(start,end):

    # Create our session link from Python to the DB
    session = Session(engine)
    # query for stations
    results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),\
        func.avg(Measurement.tobs)).filter(Measurement.date >= start)\
        .filter(Measurement.date <= end).filter(Measurement.tobs != 'None').all()
   

    session.close()

    # convert list of tuples into normal list
    #summary = list(np.ravel(results))
    summary = []
    for row in results:
        dict = {}
        dict['start date'] = start
        dict['end date'] = end
        dict['tobs min'] = row[0]
        dict['tobs max'] = row[1]
        dict['tobs avg'] = row[2]
        summary.append(dict)


    print("Server received request for /api/v1.0/<start>/<end>")
    return jsonify(summary)


if __name__ == "__main__":
    app.run(debug=True)