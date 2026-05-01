---
created: 2026-03-25T19:48:39-07:00
updated: 2026-03-25T19:48:44-07:00
---
``` dataviewjs 
let unresolved = Object.entries(dv.app.metadataCache.unresolvedLinks) .filter(([k, v]) => Object.keys(v).length) .flatMap(([source, targets]) => Object.keys(targets).map(target => ({ source: dv.fileLink(source), target: dv.fileLink(target) })) ); dv.table(["Source Note", "Uncreated Link"], unresolved.map(r => [r.source, r.target]) ); 
```
