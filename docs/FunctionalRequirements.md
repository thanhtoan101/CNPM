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

### Business Core Flow 3 - Film Processing Lifecycle Management

**Objective**

Allow Film Lab operators to manage every stage of film processing while photographers monitor order progress in real time.

**Actors**

- Film Lab Operator
- Photographer
- System

**Main Flow**

1. The Film Lab receives the film rolls and verifies the order code, requested services, and physical condition of the rolls.
2. The operator records receipt of the film rolls, and the system updates the order status to Received.
3. The Film Lab schedules the order for processing.
4. The operator performs chemical development and records completion of the stage.
5. The operator completes washing and drying and updates the corresponding processing stages.
6. The operator scans the developed film according to the requested scan quality.
7. The operator prepares the digital images, including orientation and basic output adjustments.
8. The Film Lab performs final quality verification for the processed film and digital scans.
9. The system records each stage with its status, timestamp, notes, and estimated completion time.
10. Each update is synchronized with the customer application, and the photographer receives relevant notifications.
11. The photographer monitors the complete processing lifecycle in real time.
12. After quality verification, the Film Lab marks processing as completed and forwards the digital scans to the delivery and archive flow.

**Alternative Flow**

- If the received film rolls are damaged, missing, or do not match the order, processing is paused and the photographer is notified.
- If a quality check fails, the Film Lab repeats the affected scanning or processing step when possible and updates the order status.
- If processing is delayed, the system records a revised estimated completion time and notifies the photographer.
- If synchronization is temporarily unavailable, updates are retained and synchronized when the connection is restored.

**Result**

The complete film processing lifecycle is recorded and visible to the photographer, with the order ready for digital delivery and archive management.

### Business Core Flow 4 - Digital Delivery and Film Archive Management

**Objective**

Allow Film Labs to securely deliver digital scan files and allow photographers to view, download, organize, and permanently archive their scanned photographs.

**Actors**

- Photographer
- Film Lab Operator
- System
- Cloud Storage Service

**Main Flow**

1. The Film Lab completes final quality verification and selects the corresponding service order.
2. The Film Lab operator uploads the digital scan files to secure cloud storage.
3. The system validates the uploaded files and associates them with the correct order and photographer.
4. The operator verifies available metadata, including film stock, camera model, lens, shooting date, processing method, and scanning specifications.
5. The system stores the scan files and metadata in the photographer's personal Digital Film Archive.
6. The system sends a notification that the digital scans are available.
7. The photographer opens the completed order or Digital Film Archive.
8. The photographer previews the scanned photographs and reviews their metadata.
9. The photographer downloads selected photographs or the complete set of full-resolution scan files.
10. The photographer organizes photographs using albums, tags, and favorites.
11. The system preserves the files and metadata for future access within the personal archive.

**Alternative Flow**

- If an upload fails, the system keeps the delivery pending and asks the Film Lab operator to retry.
- If a file is corrupted or unsupported, the system rejects it and asks the operator to upload a valid replacement.
- If metadata is incomplete, the system marks the missing fields and allows the Film Lab or photographer to add them later.
- If a user is not authorized to access an archive item, the system denies the request and protects the stored files.

**Result**

The photographer receives secure access to the completed digital scans, and the photographs and associated metadata are preserved in the personal Digital Film Archive.

### Business Core Flow 5 - Marketplace and Equipment Exchange

**Objective**

Allow community members to buy, sell, or exchange analog photography equipment through a transparent and traceable marketplace.

**Actors**

- Buyer
- Seller
- System
- System Administrator

**Main Flow**

1. The seller opens the Marketplace and creates a new product listing.
2. The seller provides the item category, title, description, condition, price or exchange preference, photographs, and delivery information.
3. The system validates the listing information and publishes the listing.
4. The buyer searches and filters listings by item type, brand, price, condition, location, and seller rating.
5. The system displays matching analog cameras, film rolls, lenses, and photography accessories.
6. The buyer opens a listing and reviews the item details, seller profile, ratings, and transaction history.
7. The buyer contacts the seller through the platform to ask questions, negotiate, or confirm exchange conditions.
8. The buyer submits a purchase or exchange request.
9. The seller reviews and accepts the request.
10. The system records the transaction and updates its status throughout payment, delivery, receipt, or exchange completion.
11. After completion, the buyer rates the seller and the system updates the seller's reputation.

**Alternative Flow**

- If listing information is incomplete or invalid, the system asks the seller to correct it before publication.
- If an item is no longer available, the system closes the listing and prevents new requests.
- If the seller rejects or does not respond to a request, the buyer is notified and may select another listing.
- If a transaction is cancelled, disputed, or reported as fraudulent, the system records the issue and forwards it to the System Administrator for review.
- If communication violates marketplace rules, the system restricts the content and allows users to report it.

**Result**

The purchase, sale, or exchange is transparently recorded, and marketplace listings, transaction status, and seller ratings are updated for future users.

### Business Core Flow 6

## 3.2.c.2 AI-powered Personalized Assistance

## 3.2.c.3 Main Functional Modules
