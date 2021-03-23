import numpy as np

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
Station = Base.classes.station
Measurement = Base.classes.measurement


# Flask Setup
app = Flask(__name__)

@app.route("/")
def home():
    print("Server received request for 'Home page")
    return ( 
        f"Welcome to my 'Home' page!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"/jsonified<br/>"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session link from Python to the DB
    session = Session(engine)
    # query for prcp
    results = session.query(Measurement.station, Measurement.date, Measurement.prcp)\
        .filter(Measurement.date > '2016-08-23').order_by(Measurement.date.desc()).all()
    session.close()

    # create a list of dictionaries, including the station just because
    prcp_values = []
    for row in results:
        dict = {}
        dict['station'] = row.station
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
    results = session.query(Station.station, Station.name).all()
    session.close()

    # convert list of tuples into normal list
    #all_stations = list(np.ravel(results))
    # create a list of dictionaries
    stations = []
    for row in results:
        dict = {}
        dict['station'] = row.station
        dict['name'] = row.name
        stations.append(dict)

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