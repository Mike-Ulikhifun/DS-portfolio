def load_nairobi_to_mongodb(uri):
    """
    Loads Nairobi air quality data from a Parquet file
    into MongoDB Atlas.
    """

    from pymongo import MongoClient
    from pymongo.server_api import ServerApi
    import pandas as pd

    # -------------------------------------------------
    # Connect to MongoDB Atlas
    # -------------------------------------------------
    try:
        client = MongoClient(
            uri,
            server_api=ServerApi("1"),
            serverSelectionTimeoutMS=5000
        )

        # Test the connection
        client.admin.command("ping")

        print("✅ Successfully connected to MongoDB Atlas!")

    except Exception as e:
        print("❌ Could not connect to MongoDB Atlas.")
        print(f"   Error: {e}")
        return False

    # -------------------------------------------------
    # Load the Nairobi data
    # -------------------------------------------------
    try:
        df = pd.read_parquet("nairobi.parquet")

        print(f"✅ Found nairobi.parquet")
        print(f"   Rows: {len(df)}")

    except FileNotFoundError:
        print("❌ Could not find 'nairobi.parquet'.")
        print("   Make sure the file is in the same folder as your notebook.")
        client.close()
        return False

    # -------------------------------------------------
    # Prepare the timestamp
    # -------------------------------------------------
    if "timestamp" in df.columns:
        if df["timestamp"].dtype != "object":
            df["timestamp"] = df["timestamp"].astype(str)

    # -------------------------------------------------
    # Select database and collection
    # -------------------------------------------------
    db = client["air-quality"]
    collection = db["nairobi"]

    # Remove old data
    collection.drop()

    # -------------------------------------------------
    # Insert data
    # -------------------------------------------------
    try:
        records = df.to_dict("records")

        if records:
            collection.insert_many(records)

        print("✅ Nairobi data successfully loaded!")
        print("   Database: air-quality")
        print("   Collection: nairobi")
        print(f"   Documents inserted: {len(records)}")

        return True

    except Exception as e:
        print("❌ Could not insert Nairobi data.")
        print(f"   Error: {e}")
        return False

    finally:
        client.close()
