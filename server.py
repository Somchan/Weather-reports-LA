from watchgod import run_process
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn
import os

from WeaterForecate_Hourly.fetch_weather_data import app as weather_router
from WeaterForecate_Hourly.plot_weather_data import app as plot_router
from WeaterForecate_Hourly.save_to_excel import app as save_router

from WeaterForecate_Daily.fetch_weather_data import app as daily_weather_router
from WeaterForecate_Daily.plot_weather_data import app as daily_plot_router
from WeaterForecate_Daily.save_to_excel import app as daily_save_router
app = FastAPI()


app.include_router(weather_router)
app.include_router(plot_router)
app.include_router(save_router)

app.include_router(daily_weather_router)
app.include_router(daily_plot_router)
app.include_router(daily_save_router)

load_dotenv()
HOST_URL = os.getenv("HOST_URL")
PORT = os.getenv("PORT")

def main():
    print(f"Server running at http://localhost:{PORT}/")
    uvicorn.run(app, host=HOST_URL, port=int(PORT))


if __name__ == '__main__':
    run_process('.', main)
    

# type nul > test.py