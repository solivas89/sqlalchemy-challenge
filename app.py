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
# if the file is in a different location, you have to type out the entire file path
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
ME = Base.classes.measurement
ST = Base.classes.station

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
        f"Dictionary of precipitation values<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"List of all stations in the dataset<br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"List of temperature observations of the most active station for the last year of data<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"List of the minimum temperature, the average temperature, and the max temperature for a given start or start date. (ex. 2010-01-01)<br/>"
        f"/api/v1.0/<start><br/><br/>"
        f"List of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range. (ex. 2010-01-01/2010-01-07)<br/>"
        f"/api/v1.0/<start><end><br/>"        
    )

@app.route("/api/v1.0/precipitation") #need to set this up as a dictionary []
def precipitation():
    # Create our session (link) from Python to the DB
    session=Session(engine)

    # Query date & prcp
    results = session.query(ME.date, ME.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of precipitation_values
    precipitation_values = []
    for date, prcp in results:
       precipitation_dict = {}
       precipitation_dict['date'] = date
       precipitation_dict['prcp'] = prcp
       precipitation_values.append(precipitation_dict)

    return jsonify(precipitation_values)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session=Session(engine)

    # Query stations
    results = session.query(ST.station).all()

    session.close()

    # Convert list of tuples into normal list
    station_values = list(np.ravel(results))

    return jsonify(station_values)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session=Session(engine)

    # Query the dates and temperature observations of the most active station for the last year of data
    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    sel = [ME.tobs]
    results = (session.query(*sel).\
        filter(ME.date >= previous_year).\
        filter(ME.station == 'USC00519281').all())

    session.close()

    # Convert list of tuples into normal list
    tobs_values = list(np.ravel(results))

    return jsonify(tobs_values)

@app.route("/api/v1.0/<start>")
def calc_start(start):
    # Create our session (link) from Python to the DB
    session=Session(engine)

    """ Given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than 
        and equal to the start date. 
    """
    results = session.query(func.min(ME.tobs), func.avg(ME.tobs), func.max(ME.tobs)).\
                filter(ME.date >= start).all()

    session.close()
    
    # Convert list of tuples into normal list
    calc_start = list(np.ravel(results))

    return jsonify(calc_start)

@app.route("/api/v1.0/<start>/<end>")
def calc_start_end(start, end):
    # Create our session (link) from Python to the DB
    session=Session(engine)

    """ When given the start and the end date, calculate the TMIN, TAVG, 
        and TMAX for dates between the start and end date inclusive.
    """
    results = session.query(func.min(ME.tobs), func.avg(ME.tobs), func.max(ME.tobs)).\
                filter(ME.date >= start).filter(ME.date <= end).all()

    session.close()
    
    # Convert list of tuples into normal list
    calc_start_end = list(np.ravel(results))

    return jsonify(calc_start_end)

# Define main behavior
if __name__ == '__main__':
    app.run(debug=True)
