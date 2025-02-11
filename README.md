# Resort Hotel Management System

A comprehensive hotel management system built with Django that includes booking management, analytics, room service, and more.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Features
- User Authentication & Authorization
- Hotel & Room Management
- Booking System
- Room Service Management
- Analytics Dashboard
- Inventory Management
- Staff Management
- Waitlist System
- Group Booking Management

### Analytics Features
- Revenue Analysis
- Occupancy Tracking
- Performance Metrics
- Booking Trends
- Custom Reports
- Data Export (PDF, Excel, CSV)

### Room Service Features
- Service Request Management
- Real-time Status Updates
- Feedback System
- Staff Assignment
- Priority Handling

### Booking Features
- Individual & Group Bookings
- Waitlist Management
- Package Deals
- Cancellation Policies
- Dynamic Pricing

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/tashok7003/Resort-Hotel-Management-System.git
   cd Resort-Hotel-Management-System
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Create a `.env` file in the root directory and add the following variables:
   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   DATABASE_URL=your_database_url
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password
   ```

5. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

## Usage

- Access the admin panel at `http://127.0.0.1:8000/admin/` to manage hotels, rooms, bookings, and more.
- Access the analytics dashboard at `http://127.0.0.1:8000/analytics/` to view reports and analytics.


## API Endpoints

### Analytics
- **GET** `/analytics/` - Dashboard view
- **POST** `/analytics/report/generate/` - Generate new report
- **GET** `/analytics/report/<id>/` - View specific report
- **GET** `/analytics/export/` - Export data

### Booking
- **GET** `/booking/` - List bookings
- **POST** `/booking/create/` - Create booking
- **GET** `/booking/<id>/` - View booking details
- **POST** `/booking/<id>/cancel/` - Cancel booking

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support
For support, please create an issue in the GitHub repository or contact ashokdevamani7003@gmail.com.
