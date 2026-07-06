# Endearing Peace 🥗
 
A calorie tracking web application built with Django and PostgreSQL. Endearing Peace helps users log meals, monitor daily calorie intake, and manage personal health profiles (BMI, weight/nutrition goals).
 
## Table of Contents
 
- [About the Project](#about-the-project)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Team](#team)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

## About the Project
 
Endearing Peace is a calorie and nutrition tracking platform. Users can register, set up a personal profile, log their meals, and track progress toward their health goals over time.
 
> 🚧 **Status:** Project is in early planning/setup stage. No code has been written yet — this README describes the intended scope and will evolve as development progresses.
 
## Features
 
- **User Authentication** — registration, login, logout, password management
- **User Profiles** — height, weight, age, gender, activity level
- **BMI Calculation** — automatic BMI calculation and category (underweight/normal/overweight/obese)
- **Goal Setting** — target weight, daily calorie goal, macro goals (planned)
- **Meal Logging** — add meals/food entries with calorie and nutrient info
- **Daily Summary** — track total calories consumed vs. daily goal
- **History** — view past days/weeks of logged data (planned)
## Tech Stack
 
| Layer          | Technology       |
|----------------|------------------|
| Backend        | Django (Python)  |
| Database       | PostgreSQL       |
| Frontend       | Django Templates / HTML, CSS (TBD) |
| Testing / QA   | Django Test Framework / pytest (TBD) |
| Version Control | Git & GitHub    |
 
## Team
 
| Name  | Role                                  |
|-------|----------------------------------------|
| Me    | Project Manager, Half-Developer & QA   |
| Makar | Half-Developer & QA                    |

 
### Prerequisites
 
- Python 3.11+
- PostgreSQL 14+
- pip / virtualenv

## Project Structure
 
```
endearing_peace/
├── config/            # Django project settings
├── users/             # Authentication & user profiles app
├── nutrition/         # Meal logging & calorie tracking app
├── templates/         # HTML templates
├── static/            # CSS, JS, images
├── requirements.txt
├── manage.py
└── README.md
```

## Roadmap
 
- [ ] Initialize Django project and PostgreSQL connection
- [ ] Implement user authentication & profile model
- [ ] Implement BMI calculation logic
- [ ] Implement meal/food logging model & views
- [ ] Implement daily calorie summary view
- [ ] Add goal-setting functionality
- [ ] Write unit/integration tests
- [ ] Add history & reporting views
- [ ] Deploy to production environment
## Contributing
 
This is currently a 2-person project (Me & Makar). General workflow:
 
1. Create a feature branch (`git checkout -b feature/your-feature`)
2. Commit your changes with clear messages
3. Open a Pull Request for review
4. Ensure QA/tests pass before merging
## License
 
License to be determined.
 

