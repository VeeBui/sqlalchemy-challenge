# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)


# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station



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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )



############################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    
    # Find the most recent date in the data set.
    recent_date = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).\
        first()[0]
    
    # Calculate the date one year from the last date in data set.
    date_12months = dt.datetime.strptime(recent_date,"%Y-%m-%d") - dt.timedelta(days=365)
    
    # Perform a query to retrieve the data and precipitation values (and station)
    prcp_12months = session.query(Measurement.date, Measurement.prcp, Measurement.station).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) > date_12months).all()
    
    
    session.close()
    
    # Create dictionary
    result = []
    for date, prcp, stn in prcp_12months:
        # STUDENT NOTE: this request initially didn't make sense to me, as there are many prcp
        # values for each date. So I redid it to make a multi-layer dictionary instead.
        # Code source: https://stackoverflow.com/questions/14790980/how-to-check-if-key-exists-in-list-of-dicts-in-python
        if any(date in d for d in result):
            # append to existing dictionary
            (curr_i, date_dict) = next((i,d) for i,d in enumerate(result) if date in d)
            station_dict = date_dict[date]
            
            station_dict[stn] = prcp
    
            # replace existing dictionary
            result[curr_i] = date_dict
        else:
            prcp_dict = {}
            station_dict = {}
    
            # create new dictionary with station as key, precip as value
            station_dict[stn] = prcp
    
            # create new diction with date as key, station_dict as value
            prcp_dict[date] = station_dict
            
            result.append(prcp_dict)

    return jsonify(result)



############################################
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    # Query stations
    station_list = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    # Create dictionary
    result = []
    for station, name, lat, lon, elev in station_list:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["lat"] = lat
        station_dict["lon"] = lon
        station_dict["elev"] = elev
        result.append(station_dict)

    return jsonify(result)



############################################
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Find the most recent date in the data set.
    recent_date = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).\
        first()[0]
    
    # Calculate the date one year from the last date in data set.
    date_12months = dt.datetime.strptime(recent_date,"%Y-%m-%d") - dt.timedelta(days=365)

    # Get most active station
    station_counts = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).\
        all()

    act_station = station_counts[0][0]

    # Get date and tobs from most active station
    act_station_12months = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == act_station).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) > date_12months).\
        all()

    session.close()

    # Create dictionary
    result = []
    for date, tobs in act_station_12months:
        ActStat_dict = {}
        ActStat_dict[date] = tobs
        result.append(ActStat_dict)

    return jsonify(result)



############################################
@app.route("/api/v1.0/<start>")
def tempByStart(start):
    session = Session(engine)

    values = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= dt.datetime.strptime(start,"%Y-%m-%d")).\
        all()

    session.close()

    # Create dictionary
    result = []
    for mn, avg, mx in values:
        tobs_stats_dict = {}
        tobs_stats_dict["min"] = mn
        tobs_stats_dict["avg"] = avg
        tobs_stats_dict["max"] = mx
        result.append(tobs_stats_dict)

    return jsonify(result)



############################################
@app.route("/api/v1.0/<start>/<end>")
def tempByStartEnd(start,end):
    session = Session(engine)

    values = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= dt.datetime.strptime(start,"%Y-%m-%d")).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) <= dt.datetime.strptime(end,"%Y-%m-%d")).\
        all()

    session.close()

    # Create dictionary
    result = []
    for mn, avg, mx in values:
        tobs_stats_dict = {}
        tobs_stats_dict["min"] = mn
        tobs_stats_dict["avg"] = avg
        tobs_stats_dict["max"] = mx
        result.append(tobs_stats_dict)

    return jsonify(result)



############################################
if __name__ == "__main__":
    app.run(debug=True)

















