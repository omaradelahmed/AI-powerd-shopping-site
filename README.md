# AI-Powered Shopping Site Integration

This project integrates artificial intelligence (AI) with a WooCommerce-based shopping site (WordPress). It uses Flask as a backend API to connect machine learning models that handle **recommendation systems**, **sales forecasting**, and **customer classification**.

## 🚀 Features

- **Product Association Rules:** Generates relationships between products using Apriori for recommendations.
- **Customer Classification:** Predicts product categories for users based on demographics (country, age, gender).
- **Sales Forecasting:** Predicts future sales using time series modeling (AutoTS).
- **Flask API:** Provides REST endpoints to trigger model training, generate predictions, and visualize results.
- **WooCommerce Database Integration:** Reads and writes directly to the WordPress MySQL database.

## 🧠 Project Structure

```
project/
│
├── app.py                         # Main Flask application
│
├── api/
│   ├── associationWP.py           # Association rules (Apriori model)
│   ├── classificationWP.py        # Classification model for customer behavior
│   ├── find_products_for_customer.py  # Fetch recommended products for users
│   ├── time_seriesWP.py           # Forecast future sales using AutoTS
│   └── draw_forecastWP.py         # Generates forecast plot (base64 image)
│
├── requirements.txt               # Dependencies for setup
└── README.md                      # Project documentation
```

## ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/omaradelahmed/using-ai-on-a-shopping-site.git
   cd using-ai-on-a-shopping-site
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate   # On Windows
   source venv/bin/activate  # On Linux/Mac
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Ensure you have a MySQL database connected to your WooCommerce site (`wp-ecommerce`).

## 🧩 API Endpoints

| Endpoint | Method | Description |
|-----------|--------|-------------|
| `/genCustomProducts` | POST | Generates association rules for related products |
| `/classificationWP` | POST | Builds and saves the classification model |
| `/get_products_for_user` | GET | Returns recommended products for a specific user |
| `/time_seriesWP` | POST | Trains forecasting model for sales |
| `/draw_forecast` | GET/POST | Returns sales forecast plot as Base64 image |
| `/getState` | GET/POST | Returns current task execution states |

## 📊 Database Tables Created

- `custom_products_association` — Stores generated product associations.
- `custom_country_codes`, `custom_gender_codes` — Categorical encodings for classification model.
- `custom_forecast` — Contains predicted sales data for upcoming days.

## 🧾 Usage Example

Start the Flask server:
```bash
python app.py
```

Trigger AI tasks using API calls (via Postman or Python requests).

Example (Python):
```python
import requests
requests.post("http://127.0.0.1:5000/genCustomProducts")
```

## 🧠 Technologies Used

- **Flask** – Web framework
- **MySQL** – Database (WordPress WooCommerce)
- **Pandas**, **NumPy** – Data handling
- **Scikit-learn**, **MLxtend** – Machine Learning
- **AutoTS** – Time series forecasting
- **Matplotlib** – Visualization

---

This project provides a modular, automated AI engine that enhances any WooCommerce store with intelligent product recommendations and sales insights.
