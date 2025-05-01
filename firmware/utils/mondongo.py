import os
import pymongo
from datetime import datetime

class IMUDataUploader:
    def __init__(self, mongo_uri="mongodb+srv://hageobalam:16caramelo16@clusterdp.uphnx.mongodb.net/?retryWrites=true&w=majority&appName=ClusterDP", db_name="mpu6050", collection_name = "pruebas"):
        """
        Initialize the IMU data uploader with MongoDB connection details.
        
        Parameters:
        - mongo_uri: MongoDB connection string
        - db_name: Database name
        - collection_name: Collection name for IMU data
        """
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None
        
    def connect(self):
        """Establish connection to MongoDB."""
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            return True
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            return False
    
    def upload_imu_data(self, file_path, dog_name, test_name):
        """
        Upload IMU data to MongoDB with dog and test name identifiers.
        
        Parameters:
        - file_path: Path to the IMU_data.txt file
        - dog_name: Name of the dog
        - test_name: Name of the test
        
        Returns:
        - True if upload successful, False otherwise
        - Document ID if successful, None otherwise
        """
        # Validate file exists
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} not found.")
            return False, None
        
        # Connect to MongoDB if not already connected
        if not self.collection:
            if not self.connect():
                return False, None

        # Uploading txt as is
        with open(file_path, "r", encoding="utf-8") as file:
            imu_readings = file.read()
        # Create document with metadata
        document = {
            "dog_name": dog_name,
            "test_name": test_name,
            "test_id": f"{dog_name}-{test_name}",
            "upload_date": datetime.now(),
            "readings": imu_readings
        }
        
        # Insert into MongoDB
        try:
            result = self.collection.insert_one(document)
            print(f"Successfully uploaded data with ID: {result.inserted_id}")
            return True, result.inserted_id
        except Exception as e:
            print(f"Error uploading to MongoDB: {e}")
            return False, None
    
    def get_test_data(self, dog_name, test_name):
        """
        Retrieve test data by dog name and test name.
        
        Parameters:
        - dog_name: Name of the dog
        - test_name: Name of the test
        
        Returns:
        - Test data document if found, None otherwise
        """
        if not self.collection:
            if not self.connect():
                return None
        
        try:
            test_id = f"{dog_name}-{test_name}"
            result = self.collection.find_one({"test_id": test_id})
            return result
        except Exception as e:
            print(f"Error retrieving test data: {e}")
            return None
    
    def get_all_tests_for_dog(self, dog_name):
        """
        Retrieve all tests for a specific dog.
        
        Parameters:
        - dog_name: Name of the dog
        
        Returns:
        - List of test documents if found, empty list otherwise
        """
        if not self.collection:
            if not self.connect():
                return []
        
        try:
            results = list(self.collection.find({"dog_name": dog_name}))
            return results
        except Exception as e:
            print(f"Error retrieving dog tests: {e}")
            return []
