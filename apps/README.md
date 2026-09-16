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
npm ci
npm test
npm run build
npm run dev
```

Open `http://127.0.0.1:4173`. Use the `Film Lab` and `Admin` segmented control
in the header to switch portal roles.

## Run the Flutter application

Install the Flutter SDK and verify it with `flutter doctor`, then run:

```powershell
cd apps\mobile
flutter create --platforms=android,web --project-name=film_photography_mobile .
flutter pub get
flutter analyze
flutter test
flutter run -d chrome
```

The repository contains the Flutter application sources; the `flutter create`
step generates the missing platform runners. Keep the existing `lib/`, `test/`
and `pubspec.yaml` when generating runners. Flutter has not been run on the
submission machine because the SDK is unavailable; record actual results when
running these commands. Booking is explicitly a local price preview.

The web portal persists demonstration state in browser localStorage. It does
not upload scan bytes or authenticate the selected portal role. See
`../docs/Verification.md` for tested behavior and integration limits.

The generated photograph in each application's asset directory is used only
as local demonstration media. No API keys or passwords are stored in either
application.

