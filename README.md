# Study Bridge

**Study Bridge** is an open-source platform designed for university students to access and share academic resources, interact with peers, and enhance their learning experience. This repository hosts the complete codebase for the project, covering both backend and frontend development.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Technical Stack](#technical-stack)
4. [Setup Instructions](#setup-instructions)
   - [Backend (Django)](#backend-django)
   - [Frontend (React)](#frontend-react)
   - [Using Docker](#using-docker)
5. [API Documentation](#api-documentation)
6. [Contribution Guidelines](#contribution-guidelines)
7. [Future Enhancements](#future-enhancements)
8. [License](#license)

---

## Project Overview

Study Bridge aims to:

- Provide a centralized hub for sharing lecture notes, handouts, and past papers.
- Offer interactive tutorials and peer-to-peer learning tools.
- Facilitate discussions and real-time group studies.
- Personalize the user experience based on the student’s course and year of study.

This open-source initiative invites contributors to join and help enhance the platform for a global academic audience.

---

## Features

1. **Resource Sharing**: Upload/download academic materials like notes, past papers, and tutorials.
2. **Interactive Tutorials**: Live and recorded tutorials categorized by course and semester.
3. **Discussion Forums**: Collaborative problem-solving and knowledge sharing.
4. **Personalized Dashboards**: Customized content based on the user’s course, year, and semester.
5. **Study Schedules**: Manage and share personalized study timetables.
6. **Gamification**: Reward contributors and active users with badges and leaderboard rankings.

---

## Technical Stack

### Backend:

- **Django**: Python-based backend framework.
- **Django REST Framework**: For building RESTful APIs.
- **PostgreSQL**: Relational database for storing user data and resources.

### Frontend:

- **React.js**: For building dynamic and interactive user interfaces.
- **Tailwind CSS**: For styling and responsiveness.
- **Axios**: For making API requests.

---

## Setup Instructions

### Backend (Django)

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/studybridge.git
   cd studybridge/backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables in a `.env` file:
   ```env
   SECRET_KEY=<your_django_secret_key>
   DEBUG=True
   DATABASE_URL=postgres://<username>:<password>@localhost:5432/studybridge
   ```
5. Apply migrations:
   ```bash
   python manage.py migrate
   ```
6. Start the development server:
   ```bash
   python manage.py runserver
   ```

### Frontend (React)

1. Navigate to the frontend folder:
   ```bash
   cd studybridge/frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the React development server:
   ```bash
   npm start
   ```
4. Open the app in your browser at `http://localhost:3000`.

### Using Docker

1. Ensure Docker and Docker Compose are installed:
   ```bash
   docker --version
   docker-compose --version
   ```
2. Build and run the containers:
   ```bash
   docker-compose up --build
   ```
3. Access the backend at `http://localhost:8000` and the frontend at `http://localhost:3000`.

---

## API Documentation

The API endpoints are powered by Django REST Framework. Use the interactive API documentation available at:

```
http://localhost:8000/api/docs/
```

Key endpoints include:

- **Authentication**: `/api/auth/`
- **Resources**: `/api/resources/`
- **User Profiles**: `/api/profiles/`

---

## Contribution Guidelines

We welcome contributions from developers worldwide! Here’s how to get started:

1. Fork the repository.
2. Create a new branch for your feature:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Description of your changes"
   ```
4. Push the branch to your fork:
   ```bash
   git push origin feature-name
   ```
5. Submit a pull request to the main branch.

---

## Future Enhancements

1. **AI-Based Recommendations**: Personalized resource and tutorial suggestions.
2. **Mobile App**: Android and iOS apps for better accessibility.
3. **Analytics Dashboard**: Insights for admins and educators.
4. **Real-Time Chat**: Enable discussions and live Q&A sessions.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact

For any questions or suggestions, feel free to reach out:

- **Email**: [nhousnahishaq@gmail.com](mailto:nhousnahishaq@gmail.com)
- **GitHub**: [nhbi05](https://github.com/nhbi05)

---

Happy Coding! 🚀
