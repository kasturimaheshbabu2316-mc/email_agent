# Architecture Document for **The Closer** – Cold Email Writer & Send Bot

---

## 📚 Overview
The **Closer** is a lightweight, modular Python application that automates the generation, preview, and safe sending of personalized cold outreach emails for job seekers. It is deliberately designed for live teaching demos, emphasizing **clarity**, **safety**, and **extensibility**.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Input Layer
        A["Contacts (JSON, CSV, or Hard-coded List)"]
    end
    subgraph Core Engine
        B[Contact Loader]
        C[Email Template Engine]
        D[LLM Enhancer]
        E["Preview UI or CLI"]
        F[User Confirmation]
        G["Email Sender (SMTP / Gmail API / Draft Mode)"]
        H[Logger]
    end
    subgraph Output Layer
        I[Sent or Draft Emails]
        J[Outreach Log CSV]
        K[Proof Screenshots]
    end

    A --> B --> C --> D --> E --> F --> G --> I
    G --> H --> J
    I --> K
    style Input Layer fill:#f9f9f9,stroke:#333,stroke-width:1px
    style Core Engine fill:#e6f7ff,stroke:#2b6cb0,stroke-width:2px
    style Output Layer fill:#f0fff4,stroke:#2f855a,stroke-width:1px