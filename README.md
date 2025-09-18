# 🏥 HealthQ: AI-Powered Hospital Queue Management System.

## 📋 Overview
HealthQ is an intelligent hospital management system that leverages AI to optimize patient flow and predict wait timesefficiently. The system helps reduce waiting times, improve resource allocation, and enhance overall patient experience.

## 🎯 Key Features

### 1. AI-Powered Wait Time Prediction
- Real-time prediction of patient wait times
- Uses machine learning (Random Forest) to analyze:
  - Department load
  - Patient condition
  - Emergency situations
  - Symptoms
- Continuously improves predictions based on historical data

### 2. Smart Bed Management
- Real-time bed availability tracking
- Predictive analytics for bed allocation

### 3. Queue Management
- Digital queue system for OPD
- Priority-based queue management
- Real-time queue updates
- Estimated wait time display

### 5. City-Wide Integration
- Unified dashboard for multiple hospitals across the city
- Centralized monitoring of OPD queues, bed occupancy, and emergency capacity
- Scalable architecture for expansion across urban healthcare networks



## 🛠️ Technical Stack

### Frontend
- Django Templates
- Tailwind CSS
- Chart.js for data visualization
- Responsive design for all devices

### Backend
- Python 3.13
- Django 5.1.3
- Django Channels (real-time updates)
- SQLite Database

### AI/ML Components
- Scikit-learn
- Pandas
- NumPy
- Random Forest Regressor for predictions

### Authentication & Security
- Django Authentication System

- JWT for API security

- Role-based access control

## 🚀 Getting Started

### Prerequisites
- Python 3.13 or higher
- pip (Python package manager)
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Shreyasaraf01/healthQ.git
cd healthQ
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Access the application at `http://127.0.0.1:8000`

## 📊 AI Model Training

The system includes an AI model for wait time prediction. To train the model:

1. Navigate to the AI module:
```bash
cd hospital/ai
```

2. Run the training script:
```bash
python ai_model.py
```

The model will be automatically trained on historical data and saved for future predictions.

## 🌟 Future Scope

- Advanced predictive analytics
- Multi-hospital network integration
- NLP-based patient interaction chatbots
- Government health portal integration
- Mobile application development
- Integration with IoT devices for real-time monitoring

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all contributors and team members
- Special thanks to our mentors and advisors
- Inspired by the need for better healthcare management systems

---

## 📞 Support

For support, email: shreyasaraf765@gmail.com

---

Made with ❤️ by Shreya
