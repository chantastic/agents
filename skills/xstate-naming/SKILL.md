---
name: xstate-naming
description: XState naming conventions and scaffolding. Use when naming states, events, actions, guards, or machines in XState, or when scaffolding new state machines.
---

# XState Naming Skill

You are helping the user name elements in XState state machines or scaffold new machines following a consistent naming convention grounded in linguistic principles.

## Reference

The full conventions are documented in `conventions.md` in this directory. Read it before responding.

## Capabilities

### 1. Naming Assistant

When the user describes something they need to name, return the appropriate name following conventions.

**Input examples:**
- "I need a state for when the form is being validated"
- "What should I call the event when the user clicks submit?"
- "I need a guard that checks if the user has permission"

**Response format:**
```
**Name:** `validating`
**Category:** State (active)
**Rationale:** Active states use gerunds (-ing). "Validating" describes ongoing activity.
```

If the user's description is ambiguous, ask clarifying questions:
- Is this user-initiated (command) or externally observed (notification)?
- Is this an ongoing activity or a completed state?
- What domain does this belong to for grouping?

### 2. Machine Scaffolder

When the user describes a machine or flow, generate a skeleton with properly named states, events, actions, and guards.

**Input examples:**
- "Auth flow with login, logout, and session refresh"
- "File upload with progress tracking and retry"
- "WebSocket connection manager"

**Response format:**

```ts
import { createMachine, assign } from 'xstate';

export const authenticator = createMachine({
  id: 'authenticator',
  initial: 'idling',
  context: {
    user: null,
    error: null,
  },
  states: {
    idling: {
      on: {
        AUTHENTICATE: 'authenticating',
      },
    },
    authenticating: {
      invoke: {
        id: 'authService',
        src: 'authenticate',
        onDone: {
          target: 'authenticated',
          actions: ['user.set'],
        },
        onError: {
          target: 'failed',
          actions: ['error.set'],
        },
      },
    },
    authenticated: {
      on: {
        LOGOUT: 'loggingOut',
        SESSION_EXPIRY: 'idling',
      },
    },
    loggingOut: {
      invoke: {
        id: 'logoutService',
        src: 'logout',
        onDone: {
          target: 'idling',
          actions: ['user.clear'],
        },
      },
    },
    failed: {
      on: {
        RETRY: 'authenticating',
        CANCEL: 'idling',
      },
    },
  },
});

// Actions
const actions = {
  user: {
    set: assign({ user: (_, e) => e.output }),
    clear: assign({ user: null }),
  },
  error: {
    set: assign({ error: (_, e) => e.error }),
    clear: assign({ error: null }),
  },
};

// Guards
const guards = {
  user: {
    isAuthenticated: (ctx) => !!ctx.user,
  },
};
```

After generating, briefly explain naming choices if non-obvious.

## Naming Quick Reference

| Category | Pattern | Examples |
|----------|---------|----------|
| States (active) | Gerund (-ing) | `submitting`, `authenticating`, `idling` |
| States (settled) | Past participle (-ed) | `submitted`, `authenticated`, `failed` |
| Events (commands) | Imperative verb | `SUBMIT`, `CONNECT`, `RETRY` |
| Events (notifications) | Noun | `CONNECTION_LOSS`, `TOKEN_EXPIRY` |
| Actions | Verb, grouped | `form.clear`, `user.notify` |
| Guards | `is*/are*`, grouped | `form.isComplete`, `retries.areAvailable` |
| Actors | Noun | `profileLoader`, `connectionManager` |
| Machines | Agent noun (-er/-or) | `authenticator`, `formValidator` |
| Context | Noun, composed | `user.profile`, `form.errors` |

## Key Principles

1. **Gerunds for active states** — The machine is *doing* something: `submitting`, `idling`
2. **Past participles for settled states** — The machine *did* something: `submitted`, `failed`
3. **Imperatives for commands** — User intent: `SUBMIT`, `CONNECT`
4. **Nouns for notifications** — External observations: `CONNECTION_LOSS`
5. **Copula for guards** — `is*/are*` reflects the predicate adjective grammar: `form.isComplete`
6. **Single polarity** — Define positive guards, negate at call site
7. **Grouped namespacing** — `form.clear`, `user.isAuthorized`
8. **Wordsmith for clean pairs** — `retrieving/retrieved` over `fetching/fetched`

## Linguistic Terms (for rationale)

- **Copula**: Linking verb ("is", "are") connecting subject to predicate
- **Predicate adjective**: Adjective following copula — "the form is *complete*"
- **Gerund**: Verb form ending in -ing, used as noun — "*Submitting* is in progress"
- **Agent noun**: Doer of action, often -er/-or — "authenticator"
- **Imperative**: Command form — "Submit the form"
- **Past participle**: Completed action, often -ed — "The form was submitted"
