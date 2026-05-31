# Iraq Blood Donation Bot

## Project Description

This is a professional and integrated Telegram bot project for blood donation in Iraq. It connects blood donors with patients based on governorate, blood type, location, and emergency status. The bot is designed to be fast, user-friendly, and production-ready.

## Features

- **Dynamic Start Menu**: Search for donors immediately without registration.
- **Donor Registration**: Dedicated process for those who want to help.
- **Iraqi Phone Validation**: Strict Regex for (077, 078, 079, 075) with 11 digits.
- **Governorate & Blood Type Search**: Fast filtering across all 19 Iraqi governorates.
- **GPS Location System**: Find nearest donors based on real-time location sharing.
- **Emergency Alert System**: Notify all matching donors in a specific governorate instantly.
- **Data Privacy**: Users can delete all their data with one click.
- **Donor Rating & History**: Track donations and build trust within the community.
- **Professional Admin Panel**: Statistics, user management, and broadcast capabilities.
- **Security**: Anti-spam middleware, rate limiting, and SQL injection protection.
- **Modern Arabic UI**: Clean, emoji-rich, and user-friendly interface.

## Technologies Used

- Python 3.12
- aiogram 3.x
- SQLite (initial, with PostgreSQL migration support)
- SQLAlchemy ORM
- Redis (for caching and sessions)
- Docker
- Docker Compose
- Railway or Render (for deployment)
- python-dotenv (for secret variables)
- Async Programming
- Clean Architecture
- Repository Pattern
- Modular Structure

## Project Structure

```
Iraq_Blood_Donation_Bot/
├── app/
│   ├── bot/
│   │   ├── handlers/
│   │   ├── keyboards/
│   │   ├── middlewares/
│   │   └── services/
│   ├── database/
│   ├── models/
│   ├── utils/
│   ├── config/
│   ├── admin/
│   └── logs/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
└── .env.example
```

## Keep-Alive System

The bot includes a built-in health check server (on port 8080) and a `keep_alive.py` script. 
- To keep the bot active on platforms like Render or Railway, the platform will automatically ping the health check endpoint.
- Alternatively, you can run `python keep_alive.py` on a separate process to keep the bot "awake".

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository_url>
cd Iraq_Blood_Donation_Bot
```

### 2. Environment Variables

Create a `.env` file in the root directory of the project based on `.env.example` and fill in your details:

```
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
REDIS_HOST=redis
REDIS_PORT=6379
DATABASE_URL=sqlite:///./app/database/blood_donation.db
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run with Docker Compose

```bash
docker-compose up --build
```

### 5. Run Locally (without Docker)

```bash
python app/main.py
```

## Contribution

Feel free to contribute to this project by submitting issues or pull requests.

## License

This project is licensed under the MIT License.
