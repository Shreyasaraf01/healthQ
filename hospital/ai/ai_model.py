import os
import numpy as np
import pandas as pd
import pickle
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthQ.settings")
django.setup()

from hospital.models import Patient, Hospital
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUEUE_MODEL_PATH = os.path.join(BASE_DIR, "queue_model.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "encoders.pkl")

def train_models():
    try:
        data = []
        patients = Patient.objects.select_related('hospital').all()

        for p in patients:
            data.append({
                'department': p.hospital.name,
                'patient_type': p.condition,
                'situation': p.situation,
                'symptoms': p.symptoms,
                'waiting_time': p.queue_position if hasattr(p, 'queue_position') and p.queue_position else 0
            })

        queue_data = pd.DataFrame(data)

        if queue_data.empty:
            print("No patient data found. Using default training data.")
            queue_data = pd.DataFrame({
                'department': ['General', 'ICU', 'Maternity'],
                'patient_type': ['Stable', 'Critical', 'Stable'],
                'situation': ['Normal', 'Emergency', 'Normal'],
                'symptoms': ['Cough', 'Fever', 'Headache'],
                'waiting_time': [10, 5, 15]
            })

        # Label Encoders
        dept_encoder = LabelEncoder()
        ptype_encoder = LabelEncoder()
        situation_encoder = LabelEncoder()
        symptoms_encoder = LabelEncoder()

        queue_data['department_encoded'] = dept_encoder.fit_transform(queue_data['department'])
        queue_data['patient_type_encoded'] = ptype_encoder.fit_transform(queue_data['patient_type'])
        queue_data['situation_encoded'] = situation_encoder.fit_transform(queue_data['situation'])
        queue_data['symptoms_encoded'] = symptoms_encoder.fit_transform(queue_data['symptoms'])

        X_queue = queue_data[['department_encoded', 'patient_type_encoded', 'situation_encoded', 'symptoms_encoded']]
        y_queue = queue_data['waiting_time']

        Xq_train, Xq_test, yq_train, yq_test = train_test_split(X_queue, y_queue, test_size=0.2, random_state=42)

        queue_model = RandomForestRegressor(random_state=42)
        queue_model.fit(Xq_train, yq_train)

        with open(QUEUE_MODEL_PATH, 'wb') as f:
            pickle.dump(queue_model, f)

        encoders = {
            'dept_encoder': dept_encoder,
            'ptype_encoder': ptype_encoder,
            'situation_encoder': situation_encoder,
            'symptoms_encoder': symptoms_encoder
        }

        with open(ENCODER_PATH, 'wb') as f:
            pickle.dump(encoders, f)

        print("Models trained and saved successfully.")
        return True

    except Exception as e:
        print(f"Error training models: {str(e)}")
        return False

def predict_queue(department, patient_type, situation, symptoms):
    try:
        with open(ENCODER_PATH, 'rb') as f:
            encoders = pickle.load(f)

        dept_encoder = encoders['dept_encoder']
        ptype_encoder = encoders['ptype_encoder']
        situation_encoder = encoders['situation_encoder']
        symptoms_encoder = encoders['symptoms_encoder']

        # Handle unseen values by mapping to the first class (or you can add 'Other' to your training data)
        def safe_transform(encoder, value):
            if value in encoder.classes_:
                return encoder.transform([value])[0]
            else:
                return 0  # or encoder.transform(['Other'])[0] if you add 'Other' to your training data

        dept_code = safe_transform(dept_encoder, department)
        ptype_code = safe_transform(ptype_encoder, patient_type)
        situation_code = safe_transform(situation_encoder, situation)
        symptoms_code = safe_transform(symptoms_encoder, symptoms)

        with open(QUEUE_MODEL_PATH, 'rb') as f:
            queue_model = pickle.load(f)

        input_data = np.array([[dept_code, ptype_code, situation_code, symptoms_code]])
        prediction = queue_model.predict(input_data)[0]
        return round(prediction, 2)

    except Exception as e:
        print(f"Error making prediction: {str(e)}")
        return None

# Added dummy predict_bed function to resolve ImportError
def predict_bed(department, patient_type, situation, symptoms):
    return 0

# Initialize models if they don't exist
if not os.path.exists(QUEUE_MODEL_PATH) or not os.path.exists(ENCODER_PATH):
    train_models()