import time

import googlemaps
import numpy as np
from geopy import Point
from geopy.distance import geodesic
from tinydb import TinyDB, Query

gmaps = googlemaps.Client(key='put_your_google_maps_api_key_here')

center = (3.1386741, 101.604588)
small_radius = 1
radius = 5
min_rating = 4.4
min_rating_total = 900
keyword = "cafe"

# MongoDB
db = TinyDB('google_places.json')


def get_centers_small_circles(lat: float, lon: float, small_radius: int, big_radius: int):
    centers = [(lat, lon)]
    distance_top_corner = 0

    total_layers = (big_radius - small_radius) // small_radius

    for layer in range(total_layers):
        circles = layer + 1
        distance_top_corner += small_radius * 2
        angle = 120
        # print("Layer:", layer, "Distance:", distance_top_corner, "Circles on border:", circles)
        for v in range(6):
            vertex = geodesic(kilometers=distance_top_corner).destination(Point(lat, lon), v * 60)
            for i in range(circles):
                from_point = vertex if i == 0 else centers[-1]
                new_position = geodesic(kilometers=small_radius * 2).destination(from_point, angle)
                # print("Vertex:", v, "Angle:", angle, "Position:", new_position.latitude, new_position.longitude)
                centers.append((new_position.latitude, new_position.longitude))
            angle += 60
        # print("Total centers:", len(centers))
    return centers


def find_places_nearby(location: tuple, token: str = None):
    string_params = f'{location[0]}_{location[1]}_{small_radius}_{token}_{keyword}'
    data = read_from_cache(string_params)
    if data:
        print("From cache")
        return data
    data = gmaps.places_nearby(
        location=location,
        radius=small_radius * 1000,
        keyword=keyword,
        # open_now=False,
        page_token=token
    )
    save_to_cache(string_params, data)
    return data


def save_to_cache(key: str, data: dict):
    db.insert({'key': key, 'data': data})


def read_from_cache(key: str):
    result = db.get(Query().key == key)
    if not result:
        return None
    data = result['data']
    data['read_from_cache'] = True
    return data


def find_places_nearby_with_location():
    found_places = dict()
    ratings = list()
    rating_count = list()
    total_places = set()
    total_places_checked: int = 0
    circles = get_centers_small_circles(center[0], center[1], small_radius, radius)
    circle_num = 0
    for circle in circles:
        page_token = None
        i = 0
        circle_num += 1
        while True:
            print("Page:", i + 1, f'Circle: {circle_num}/{len(circles)}')
            i += 1
            places = find_places_nearby(circle, page_token)
            total_places_checked += len(places["results"])
            for place in places["results"]:
                total_places.add(place["place_id"])
                ratings.append(place.get("rating", 0))
                rating_count.append(place.get("user_ratings_total", 0))
                if place.get("rating", 0) < min_rating or place["user_ratings_total"] < min_rating_total:
                    continue
                place_id = place["place_id"]
                place_url = f"https://www.google.com/maps/search/?api=1&query=Google&query_place_id={place_id}"
                distance = geodesic(center,
                                    (place["geometry"]["location"]["lat"], place["geometry"]["location"]["lng"])).km
                found_places[
                    place_id] = f'{place["name"]} ({round(distance, 2)} km) - {place["rating"]} ({place["user_ratings_total"]}) - {place_url}'
            if "next_page_token" not in places:
                break
            page_token = places["next_page_token"]
            if not places.get('read_from_cache', False):
                time.sleep(2)
    print("-----------------------------------")
    percentile = 90
    print("Total results:", total_places_checked)
    print("Unique places:", len(total_places))
    print(f'{percentile}% of places have less {np.percentile(np.array(ratings), percentile)} stars')
    print(f'{percentile}% of places have less {int(np.percentile(np.array(rating_count), percentile))} ratings')
    print("")
    return found_places


best_places = find_places_nearby_with_location()
for place in best_places.values():
    print(place)

db.close()
