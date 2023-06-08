import googlemaps
from fermerce.core.settings import config
from fermerce.lib.google_map_services import schemas

gmaps = googlemaps.Client(key=config.google_api_key)

import googlemaps


api_key = "YOUR_API_KEY"
gmaps = googlemaps.Client(key=api_key)


def format_address(street: str, city: str, zipcode: str, state: str) -> str:
    return f"{street}, {city}, {zipcode}, {state}"


def calculate_distance(
    origin: str, destination: str, units: str = "metric"
) -> schemas.DistanceResponse:
    origin_geocode = gmaps.geocode(origin)
    destination_geocode = gmaps.geocode(destination)

    origin_lat = origin_geocode[0]["geometry"]["location"]["lat"]
    origin_lng = origin_geocode[0]["geometry"]["location"]["lng"]
    destination_lat = destination_geocode[0]["geometry"]["location"]["lat"]
    destination_lng = destination_geocode[0]["geometry"]["location"]["lng"]

    distance_matrix = gmaps.distance_matrix(
        (origin_lat, origin_lng),
        (destination_lat, destination_lng),
        units=units,
    )

    distance = distance_matrix["rows"][0]["elements"][0]["distance"]["text"]
    duration = distance_matrix["rows"][0]["elements"][0]["duration"]["text"]

    return schemas.DistanceResponse(
        origin=schemas.Location(lat=origin_lat, lng=origin_lng),
        destination=schemas.Location(lat=destination_lat, lng=destination_lng),
        distance=distance,
        duration=duration,
    )


# Usage
origin_address = "Address 1"
destination_address = "Address 2"

response = calculate_distance(origin_address, destination_address)
print("Origin Latitude:", response.origin.lat)
print("Origin Longitude:", response.origin.lng)
print("Destination Latitude:", response.destination.lat)
print("Destination Longitude:", response.destination.lng)
print("Distance:", response.distance)
print("Duration:", response.duration)
