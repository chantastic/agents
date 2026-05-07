---
name: convex-fucd-naming
description: Apply the FUCD naming convention and Convex module categories for table access, views, commands, and workflows. Use this skill whenever writing or editing Convex backend code (anything under a `convex/` directory, any use of `query`, `mutation`, `internalQuery`, `internalMutation`, `action`, `internalAction`, `defineTable`), whenever adding CRUD/data operations to a Convex table, whenever reviewing or refactoring function names in a Convex project, or whenever the user mentions FUCD, "find/upsert/collect/destroy" naming, commands, workflows, views, or asks how to name a Convex function. Covers verb selection (find, upsert, collect, paginate, count, destroy), access-mechanism suffixes (Scan, Search), bulk forms (Many), public/internal split, return-value defaults, table files vs view/command/workflow files, and index management.
---

# FUCD: Convex Function Naming

A naming convention for Convex backend modules. Constrains raw table-CRUD vocabulary so files are predictable; gives views, commands, and workflows their own categories so richer application architecture remains legible.

## Scope

In:

- Raw table access in `query`, `mutation`, `internalQuery`, and `internalMutation`
- Composed reads in view modules
- Intent-oriented transactional mutations in command modules
- External side-effect orchestration in workflow modules using `action` or `internalAction`

FUCD verbs apply only to raw table access. Views, commands, and workflows have separate naming vocabularies.

## Architecture principle

Always choose strong architecture over ceremony avoidance.

Use explicit category boundaries when they make ownership, side effects, data flow, authorization, retries, or future SaaS/tenant behavior clearer. Extra modules are worthwhile when they prevent feature code from becoming a pile of one-off route handlers and helper calls.

## File layout

```
convex/
  users.ts                // FUCD verbs for the `users` table
  posts.ts                // FUCD verbs for the `posts` table
  follows.ts              // FUCD verbs for the `follows` table
  userProfileViews.ts     // composed/hydrated reads; freeform get* names
  feedViews.ts            // composed/hydrated reads; freeform get* names
  userCommands.ts         // intent-oriented transactional mutations
  billingCommands.ts      // DB-only business operations
  emailWorkflows.ts       // actions/internalActions and scheduled side effects
  billingWorkflows.ts     // external API orchestration and job status updates
  schema.ts
```

One file per table, named after the table. Category modules live beside table files with plural suffixes:

- `*Views.ts`
- `*Commands.ts`
- `*Workflows.ts`

If an existing project already uses singular `*View.ts`, follow the local pattern until migrating it deliberately. New modules should prefer plural category suffixes because each module can contain multiple functions.

## Core verbs

| Verb | Returns | Purpose |
|---|---|---|
| `find` | one doc or `null` | Lookup by id or unique field |
| `upsert` | the written doc | Insert if no id, update if id present |
| `collect` | doc array | All matching docs |
| `paginate` | `{ page, isDone, continueCursor }` | Paginated docs |
| `count` | number | Count of matching docs |
| `destroy` | the deleted doc | Remove a doc |

**`find` is for unique lookups only** — by `_id` or by a unique-indexed field. Multiple matches → wrong verb; use `collect`.

## Field suffix: `By*`

`*By<Field>` means "filtered by that field, using an index named `by_<field>`":

```
findByEmail(email)       // unique lookup via by_email index
collectByAuthorId(id)    // many docs via by_authorId index
paginateByOrgId(id)      // paginated via by_orgId index
countByStatus(status)    // count via by_status index
```

