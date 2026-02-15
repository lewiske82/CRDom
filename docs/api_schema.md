# Adat- és API-séma (vázlat)

## Firestore kollekciók
- `customers/{customerId}`
  - name, email, status, channel, tags[], createdAt, updatedAt
- `interactions/{interactionId}`
  - customerId, channel, note, occurredAt, ownerId
- `tasks/{taskId}`
  - customerId, title, dueAt, status, ownerId
- `audit_events/{eventId}`
  - tier, actor, action, detail, createdAt
- `memory_events/{eventId}`
  - userId, namespace, data, createdAt

## REST vázlat
- `POST /api/customers`
- `GET /api/customers/{id}`
- `POST /api/interactions`
- `POST /api/tasks`
- `POST /api/audit`
- `POST /api/memory`

## Webhookok
- `POST /webhooks/oracle/sync`
- `POST /webhooks/blockchain/event`
