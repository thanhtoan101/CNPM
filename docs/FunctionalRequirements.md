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

### Business Core Flow 6 - Knowledge Sharing and Community Engagement

**Objective**

Allow photography experts and community members to share knowledge, join discussions, and participate in activities that strengthen the analog photography community.

**Actors**

- Photographer
- Photography Expert
- Community Member
- System
- System Administrator

**Main Flow**

1. A photography expert or community member opens the Knowledge Sharing section.
2. The contributor creates content such as tutorials, technical articles, equipment reviews, laboratory recommendations, or personal photography experiences.
3. The system validates the content and publishes it to the community knowledge base.
4. Photographers and community members browse, search, and read published content.
5. Users join discussions by commenting, asking questions, or sharing related experiences.
6. A community organizer or expert creates a workshop or photowalk event with schedule, location, and participation details.
7. Interested users register for the workshop or photowalk through the platform.
8. The system records registrations and sends notifications or reminders about the event.
9. Users attend the event and continue sharing feedback, notes, or follow-up discussion after it ends.
10. The system preserves valuable discussions, event information, and educational content in the shared knowledge base for future users.

**Alternative Flow**

- If submitted content violates community guidelines or is incomplete, the system rejects or flags it for moderation before publication.
- If a workshop or photowalk reaches maximum capacity, the system closes registration or places later users on a waiting list.
- If an event is changed or cancelled, the system updates the event status and notifies registered users.
- If a discussion contains inappropriate or misleading information, users can report it and the System Administrator reviews the report.
- If search results are limited, the system suggests related articles, topics, or contributors.

**Result**

Community knowledge continuously grows through published content, discussions, and events, helping photographers learn, connect, and engage more actively on the platform.

## 3.2.c.2 AI-powered Personalized Assistance

**Objective**

Provide photographers with personalized support when selecting Film Labs, evaluating scan quality, asking technical questions, and finding suitable learning resources.

**Actors**

- Photographer
- AI Assistant
- System
- Film Lab

**Preconditions**

- The photographer has signed in to the platform.
- The system has access to available Film Lab information and community knowledge resources.
- The AI service is available.

**Main Flow**

1. The photographer opens the AI Assistant and selects a support topic or enters a question.
2. The system collects relevant context, such as the photographer's preferences, previous service orders, saved Film Labs, and community feedback.
3. The AI analyzes the request and available context.
4. For Film Lab discovery, the AI recommends suitable labs and explains the main reasons for each recommendation.
5. For scan quality support, the photographer submits a scan and the AI identifies possible issues such as dust, color cast, low contrast, or incorrect exposure.
6. For technical questions, the AI uses the platform knowledge base to provide a clear answer and suggest related articles.
7. For learning support, the AI recommends tutorials, workshops, or community discussions that match the photographer's interests and experience level.
8. The photographer reviews the response and may ask a follow-up question or choose a recommended action.
9. The system records the photographer's feedback to improve later recommendations.

**Alternative Flow**

- If the photographer has little or no activity history, the AI asks for basic preferences and provides general recommendations.
- If the request is unclear, the AI asks the photographer to provide more information before giving an answer.
- If the AI has low confidence, the system states the limitation and suggests verified community resources or direct support from a Film Lab.
- If the AI service is unavailable, the system keeps standard search, filtering, and knowledge-base features available.
- If an uploaded scan is invalid or unsupported, the system asks the photographer to upload another file.

**Result**

The photographer receives relevant assistance and can continue with a suitable Film Lab, improve a scan, resolve a technical question, or select an appropriate learning resource.

## 3.2.c.3 Main Functional Modules

The platform is divided into the following main functional modules. Each module supports one or more business core flows described above.

### Module 1 - Account and Profile Management

- Allow users to register, sign in, sign out, and recover their accounts.
- Manage personal information, photography interests, service preferences, and delivery addresses.
- Support different roles, including Photographer, Film Lab Operator, Photography Expert, and System Administrator.

### Module 2 - Film Lab Discovery and Recommendation

- Maintain Film Lab profiles, services, prices, supported film formats, turnaround times, and locations.
- Allow photographers to search, filter, compare, and view Film Labs.
- Rank suitable Film Labs using user preferences, previous activities, ratings, and AI recommendations.
- Allow users to submit ratings and reviews after using a Film Lab service.

### Module 3 - Service Booking and Film Collection

- Allow photographers to select processing, scanning, printing, and other service options.
- Calculate estimated service and collection costs before order confirmation.
- Support direct film delivery and pickup requests through Delivery Partners.
- Create service orders and provide order codes, confirmations, and film handling instructions.

### Module 4 - Film Processing Lifecycle Management

- Allow Film Lab operators to receive, verify, and schedule film orders.
- Record development, washing, drying, scanning, image preparation, and quality-check stages.
- Store timestamps, notes, estimated completion times, and processing problems.
- Synchronize order status so photographers can track progress in real time.

### Module 5 - Digital Delivery and Film Archive

- Allow Film Labs to upload completed digital scans to secure cloud storage.
- Validate files and associate them with the correct order and photographer.
- Allow photographers to preview, download, organize, tag, and favorite photographs.
- Store film, camera, lens, processing, and scanning metadata with each archive item.
- Protect archive files through authentication and access control.

### Module 6 - Marketplace and Equipment Exchange

- Allow users to create and manage listings for analog cameras, lenses, film rolls, and accessories.
- Support listing search, filtering, buyer-seller communication, and purchase or exchange requests.
- Track transaction status from agreement to delivery or exchange completion.
- Support seller ratings, cancellation, dispute reporting, and administrator review.

### Module 7 - Knowledge Sharing and Community

- Allow experts and community members to publish tutorials, articles, reviews, and experiences.
- Support searching, reading, commenting, asking questions, and community discussions.
- Allow organizers to create workshops and photowalk events and manage registrations.
- Support content reporting and moderation to maintain community quality.

### Module 8 - AI-powered Personalized Assistance

- Recommend Film Labs based on user preferences, history, and community feedback.
- Identify common quality problems in uploaded film scans.
- Answer technical questions using the platform knowledge base.
- Recommend suitable tutorials, workshops, articles, and discussions.
- Collect user feedback to improve later recommendations.

### Module 9 - Notification and Administration

- Notify users about order confirmation, pickup, processing progress, digital delivery, transactions, and events.
- Allow administrators to manage users, Film Labs, service information, reported content, and disputes.
- Record important system activities for monitoring and review.
- Provide basic management reports about orders, users, marketplace activity, and community content.
