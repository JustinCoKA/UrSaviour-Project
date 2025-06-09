
# UrSaviour: Grocery Discount Assistant

## 📄 Project Overview

**Course:** NIT3003 – IT Capstone Project (2025 S1B4)  
**Project Title:** UrSaviour – Grocery Discount Assistant: Personalized Savings Application  
**Submission Date:** June 1, 2025

---

## 🧭 Table of Contents

1. [Introduction](#introduction)  
2. [Functional Requirements](#functional-requirements)  
3. [Non-Functional Requirements](#non-functional-requirements)  
4. [Use Case Descriptions](#use-case-descriptions)  
5. [Data Pipeline Architecture](#data-pipeline-architecture)  
6. [Tools](#tools)  
7. [Sequence Diagrams](#sequence-diagrams)  
8. [Resource Management](#resource-management)  
9. [UI Design](#ui-design)  
10. [Risk Management](#risk-management)  
11. [Timeline Gantt Chart](#timeline-gantt-chart)  
12. [References](#references)  

---

## 📘 Introduction

### General Background
Due to rising inflation and living costs, Australian families face difficulties in managing grocery expenses. UrSaviour addresses this by providing a centralized web platform to simulate grocery discount pamphlets using internal datasets rather than web scraping, ensuring legality and sustainability.

### Market Analysis
- AUD 125B grocery sector (2023)
- Users struggle to manually check promotions across platforms.
- New international consumers often lack access or understanding of promotions.

### Competitor Analysis
- **Frugl:** Comprehensive, but relies heavily on scraping.
- **WhichGrocer:** Easy UI but limited features without subscription.
- **Grocerize:** Minimal and fast, but lacks scalability.

### Project Aims & Unique Value
UrSaviour is a lawful, ethical, and user-friendly discount tracking platform featuring:
- Personalized watchlists
- AI chatbot
- Internal fake data generation

---

## 🎯 Functional Requirements

- **User Registration & Login**
- **PDF Scraping & ETL Management**
- **Product Info & Price Display**
- **Watchlist Management**
- **AI Assistant Integration**
- **Admin Login**
- **Database Management**

---

## 🛠️ Tools

- **Frontend:** HTML, CSS, JavaScript, WIX (for UI/UX)
- **Backend:** Python (FastAPI / Flask)
- **Database:** MySQL
- **Cloud & ETL:** AWS EC2, Lambda, S3
- **API Integration:** REST, OpenAI (Chatbot)

---

## 🚦 Non-Functional Requirements

- Password complexity, secure login/session
- Responsive UI (<2–3 sec interaction time)
- Encrypted communication (HTTPS)
- Ethical data handling
- Resilient background notification and ETL process

---

## 💡 Use Case Descriptions

- **User Registration:** Validates and stores new users.
- **Login:** Authenticates with secure sessions.
- **View Product Info & Compare Prices:** Multi-store price comparison.
- **Watchlist Management:** Monitor selected items and receive alerts.
- **Chatbot (AI Assistant):** Query discounts via natural language.
- **ETL Execution:** Parses weekly simulated PDFs for price updates.
- **Admin Management:** Admin dashboard to manage data, users, ETL logs.

---

## 🔄 Data Pipeline Architecture

1. **Foundational Dataset:** CSV/XLSX with product details stored in AWS S3
2. **PDF Generation:** Simulated weekly offers via ReportLab
3. **ETL Workflow:** AWS Lambda auto-triggers on S3 upload, parses PDF, updates RDS (MySQL)

```mermaid
graph TD
    subgraph "Users"
        U[User]
        A[Admin]
    end

    subgraph "UrSaviour Web Application"
        FE[("Front-End <br> HTML/CSS/JS")]
    end

    subgraph "UrSaviour Back-End (Python)"
        API[REST API]
        AI_GW[AI Assistant Gateway]
    end

    subgraph "Data & Storage (AWS)"
        RDS[("MySQL Database <br> Amazon RDS")]
        subgraph "Data Generation & ETL Pipeline"
            S3_DS[("Foundational Dataset <br> Amazon S3")]
            Script[("PDF Generation Script <br> EC2 / Lambda")]
            S3_PDF[("Simulated PDF Watch Folder <br> Amazon S3")]
            ETL[("ETL Process <br> Amazon Lambda")]
        end
    end

    subgraph "External Services"
        OpenAI[("OpenAI GPT API")]
        Email[Email Service]
    end

    U --> FE
    A --> FE
    FE --> API
    API --> RDS
    API --> AI_GW
    AI_GW --> OpenAI
    S3_DS --> Script
    Script --> S3_PDF
    S3_PDF -- S3 Event Trigger --> ETL
    ETL --> RDS
    API -- Triggers Notifications --> Email
    Email --> U
---

## 🔧 UI & Sequence Diagrams

- Clear wireframes and mockups for:
  - Registration
  - Login
  - Product Browsing
  - Watchlist
  - Chatbot Interface
  - Admin Dashboard

---

## 👥 Resource Management

- Task allocation across team
- Resource scheduling and contingency plans
- Evaluation metrics for project delivery

---

## ⚠️ Risk Management

- PDF parsing or data validation failure
- Email script or backend outages
- Database unavailability
- Ethical concerns with fake data generation

---

## 📅 Timeline (Gantt Chart)

Project timeline includes planning, development, testing, deployment, and report submission phases.

---

## 📚 References

- ABS Australia
- ACCC reports
- Woolworths & Coles API policies
- Industry analysis sources
