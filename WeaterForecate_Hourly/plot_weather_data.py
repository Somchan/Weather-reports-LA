from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Query
import matplotlib.pyplot as plt
from datetime import datetime
import plotly.express as px
from io import BytesIO
import schedule
import base64
import time
from WeaterForecate_Hourly.fetch_weather_data import fetch_weather_data_search


router = APIRouter()


def plot_weather_data(weather_data):
    # Calculate average temperature
    weather_data['temperature_2m_avg'] = (
        weather_data['temperature_2m'] + weather_data['apparent_temperature']) / 2

    # Create a Matplotlib figure and axis
    fig, ax = plt.subplots()

    # Plot the data on the axis
    ax.plot(weather_data['date'], weather_data['temperature_2m'], label='Temperature 2m')
    ax.plot(weather_data['date'], weather_data['apparent_temperature'], label='Apparent Temperature')
    ax.plot(weather_data['date'], weather_data['temperature_2m_avg'], label='Average Temperature')

    # Set labels and title
    ax.set_xlabel('Date')
    ax.set_ylabel('Temperature (°C)')
    ax.set_title('Hourly Temperature Variation')
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)

    # Add legend
    ax.legend()

    # Save the plot as a full HD image (1920x1080) with high DPI
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300)  # Save the plot as PNG format with high DPI
    plt.close(fig)  # Close the plot to free memory
    buffer.seek(0)  # Reset the buffer position to the beginning

    # Encode the plot bytes as base64
    plot_bytes = base64.b64encode(buffer.getvalue()).decode()

    return plot_bytes

def schedule_plot_weather_endpoint():
    # Schedule the task to run every day at midnight
    schedule.every().day.at("00:00").do(run_plot_weather_endpoint)

    # Continuously check for scheduled tasks and run them
    while True:
        schedule.run_pending()
        time.sleep(1)  # Adjust sleep time as needed

# Define the actual task to run plot_weather_endpoint
def run_plot_weather_endpoint():
    # Get today's date in the required format
    today_date = datetime.now().strftime("%Y-%m-%d")

    # Call the plot_weather_endpoint function with today's date as start and end dates
    plot_weather_endpoint(today_date, today_date)

date_pattern = r'^\d{4}-\d{2}-\d{2}$'



@router.get("/plot-weather-H")
async def plot_weather_endpoint(
    start_date: str = Query(default='2023-03-26', description="Start date in YYYY-MM-DD ",regex=date_pattern),
    end_date: str = Query(default='2023-03-26', description="End date in YYYY-MM-DD ",regex=date_pattern)
):
    # Call the fetch_weather_data function to get weather data
    weather_data = fetch_weather_data_search(start_date, end_date)

    # Plot the weather data and get the plot bytes
    plot_bytes = plot_weather_data(weather_data)

    # Return the plot bytes as a Show file
    show = StreamingResponse(BytesIO(base64.b64decode(plot_bytes)), media_type="image/png")
    # Return the plot bytes as a downloadable file
    dow = StreamingResponse(BytesIO(base64.b64decode(plot_bytes)), media_type="image/png", headers={"Content-Disposition": "attachment; filename=Weather_Hourly_Chart.png"})
    return show

app = APIRouter()
app.include_router(router, prefix='/api', tags=["Weather Hour"])
