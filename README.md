# Camp App

The **Camp App** is a Python-based application designed to manage and display camping-related data. It is built using the [Streamlit](https://streamlit.io/) framework for creating interactive web applications. This README provides instructions for running the app locally and within a Docker container.

---

## Features
- Interactive user interface for managing camping data.
- Built with Streamlit for simplicity and flexibility.
- Can be deployed locally or using Docker.

---

## Prerequisites
Before running the app, ensure you have the following installed:
- **Python 3.8+** (for local deployment)
- **Docker** (for containerized deployment)

---

## Running the App Locally

1. **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd camp_app
    ```

2. **Install Dependencies**:
    Use [UV](https://github.com/uv-org/uv) to manage dependencies:
    ```bash
    pip install uv
    uv sync
    ```

3. **Launch the App**:
    Run the Streamlit app:
    ```bash
    streamlit run camp_app.py
    ```
    The app will be accessible at `http://localhost:8501`.

---

## Running the App with Docker

1. **Build the Docker Image**:
    From the `camp_app` directory, build the Docker image:
    ```bash
    docker build -t camp-app .
    ```

2. **Run the Docker Container**:
    Start the container:
    ```bash
    docker run -p 8501:8501 camp-app
    ```
    The app will be accessible at `http://localhost:8501`.

---

## File Structure
camp_app/
├── camp_app/                     # Application source code
│   ├── __init__.py               # Package initializer
│   ├── camp_app.py               # Main application file
│   ├── pair_optimiser_app.py     # Student pair optimiser module
│   ├── parent_info_app.py        # Parent info joiner module
│   ├── student_pair_optimiser.py # Student pairing logic
│   ├── group_info.xlsx           # Example data file
│   ├── pyproject.toml            # Project dependencies and configuration
│   ├── uv.lock                   # Dependency lock file
├── nbs/                          # Jupyter notebooks for analysis
│   ├── parent_info.ipynb         # Notebook for parent info processing
│   ├── student_pair_optimiser.ipynb # Notebook for student pairing optimisation
├── Dockerfile                    # Docker configuration
├── README.md                     # Documentation
├── .gitignore                    # Git ignore rules
```

---

## Troubleshooting
- **Port Already in Use**: Ensure no other application is using port `8501`.
- **Docker Issues**: Verify Docker is installed and running properly.

---

Enjoy using the Camp App!
