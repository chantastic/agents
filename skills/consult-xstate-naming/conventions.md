# XState Naming Conventions

A style guide for naming states, events, actions, guards, actors, and machines in XState, grounded in linguistic principles and designed for consistency and readability.

---

## Linguistic Foundations

This guide uses grammatical concepts to inform naming decisions:

| Term | Definition | Example |
|------|------------|---------|
| **Copula** | A linking verb connecting subject to predicate | "The form **is** complete" |
| **Predicate adjective** | Adjective following a copula, describing the subject | "The form is **complete**" |
| **Gerund** | Verb form ending in *-ing*, functioning as a noun | "**Submitting** is in progress" |
| **Agent noun** | Noun denoting the doer of an action, often *-er/-or* | "**Authenticator**", "**validator**" |
| **Imperative** | Verb form expressing a command | "**Submit** the form" |
| **Past participle** | Verb form expressing completed action, often *-ed* | "The form was **submitted**" |

---

## States

States describe what the machine is doing or has done.

### Active states (async/in-progress)

Use **gerunds** (*-ing* form) to indicate ongoing activity:

```ts
states: {
  submitting: {},
  authenticating: {},
  retrieving: {},    // prefer over "fetching"
  connecting: {},
  preparing: {},     // prefer over "readying"
}
```

### Settled states (completed)

Use **past participles** (*-ed* form) to indicate completion:

```ts
states: {
  submitted: {},
  authenticated: {},
  retrieved: {},
  connected: {},
  prepared: {},
  failed: {},        // prefer over "errored"
}
```

### Idling state

Use `idling` for states awaiting input with no work in progress. Like an engine idling—running but not engaged—the machine is actively waiting.

```ts
states: {
  idling: {},        // awaiting input, engine running
  submitting: {},    // work in progress
  submitted: {},     // work complete
}
```

This departs from convention (most state machine literature uses `idle`), but maintains grammatical consistency: all active states are gerunds. The machine metaphor reinforces the model—a state machine is never truly "off," it's always *doing* something, even if that something is waiting.

For domain-specific alternatives, consider:
- `listening` — for event-driven machines (sockets, streams)
- `waiting` — when expecting a specific input
- `ready` — when emphasizing capability

### Wordsmithing for clean pairs

When an *-ing/-ed* pair is awkward, find a synonym:

| Avoid | Prefer |
|-------|--------|
| `fetching` / `fetched` | `retrieving` / `retrieved` |
| `erroring` / `errored` | `failing` / `failed` |
| `readying` / `readied` | `preparing` / `prepared` |
| `checking` / `checked` | `validating` / `validated` |

### Hierarchy and composition

Use nested states for composition. Let the parent provide context; avoid redundant naming:

```ts
// Preferred: hierarchy provides context
authenticated: {
  states: {
    idling: {},
    loading: {},      // "authenticated.loading" is clear
    failed: {},
  }
}

// Avoid: redundant context
authenticated: {
  states: {
    idling: {},
    loadingProfile: {},   // redundant—parent already says "authenticated"
    profileFailed: {},
  }
}
```

---

## Events

Events represent things that happen. Distinguish between commands (intent) and notifications (observations).

### Commands (user/application intent)

Use **imperative verbs**—these are requests for the machine to act:

```ts
type Commands =
  | { type: 'SUBMIT' }
  | { type: 'CONNECT' }
  | { type: 'RETRY' }
  | { type: 'CANCEL' }
  | { type: 'AUTHENTICATE' }
```

### Notifications (external observations)

Use **nouns**—these inform the machine of external reality:

```ts
type Notifications =
  | { type: 'CONNECTION_LOSS' }
  | { type: 'TOKEN_EXPIRY' }
  | { type: 'SESSION_TIMEOUT' }
  | { type: 'QUOTA_BREACH' }
  | { type: 'FILE_CHANGE' }
```

### Rationale

The distinction encodes **agency**:
- Commands express intent: "please do this"
- Notifications report facts: "this happened"

This reads naturally: "In the event of a `CONNECTION_LOSS`, `CONNECT`."

---

## Actions

Actions are synchronous operations triggered by transitions. They may update context, fire side effects, or both.

### Naming

Use **verbs**, grouped by domain:

```ts
const actions = {
  form: {
    clear: assign({ name: '', email: '', errors: null }),
    validate: assign({ errors: (ctx) => validateForm(ctx) }),
    logSubmission: () => analytics.track('form_submit'),
  },
  user: {
    notify: (ctx) => toast.show(ctx.message),
    setProfile: assign({ profile: (_, e) => e.profile }),
  },
  session: {
    refresh: assign({ token: (_, e) => e.token }),
    invalidate: assign({ token: null, user: null }),
  },
};
```

### Avoid

- **`assign*` prefix**: Encodes implementation detail. `assignUser` must be renamed if the action gains side effects.
- **Hungarian notation**: Don't encode return type or mechanism in the name.

### Usage

```ts
entry: ['form.clear'],
exit: ['session.invalidate'],
actions: ['user.notify', 'form.logSubmission'],
```

---

## Guards

Guards are predicates that control whether a transition fires. They answer the question: "Is [subject] [predicate adjective]?"

### Naming

Use **copula + predicate adjective** (`is*` / `are*`), grouped by domain:

```ts
const guards = {
  form: {
    isComplete: (ctx) => !!ctx.name && !!ctx.email,
    isPristine: (ctx) => !ctx.touched,
    isValid: (ctx) => ctx.errors.length === 0,
  },
  user: {
    isAuthorized: (ctx) => ctx.user?.role === 'admin',
    isAuthenticated: (ctx) => !!ctx.user,
  },
  retries: {
    areAvailable: (ctx) => ctx.attempts < ctx.maxAttempts,
    areExhausted: (ctx) => ctx.attempts >= ctx.maxAttempts,
  },
};
```

