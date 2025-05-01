import os
import numpy as np
import pandas as pd
from pymongo import MongoClient
from io import StringIO

class IMUDataProcessor:
    def __init__(self, data_folder=None):
        self.data_folder = data_folder
        # Accelerometer calibration
        self.calibration_matrix = np.array([
            [0.982992, 0.005301, 0.037799],
            [0.005301, 0.989868, 0.002955],
            [0.037799, 0.002955, 0.981239]
        ])
        self.bias_vector = np.array([0.054144, 0.002268, -0.071535])
        
        # Gyroscope calibration (from your provided values)
        # Try these adjusted offsets based on your means:
        self.gyro_offsets = {
            'x': 3.384,   # original + observed mean
            'y': 2.511,
            'z': 0.560 
        }
        # Increase noise estimates based on your std dev:
        self.gyro_noise = {
            'x': 0.13,  
            'y': 0.14,  
            'z': 0.13   
        }
        
        # Gyroscope normalization factor (131 LSB/°/s for ±250°/s range)
        self.gyro_normalization = 131.0

    def calibrate_accelerometer_data(self, df):
        """Apply calibration parameters to accelerometer data."""
        raw_values = df[['acc_x', 'acc_y', 'acc_z']].values
        calibrated_values = np.dot(self.calibration_matrix, (raw_values - self.bias_vector).T).T
        df_calibrated = pd.DataFrame(calibrated_values, columns=['acc_x', 'acc_y', 'acc_z'])
        
        # Copy other columns
        for col in df.columns:
            if col not in ['acc_x', 'acc_y', 'acc_z'] and col not in df_calibrated.columns:
                df_calibrated[col] = df[col]
                
        return df, df_calibrated

    def calibrate_gyroscope_data(self, df):
        """Apply calibration and normalization to gyroscope data."""
        df_calibrated = df.copy()
        
        # Step 1: Apply offsets
        df_calibrated['gyro_x'] = df['gyro_x'] - self.gyro_offsets['x']
        df_calibrated['gyro_y'] = df['gyro_y'] - self.gyro_offsets['y']
        df_calibrated['gyro_z'] = df['gyro_z'] - self.gyro_offsets['z']
        
        # Step 2: Normalize to degrees/second
        df_calibrated['gyro_x'] = df_calibrated['gyro_x'] / self.gyro_normalization
        df_calibrated['gyro_y'] = df_calibrated['gyro_y'] / self.gyro_normalization
        df_calibrated['gyro_z'] = df_calibrated['gyro_z'] / self.gyro_normalization
        
        return df_calibrated

    def process_mongo_documents(self):
        """Process IMU data from MongoDB documents."""
        client = MongoClient("mongodb+srv://hageobalam:16caramelo16@clusterdp.uphnx.mongodb.net/?retryWrites=true&w=majority&appName=ClusterDP")
        db = client["mpu6050"]
        collection = db["pruebas"]
        
   
        cursor = collection.find().limit(4)
        documents = list(cursor)

        all_data = []
        for doc in documents:
            try:
                # Extract metadata and data
                perro = doc.get('perro', 'unknown')
                prueba = doc.get('prueba', 'unknown')
                imu_data = doc.get('lecturas_imu', '')
                
                if not imu_data:
                    continue
                
                # Parse into DataFrame
                df = pd.read_csv(StringIO(imu_data), 
                               header=None,
                               names=['timestamp', 'acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z'])
                
                # Apply scaling and calibration
                df[['acc_x', 'acc_y', 'acc_z']] = df[['acc_x', 'acc_y', 'acc_z']] / 16384.0  # Accelerometer scaling
                _, df_acc_cal = self.calibrate_accelerometer_data(df)
                df_full_cal = self.calibrate_gyroscope_data(df_acc_cal)
                
                # Add metadata
                df_full_cal['perro'] = perro
                df_full_cal['prueba'] = prueba
                
                # Reorder columns
                df_full_cal = df_full_cal[['perro', 'prueba', 'timestamp',
                                          'acc_x', 'acc_y', 'acc_z',
                                          'gyro_x', 'gyro_y', 'gyro_z']]
                
                all_data.append(df_full_cal)
                
            except Exception as e:
                print(f"Error processing document {doc.get('_id')}: {str(e)}")
        
        client.close()
        return pd.concat(all_data, ignore_index=True) if all_data else None

    def save_processed_data(self, df, output_dir="processed_data"):
        """Save processed data to CSV files organized by dog/test."""
        if df is None:
            print("No data to save")
            return
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Group by dog and test
        grouped = df.groupby(['perro', 'prueba'])
        for (perro, prueba), group in grouped:
            test_dir = os.path.join(output_dir, perro, prueba)
            os.makedirs(test_dir, exist_ok=True)
            output_path = os.path.join(test_dir, "processed_imu_data.csv")
            group.to_csv(output_path, index=False)
            print(f"Saved {len(group)} records to {output_path}")

