# 3.2.c Functional Requirements

## 3.2.c.1 Business Core Flows

### Business Core Flow 1 - Intelligent Film Lab Discovery

**Objective**

Allow photographers to search for and select a suitable Film Lab based on their needs and preferences.

**Actors**

- Photographer
- System
- Film Lab
- AI Recommendation Service

**Main Flow**

1. The photographer opens the Film Lab Discovery feature.
2. The photographer enters criteria such as location, film type, price, processing time, and rating.
3. The system retrieves Film Labs that match the criteria.
4. The AI analyzes the photographer's preferences and usage history.
5. The system ranks and displays recommended Film Labs.
6. The photographer views the details of a Film Lab.
7. The photographer selects a Film Lab and proceeds to booking.

**Alternative Flow**

- If no Film Lab matches, the system suggests changing the search filters.
- If personalization data is unavailable, Film Labs are ranked by rating and relevance.

**Result**

The photographer finds a suitable Film Lab and can continue to book its services.

### Business Core Flow 2 - Service Booking and Film Collection

**Objective**

Allow photographers to create a film processing service order and choose how their film rolls are delivered to the selected Film Lab.

**Actors**

- Photographer
- Film Lab
- System
- Delivery Partner

**Main Flow**

1. The photographer selects a Film Lab from the discovery results.
2. The photographer views the available services, prices, and estimated turnaround times.
3. The photographer specifies the film type, processing options, scanning quality, printing requirements, and additional requests.
4. The photographer chooses to deliver the film rolls directly or request a pickup service.
5. If pickup is selected, the photographer enters the pickup information and chooses an available time.
6. The system calculates the estimated service and collection costs.
7. The photographer reviews the order details and submits the request.
8. The system creates the service order and, when required, sends a pickup request to a Delivery Partner.
9. The Film Lab verifies the incoming order and schedules processing.
10. The system confirms the order and provides an order code and film handling instructions.

**Alternative Flow**

- If a selected service is unavailable, the system asks the photographer to change the service options.
- If no Delivery Partner is available, the photographer can choose another pickup time or deliver the film rolls directly.
- If the Film Lab cannot accept the order, the system notifies the photographer so another Film Lab can be selected.
- If required information is missing, the system asks the photographer to complete it before submitting the order.

**Result**

A confirmed service order and collection method are recorded, allowing the film rolls to be received and prepared for processing.

### Business Core Flow 3

### Business Core Flow 4

### Business Core Flow 5

### Business Core Flow 6

## 3.2.c.2 AI-powered Personalized Assistance

## 3.2.c.3 Main Functional Modules