### Rationale

The `is*`/`are*` prefix is acceptable here because:

1. **Linguistically accurate**: Guards evaluate propositions. The copula (`is`/`are`) is the verb of that proposition.
2. **Scoped to one utility**: `is*` always means "guard"—no ambiguity.
3. **Reads as a sentence**: `form.isComplete` parses as "form is complete."
4. **Disambiguates from actions**: `form.complete` could be "complete the form" (action). `form.isComplete` cannot.

This is distinct from general boolean naming (`isLoading`, `isValid` as variables), which encodes *type* rather than *grammar*.

### Polarity

Define guards in a single polarity (typically positive). Negate at the call site:

```ts
// Define only the positive case
const guards = {
  user: {
    isAuthorized: (ctx) => ctx.user?.permissions.includes('write'),
  },
};

// Negate at call site
on: {
  DELETE: [
    { target: 'unauthorized', guard: { type: 'not', guard: 'user.isAuthorized' } },
    { target: 'deleting', guard: 'user.isAuthorized' },
  ]
}
```

Helper for readability:

```ts
const not = (guard: string) => ({ type: 'not', guard });

on: {
  DELETE: [
    { target: 'unauthorized', guard: not('user.isAuthorized') },
    { target: 'deleting', guard: 'user.isAuthorized' },
  ]
}
```

---

## Actors (Invoked Services)

When a state invokes a promise, callback, or child machine, the actor needs an identifier.

### Naming

Use **nouns** describing what the actor *is*:

```ts
states: {
  loading: {
    invoke: {
      id: 'profileLoader',      // noun: "the profile loader"
      src: 'loadProfile',
      onDone: 'loaded',
      onError: 'failed',
    }
  },
  connecting: {
    invoke: {
      id: 'connectionManager',  // noun: "the connection manager"
      src: 'establishConnection',
      onDone: 'connected',
      onError: 'failed',
    }
  }
}
```

### Avoid

- **Verbs**: `loadProfile` as an ID conflicts with action naming.
- **Gerunds**: `loadingProfile` is ambiguous with state names.

---

## Machines

Machine names are used for exports, debugging, and devtools.

### Naming

Use **agent nouns** (*-er/-or* form) describing what the machine does:

```ts
// The machine that authenticates
export const authenticator = createMachine({ ... });

// The machine that validates forms
export const formValidator = createMachine({ ... });

// The machine that manages connections
export const connectionManager = createMachine({ ... });
```

### Rationale

Agent nouns reserve a distinct grammatical form for machines, avoiding collision with:
- States (gerunds/participles)
- Events (imperatives/nouns)
- Actions (verbs)
- Actors (plain nouns)

---

## Context Properties

Context holds the machine's data.

### Naming

Use **nouns**. Compose via nesting rather than prefixing:

```ts
// Preferred: composed nouns
context: {
  user: {
    profile: { name: '', email: '' },
    preferences: { theme: 'light' },
  },
  form: {
    values: { name: '', email: '' },
    errors: [],
    touched: false,
  },
  connection: {
    status: 'disconnected',
    attempts: 0,
  },
}

// Avoid: prefixed flat structure
context: {
  userName: '',
  userEmail: '',
  formName: '',
  formEmail: '',
  formErrors: [],
}
```

### Rationale

Verbs in context names often indicate the data belongs in a child machine's state rather than in context. If you're tempted to write `pendingRequest` or `selectedUser`, consider whether that's actually a state (`selecting`, `requesting`) in a composed machine.

---

## Summary Table

| Category | Form | Example |
|----------|------|---------|
| **States (active)** | Gerund (*-ing*) | `submitting`, `authenticating` |
| **States (settled)** | Past participle (*-ed*) | `submitted`, `authenticated`, `failed` |
| **States (waiting)** | Gerund (*-ing*) | `idling`, `listening`, `waiting` |
| **Events (commands)** | Imperative verb | `SUBMIT`, `CONNECT`, `RETRY` |
| **Events (notifications)** | Noun | `CONNECTION_LOSS`, `TOKEN_EXPIRY` |
| **Actions** | Verb, grouped | `form.clear`, `user.notify` |
| **Guards** | `is*`/`are*`, grouped | `form.isComplete`, `retries.areAvailable` |
| **Actors** | Noun | `profileLoader`, `connectionManager` |
| **Machines** | Agent noun (*-er/-or*) | `authenticator`, `formValidator` |
| **Context** | Noun, composed | `user.profile`, `form.errors` |

---

## Edge Cases

### Guards that don't fit `is*`

Some predicates don't naturally take `is`:

| Awkward | Better |
|---------|--------|
| `retries.isRemaining` | `retries.areAvailable` |
| `connection.isExisting` | `connection.isEstablished` |
| `items.isEmpty` | `items.areExhausted` or `items.isPopulated` (inverted) |

Wordsmith to fit the pattern. The constraint encourages precision.

### Events that blur command/notification

Some events could be either:

```ts
// Is DISCONNECT a command or observation?
'DISCONNECT'      // command: "please disconnect"
'DISCONNECTION'   // noun: "a disconnection occurred"
```

Choose based on the source. If the user/app initiates it, use imperative. If it's observed externally, use noun form.

### Actions with mixed concerns

If an action both updates context and fires side effects, name it for the *intent*, not the mechanism:

```ts
const actions = {
  session: {
    // Updates context AND logs—name describes intent
    terminate: [
      assign({ user: null, token: null }),
      () => analytics.track('session_end'),
    ],
  },
};
```
