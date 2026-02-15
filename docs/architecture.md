# Unified Dev Core – Mini CRM alap (többszintű audit + multi-agent)

## Rövid terv (szállítási sorrend)
1. **Terv**: célok, szerepkörök, ELI10 kérdéslista.
2. **Adat- és API-séma**: CRM entitások + audit/memória naplók.
3. **Moduláris kód**: Firebase/Swift/JS/Python/WP stubok és integrációs váz.
4. **Teszt**: unit + integrációs tesztek (policy, audit, sync).
5. **Build/Deploy**: lokális + Oracle-hibrid + offline csomagolás.

## Többszintű audit
- **App**: funkcionális események (pl. ügyfél létrehozás).
- **Security**: hozzáférés, token és kulcs kezelés.
- **Compliance**: GDPR, törlési kérelmek, consent döntések.

## ELI10 kérdéslista (minden hiányzó paraméterhez)
- API-kulcs(ok)
- Endpoint(ok)
- Domain/tenant
- Offline cache helye
- Oracle Cloud régió és VCN
- Blockchain node típus (privát/public) és konszenzus

## Hibák előrejelzése (Production Manager)
- API limit/kreditek kimerülése.
- Nem engedélyezett domain hozzáférés.
- Offline/online szinkron ütközés.
- GDPR törlési kérelem feldolgozatlan.

## CRM alap entitások
- **Customer**: név, email, státusz, csatorna, címkék.
- **Interaction**: időpont, csatorna, jegyzet.
- **Task/Follow-up**: határidő, tulajdonos, állapot.
- **AuditEvent**: tier, actor, action, detail.
- **MemoryEvent**: user, namespace, data.
