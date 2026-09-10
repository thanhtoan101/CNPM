# Khanh Mobile and Web Prototypes

This directory contains the implementation prototype for Nguyen Dao Quoc
Khanh's assigned Mobile and Web contribution.

## Included applications

- `mobile/`: Flutter Photographer App with Film Lab discovery, booking preview,
  order tracking, Digital Film Archive, Marketplace, AI Assistant demo, and
  profile preferences.
- `web/`: React and TypeScript portal with Film Lab operations, order tables,
  processing board, scan delivery, services, customer reports, Film Lab
  approval, moderation, Marketplace, and Digital Film Archive views.

The applications currently use local demonstration data because the shared
backend API and authentication service are assigned to another team member.
The interface state and service boundaries can be connected to the backend
without changing the main screen structure.

## Run the Web portal

```powershell
cd apps\web
npm install
npm run dev
```

Open `http://127.0.0.1:4173`. Use the `Film Lab` and `Admin` segmented control
in the header to switch portal roles.

## Run the Flutter application

Install the Flutter SDK and verify it with `flutter doctor`, then run:

```powershell
cd apps\mobile
flutter pub get
flutter run
```

The generated photograph in each application's asset directory is used only
as local demonstration media. No API keys or passwords are stored in either
application.

