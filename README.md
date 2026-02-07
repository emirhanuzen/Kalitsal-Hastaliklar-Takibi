# 🧬 KRAP – Hereditary Risk Analysis Platform

![TEKNOFEST Logo](https://cdn.teknofest.org/media/upload/userFormUpload/teknofest_logo_2024_eng.png)

> **🏆 TEKNOFEST 2026 - Technology for Humanity Competition Project**
> *Category: Health and First Aid*

**KRAP (Hereditary Risk Analysis Platform)** is a modern **web-based Mendelian genetics simulation platform** developed for TEKNOFEST, designed to analyze hereditary disease risks using a hybrid database architecture (SQL Server + MongoDB).

This project aims to raise awareness about hereditary diseases (such as SMA, Cystic Fibrosis) and contribute to preventive health services by predicting genetic risks through mathematical modeling and AI, offering a domestic and national solution for health tech.

---

**KRAP (Hereditary Risk Analysis Platform)** is a modern **web-based Mendelian genetics simulation platform** designed to analyze hereditary disease risks, utilizing a hybrid database architecture (SQL Server + MongoDB).

The platform generates completely **fictional (synthetic) family trees** instead of real person data; however, inheritance in these trees is scientifically calculated using **Mendelian inheritance rules** (recessive, carrier, X-linked, etc.). Instead of randomly assigning diseases, the system:

- ✅ Calculates **allele frequencies**
- ✅ Applies **genotype → phenotype** transformation
- ✅ Generates **probabilistic risk predictions** for the user and their family
- ✅ Enriches disease information with **Google Gemini AI**

---

## 🏗️ Architecture and Technology Stack

### Backend (Python/Flask)
- **Framework**: Flask 2.0+ (RESTful API)
- **Databases**:
  - **Microsoft SQL Server**: User accounts, disease master data
  - **MongoDB**: Family trees, individual documents (NoSQL)
- **Connection Libraries**:
  - `pyodbc` – SQL Server connection
  - `pymongo` – MongoDB connection
- **Security**: `bcrypt` – Password hashing
- **AI Integration**: `google-generativeai` – Gemini API

### Frontend (Next.js/React)
- **Framework**: Next.js 16.0.7 (App Router)
- **UI Libraries**:
  - React 19.2.0
  - Bootstrap 5.3.8
  - Tailwind CSS 4
- **Language**: TypeScript 5
- **Linter/Formatter**: Biome 2.2.0

### Features
- 🎨 Modern, responsive UI design
- 🔄 Next.js API Routes proxy to Flask backend
- 📱 Mobile-friendly interface
- ⚡ Fast and optimized performance

---

## 📁 Project Structure

```
KRAP/
├── app.py                    # 🚀 Flask API Backend - Main application file
├── config.py                 # ⚙️ Database and application configuration
├── database.py               # 🗄️ Hybrid database connections (SQL + MongoDB)
├── validators.py             # ✅ Input validation and business rules
├── routes.py                 # 🌐 Additional API routes (registration, test, etc.)
├── soy_agaci_ureteci.py      # 🌳 Family tree generation algorithm
│
├── services/                 # 🧠 Business logic and services
│   ├── registration_service.py  # Registration operations (New family / Join existing family)
│   ├── gemini_service.py         # Google Gemini AI integration
│   └── tree_cleanup.py          # Helper cleanup functions
│
├── genetics/                 # 🔬 Mendelian genetics calculations
│   ├── constants.py          # Name lists, constants, genetic parameters
│   ├── genetics.py           # Allele frequencies, genotype generation, X-linked/recessive rules
│   ├── person.py             # Person (individual) object creation
│   ├── family_tree.py        # Gene transmission on family tree (ancestor → child)
│   ├── risk_analysis.py      # User-based hereditary risk analysis
│   └── carrier_guarantee.py  # Carrier guarantee algorithm
│
├── frontend/                 # ⚛️ Next.js Frontend Application
│   ├── app/                  # Next.js App Router
│   │   ├── page.tsx          # Main login page
│   │   ├── kayit-ol/         # Registration page
│   │   │   └── page.tsx
│   │   ├── profil/           # Profile page (Family tree + Risk analysis)
│   │   │   └── page.tsx
│   │   ├── api/              # Next.js API routes (proxy to Flask)
│   │   │   ├── login/route.ts
│   │   │   ├── register/route.ts
│   │   │   ├── profil/route.ts
│   │   │   ├── family-tree/route.ts
│   │   │   └── hastalik-bilgileri/route.ts
│   │   ├── layout.tsx        # Root layout
│   │   └── globals.css        # Global CSS styles
│   ├── package.json          # Node.js dependencies
│   ├── next.config.ts        # Next.js configuration (API proxy)
│   ├── tsconfig.json         # TypeScript configuration
│   └── biome.json            # Biome linter/formatter settings
│
└── requirements.txt          # Python dependencies
```

---

## 🌟 Core Features and Scenarios

### 1️⃣ Scenario 1 – Starting a New Family Universe

The user registers with their own **fictional ID number**, date of birth, gender, etc. The system:

1. Determines the user's **generation position based on age** (e.g., 3rd generation = parent)
2. Generates **ancestor generations backwards**:
   - Mother, father
   - Grandmother, grandfather
   - Great-grandmother/grandfather (5-6 generations back)
3. Simulates **forward** child and grandchild generations
4. Generates **genotype** and corresponding **disease status** (Healthy / Carrier / Affected) for each individual
5. Stores the entire family tree in a hybrid database model:
   - **SQL Server** → User accounts (`Users` table)
   - **MongoDB** → Family trees (`FamilyTrees.agac_verisi` document)

### 2️⃣ Scenario 2 – Joining an Existing Family

When registering, the user enters:
- **Parent Fictional ID** (parent's fictional ID number)
- **Own Fictional ID** (fictional ID assigned to them in the tree)

Workflow:

1. Parent user is found on SQL side (`FamilyTreeID_Mongo`, `BireyID_Mongo`)
2. Family tree is retrieved from MongoDB with the same `FamilyTreeID_Mongo`
3. Individual with `fictional_id == own_id` is found **within the tree**
4. **Lineage relationship** between parent and child is verified (`mother_id == parent_uuid` or `father_id == parent_uuid`)
5. Checks if a user account has been created for this individual before
6. If everything is correct, the new user is linked to this individual in SQL

This allows **multiple users within the same family universe** to use the system together, corresponding to different individuals.

### 3️⃣ Risk Analysis and AI-Powered Information

- **Mendelian Genetics Calculations**: Allele frequencies, genotype-phenotype transformation
- **Hereditary Risk Analysis**: Disease transmission probabilities from previous generations for the user
- **Google Gemini AI Integration**: Dynamic, personalized information for each disease
- **Visual Family Tree**: Visualization of past generations and future simulation (children)

---

## 🚀 Installation and Running

### Prerequisites

- **Python 3.x** (3.8+ recommended)
- **Node.js 18+** and npm
- **Microsoft SQL Server** (Express Edition is sufficient)
- **MongoDB** (Local or MongoDB Atlas)
- **ODBC Driver** (for SQL Server, usually comes pre-installed on Windows)

### 1. Clone the Repository

```bash
git clone https://github.com/<user>/KRAP.git
cd KRAP
```

### 2. Backend Installation

#### Create Python Virtual Environment

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

#### Install Python Dependencies

```bash
pip install -r requirements.txt
```

Main packages:
- Flask>=2.0.0
- flask-cors>=4.0.0
- pyodbc>=4.0.0
- pymongo>=4.0.0
- bcrypt>=4.0.0
- google-generativeai>=0.3.0

#### Database Configuration

Update the following fields in the `config.py` file:

```python
# MongoDB Connection Settings
MONGO_CONNECTION_STRING = 'mongodb://localhost:27017/'  # or MongoDB Atlas connection string
MONGO_DATABASE_NAME = 'KRAP_NoSQL_DB'

# MS SQL Server Settings
SQL_SERVER_SUNUCU_ADI = 'localhost\\SQLEXPRESS'  # Your server name
SQL_SERVER_VERITABANI_ADI = 'KRAP'  # Database name
```

#### SQL Server Database Preparation

1. Create a database named `KRAP`
2. At minimum, the following tables are required:
   - `Users` (Email, PasswordHash, KurgusalTC, DogumTarihi, Isim, Soyad, FamilyTreeID_Mongo, BireyID_Mongo, ...)
   - `Hastaliklar` (HastalikAdi, GorulmeOrani, KalitimSekli, ...)

#### MongoDB Preparation

- If using local MongoDB, ensure the MongoDB service is running
- If using MongoDB Atlas, update the connection string in `config.py`
- The `FamilyTrees` collection will be created automatically

### 3. Frontend Installation

```bash
cd frontend
npm install
```

### 4. Running the Application

#### Backend (Flask) - Terminal 1

```bash
# In project root directory
python app.py
```

The Flask application runs by default at:
```
http://localhost:5000
```

#### Frontend (Next.js) - Terminal 2

```bash
# In frontend/ directory
npm run dev
```

The Next.js frontend application runs at:
```
http://localhost:3000
```

**Note:** The frontend proxies to the Flask backend via Next.js API Routes. Both servers must be running.

---

## 📖 Usage

### Logging In

1. Go to `http://localhost:3000`
2. Log in with your fictional ID number and password

### New Registration

1. Click the "Create New Account" button
2. Enter your personal information (Name, Surname, Gender, Date of Birth, ID)
3. Enter your account information (Email, Password)
4. Leave the **Parent ID** field empty → **Scenario 1** (New family universe)
5. Fill in the **Parent ID** field → **Scenario 2** (Join existing family)

### Profile and Risk Analysis

- **Profile Tab**: Your personal information and AI-powered risk analysis
- **Family Tree Tab**: 
  - **My Ancestors**: Visualization of past generations
  - **My Children**: Future simulation (probabilistic)

---

## 🔬 Genetic Calculation Details

### Mendelian Inheritance Rules

The platform supports the following inheritance patterns:

1. **Recessive (Autosomal Recessive)**
   - Genotype: NN (Normal), NT (Carrier), TT (Affected)
   - Phenotype: TT → Affected, NT → Carrier, NN → Healthy

2. **X-Linked Recessive**
   - Male: XnY (Healthy), XtY (Affected)
   - Female: XnXn (Healthy), XnXt (Carrier), XtXt (Affected)

### Allele Frequency Calculation

- **Recessive**: `q = √(prevalence rate)`, `p = 1 - q`
- **X-Linked**: `q = prevalence rate`, `p = 1 - q`

### Risk Analysis

- Disease transmission probabilities from the user's parents and previous generations are calculated
- **Risk level** (Low, Medium, High, Very High) is determined for each disease
- **Carrier probability** percentage is calculated

---

## 🤝 Contributing

If you want to suggest, report bugs, or contribute:

- You can open an issue
- You can send a Pull Request
- You can improve missing areas by following `TODO` / `DEBUG` notes in the code

KRAP is currently a **research and prototype** project; contributions, especially in the genetic modeling and risk analysis layer, will significantly improve the quality of realistic simulation. 🙌

---

## 📝 License

This project is for research and educational purposes. It should not be used for real medical decisions.

---

## 🔗 Contact and Support

You can use GitHub Issues for questions or suggestions.
