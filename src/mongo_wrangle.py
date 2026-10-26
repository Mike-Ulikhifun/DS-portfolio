"""
MongoDB Data Wrangling Module for Nairobi Air Quality Data

This module provides functions to retrieve and clean air quality data
from MongoDB for time series analysis.
"""

import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi

def wrangle_data(uri):
    """
    Retrieve and clean Nairobi air quality data from MongoDB.
    """

    

    # MongoDB database and collection
    db = "air-quality"
    collection = "nairobi"

      # Connect to MongoDB
    client = MongoClient(uri, server_api=ServerApi("1"))

    # Query and clean data using method chaining
    return(
        pd.DataFrame(
            list(
                client[db][collection]
                .find({"value_type": "P2"}, 
                      projection={"value": 1, "timestamp": 1, "_id": 0})
                .sort("timestamp", 1)
            )
        )
        # Convert timestamp to datetime
        .assign(timestamp=lambda x: pd.to_datetime(x["timestamp"]))
        # Set timezone (data is in UTC, convert to Nairobi time)
        .assign(timestamp=lambda x: x["timestamp"].dt.tz_localize("UTC").dt.tz_convert("Africa/Nairobi"))
        # Set index
        .set_index("timestamp")
        # Handle missing values
        .dropna()
        # Sort chronologically
        .sort_index()
        # Rename column for clarity
        .rename(columns={"value": "pm25"})
    )