Convention: `collectBy<Field>` ⟺ index `by_<field>` exists in `schema.ts`. Same shape for `findBy*`, `paginateBy*`, `countBy*`. See [Indexes](#indexes).

## Mechanism suffixes: `Scan`, `Search`

These indicate *how* the read happens, not *what* it filters by. Append to the field-suffixed name.

### `*Scan` — full table scan + filter (no index)

Use only when indexing is impractical (tiny tables, ad-hoc admin, predicates too dynamic to index). Costs grow linearly with table size.

```
collectByEmailScan(email)        // full scan + filter; OK if rare/admin
collectByActiveScan()            // tiny enum-like field on tiny table
findByEmailScan(email)           // ⚠️ almost always wrong — add an index
```

### `*Search` — search index, ranked results

For full-text search via `withSearchIndex`. Returns relevance-ranked docs. **Collect/paginate only** — `find` doesn't apply because "first ranked result" is rarely what you want.

```
collectByTitleSearch(query)
paginateByTitleSearch(query)
collectByBodySearch(query)
```

## Bulk forms: `*Many`

Form: `<verb>Many[By<Field>]`. The `Many` sits between verb and field.

```
upsertMany(records)              // bulk write
destroyMany(ids)                 // bulk delete by ids
destroyManyByAuthorId(id)        // cascade delete (e.g. delete user's posts)
destroyManyByEmailScan(email)    // bulk + scan; ugly on purpose
```

`Many` only exists for `upsert` and `destroy`. For reads, `collect` and `paginate` are inherently many-valued.

## Public vs internal: `*Internal` suffix

Convex distinguishes public functions (callable from clients) and internal functions (callable only from other server functions). When both forms exist for the same verb, suffix the internal one:

```ts
export const find = query({ ... });
export const findInternal = internalQuery({ ... });

export const upsert = mutation({ ... });
export const upsertInternal = internalMutation({ ... });
```

If only the internal form exists, still use the suffix — the suffix marks the access boundary, not the relationship to a public sibling.

## Returns

**Default: write verbs return the full doc (or doc array for `Many`).** Read verbs return docs as expected.

```ts
// upsert returns the written doc
export const upsert = mutation({
  args: { id: v.optional(v.id("users")), email: v.string(), name: v.string() },
  handler: async (ctx, { id, ...fields }) => {
    if (id) {
      await ctx.db.patch(id, fields);
      return await ctx.db.get(id);
    }
    const newId = await ctx.db.insert("users", fields);
    return await ctx.db.get(newId);
  },
});

// destroy returns the deleted doc
export const destroy = mutation({
  args: { id: v.id("users") },
  handler: async (ctx, { id }) => {
    const doc = await ctx.db.get(id);
    if (!doc) return null;
    await ctx.db.delete(id);
    return doc;
  },
});
```

This costs one extra read per write vs. raw Convex primitives (which return id/void). Worth it for ergonomic consistency. **Opt out only when justified** (hot paths, large docs); call `db.insert`/`db.patch`/`db.delete` directly and document the deviation.

## Indexes

`findBy*`, `collectBy*`, `paginateBy*`, `countBy*`, and `destroyManyBy*` all imply an index `by_<field>` exists on the table.

**When generating one of these and the index is missing:**
1. Add it to `schema.ts`: `.index("by_<field>", ["<field>"])`
2. **Alert the user** that the index was added — surface it explicitly in the response.
3. If adding the index is unwise, refuse and recommend `*Scan` instead.

**When indexing is unwise:**
- Tiny tables (<~100 rows, e.g. settings/config) — index overhead exceeds scan cost.
- Very high-write, rarely-queried fields — index maintenance dominates.
- Predicates too dynamic for a fixed index (e.g. multi-field ad-hoc filters where each combination would need its own index). Reach for `*Scan` or rethink the query.
- Search use cases — use `withSearchIndex` and the `*Search` suffix instead.

When in doubt, prefer the index.

## Views

Composed reads (joins, hydration, derived shapes, materialized projections). Different vocabulary signals "this isn't raw table access."

**Conventions:**
- Filename: `<thing>Views.ts`, flat with table files.
- Freeform descriptive function names: `get`, `getProfile`, `getForOrg`, `getRecommendations`, `getTopByEngagement`. **Do not** use FUCD verbs in view files.
- One view file per logical view. Multiple variants of the same view share a file.

**Example:**

```ts
// convex/userProfileViews.ts
import { query } from "./_generated/server";
import { v } from "convex/values";

export const get = query({
  args: { userId: v.id("users") },
  handler: async (ctx, { userId }) => {
    const user = await ctx.db.get(userId);
    if (!user) return null;
    const posts = await ctx.db.query("posts")
      .withIndex("by_authorId", q => q.eq("authorId", userId))
      .collect();
    const followerCount = await ctx.db.query("follows")
      .withIndex("by_followeeId", q => q.eq("followeeId", userId))
      .collect()
      .then(r => r.length);
    return { ...user, posts, followerCount };
  },
});

export const getForOrg = query({ /* all profiles for an org */ });
```

Why no FUCD in views: views are inherently looser-shaped than tables. Forcing `find`/`collect` creates awkward fits ("is `collectByOrgId` on a view describing an indexed field, or a join axis?"). The `Views` suffix + `get*` vocabulary keeps the boundary crisp.

## Commands

Intent-oriented transactional mutations. Commands are where business intent and invariants live. They may read records, validate state, patch/insert/delete multiple tables, and schedule workflows after recording intent.

**Conventions:**
- Filename: `<thing>Commands.ts`, flat with table and view files.
- Use `mutation` / `internalMutation`.
- Name by user or system intent, not storage mechanics: `setVideoType`, `applyTitleOverride`, `assignSpeaker`, `recordTitleQualityChecks`, `requestTitleGeneration`.
- Avoid generic `patch*` / `update*` names as the default. Commands can use `ctx.db.patch` internally after reading the record, but the exported name should describe why the record is changing.
- Do not call external APIs directly from commands.
- Commands may schedule internal workflows after durable intent is written.
- Prefer returning the updated doc, view payload, or job/status record that the caller can use immediately.

**Example:**

```ts
// convex/videoCommands.ts
import { v } from "convex/values";
import { mutation } from "./_generated/server";

export const applyTitleOverride = mutation({
  args: { youtubeVideoId: v.string(), titleOverride: v.string() },
  handler: async (ctx, { youtubeVideoId, titleOverride }) => {
    const video = await ctx.db
      .query("videos")
      .withIndex("by_youtubeVideoId", q => q.eq("youtubeVideoId", youtubeVideoId))
      .unique();
    if (!video) throw new Error("Video not found");
    await ctx.db.patch(video._id, { titleOverride });
    return await ctx.db.get(video._id);
  },
});
```

## Workflows

External side-effect orchestration: API calls, scheduled jobs, retries, long-running work, and persisted status. Workflows are not table CRUD and do not use FUCD verbs.

**Conventions:**
- Filename: `<thing>Workflows.ts`, flat with table, view, and command files.
- Use `action` / `internalAction`, scheduled functions, or a workflow component when durable execution is needed.
- Name by capability: `generateTitleAlternatives`, `validateTitleQuality`, `refreshYoutubeVideoSnapshot`, `pushYoutubeTitle`.
- Prefer the pattern: command records intent → command schedules internal workflow → workflow calls provider → workflow writes results via internal mutation/command → UI observes state.
- Batch database reads/writes through purpose-built internal queries/mutations. Avoid many small `ctx.runQuery` / `ctx.runMutation` calls when one internal function can provide a consistent payload.
- Access provider secrets and tokens through narrow helpers. Do not scatter `process.env` or OAuth refresh logic across workflows.

**Example:**

```ts
// convex/youtubeWorkflows.ts
import { v } from "convex/values";
import { internalAction } from "./_generated/server";
import { internal } from "./_generated/api";

export const pushYoutubeTitle = internalAction({
  args: { jobId: v.id("youtubeUpdateJobs") },
  handler: async (ctx, { jobId }) => {
    const job = await ctx.runQuery(internal.youtubeUpdateJobs.findInternal, { id: jobId });
    // Get token through a provider boundary, call YouTube, then write result.
    await ctx.runMutation(internal.youtubeUpdateJobs.upsertCompletedInternal, { id: jobId });
  },
});
```

## Quick reference

```
TABLE FILE (e.g. users.ts):
  find(id)                              → one doc | null
  findByEmail(email)                    → one doc | null   [needs by_email]
  findByEmailScan(email)                → ⚠️ avoid; add index instead
  findInternal / findByEmailInternal    → internal-only variants

  upsert(args)                          → written doc
  upsertMany(records)                   → written docs
  upsertInternal                        → internal-only variant

  collect()                             → docs[]
  collectByAuthorId(id)                 → docs[]            [needs by_authorId]
  collectByAuthorIdScan(id)             → docs[]; full scan
  collectByTitleSearch(q)               → docs[]; ranked    [needs search index]

  paginate(opts)                        → page
  paginateByOrgId(id, opts)             → page              [needs by_orgId]
  paginateByTitleSearch(q, opts)        → page; ranked

  count()                               → number
  countByStatus(status)                 → number            [needs by_status]

  destroy(id)                           → deleted doc | null
  destroyMany(ids)                      → deleted docs[]
  destroyManyByAuthorId(id)             → deleted docs[]    [cascade]

VIEW FILE (e.g. userProfileViews.ts):
  get(args)                             → freeform shape
  getForOrg / getRecommendations / ...  → freeform shape

COMMAND FILE (e.g. videoCommands.ts):
  setVideoType(args)                    → intent-oriented DB mutation
  applyTitleOverride(args)              → read/validate/patch by business intent
  requestTitleGeneration(args)          → record intent and schedule workflow

WORKFLOW FILE (e.g. youtubeWorkflows.ts):
  refreshYoutubeVideoSnapshot(args)     → external API orchestration
  pushYoutubeTitle(args)                → side effect + persisted status
  generateTitleAlternatives(args)       → model call + result writeback
```

## When applying the convention

1. Identify what's being named: a table-CRUD operation, a view, a command, or a workflow.
2. If table-CRUD: pick the verb (one vs many vs count vs paginate vs write vs delete), then the field suffix (`By<Field>`), then mechanism (`Scan`/`Search`) only if non-default.
3. If the name implies an index, check `schema.ts`. If missing: add it and alert, or refuse and recommend `*Scan` if indexing is unwise.
4. Default to full-doc returns for writes; deviate only with justification.
5. If the operation is a join or derived read shape, redirect to a `*Views.ts` file with freeform `get*` naming.
6. If the operation is business intent with transactional DB changes, use a `*Commands.ts` file with intention-oriented naming.
7. If the operation calls external APIs, coordinates retries, or performs background work, use a `*Workflows.ts` file with capability-oriented naming.

## When auditing existing code

Flag deviations:
- `find*` returning arrays → should be `collect*` or `paginate*`.
- `getX` / `listX` / `fetchX` / `loadX` in a table file → rename to FUCD verb.
- `collectByX` with no `by_x` index → either add the index or rename to `collectByXScan`.
- Hydration/joins inside a table file → extract to a `*Views.ts` file.
- Intent-oriented business mutations inside table files → extract to a `*Commands.ts` file unless they are truly raw table CRUD.
- External provider calls in route handlers or mutations → move toward a `*Workflows.ts` file and persisted workflow state.
- Repeated direct secret/env access in feature code → introduce a provider/secret boundary.
- Bulk operations using ad-hoc names (`bulkInsertX`, `removeAllX`) → rename to `*Many` form.
- Internal functions without `*Internal` suffix → rename.
- Write verbs returning ids/void by default → return the doc unless deviation is documented.
