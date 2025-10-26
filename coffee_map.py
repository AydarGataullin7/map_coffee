import json
import requests
import os
import geopy
import folium

from geopy import distance
from dotenv import load_dotenv


def fetch_coordinates(apikey, your_place):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": your_place,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json(
    )['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def cof_dist(data, your_coords):
    coffee_dist = []
    for coffees in data:
        coords = coffees['geoData']['coordinates']
        coffee_coords = (coords[1], coords[0])
        dist_from_cof = distance.distance(your_coords, coffee_coords).km
        coffee_dist.append({
            'title': coffees['Name'],
            'longitude': coords[0],
            'latitude': coords[1],
            'distance': dist_from_cof
        })
    return coffee_dist


def closest(coffee_dist):
    return coffee_dist['distance']


def near(coffee_dist):
    near_coffee = sorted(coffee_dist, key=closest)
    closest_coffee = near_coffee[:5]
    return closest_coffee


def create_map(your_coords, closest_coffee):
    m = folium.Map(location=(your_coords[0], your_coords[1]), zoom_start=12)
    folium.Marker(
        location=(your_coords[0], your_coords[1]),
        popup="Ваше местоположение",
        icon=folium.Icon(color="red", icon="user"),
    ).add_to(m)
    for coffee in closest_coffee:
        folium.Marker(
            location=[coffee['latitude'], coffee['longitude']],
            popup="{0} {1:.2f} км".format(coffee['title'], coffee['distance']),
            icon=folium.Icon(color="green", icon="coffee"),
        ).add_to(m)
    m.save("index.html")


def main():
    load_dotenv()
    apikey = os.getenv('API_KEY')

    with open("coffee.json", "r", encoding="cp1251") as coffee:
        data = json.load(coffee)

    your_place = input("Где вы находитесь?: ")
    your_coords = fetch_coordinates(apikey, your_place)

    print('Ваши координаты: ', your_coords)

    coffee_distances = cof_dist(data, your_coords)
    closest_coffee = near(coffee_distances)
    create_map(your_coords, closest_coffee)


if __name__ == '__main__':
    main()