# Example usage in notebook:
if __name__ == "__main__":
    # Initialize processor
    processor = IMUDataProcessor()
    
    # Process all MongoDB documents
    print("Processing data from MongoDB...")
    processed_data = processor.process_mongo_documents()
    
    if processed_data is not None:
        print("\nFirst 5 rows of processed data:")
        print(processed_data.head())
        
        # Verify gyro normalization
        print("\nGyroscope values after normalization (should be in °/s):")
        print(processed_data[['gyro_x', 'gyro_y', 'gyro_z']].describe())
        
        # Save processed data
        print("\nSaving processed data...")
        processor.save_processed_data(processed_data)
    else:
        print("No valid data found in MongoDB")
import numpy as np
import pandas as pd

class MadgwickFilter:
    """
    Implementation of Madgwick's IMU orientation filter for sensor fusion
    
    The Madgwick filter combines accelerometer and gyroscope data to estimate 
    orientation using quaternion representation.
    
    Attributes:
        delta_t (float): Sampling period in seconds
        beta (float): Filter gain (noise sensitivity)
        q (np.ndarray): Current orientation quaternion
    """
    
    def __init__(self, delta_t=0.01, beta=0.1):
        """
        Initialize the Madgwick filter.
        
        Args:
            delta_t (float, optional): Sampling period. Defaults to 0.01s (100Hz).
            beta (float, optional): Filter gain. Defaults to 0.1.
        """
        self.delta_t = delta_t
        self.beta = beta
        self.q = np.array([1.0, 0.0, 0.0, 0.0])  # Initial quaternion [w, x, y, z]
    
    def update(self, ax, ay, az, gx, gy, gz):
        """
        Update orientation estimate with new IMU measurements.
        
        Args:
            ax, ay, az (float): Calibrated accelerometer readings (in g)
            gx, gy, gz (float): Calibrated gyroscope readings (in rad/s)
        
        Returns:
            np.ndarray: Updated quaternion
        """
        # Normalize accelerometer measurement
        a_norm = np.sqrt(ax*ax + ay*ay + az*az)
        if a_norm > 0:
            ax, ay, az = ax/a_norm, ay/a_norm, az/a_norm

        # Quaternion components
        q1, q2, q3, q4 = self.q

        # Compute objective function
        f = np.array([
            2*(q2*q4 - q1*q3) - ax,
            2*(q1*q2 + q3*q4) - ay,
            2*(0.5 - q2**2 - q3**2) - az
        ])
        
        # Compute Jacobian
        J = np.array([
            [-2*q3, 2*q4, -2*q1, 2*q2],
            [2*q2, 2*q1, 2*q4, 2*q3],
            [0, -4*q2, -4*q3, 0]
        ])

        # Compute gradient and normalize
        gradient = J.T @ f
        gradient_norm = np.linalg.norm(gradient)
        if gradient_norm > 0:
            gradient /= gradient_norm

        # Gyroscope quaternion rate
        q_dot = 0.5 * self.quat_mult(self.q, [0, gx, gy, gz])
        
        # Apply gradient descent
        q_dot -= self.beta * gradient
        
        # Integrate to update orientation
        self.q += q_dot * self.delta_t
        self.q /= np.linalg.norm(self.q)
        
        return self.q

    def quat_mult(self, q1, q2):
        """
        Quaternion multiplication.
        
        Args:
            q1, q2 (np.ndarray): Quaternions to multiply
        
        Returns:
            np.ndarray: Resulting quaternion
        """
        return np.array([
            q1[0]*q2[0] - q1[1]*q2[1] - q1[2]*q2[2] - q1[3]*q2[3],
            q1[0]*q2[1] + q1[1]*q2[0] + q1[2]*q2[3] - q1[3]*q2[2],
            q1[0]*q2[2] - q1[1]*q2[3] + q1[2]*q2[0] + q1[3]*q2[1],
            q1[0]*q2[3] + q1[1]*q2[2] - q1[2]*q2[1] + q1[3]*q2[0]
        ])

    def get_euler(self):
        """
        Convert current quaternion to Euler angles.
        
        Returns:
            tuple: (roll, pitch, yaw) in degrees
        """
        q1, q2, q3, q4 = self.q
        
        # Roll (x-axis rotation)
        roll = np.arctan2(2*(q2*q3 + q1*q4), q1**2 + q2**2 - q3**2 - q4**2)
        
        # Pitch (y-axis rotation)
        pitch = -np.arcsin(2*(q2*q4 - q1*q3))
        
        # Yaw (z-axis rotation)
        yaw = np.arctan2(2*(q3*q4 + q1*q2), q1**2 - q2**2 - q3**2 + q4**2)
        
        return np.degrees(roll), np.degrees(pitch), np.degrees(yaw)

