import requests

def get_location_from_pincode(pincode):
    try:
        url = f"https://api.postalpincode.in/pincode/{pincode}"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

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