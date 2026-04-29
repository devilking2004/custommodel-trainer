# CustomModel Trainer Frontend

A mock-data Next.js frontend for **CustomModel Trainer**, a no-code AI model training platform.

## Stack

- Next.js App Router
- TypeScript
- Tailwind CSS
- Shadcn-style local UI components
- Framer Motion
- Lucide icons

## Run locally

```bash
pnpm install
pnpm dev
```

Or with npm:

```bash
npm install
npm run dev
```

Open:

```txt
http://localhost:3000
```

## Important routes

```txt
/                                      Landing page
/login                                 Login
/signup                                Signup
/dashboard                             Dashboard
/models/new                            Create model
/models/demo-cx-bot/setup              Model setup
/models/demo-cx-bot/data               Data upload
/models/demo-cx-bot/readiness          Data readiness score
/models/demo-cx-bot/training           Training progress
/models/demo-cx-bot/playground         Testing playground
/models/demo-cx-bot/api                API usage
/models/demo-cx-bot/feedback           Feedback review
/models/demo-cx-bot/versions           Model versions
/settings                              Settings
```

## Notes

This version uses mock data only. Later, replace `lib/mock-data.ts` with API calls to your FastAPI backend.
