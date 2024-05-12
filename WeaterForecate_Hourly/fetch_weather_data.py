from fastapi import APIRouter, Query
from retry_requests import retry
from dotenv import load_dotenv
import openmeteo_requests
import requests_cache
import pandas as pd
import os

router = APIRouter()
load_dotenv()

URL_API = os.getenv("URL_API")

def fetch_weather_data_search(start_date, end_date):
    try:
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = URL_API
        params = {
            "latitude": 18,
            "longitude": 105,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature", "precipitation", "rain", "wind_speed_10m"],
            "timezone": "Asia/Bangkok"
        }
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()

        # Prepare hourly data
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            ),
            "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
            "relative_humidity_2m": hourly.Variables(1).ValuesAsNumpy(),
            "dew_point_2m": hourly.Variables(2).ValuesAsNumpy(),
            "apparent_temperature": hourly.Variables(3).ValuesAsNumpy(),
            "precipitation": hourly.Variables(4).ValuesAsNumpy(),
            "rain": hourly.Variables(5).ValuesAsNumpy(),
            "wind_speed_10m": hourly.Variables(6).ValuesAsNumpy()
        }

        # Create DataFrame
        hourly_dataframe = pd.DataFrame(data=hourly_data)

        # Handle NaN values
        hourly_dataframe.fillna(0, inplace=True)  # Replace NaN with 0, you can choose another value or method for handling NaN

        return hourly_dataframe

    except Exception as e:
        # Handle the exception (e.g., log the error, return a default value, etc.)
        print(f"An error occurred: {e}")
        return None

date_pattern = r'^\d{4}-\d{2}-\d{2}$'

@router.get('/fetch-weather-H')
async def get_weather_data(
    start_date: str = Query(default='2023-03-26', description="Start date in YYYY-MM-DD ",regex=date_pattern),
    end_date: str = Query(default='2023-03-26', description="End date in YYYY-MM-DD ",regex=date_pattern)
    ):
    # Call your fetch_weather_data function with the provided parameters
    weather_data = fetch_weather_data_search(start_date, end_date)
    
    # Handle NaN values in the DataFrame
    weather_data = weather_data.fillna(0)  # Replace NaN values with 0 or any other appropriate value
    
    return {"weather_data": weather_data.to_dict()}


app = APIRouter()
app.include_router(router, prefix='/api', tags=["Weather Hour"])
