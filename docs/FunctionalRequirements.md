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

### Business Core Flow 2 - Film Processing Service Booking

**Objective**

Allow photographers to book a film processing service from a selected Film Lab.

**Actors**

- Photographer
- Film Lab
- System

**Main Flow**

1. The photographer selects a Film Lab from the discovery results.
2. The photographer views the available processing services and prices.
3. The photographer chooses options such as film type, development method, scan quality, and film return method.
4. The photographer enters the number of film rolls and delivery or drop-off information.
5. The system calculates the estimated price and processing time.
6. The photographer reviews the booking details and submits the request.
7. The system creates the booking and sends it to the Film Lab.
8. The Film Lab accepts the request.
9. The system confirms the booking and provides an order code and handling instructions.

**Alternative Flow**

- If a selected service is unavailable, the system asks the photographer to choose another service.
- If the Film Lab cannot accept the request, the photographer is notified and can select another Film Lab.
- If required information is missing, the system asks the photographer to complete it before submitting.

**Result**

A confirmed film processing booking is recorded, and both the photographer and Film Lab can track the order.

### Business Core Flow 3

### Business Core Flow 4

### Business Core Flow 5

### Business Core Flow 6

## 3.2.c.2 AI-powered Personalized Assistance

## 3.2.c.3 Main Functional Modules
