# Docker Usage Manual for Team Members

---

## ✅ Requirements

- Install **Docker Desktop**  
  → Available for Mac and Windows.
- (Optional) Install [Git](https://git-scm.com/)  
  → Required if you want to clone the project from GitHub.

---

## 📁 1. Clone the Repository

```bash
git clone https://github.com/JustinCoKA/UrSaviour-Project.git
cd UrSaviour-Project
```

↺ Or:  
If the project is shared via ZIP, unzip and open the project folder in VSCode.

---

## ▶️ 2. Start the Docker Containers

```bash
docker-compose up --build
```

- This will build and start the FastAPI backend and MySQL database.
- Access FastAPI at:  
  `http://localhost:8000`

---

## 🛠️ 3. Initialize the Database

After the containers are running:

```bash
docker exec -it ursaviour-backend-1 bash
python init_db.py
```

*(Replace `ursaviour-backend-1` with your actual container name. You can check it with `docker ps`.)*

---

## 🔄 4. Rebuild if Changes Are Made

```bash
docker-compose up --build
```

Use `--build` when you update dependencies or Dockerfile.

---

## 🔚 5. Stop Containers

```bash
docker-compose down
```

---

## 💡 Notes

- MySQL credentials are stored in the `.env` file.
- FastAPI backend code is in `backend/app/`.
- Frontend code (HTML/CSS/JS) is in the `frontend/` folder.

---