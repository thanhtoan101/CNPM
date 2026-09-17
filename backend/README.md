# Business API

Requires Node.js 22.18+ (24 LTS recommended for all repository tests), npm and PostgreSQL. This is an API baseline, independent of the local-data React/Flutter prototypes.

## Start locally

1. Run `npm ci` in this directory. Do not rely on the historical checked-in `node_modules` snapshot: it contains incomplete package distributions.
2. Create a NEW development database named `film_platform` and apply `psql -d film_platform -f schema.sql`. The schema is a bootstrap, not an automatic migration for a teammate's existing database.
3. Copy `.env.example` to `.env`. Set `DATABASE_URL` and a unique `JWT_SECRET` of at least 32 characters. Generate a secret with `node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"`.
4. Set `DATABASE_SSL=false` only for local PostgreSQL. Hosted databases use verified TLS; configure a trusted CA if required.
5. Provision test users with bcrypt password hashes and one of `photographer`, `lab_owner`, `expert`, `moderator`, `admin`. No public registration or default admin password is included. Never store clear-text passwords.
6. Run `npm test`, then `npm start`. The development server listens at `http://127.0.0.1:3000`.

## Current routes

| Route | Access / behavior |
| --- | --- |
| `POST /auth/login` | Email/password; returns a one-hour HS256 token. Unknown account and incorrect password return the same message. |
| `GET /labs`, `GET /courses` | Bearer token required. |
| `GET /orders` | Photographers see their own orders; admin can list all. A lab-staff order query is still an integration task. |
| `POST /labs` | `lab_owner` or `admin`; validates name/address; clients cannot set ratings. |
| `POST /courses` | `expert` or `admin`; validates required details, status and date range. |
| `POST /orders` | `photographer` or `admin`; integer lab/service IDs, quantity 1–100; price comes from the active service at that lab. Client `total_price` is ignored. |
| `GET /users`, `/users/full`, `/tables`, `/schema/:table` | Administrator only. User results never include password hashes. |

Use `Authorization: Bearer <token>`. Tests cover signing/verification consistency, token failures, role enforcement, ownership and login response shape using a database stub. They do not prove connection to a live PostgreSQL instance.

## Integration boundaries

The existing GET/POST routes are not a complete CRUD system: update/delete, refresh/revoke tokens, rate limiting, lab employee access, server-side order transitions, audit persistence, uploads and frontend API wiring remain future work. No cloud credentials, database contents or deployment are included in the submission. See `../docs/AcceptanceTraceability.md` and `../docs/Verification.md` for the checked scope.
