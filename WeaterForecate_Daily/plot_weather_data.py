from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Query
import matplotlib.pyplot as plt
from io import BytesIO
from WeaterForecate_Daily.fetch_weather_data import fetch_weather_data

router = APIRouter()

def plot_weather_data(weather_data):
    # Calculate average temperature
    weather_data['temperature_2m_avg'] = (
        weather_data['temperature_2m_max'] + weather_data['temperature_2m_min']) / 2

    # Create a line plot using Matplotlib
    plt.figure(figsize=(16, 9))  # Set the figure size for full HD image
    plt.plot(weather_data['date'], weather_data['temperature_2m_max'], label='Max Temperature')
    plt.plot(weather_data['date'], weather_data['temperature_2m_min'], label='Min Temperature')
    plt.plot(weather_data['date'], weather_data['temperature_2m_avg'], label='Avg Temperature')

    # Customize the plot
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.title('Daily Temperature Variation')
    plt.legend()
    plt.xticks(rotation=45)

    # Save the plot bytes in memory
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300)  # Set dpi for high resolution
    plt.close()  # Close the plot to free memory
    buffer.seek(0)  # Reset the buffer position to the beginning

    return buffer.getvalue()

date_pattern = r'^\d{4}-\d{2}-\d{2}$'

@router.get("/plot-weather-D")
async def plot_weather_endpoint(
    start_date: str = Query(default='2023-01-26', description="Start date in YYYY-MM-DD ",regex=date_pattern),
    end_date: str = Query(default='2023-03-26', description="End date in YYYY-MM-DD ",regex=date_pattern)
    ):
    # Call the fetch_weather_data function to get weather data
    weather_data = fetch_weather_data(start_date, end_date)

    # Generate the plot bytes
    plot_bytes = plot_weather_data(weather_data)
    
    # Return the plot bytes as a Show file
    show = StreamingResponse(BytesIO(plot_bytes), media_type="image/png")
    # Return the plot bytes as a downloadable file
    dow = StreamingResponse(BytesIO(plot_bytes), media_type="image/png", headers={"Content-Disposition": "attachment; filename=Weather_Daily_Chart.png"})
    return show 

app = APIRouter()
app.include_router(router, prefix='/api', tags=["Weather Daily"])
