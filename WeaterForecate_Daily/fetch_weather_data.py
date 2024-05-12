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

def fetch_weather_data(start_date, end_date):
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
            "daily": [
                "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
                "apparent_temperature_max", "apparent_temperature_min", "apparent_temperature_mean",
                "daylight_duration", "precipitation_sum", "rain_sum", "wind_speed_10m_max", "wind_gusts_10m_max"
            ],
            "timezone": "Asia/Bangkok"
        }
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]

        daily = response.Daily()

        daily_data = {
            "date": pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive="left"
            ),
            "temperature_2m_max": daily.Variables(0).ValuesAsNumpy(),
            "temperature_2m_min": daily.Variables(1).ValuesAsNumpy(),
            "temperature_2m_mean": daily.Variables(2).ValuesAsNumpy(),
            "apparent_temperature_max": daily.Variables(3).ValuesAsNumpy(),
            "apparent_temperature_min": daily.Variables(4).ValuesAsNumpy(),
            "apparent_temperature_mean": daily.Variables(5).ValuesAsNumpy(),
            "daylight_duration": daily.Variables(6).ValuesAsNumpy(),
            "precipitation_sum": daily.Variables(7).ValuesAsNumpy(),
            "rain_sum": daily.Variables(8).ValuesAsNumpy(),
            "wind_speed_10m_max": daily.Variables(9).ValuesAsNumpy(),
            "wind_gusts_10m_max": daily.Variables(10).ValuesAsNumpy()
        }

        daily_dataframe = pd.DataFrame(data=daily_data)
        return daily_dataframe

    except Exception as e:
        # Handle the exception (e.g., log the error, return a default value, etc.)
        print(f"An error occurred while fetching weather data: {e}")
        return None


date_pattern = r'^\d{4}-\d{2}-\d{2}$'

# Define your FastAPI endpoint for fetching weather data
@router.get('/fetch-weather-D')
async def get_weather_data(
    start_date: str = Query(default='2023-01-26', description="Start date in YYYY-MM-DD ",regex=date_pattern),
    end_date: str = Query(default='2023-03-26', description="End date in YYYY-MM-DD ",regex=date_pattern)
    ):
    # Call your fetch_weather_data function with the provided parameters
    weather_data = fetch_weather_data(start_date, end_date)

    # Handle NaN values in the DataFrame
    # Replace NaN values with 0 or any other appropriate value
    weather_data = weather_data.fillna(0)

    return {"weather_data": weather_data.to_dict()}


app = APIRouter()
app.include_router(router, prefix='/api', tags=["Weather Daily"])
