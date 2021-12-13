import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# Flask Setup
app = Flask(__name__)

latest_date = (session.query(Measurement.date).order_by(Measurement.date.desc()).first())
latest_date = list(np.ravel(latest_date))[0]

latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
latest_year = int(dt.datetime.strftime(latest_date, '%Y'))
latest_month = int(dt.datetime.strftime(latest_date, '%m'))
latest_day = int(dt.datetime.strftime(latest_date, '%d'))

year_before = dt.date(latest_year, latest_month, latest_day) - dt.timedelta(days=365)
year_before = dt.datetime.strftime(year_before, '%Y-%m-%d')

# Flask Routes
@app.route("/")
def home():
    return (f"Welcome to Surf's Up!: Hawaii's Climate API for vacation <br/>"
            f" Available Routes:<br/>"
            f"/api/v1.0/precipitaton ~~ This year's rain data is here<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"~~~ datesearch (yyyy-mm-dd)  Input any date data available from 2010-01-01 to 2017-08-23<br/>"
            f"/api/v1.0/datesearch/2015-05-30  ~~~~~~~~~~~ Historical Low, High, and Average temperatures for date you need<br/>"
            f"/api/v1.0/datesearch/2015-05-30/2017-08-23 ~~ Low, High, and Average temperatures for date rage.<br/>"
            )

@app.route("/api/v1.0/precipitaton")
def precipitation():

    results = (session.query(Measurement.date, Measurement.prcp, Measurement.station).filter(Measurement.date > year_before).order_by(Measurement.date).all())
        
    prec_data = []
    for result in results:
            prec_dict = {result.date: result.prcp, "Station": result.station}
            prec_data.append(prec_dict)

    return jsonify(prec_data)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def temperature():

    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station).filter(Measurement.date > year_before).order_by(Measurement.date).all())

    tempData = []
    for result in results:
        tempDict = {result.date: result.tobs, "Station": result.station}
        tempData.append(tempDict)

    return jsonify(tempData)

@app.route('/api/v1.0/datesearch/<startDate>')
def start(startDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate).group_by(Measurement.date).all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

@app.route('/api/v1.0/datesearch/<startDate>/<endDate>')
def startEnd(startDate, endDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= endDate)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

if __name__ == '__main__':
    app.run(debug=True)