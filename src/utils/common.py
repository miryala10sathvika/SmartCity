from pymongo import MongoClient
from datetime import datetime

def store_to_mongodb(sensor_name, timestamp, sensor1_data, sensor2_data):
    """This function stores the given data into MongoDB database."""
    client = MongoClient('mongodb://localhost:27017/')
    db = client['sensordatabaseversion2']
    collection = db['sensordata']
    sensor_data = {
        'value1': sensor1_data,
        'value2': sensor2_data
    }
    
    update_data = {sensor_name: sensor_data}
    collection.update_one(
        {'_id': timestamp},
        {'$set': update_data},
        upsert=True
    )
    
    # print(f"Data stored successfully for {sensor_name} at {timestamp}. Current time: {current_time}")


def store_to_mongodb_sensor(db_name, collection_name, sensor_name, timestamp, sensor1_data, sensor2_data):
    """This function stores the given data into the specified MongoDB collection."""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client[db_name]
        collection = db[collection_name]
        sensor_data = {
            'value1': sensor1_data,
            'value2': sensor2_data
        }
        
        update_data = {sensor_name: sensor_data}
        collection.update_one(
            {'_id': timestamp},
            {'$set': update_data},
            upsert=True
        )
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Data stored successfully for {sensor_name} at {timestamp}. Current time: {current_time}")
    except Exception as e:
        print(f"Error storing data to MongoDB: {e}")