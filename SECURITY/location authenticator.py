from flask import Flask, request, render_template
from geopy.distance import geodesic
import folium


app = Flask(__name__)


allowed_location = (14.599010080486975, 121.00538519569768)
radius = 50


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/map', methods=['POST'])
def result():

    lat = float(request.form['latitude'])
    lon = float(request.form['longitude'])

    user_location = (lat, lon)

    distance = geodesic(allowed_location, user_location).meters

    if distance <= radius:
        status = "ACCESS GRANTED"
    else:
        status = "ACCESS DENIED"

    m = folium.Map(location=[lat, lon], zoom_start=18)

    folium.Marker(
        [lat, lon],
        popup="Current Location",
        icon=folium.Icon(color="red")
    ).add_to(m)

    folium.Marker(
        allowed_location,
        popup="Allowed Location",
        icon=folium.Icon(color="green")
    ).add_to(m)

    folium.PolyLine(
        locations=[user_location, allowed_location],
        color="black",
        weight=3,
        tooltip=f"Distance: {distance:.2f} meters"
    ).add_to(m)

    folium.Circle(
        location=allowed_location,
        radius=radius,
        color="green",
        fill=True,
        fill_opacity=0.2
    ).add_to(m)

    m.save('templates/map.html')

    return render_template('result.html', status=status, distance=round(distance, 2))


@app.route('/show-map')
def show_map():
    return render_template('map.html')


if __name__ == '__main__':  
    app.run(debug=True)