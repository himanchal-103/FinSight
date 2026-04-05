# FinSight
Finsight is a RESTful backend API built with Django and Django REST Framework for managing personal finances. 
It provides endpoints for **user authentication**, **role-based authorization**, **transaction management**, and a **financial dashboard**.
This implements caching via **Redis**, **PostgreSQL** as a database, and a **rate limiter** controlling the number of requests made to an api endpoint.

This README.md file serves as an overview for how to run this project. For detailed documentation, refer to the **Documentation** file in the repository.

### 📁 Project Structure
```
├── backend
│   ├── accounts/          # User auth, registration, permissions
│   ├── dashboard/         # Aggregated financial dashboard
│   ├── transactions/      # Transaction management
│   ├── utils/             # Shared utilities (rate limiting, etc.)
│   ├── finsight/          # Django project settings & URL config
│   ├── manage.py
│   ├── requirements.txt
│   └── docker-compose.yml
├── .gitignore
└── README.md
```

### ⚙️ Tech Stack
1. Language: Python3
2. Framework: Django + Django REST Framework
3. Caching: Redis
4. Database: PostgreSQL
5. Containerization: Docker + Docker Compose

#### Prerequisites
Make sure you have the following installed:
1. Python
2. Docker
3. Git

### 🚀 Getting Started

1. Clone the Repository
```
# clone the repository
git clone https://github.com/your-username/finsight.git

# change directory
cd finsight/backend/
```

2. Start Docker container (PostgreSQL and Redis container)
```
docker compose up -d
```
This will:

- Build the PostgreSQL and Redis image
- Spin up a PostgreSQL database and Redis container
- To stop and remove containers:
  ```
  docker compose down
  ```
- To stop and remove volumes (wipes the database):
  ```
  docker compose down -v
  ```
- To start the container
  ```
  docker compose start
  ```
- To stop the container
  ```
  docker compose stop
  ```

3. Start the Django server
```
# To create migrations
python3 manage.py makemigrations

# To apply migrations
python3 manage.py migrate

# To start the Django server
python3 manage.py runserver
```
4. The server will be available at
```
http://127.0.0.1:8000/
```













