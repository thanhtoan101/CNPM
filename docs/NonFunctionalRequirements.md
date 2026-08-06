# 3.2.d Non-Functional Requirements
The non-functional requirements define the quality attributes, technical constraints, and operational characteristics of the AI-powered Film Photography Platform. These requirements ensure that the platform is secure, reliable, maintainable, scalable, and capable of supporting multiple Film Labs and users.

## 3.2.d.1 Security and Access Control
- The system shall provide secure user authentication using JSON Web Token (JWT).
- Role-Based Access Control (RBAC) shall be applied to control access permissions for different system roles, including Photographer, Film Lab Owner, Photography Expert, Delivery Partner, System Administrator, and AI Assistant.
- Users shall only be allowed to access functions and data corresponding to their assigned roles.
- Sensitive information such as user credentials, personal information, order information, and digital scan files shall be protected from unauthorized access.

## 3.2.d.2 Cloud Storage and Data Protection
- Digital scan files shall be stored using cloud-based storage services.
- The system shall provide backup and recovery mechanisms to reduce the risk of data loss.
- Users shall be able to securely access and manage their digital scan files through the Digital Film Archive.
- Stored data shall remain consistent and accessible to authorized users.

## 3.2.d.3 Modular Architecture
- The system shall use a modular architecture that separates major components, including Mobile Application, Web Portal, Backend Services, AI Services, Database, and Cloud Storage.
- Each component should be developed and maintained independently to improve system maintainability.
- The modular architecture shall support future expansion without requiring major modifications to the entire system.
- AI services and other platform components should be capable of being upgraded or extended independently.

## 3.2.d.4 Integration and API Requirements
- The system shall provide RESTful APIs for communication between the mobile application, web portal, backend services, and other system components.
- The APIs shall support integration with payment gateways and third-party logistics providers.
- The architecture should allow additional photography-related services to be integrated in the future.
- Data exchanged between system components shall follow consistent and secure communication mechanisms.

## 3.2.d.5 Availability and Scalability
- The system shall provide high availability to support users and Film Labs during normal operations.
- The platform shall be scalable to accommodate an increasing number of photographers, Film Labs, orders, digital images, and community activities.
- The system shall support multiple Film Labs operating simultaneously within the same platform.
- System performance and data consistency should be maintained when the number of users and transactions increases.


# 3.2.e Theory & Practical
The project applies software engineering principles and modern technologies to develop an integrated digital ecosystem for the analog photography community.
The proposed technologies for each major system component are described below.

## 3.2.e.1 Mobile Application – Flutter
Flutter is used to develop the mobile application for photographers on Android and iOS platforms.
The mobile application provides major user functions such as searching for Film Labs, booking film processing services,
tracking orders, accessing digital scans, managing the Digital Film Archive, participating in the Marketplace, and interacting with the AI Assistant.

## 3.2.e.2 Web Portal – ReactJS / Next.js
ReactJS or Next.js is used to develop the web-based interfaces of the platform.
The web portal supports Film Lab owners in managing laboratory profiles, service packages,
customer orders, processing workflows, digital scan delivery, customers, and operational reports.
It can also support administration functions for managing the overall platform.

## 3.2.e.3 Backend Services – ASP.NET Core Web API / Node.js
ASP.NET Core Web API or Node.js with Express can be used to implement the backend services.
The backend is responsible for processing business logic, managing requests from mobile and web applications,
communicating with the database, providing RESTful APIs, and integrating external services.

## 3.2.e.4 Database – PostgreSQL
PostgreSQL is used as the relational database management system of the platform.
The database stores structured information such as user accounts, Film Lab profiles,
service packages, orders, processing status, marketplace information, reviews, and other system data.

## 3.2.e.5 Authentication – JWT & OAuth2
JWT and OAuth2 are used to support secure authentication and authorization.
JWT can be used to maintain authenticated user sessions when users access protected APIs.
Role-Based Access Control can be combined with authentication mechanisms to manage permissions for different system roles.

## 3.2.e.6 Cloud Storage – Azure Blob Storage / Firebase Storage
Azure Blob Storage or Firebase Storage can be used to store digital scan files and other media resources.
Cloud-based storage allows the platform to manage a large number of digital photographs while supporting secure access, 
backup, recovery, and future scalability.

## 3.2.e.7 AI Integration
Artificial Intelligence is integrated into the platform to provide intelligent and personalized services.
The proposed AI technologies include:
- OpenAI GPT API for conversational AI capabilities.
- LangChain or Semantic Kernel for developing AI-powered workflows.
- Retrieval-Augmented Generation (RAG) for providing domain-specific photography knowledge to the AI Assistant.
- Recommendation Systems for suggesting suitable Film Labs, film types, services, and educational resources.
- Computer Vision models for analyzing the quality of scanned film images.

These technologies support the AI-powered Photography Assistant and personalized recommendation features of the platform.

## 3.2.e.8 Search Engine – Elasticsearch / OpenSearch
Elasticsearch or OpenSearch can be used to provide efficient search capabilities.
The search engine can support Film Lab discovery, service searching, marketplace searching,
and retrieval of photography-related knowledge and content.

## 3.2.e.9 Cloud Deployment – Microsoft Azure
Microsoft Azure is proposed as the cloud deployment platform.
Azure can provide cloud infrastructure for deploying backend services, databases, storage services 
and other components required to operate and scale the platform.

## 3.2.e.10 CI/CD – GitHub Actions
GitHub Actions can be used to support Continuous Integration and Continuous Deployment (CI/CD).
It helps automate development processes such as building, testing, and preparing project components for deployment when changes are made to the source code.

## 3.2.e.11 Version Control – GitHub
GitHub is used as the version control and collaboration platform for the project.
Team members can work on separate branches, record changes through commits, review changes using pull requests, and merge completed work into the main project branch.

## 3.2.e.12 Technology Integration
The project combines Software Engineering, Digital Asset Management, Artificial Intelligence, Computer Vision, Recommendation Systems, and Knowledge Management.
These technologies work together to build a scalable digital ecosystem that connects photographers, Film Labs, photography experts, delivery partners, 
and administrators while supporting intelligent AI-powered services for the analog photography community.

