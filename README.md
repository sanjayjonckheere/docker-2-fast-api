## **PROJECT OVERVIEW**
---

#### This project is a web app built using **FastAPI** with a **SQLite database** and **Redis for caching**. It allows users to interact with a **RESTful API for creating and retrieving users**. The project is **containerised using Docker**, making it easy to deploy and run in any environment.
---
**FEATURES** 
1. **FastAPI**: High-performance API framework to handle HTTP requests.
2. **SQLite**: Lightweight database to store user data.
3. **Redis**: Used as a caching mechanism to store and retrieve user data quickly.
4. **Docker**: Simplified deployment using Docker containers.
5. **Nginx**: Used as a reverse proxy to handle requests.
6. **PyCharm Professional**: Full development setup with Docker integration.
---

**PROJECT STRUCTURE**
       
       ├── .gitignore              # Files to ignore in version control
       ├── Dockerfile              # Docker image definition
       ├── docker-compose.yml      # Docker Compose configuration
       ├── main.py                 # FastAPI application with endpoints
       ├── models.py               # SQLAlchemy models for database
       ├── nginx.conf              # Nginx configuration file
       ├── requirements.txt        # Project dependencies
       └── test_main.http          # HTTP request tests for the API
---

**PREREQUISITES** 
1. **Docker**: Ensure you have Docker and Docker Compose installed.
2. **Python**: Python 3.9 or higher.
3. **PyCharm Professional**: For an integrated development environment with Docker support.
---

**CREATE A NEW PROJECT IN PYCHARM**
1. **PYCHARM workflow:** Select the FASTapi template, which contains a pre-configured project structure and essential files to kickstart the development of FastAPI apps.  Good for small projects. For larger projects, check Cookiecutter template.
The app will be running on your local machine on local host, port 8000.
---

**CONTAINERISATION** 
1. **Create requirements.txt and specify all dependencies** 
    1. pip3 freeze > requirements.txt 
    2. git add requirements.txt (staging)
    3. git commit -m "Add requirements.txt with dependencies”

2. **Create a Dockerfile in PyCharm**
    1. Go to the root directory 
        1. New -> file -> Dockerfile (used to build the container image)
        2. Inside the dockerfile
        3. FROM python:3
        4. WORKDIR /app
        5. COPY requirements.txt ./     (copying to the container)
        6. RUN pip install —no-cache-dir -r requirements.txt (No cache, keep it as small as possible and use the requirements.txt)
        7.  COPY . .    So we copy it to our app folder
        8. CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port”,  “8000"]
            1.  —host 0.0.0.0 set the host to any valid interface
            2. —port 8000 set the ports to whatever we like

    2. Once the required dependencies are installed, we'll copy all source files from the project's root directory into the app. If your source files are located in a subdirectory like 'app', you'll need to specify that path instead of a dot.
    3. The Docker container will be built and started. However, if you click the URL or try to access localhost, it won't work. This is because the container is isolated. Its ports are not exposed to the host system by default.
    4. To expose the ports we go to the docker container settings:
        1. Set the port bindings + add
        2. --publish 8000 which is exposed by the fast api
        3. Go to modify options add a host port
        4. Add the host port 8000, This will map the 8000 port on the container to the 8000 port on your local machine. 
 ---     
           
