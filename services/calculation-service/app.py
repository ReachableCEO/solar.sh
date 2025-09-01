import os
import io
import base64
import laspy
import pvlib
import psycopg2
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from shapely.geometry import Point
from shapely import wkb

app = Flask(__name__)

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    project_name = data.get('project_name')
    location = data.get('location') # {"lat": 35.79, "lon": -78.78}
    lidar_data_b64 = data.get('lidar_data') # base64 encoded .las or .laz
    panel_specs = data.get('panel_specs')
    ground_mount_config = data.get('ground_mount_config')

    if not all([project_name, location, lidar_data_b64, panel_specs]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # 1. Decode and parse LIDAR data
        lidar_bytes = base64.b64decode(lidar_data_b64)
        # Use io.BytesIO to treat bytes as a file
        with io.BytesIO(lidar_bytes) as f:
            las = laspy.read(f)

        # For simplicity, let's just get the bounding box of the LIDAR data
        # and store it as a PostGIS geometry (e.g., a Point representing the center)
        # In a real app, you'd process the full point cloud.
        min_x, min_y, min_z = las.header.mins
        max_x, max_y, max_z = las.header.maxs
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        
        # Create a Shapely Point and convert to WKB for PostGIS
        lidar_geom = Point(center_x, center_y).wkb_hex # Assuming SRID 4326 for lat/lon

        # 2. Store project details in the projects table
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Insert project and get its ID
        cur.execute(
            "INSERT INTO projects (project_name, location_lat, location_lon, lidar_geom, status) VALUES (%s, %s, %s, ST_GeomFromWKB(%s::bytea, 4326)) RETURNING id",
            (project_name, location['lat'], location['lon'], lidar_geom)
        )
        project_id = cur.fetchone()[0]

        # 3. Perform a basic solar simulation using pvlib
        # This is a highly simplified example. A real simulation would be much more complex.
        # It would involve detailed panel orientation, shading analysis from LIDAR, etc.
        
        # Dummy values for pvlib simulation
        latitude = location['lat']
        longitude = location['lon']
        tz = 'Etc/GMT+8' # Example timezone, should be derived from location
        system = {'module_type': 'cec', 'module': 'Canadian_Solar_CS5P_220M', 'inverter': 'ABB__PVI_5000_US__208V_'}
        temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

        # Get typical meteorological year (TMY) data (placeholder)
        # In a real scenario, you'd fetch actual weather data for the location
        times = pvlib.data.get_tmy(latitude, longitude).index
        weather = pvlib.data.get_tmy(latitude, longitude)[['ghi', 'dni', 'dhi', 'temp_air', 'wind_speed']]

        # Calculate solar position
        solpos = pvlib.solar.get_solarposition(times, latitude, longitude)

        # Calculate angle of incidence
        # Assuming a fixed tilt and azimuth for simplicity
        surface_tilt = 30
        surface_azimuth = 180 # South
        aoi = pvlib.irradiance.aoi(surface_tilt, surface_azimuth, solpos['apparent_zenith'], solpos['azimuth'])

        # Calculate plane of array irradiance
        poa_irradiance = pvlib.irradiance.get_total_irradiance(
            surface_tilt, surface_azimuth, solpos['apparent_zenith'], solpos['azimuth'],
            weather['dni'], weather['ghi'], weather['dhi']
        )

        # Calculate cell temperature
        cell_temperature = pvlib.temperature.sapm(
            poa_irradiance['poa_global'], weather['temp_air'], weather['wind_speed'],
            temperature_model_parameters['a'], temperature_model_parameters['b'],
            temperature_model_parameters['deltaT'], temperature_model_parameters['gamma_pdc']
        )

        # Calculate DC power
        dc = pvlib.pvsystem.sapm(
            system['module'], poa_irradiance['poa_direct'], poa_irradiance['poa_diffuse'], cell_temperature
        )

        # Calculate AC power
        ac = pvlib.inverter.sandia(system['inverter'], dc['p_mp'])

        # Calculate annual energy yield (example: sum of AC power, convert to kWh)
        annual_kwh = ac.sum() / 1000 # Convert W to kW, then sum over hours
        shading_loss_pct = 0.05 # Placeholder, would be derived from LIDAR analysis

        # 4. Store calculation results in the calculations table
        cur.execute(
            "INSERT INTO calculations (project_id, annual_kwh, shading_loss_pct, financial_data) VALUES (%s, %s, %s, %s)",
            (project_id, annual_kwh, shading_loss_pct, json.dumps({"cost": 10000, "roi": 0.15})) # Dummy financial data
        )
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"project_id": str(project_id), "status": "completed", "annual_kwh": annual_kwh})

    except laspy.errors.LaspyError as e:
        app.logger.error(f"LIDAR parsing error: {e}")
        return jsonify({"error": f"LIDAR data processing failed: {e}"}), 400
    except psycopg2.Error as e:
        app.logger.error(f"Database error: {e}")
        return jsonify({"error": f"Database operation failed: {e}"}), 500
    except Exception as e:
        app.logger.error(f"Calculation error: {e}")
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

@app.route("/health")
def health():
    # Basic health check, could be extended to check DB connection
    try:
        conn = get_db_connection()
        conn.close()
        return "OK", 200
    except Exception as e:
        app.logger.error(f"Health check failed: {e}")
        return "Database connection failed", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)