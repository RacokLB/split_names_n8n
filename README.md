# n8n Name Splitter Automation for Google Workspace

This project provides an automated solution for splitting complex Spanish full names into individual components (First Name, Second Name, Third Name, First Surname, Second Surname) using an **n8n workflow** and a **FastAPI** backend service.

## 🚀 Overview

Processing names in Spanish can be challenging due to composite last names (e.g., "de la Cruz") and multiple first names. This solution uses a Python-based logic to handle these cases intelligently, integrated into a seamless n8n automation flow that works with Google Drive and Gmail.

### Key Features

- **Intelligent Name Splitting**: Processes "de", "la", "los", "del", etc., to correctly group surnames.
- **XLSX File Processing**: Upload an Excel file and receive a processed file with names split into columns, rejected rows, and a summary sheet.
- **Data Validation**: Validates Cédula (6-8 digits), Nacionalidad (V/E), and cleans name fields automatically.
- **n8n Automation**: Automatically triggers when a new Excel file is uploaded to a Google Drive folder.
- **Google Workspace Integration**: Downloads from Drive, processes via API, uploads result back to Drive.
- **Email Notifications**: Sends Gmail alerts with the processed file attached on success, or error details on failure.
- **Dockerized Backend**: The FastAPI service and tunnel are deployed together using Docker Compose.
- **API Security**: Protected with API Key authentication and rate limiting.

---

## 🛠️ Components

1. **FastAPI Backend (`main.py`)**: A Python service with two endpoints for name splitting — JSON-based and file upload.
2. **Data Validators (`validators.py`)**: Input validation and cleaning module for XLSX processing (Cédula, Nacionalidad, Name).
3. **n8n Workflow (`📝Split Names v2 — File Upload _ FAST API _ PYTHON.json`)**: The automation logic that coordinates the data flow between Google services and the API.
4. **Docker Setup**: `Dockerfile` and `docker-compose.yml` for easy deployment with built-in tunnel.

---

## 📋 Prerequisites

- **n8n** (Self-hosted or Desktop)
- **Docker** & **Docker Compose**
- **Google Cloud Console Project** (with Google Drive API enabled)
- **Gmail Account** (for notifications)
- **LocalXpose Account** (for tunnel, or use any tunnel service)

---

## 🔧 Installation & Setup

### 1. Backend Deployment

Clone the repository and create a `.env` file:

```env
API_KEY=your-secret-api-key-here
LX_ACCESS_TOKEN=your-localxpose-token-here
```

Run the service using Docker:

```bash
docker-compose up --build -d
```

Get the public tunnel URL:

```bash
docker logs loclx-tunnel
```

> [!NOTE]
> The tunnel URL changes each time you restart. Update the n8n workflow HTTP Request node accordingly.

### 2. n8n Workflow Configuration

1. Open n8n and click on **Workflows > Import from File**.
2. Select the `📝Split Names v2 — File Upload _ FAST API _ PYTHON.json` file.
3. **Configure Credentials**:
   - **Google Drive Trigger**: Connect your Google account.
   - **Google Drive Nodes**: Connect your Google account.
   - **Gmail Node**: Connect your Google account.
4. **Update Configuration**:
   - In the **Google Drive Trigger**, select the folder you want to watch.
   - In the **Upload to API** node, update the URL to your tunnel URL (e.g., `https://your-subdomain.loclx.io/process_file?header_row=1`).
   - Set the **API Key** in n8n Variables as `API_KEY`.
   - In the **Upload Result to Drive** node, select your target Google Drive folder.

---

## 📖 API Documentation

### POST `/split_names`

Accepts a JSON list of objects containing a `NOMBRE_COMPLETO` field and returns the objects with split name components.

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

### POST `/process_file`

Upload an XLSX file for batch processing. Returns a processed XLSX with three sheets.

**Parameters:**

- `file` (form-data): The XLSX file to process.
- `header_row` (query, default: `4`): Row number where column headers are located (1-indexed).
- `sheet_name` (query, optional): Specific sheet name to process.

**Expected XLSX Columns:**

| Raw Header               | Maps To           | Validation          |
| ------------------------ | ----------------- | ------------------- |
| `CANT. REG`              | `N°`              | Row number          |
| `NAC.`                   | `Nacionalidad`    | Must be `V` or `E`  |
| `N° CÉDULA DE IDENTIDAD` | `Cedula`          | Numeric, 6-8 digits |
| `NOMBRE Y APELLIDOS`     | `NOMBRE_COMPLETO` | Non-empty, cleaned  |

**Response:** A downloadable XLSX file with three sheets:

- **Processed**: Successfully split names with all output columns.
- **Rejected**: Rows that failed validation with error details.
- **Summary**: Processing statistics.

**Output Columns:**

| Column            | Description         |
| ----------------- | ------------------- |
| `N°`              | Row number          |
| `Nacionalidad`    | V or E              |
| `Cedula`          | ID number           |
| `NOMBRE_COMPLETO` | Full name (cleaned) |
| `p_nombre`        | First name          |
| `s_nombre`        | Second name         |
| `t_nombre`        | Third name          |
| `p_apellido`      | First surname       |
| `s_apellido`      | Second surname      |

---

## 🔄 n8n Workflow Flow

```
Google Drive Trigger → Backup Original → Download XLSX → Upload to API
    → If Success (200) → Upload Result to Drive → Merge → Success Email (with attachment) → Delete Original
    → If Error → Error Email
```

---

## 🤝 Contribution

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
