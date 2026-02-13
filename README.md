# n8n Name Splitter Automation for Google Workspace

This project provides an automated solution for splitting complex Spanish full names into individual components (First Name, Second Name, First Surname, Second Surname) using an **n8n workflow** and a **FastAPI** backend service.

## 🚀 Overview

Processing names in Spanish can be challenging due to composite last names (e.g., "de la Cruz") and multiple first names. This solution uses a Python-based logic to handle these cases intelligently, integrated into a seamless n8n automation flow that works with Google Drive and Google Sheets.

### Key Features

- **Intelligent Name Splitting**: Processes "de", "la", "los", "del", etc., to correctly group surnames.
- **n8n Automation**: Automatically triggers when a new Excel file is uploaded to a Google Drive folder.
- **Google Workspace Integration**: Reads from Excel on Drive and appends results to a Google Sheet.
- **Dockerized Backend**: The FastAPI service is ready to be deployed using Docker.
- **Error Notifications**: Sends Gmail alerts if the processing fails or if data is missing.

---

## 🛠️ Components

1.  **FastAPI Backend (`main.py`)**: A lightweight Python service that performs the name splitting logic.
2.  **n8n Workflow (`n8n_workflow.json`)**: The automation logic that coordinates the data flow between Google services and the API.
3.  **Docker Setup**: `Dockerfile` and `docker-compose.yml` for easy deployment.

---

## 📋 Prerequisites

- **n8n** (Self-hosted or Desktop)
- **Docker** & **Docker Compose**
- **Google Cloud Console Project** (with Google Drive and Google Sheets APIs enabled)
- **Gmail Account** (for notifications)

---

## 🔧 Installation & Setup

### 1. Backend Deployment

Clone the repository and run the service using Docker:

```bash
docker-compose up --build -d
```

The API will be available at `http://localhost:8000`.

> [!NOTE]
> If you are using n8n cloud or a remote instance, you must expose this API using a tunnel (like Localtunnel or Ngrok) or host it on a public server.

### 2. n8n Workflow Configuration

1.  Open n8n and click on **Workflows > Import from File**.
2.  Select the `n8n_workflow.json` file from this repository.
3.  **Configure Credentials**:
    - **Google Drive Trigger**: Connect your Google account.
    - **Google Drive Node**: Connect your Google account.
    - **Google Sheets Node**: Connect your Google account.
    - **Gmail Node**: Connect your Google account.
4.  **Update IDs**:
    - In the **Google Drive Trigger**, select the folder you want to watch.
    - In the **HTTP Request** node, update the URL to point to your FastAPI service (e.g., `https://your-tunnel-url.loclx.io/split_names`).
    - In the **Append row in sheet** node, select your target Google Sheet.

---

## 📖 API Documentation

### POST `/split_names`

Accepts a list of objects containing a `NOMBRE_COMPLETO` field and returns the objects with split name components.

**Request Body:**

```json
[
  {
    "NOMBRE_COMPLETO": "JUAN DE LA CRUZ PEREZ GARCIA",
    "Cedula": "12345678"
  }
]
```

**Response Body:**

```json
[
  {
    "NOMBRE_COMPLETO": "JUAN DE LA CRUZ PEREZ GARCIA",
    "Cedula": "12345678",
    "p_nombre": "Juan",
    "s_nombre": "De La Cruz",
    "t_nombre": "",
    "p_apellido": "Perez",
    "s_apellido": "Garcia"
  }
]
```

---

## 🤝 Contribution

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
