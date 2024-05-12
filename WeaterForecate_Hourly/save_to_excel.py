from openpyxl.chart import LineChart, Reference
from fastapi import APIRouter,Response, Query
from openpyxl import Workbook
from datetime import datetime
from WeaterForecate_Hourly.fetch_weather_data import fetch_weather_data_search


router = APIRouter()

def calculate_avg_temperature(weather_data):
    # Calculate average temperature and add it to the DataFrame
    weather_data['temperature_2m_avg'] = (weather_data['temperature_2m'] + weather_data['apparent_temperature']) / 2
    return weather_data


def save_to_excel(weather_data):
    try:
        # Create a new Excel workbook
        wb = Workbook()

        # Add the DataFrame to an Excel sheet named 'Weather Data'
        ws = wb.active
        ws.title = 'Weather Data'
        ws.append(['Date', 'Temperature', 'Apparent Temperature', 'Avg Temperature',
                   'Relative Humidity', 'Dew Point', 'Precipitation', 'Rain',
                   'Wind Speed'])

        # Append the data from your DataFrame to the Excel sheet
        for index, data in weather_data.iterrows():
            # Convert datetime to string format without timezone information
            date_str = data['date'].strftime("%Y-%m-%d %H:%M:%S")
            ws.append([date_str, data["temperature_2m"], data["apparent_temperature"], data["temperature_2m_avg"],
                       data["relative_humidity_2m"], data["dew_point_2m"], data["precipitation"], data["rain"],
                       data["wind_speed_10m"]])

        # Create a line chart
        chart = LineChart()
        chart.title = 'Hourly Temperature Variation'
        chart.y_axis.title = 'Temperature (°C)'
        chart.x_axis.title = 'Date'

        # Define the data ranges for the chart
        data = Reference(ws, min_col=2, min_row=1, max_col=4, max_row=len(weather_data) + 1)
        categories = Reference(ws, min_col=1, min_row=2, max_row=len(weather_data) + 1)

        # Add the data to the chart
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(categories)

        # Add the chart to the worksheet
        ws.add_chart(chart, 'F2')

        # Save the Excel file with the current datetime in the filename
        current_datetime = datetime.now().strftime("%Y-%m-%d")
        wb.save(f"Weather Hourly Data {current_datetime}.xlsx")

    except Exception as e:
        # Handle the exception (e.g., log the error, return a default value, etc.)
        print(f"An error occurred: {e}")

date_pattern = r'^\d{4}-\d{2}-\d{2}$'

@router.get("/save-weather-H", response_class=Response)
async def save_weather_endpoint(
    start_date: str = Query(default='2023-01-26', description="Start date in YYYY-MM-DD ",regex=date_pattern),
    end_date: str = Query(default='2023-03-26', description="End date in YYYY-MM-DD ",regex=date_pattern)
    ) -> Response:
    try:
        # Call the fetch_weather_data function to get weather data
        weather_data = fetch_weather_data_search(start_date, end_date)

        # Calculate average temperature
        weather_data = calculate_avg_temperature(weather_data)

        # Save weather data to Excel
        save_to_excel(weather_data)

        # Prepare the file for download
        file_path = f"Weather Hourly Data {datetime.now().strftime('%Y-%m-%d')}.xlsx"
        with open(file_path, "rb") as file:
            file_content = file.read()

        # Set response headers for file download
        headers = {
            'Content-Disposition': 'attachment; filename=Weather_Hourly_Data.xlsx',
            'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        }

        return Response(content=file_content, headers=headers)

    except Exception as e:
        error_message = f"An error occurred while processing the request: {str(e)}"
        return Response(content=error_message, status_code=500)

app = APIRouter()
app.include_router(router, prefix='/api', tags=["Weather Hour"])
