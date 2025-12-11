# Full-stack Movie website Project
# Important Notice:
Make sure you have `ffmpeg` installed before testing this site. This github repo does not contain movies and their files to not make the repository heavy. The UI may look messed up with no movies in the site but once movies are added this site looks very clean and attractive.

## Introduction
Welcome to the full stack movie website **Streamify** project! This repository contains both the frontend and backend for the  movie streaming web application. Below are the instructions to set up and run the project locally.

## Prerequisites

Before you start, make sure you have the following installed on your machine:

- Python 3.x
- Node.js
- npm (Node Package Manager)
- Git
- ffmpeg (for streaming purposes a simple ffmpeg algorithm is added)

## Setting Up the Backend

The backend is a Django-based application. Follow these steps to set it up:

### 1. Navigate to the `backend` folder
Open your terminal and navigate to the `backend` folder:

```bash
cd backend
```
### 2. Setup a virtual environment in the backend to avoid conflicts
`python -m venv venv`

  #### Activate the virtual environment:
    `venv\Scripts\activate`
### 3. Install required dependencies:
  `pip install -r requirements.txt`

### 4. Setup the database
```
python manage.py makemigrations
python manage.py migrate
```


## Setting up the Frontend

### 1. Navigate to the `frontend` folder
Open your terminal and navigate to the `backend` folder:

```bash
cd /frontend
```
### 2. Make sure you’re in the frontend folder, and install the dependencies listed in package.json:
```bash
npm install
```

# Running both servers(Running the code):

## 1. In the first terminal window, run the Django backend server:
```bash
cd /backend
python manage.py runserver
```

## 2. In the second terminal window, run the django frontend server:
```bash
cd /frontend
npm start
```




