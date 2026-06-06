# Storefront

Customer-facing web UI for browsing 5G product offerings and placing orders.

**Port:** 3000 (dev) / configurable (production)
**Framework:** Next.js 14.2.30 (App Router)
**Styling:** Tailwind CSS 3
**Language:** TypeScript 5
**Source root:** `src/storefront/`

---

## Purpose

The storefront is the customer-facing entry point into the Tech-Co lab. It fetches
product offerings from the TMF620 Catalog API, renders them as browsable cards, lets
a customer select an offering and place an order via the TMF622 Order Engine, and then
polls for the live order status until a terminal state is reached.

It does not contain any business logic. All data comes from the two backend APIs.

---

## Stack

| Dependency      | Version  | Role                                    |
|-----------------|----------|-----------------------------------------|
| next            | 14.2.30  | App Router SSR framework                |
| react           | 18.3.1   | UI rendering                            |
| react-dom       | 18.3.1   | DOM bindings                            |
| tailwindcss     | ^3       | Utility-first CSS                       |
| typescript      | ^5       | Type checking                           |

Source: `src/storefront/package.json`.

---

## Routes

All routes use the Next.js App Router (`src/storefront/src/app/`).

| Route              | File                                     | Type           | Description                                      |
|--------------------|------------------------------------------|----------------|--------------------------------------------------|
| `/`                | `src/app/page.tsx`                       | Server Component | Fetches all offerings from TMF620, renders card grid |
| `/offering/[id]`   | `src/app/offering/[id]/page.tsx`         | Server Component | Fetches single offering detail, specs table, pricing table, terms, Buy Now button |
| `/order/[id]`      | `src/app/order/[id]/page.tsx`            | Client Component | Polls TMF622 every 3 seconds for order state, renders progress tracker |

---

## API Client (`src/lib/api.ts`)

All TMF620 and TMF622 HTTP calls go through `src/storefront/src/lib/api.ts`.

```
CATALOG_API = process.env.NEXT_PUBLIC_CATALOG_API ?? "http://localhost:8081"
ORDER_API   = process.env.NEXT_PUBLIC_ORDER_API   ?? "http://localhost:8080"
```

Exported functions:

| Function           | Method | URL                                                                          |
|--------------------|--------|------------------------------------------------------------------------------|
| `fetchOfferings()` | GET    | `{CATALOG_API}/tmf-api/productCatalogManagement/v4/productOffering`          |
| `fetchOffering(id)`| GET    | `{CATALOG_API}/tmf-api/productCatalogManagement/v4/productOffering/{id}`     |
| `placeOrder(input)`| POST   | `{ORDER_API}/tmf-api/productOrderingManagement/v4/productOrder`              |
| `fetchOrder(id)`   | GET    | `{ORDER_API}/tmf-api/productOrderingManagement/v4/productOrder/{id}`         |

`placeOrder()` constructs a minimal TMF622 ProductOrder body with one `productOrderItem`
containing `action: "add"` and the offering reference. The order engine's decomposer
handles the rest.

All fetch calls on the server side pass `{ cache: "no-store" }` to prevent Next.js
from caching dynamic data. The order polling on `/order/[id]` uses `useEffect` +
`setInterval` (3000ms) and stops when `isTerminal(state)` returns true (states:
`completed`, `failed`, `cancelled`).

---

## Page Behavior

### Home page (`/`)

- Server Component. Renders on each request (no cache).
- Fetches all offerings and renders a responsive card grid (1 / 2 / 3 columns via
  Tailwind `sm:grid-cols-2 lg:grid-cols-3`).
- Each card shows: category badge, offering name (underscores replaced with spaces),
  truncated description, formatted price (recurring + one-time activation), and a
  "View details" link.
- If the catalog API is unreachable, renders an error panel with the configured API URL.

### Offering detail page (`/offering/[id]`)

- Server Component. Fetches a single offering by ID from TMF620.
- Renders sections: category badge, name, ID, description, technical specifications
  table (from `productSpecification.productSpecCharacteristic`), pricing table
  (from `productOfferingPrice`), terms list, and a Buy Now button.
- The Buy Now button (`buy-now-button.tsx`) is a Client Component because it fires a
  POST to the order engine and then uses `router.push()` to navigate to `/order/{id}`.

### Order status page (`/order/[id]`)

- Client Component (`"use client"` directive at line 10).
- On mount: fetches order immediately via `fetchOrder`.
- `setInterval(poll, 3000)` continues until the order reaches a terminal state.
- Renders a 3-step progress tracker (acknowledged / In Progress / Completed), a state
  badge with color coding, an order items table, and timestamps.
- State colors: `acknowledged` yellow, `inProgress` blue, `completed` green, `failed`
  red, `partial` purple, `cancelled` / `pending` / `held` gray.

---

## Build Verification

Per stage 7, `npm run build` succeeds with 4 static pages generated. To verify:

```bash
cd src/storefront
npm install
npm run build
```

---

## Environment Variables

| Variable                  | Default                  | Description                                 |
|---------------------------|--------------------------|---------------------------------------------|
| `NEXT_PUBLIC_CATALOG_API` | `http://localhost:8081`  | TMF620 Catalog API base URL                 |
| `NEXT_PUBLIC_ORDER_API`   | `http://localhost:8080`  | TMF622 Order Engine base URL                |

These are read at build time and baked into the client bundle (prefix `NEXT_PUBLIC_`).
Override by creating `src/storefront/.env.local`. A `.env.example` file exists at
`src/storefront/.env.example`.

---

## Running Locally

```bash
cd src/storefront
npm install
npm run dev        # development server on port 3000 with hot reload
```

For production:

```bash
npm run build
npm run start      # production server on port 3000
```

---

## Known Limitations

- No authentication or session management. The Buy Now button submits orders as an
  anonymous caller.
- No styling polish beyond Tailwind utility defaults. Responsive layout uses grid
  breakpoints only; no custom design system.
- No responsive design beyond Tailwind defaults (`sm:` and `lg:` breakpoints on the
  offering grid).
- No pagination on the offerings list. All offerings from the catalog API are rendered
  in a single page.
- Error boundaries are per-page inline fallbacks only; no global error page.

---

## Relationship to the Mission-Control Dashboard

`Tech-Co/components/legacy-standalone-5g-emulator/demo_front-end/` is a separate mission-control
dashboard used during lab demos to visualize NF health, order engine state, and AI
observer output. It is not the customer storefront. The two apps are entirely
independent; the storefront is focused on the buyer journey (browse, order, track)
while the dashboard is focused on operator visibility.
