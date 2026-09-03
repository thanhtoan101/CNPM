# Mobile and Web Design

**Responsible member:** Nguyen Dao Quoc Khanh

This document describes the initial structure for the mobile and web interfaces
of the AI-powered Film Photography Platform. The mobile application is intended
for photographers, while the web portals support Film Lab operators and system
administrators.

## 1. UI/UX Guidelines

- Keep navigation simple and consistent across mobile and web screens.
- Use clear order statuses for pickup, processing, scanning, and delivery.
- Show important actions such as booking, tracking, uploading, and downloading
  in visible positions.
- Support responsive layouts and readable content on common screen sizes.
- Display confirmation, loading, empty, and error states for user actions.

## 2. Photographer Mobile Application

The Flutter mobile application will include:

- Registration, login, and profile management.
- Film Lab search, filtering, comparison, and recommendation.
- Service booking and pickup requests.
- Real-time order tracking.
- Scan notification, preview, and download.
- Digital Film Archive management.
- Marketplace and community access.
- AI Photography Assistant interaction.

## 3. Film Lab Web Portal

The Film Lab portal will include:

- Lab profile, supported film formats, services, and pricing management.
- Incoming order confirmation and processing schedule.
- Processing workflow and order status updates.
- Digital scan upload and customer delivery.
- Customer, revenue, and activity reports.

## 4. Administration Web Portal

The administration portal will include:

- User, role, and Film Lab approval management.
- Service category and transaction fee management.
- Payment and platform activity monitoring.
- Review, community content, complaint, and dispute moderation.
- Basic platform reports and audit information.

## 5. Marketplace UI

- Create, edit, and remove equipment listings.
- Search and filter cameras, lenses, film rolls, and accessories.
- View seller information, ratings, and item details.
- Support buyer-seller communication and transaction status tracking.
- Report suspicious listings or transaction problems.

## 6. Digital Film Archive UI

- Display scans by order, album, film stock, and shooting date.
- Preview, download, organize, tag, and favorite photographs.
- Show camera, lens, processing, and scanning metadata.
- Provide clear storage, privacy, and access states.

## 7. Main UI Flows

### Photographer Booking Flow

`Login -> Search Film Lab -> Compare Services -> Select Service -> Enter Film Details -> Choose Pickup -> Confirm Order -> Track Status`

### Film Lab Processing Flow

`Login -> Review Incoming Order -> Confirm Order -> Update Processing Stages -> Upload Scans -> Complete Order`

### Digital Delivery Flow

`Processing Completed -> Customer Notification -> Preview Scans -> Download Files -> Save to Digital Film Archive`

## 8. Frontend Component Architecture

- **Presentation layer:** screens, pages, reusable components, and responsive
  layouts.
- **State layer:** authentication, profile, order, marketplace, archive, and
  notification state.
- **Service layer:** REST API clients, upload/download services, and real-time
  updates.
- **Shared layer:** theme, form validation, error handling, localization, and
  reusable models.

## 9. Frontend Sequence Diagrams

Sequence diagrams will be prepared for these main interactions:

1. Photographer creates a service order.
2. Film Lab updates the film processing status.
3. Film Lab uploads scans and the photographer downloads them.
4. Administrator reviews a reported marketplace listing.

## 10. Planned Deliverables

- Mobile and web screen list.
- UI flow diagram.
- Frontend component architecture diagram.
- Frontend sequence diagrams.
- Initial wireframes for the Photographer App, Film Lab Portal, Admin Portal,
  Marketplace, and Digital Film Archive.
- Presentation notes for the Mobile and Web section.
