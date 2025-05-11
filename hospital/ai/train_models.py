import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

# Define file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
queue_model_path = os.path.join(BASE_DIR, "queue_model.pkl")
bed_model_path = os.path.join(BASE_DIR, "bed_model.pkl")

# Sample data for Queue Model (Example Data)
queue_data = {
    'age': [25, 35, 45, 55, 65],
    'condition_severity': [1, 2, 3, 2, 1],
    'queue_position': [1, 2, 3, 4, 5],
    'status': [0, 1, 0, 1, 0]  # 0 = Waiting, 1 = Consulting
}
queue_df = pd.DataFrame(queue_data)
X_queue = queue_df.drop('status', axis=1)
y_queue = queue_df['status']

# Train Queue Model
queue_model = RandomForestClassifier()
queue_model.fit(X_queue, y_queue)

# Save Queue Model
with open(queue_model_path, 'wb') as f:
    pickle.dump(queue_model, f)
print(f"Queue model saved at: {queue_model_path}")


# Sample data for Bed Model (Example Data)
bed_data = {
    'ward_type': [1, 2, 1, 2, 3],
    'beds_available': [5, 0, 3, 1, 4],
    'beds_occupied': [10, 15, 8, 12, 6],
    'status': [1, 0, 1, 0, 1]  # 1 = Available, 0 = Full
}
bed_df = pd.DataFrame(bed_data)
X_bed = bed_df.drop('status', axis=1)
y_bed = bed_df['status']

# Train Bed Model
bed_model = RandomForestClassifier()
bed_model.fit(X_bed, y_bed)

# Save Bed Model
with open(bed_model_path, 'wb') as f:
    pickle.dump(bed_model, f)
print(f"Bed model saved at: {bed_model_path}")