def apply_madgwick_filter(df, delta_t=0.01, beta=0.1):
    """
    Apply Madgwick filter to processed IMU data.
    
    Args:
        df (pd.DataFrame): DataFrame with calibrated IMU data
        delta_t (float, optional): Sampling period. Defaults to 0.01s.
        beta (float, optional): Filter gain. Defaults to 0.1.
    
    Returns:
        pd.DataFrame: DataFrame with added orientation information
    """
    # Initialize filter 
    mfilter = MadgwickFilter(delta_t=delta_t, beta=beta)
    
    # Convert gyro to rad/s if needed
    gyro_scale = np.pi/180 if np.max(np.abs(df[['gyro_x','gyro_y','gyro_z']])) > 2*np.pi else 1.0
    
    # Process each sample
    quats, eulers = [], []
    for _, row in df.iterrows():
        q = mfilter.update(
            row['acc_x'], row['acc_y'], row['acc_z'],
            row['gyro_x']*gyro_scale, 
            row['gyro_y']*gyro_scale,
            row['gyro_z']*gyro_scale
        )
        roll, pitch, yaw = mfilter.get_euler()
        quats.append(q)
        eulers.append([roll, pitch, yaw])
    
    # Add to dataframe
    df[['q1','q2','q3','q4']] = quats
    df[['roll','pitch','yaw']] = eulers
    return df

processor = IMUDataProcessor()
data = processor.process_mongo_documents()
data_with_orientation = apply_madgwick_filter(data)

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder

# Assuming your dataframe is named 'data_with_orientation'

# 1. Prepare the data
# Separate features and target
X = data_with_orientation.drop(['perro', 'prueba'], axis=1)  # Drop non-feature columns
y = data_with_orientation['prueba']  # Target variable

# Encode the target labels if they're strings
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# 2. Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

# 3. Initialize and train the Random Forest classifier
rf_classifier = RandomForestClassifier(
    n_estimators=100,  # Number of trees in the forest
    max_depth=None,    # Let trees grow as much as needed
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42,
    n_jobs=-1          # Use all available cores
)

rf_classifier.fit(X_train, y_train)

# 4. Make predictions and evaluate the model
y_pred = rf_classifier.predict(X_test)

# 5. Print evaluation metrics
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

# 6. Feature importance (optional)
feature_importances = pd.DataFrame({
    'Feature': X.columns,
    'Importance': rf_classifier.feature_importances_
}).sort_values('Importance', ascending=False)

print("\nFeature Importances:")
print(feature_importances)

from joblib import dump
dump(rf_classifier, 'dog_behavior_classifier.joblib')
dump(label_encoder, 'label_encoder.joblib')
