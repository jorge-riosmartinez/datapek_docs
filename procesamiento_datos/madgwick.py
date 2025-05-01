import numpy as np
#
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
