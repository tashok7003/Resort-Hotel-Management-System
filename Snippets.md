# Hotel Management System

A comprehensive hotel management system built with Django that includes booking management, analytics, room service, and more.

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

1. Clone the repository:
bash
git clone https://github.com/yourusername/hotel-management-system.git
cd hotel-management-system

2. Install dependencies:
bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt

3. Configure environment variables:
- Create a .env file in the root directory
- Add the following variables:

    SECRET_KEY=your_secret_key
    DEBUG=True
    DATABASE_URL=your_database_url
    EMAIL_HOST=smtp.gmail.com
    EMAIL_PORT=587
    EMAIL_HOST_USER=your_email@gmail.com
    EMAIL_HOST_PASSWORD=your_app_password


4. Run migrations:
bash
python manage.py makemigrations
python manage.py migrate

5. Create a superuser:
bash
python manage.py createsuperuser

6. Run the development server:
bash
python manage.py runserver




