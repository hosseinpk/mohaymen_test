import httpx
import csv

API_BASE = "http://api:8000"
CSV_PATH = "CountryCode-City.csv"


def post_data(client: httpx.Client, city: str, code: str):
    try:
        res = client.post(
            f"{API_BASE}/api/cities",
            json={"city": city, "countrycode": code},
            timeout=10,
        )
        if res.status_code in (200, 201):
            return True
    except Exception as e:
        print(f"error: {e}")
        return False


def main():

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        client = httpx.Client()
        for row in reader:
            city = row.get("city", "").strip()
            code = row.get("countyCode", "").strip()

            if city and code:
                post_data(client=client, city=city, code=code)


if __name__ == "__main__":
    main()
