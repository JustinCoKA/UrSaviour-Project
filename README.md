## 🏛️ System Architecture

This project is built on an event-driven architecture using AWS cloud services. The entire pipeline, from data generation to the final database load, is designed to be automated, as shown in the project documentation.

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
