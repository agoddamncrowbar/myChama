# High-Level Architecture – MyChama

This document outlines the high-level architectural design of the MyChama platform. The architecture is modular and scalable, leveraging a service-oriented approach to support various user roles, financial operations, and communication needs within chama groups.

---

## 1. Architectural Overview

MyChama consists of the following layers:

### 1.1 Presentation Layer
- **Technology**: React (Web), Flutter or React Native (Mobile)
- **Purpose**: Interfaces for members, treasurers, and chairpersons to interact with the system.
- **Key Features**:
  - Registration, login
  - Dashboards for financial and group activities
  - Meeting scheduling, notifications, loan request forms

---

### 1.2 Application Layer (API Gateway)
- **Technology**: Node.js with Express.js
- **Purpose**: Central routing layer that manages client requests and delegates to appropriate microservices.
- **Responsibilities**:
  - Authentication & session management
  - Role-based access control
  - Aggregation of data across services

---

### 1.3 Microservices Layer
Each microservice handles a specific domain function. Services are loosely coupled and communicate via REST APIs.

| Service               | Description                                         |
|-----------------------|-----------------------------------------------------|
| **User Service**      | Handles user profiles, registration, authentication |
| **Finance Service**   | Manages contributions, loans, repayments            |
| **Notification Service** | Sends reminders, announcements, and loan updates  |
| **Meeting Service**   | Manages meeting schedules, minutes, reminders       |
| **Polling Service**   | Manages group votes and polls                       |

Each service has its own controller, service logic, and internal database if needed (or shares via central DB with scoped collections).

---

### 1.4 Data Layer
- **Database**: MongoDB (NoSQL)
- **Structure**: Collections for users, groups, contributions, loans, polls, and meetings
- **Features**:
  - JSON-style flexible schema for evolving features
  - Embedded documents for relationships like member-loans

---

### 1.5 Infrastructure Layer
- **Hosting**: Cloud (e.g., Render, Railway, or AWS Elastic Beanstalk)
- **Storage**: Firebase for user files (optional), S3-compatible for reports
- **Messaging**: Firebase Cloud Messaging (FCM) or OneSignal for notifications
- **CI/CD**: GitHub Actions for automated testing and deployment

---

## 2. Data Flow Overview

1. User logs in from frontend → API Gateway → User Service authenticates → token returned
2. User submits contribution → API Gateway → Finance Service updates DB → Notification Service sends confirmation
3. Member requests loan → Approval handled via Finance + Notification + User services
4. Chairperson sends announcement → Notification Service → Push to all members

---

## 3. Security Considerations

- JWT-based authentication and refresh tokens
- Rate limiting and input validation
- Role-based authorization (admin, treasurer, chairperson, member)
- HTTPS enforced on all endpoints

---

## 4. Scalability & Maintainability

- Each microservice can be deployed independently
- Services are container-ready (Docker)
- Future-proof design allows for integration with payment APIs (e.g., M-Pesa, PayPal)
- Easily extendable to support investment tracking, audit logs, and group savings goals

