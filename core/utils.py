import requests
import math
PINCODE_CACHE = {}


# 🔥 PINCODE → LOCATION
def get_location_from_pincode(pincode):
    try:
        url = f"https://api.postalpincode.in/pincode/{pincode}"

        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()

        if not isinstance(data, list) or len(data) == 0:
            return None

        result = data[0]

        if result.get("Status") != "Success":
            return None

        post_offices = result.get("PostOffice")
        if not post_offices:
            return None

        post_office = post_offices[0]

        return {
            "name": post_office.get("Name"),
            "city": post_office.get("District"),
            "state": post_office.get("State")
        }

    except Exception as e:
        print("PINCODE ERROR:", str(e))
        return None


# 🔥 CITY → LAT/LONG
def get_lat_long(city):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json"

        headers = {"User-Agent": "parcel-system-app"}

        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code != 200:
            return None, None

        data = response.json()

        if not data:
            return None, None

        return float(data[0]['lat']), float(data[0]['lon'])

    except Exception as e:
        print("LAT/LONG ERROR:", str(e))
        return None, None


# 🔥 DISTANCE CALCULATION (HAVERSINE)
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# 🔥 CITY → CITY DISTANCE
def get_distance_between_cities(source_city, dest_city):
    lat1, lon1 = get_lat_long(source_city)
    lat2, lon2 = get_lat_long(dest_city)

    if not lat1 or not lat2:
        return 100  # 🔥 fallback

    return calculate_distance(lat1, lon1, lat2, lon2)


# 🔥 ETA (DAYS)
def estimate_eta(source_city, dest_city):
    distance = get_distance_between_cities(source_city, dest_city)

    speed = 300  # km/day

    days = round(distance / speed)

    return max(1, days)


 

def get_location_from_pincode(pincode):
    if pincode in PINCODE_CACHE:
        return PINCODE_CACHE[pincode]

    try:
        url = f"https://api.postalpincode.in/pincode/{pincode}"
        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()

        if data and data[0]["Status"] == "Success":
            post = data[0]["PostOffice"][0]

            result = {
                "name": post.get("Name"),
                "city": post.get("District"),
                "state": post.get("State")
            }

            PINCODE_CACHE[pincode] = result
            return result

    except Exception as e:
        print("PINCODE ERROR:", str(e))

    return {"city": "Unknown", "state": "Unknown", "name": "Unknown"}


def calculate_price_from_data(weight, source, dest, dimensions=""):
    base_price = 50
    per_kg = 20
    cost_per_km = 0.2

    # 🔥 LOCATION
    source_data = get_location_from_pincode(source)
    dest_data = get_location_from_pincode(dest)

    source_city = source_data.get("city") if source_data else "Unknown"
    dest_city = dest_data.get("city") if dest_data else "Unknown"

    # 🔥 DISTANCE
    distance = get_distance_between_cities(source_city, dest_city)

    # 🔥 VOLUMETRIC
    volumetric_weight = 0
    if dimensions:
        try:
            l, w, h = map(float, dimensions.split("x"))
            volumetric_weight = (l * w * h) / 5000
        except:
            volumetric_weight = 0

    chargeable_weight = max(weight, volumetric_weight)

    # 🔥 COST BREAKDOWN
    weight_cost = chargeable_weight * per_kg
    distance_cost = distance * cost_per_km

    total = base_price + weight_cost + distance_cost

    return {
        "base": round(base_price, 2),
        "weight_charge": round(weight_cost, 2),
        "distance_charge": round(distance_cost, 2),
        "total": round(total, 2),

        # optional (nice for UI)
        "distance_km": round(distance, 2),
        "chargeable_weight": round(chargeable_weight, 2)
    }

def calculate_price_details(parcel):
    return calculate_price_from_data(
        weight=float(parcel.weight),
        source=parcel.source_pincode,
        dest=parcel.destination_pincode,
        dimensions=parcel.dimensions
    )