# google_places_find
Helps to find place using Google Maps API

## Description
This script helps to find places using Google Maps API.
It takes the `center`, `radius` in km, `min_rating`, `min_rating_total` and `keyword` and returns a list of places that match the criteria.
It uses TinyDB to cache the results to avoid unnecessary API calls.
YouTube how-to video: https://www.youtube.com/watch?v=

## Set up
1. Obtain Google maps key from https://developers.google.com/maps/get-started
2. Replace `put_your_google_maps_api_key_here` with this key in line `gmaps = googlemaps.Client(key='put_your_google_maps_api_key_here')`
3. Run the script
