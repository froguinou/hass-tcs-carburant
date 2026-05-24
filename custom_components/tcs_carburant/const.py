DOMAIN = "tcs_carburant"

FIREBASE_API_KEY = "AIzaSyCQ8f6sXb1gYIiv5rlHKeZ2EVMzC-anzIU"

URL = (
    "https://firestore.googleapis.com/v1/projects/"
    "gas-prices-prod/databases/(default)/documents:runQuery"
    f"?key={FIREBASE_API_KEY}"
)

FUEL_TYPES = ["SP95", "SP98", "DIESEL"]

DEFAULT_RADIUS_KM = 20