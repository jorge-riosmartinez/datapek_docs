import os
import numpy as np
import pandas as pd
from io import StringIO
from procesamiento_datos.madgwick import * 
from .modelos.model import *

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
    

    def save(self, output_dir, df):
        
        """Save processed data to CSV files organized by dog/test."""
        if df is None:
            print("No data to save")
            return
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Group by dog and test (though there will only be one group now)
        grouped = df.groupby(['perro', 'prueba'])
        for (perro, prueba), group in grouped:
            test_dir = os.path.join(output_dir, perro, prueba)
            os.makedirs(test_dir, exist_ok=True)
            output_path = os.path.join(test_dir, "processed_imu_data.csv")
            group.to_csv(output_path, index=False)
            print(f"Saved {len(group)} records to {output_path}")

    def process_imu_data(self, perro, prueba):
        """Process IMU data from a local text file."""
        
        file_path = os.path.join(self.data_folder, perro, prueba, 'IMU_data.txt')
        
        try:
            # Check if file exists first
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return None
                
            # Read the file
            with open(file_path, 'r') as file:
                imu_data = file.read()
                
            if not imu_data:
                print("No data found in the file")
                return None
                
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
            df_full_cal = df_full_cal[['timestamp', 'perro', 'prueba',
                                    'acc_x', 'acc_y', 'acc_z',
                                    'gyro_x', 'gyro_y', 'gyro_z']]
            
            try:
                # Additional processing with potential errors
                df_mad = apply_madgwick_filter(df_full_cal)
                df_pred = predict_on_last_document(df_mad)


                # Save the processed data
                report_path = os.path.join(self.data_folder, perro, prueba, 'processed_report.csv')
                 
                # Ensure directory exists
                os.makedirs(os.path.dirname(report_path), exist_ok=True)
                
                df_pred.to_csv(report_path, index=False)
                print(f"Saved processed report to {report_path}")
            except Exception as e:
                print(f"Error in advanced processing: {str(e)}")
                # Continue to return basic processed data even if advanced processing fails
            
            return df_full_cal
            
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            return None
        
        
            
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            return None


