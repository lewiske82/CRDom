# GitHub összekapcsolás (HU)

Ez a rövid útmutató segít a helyi repót a GitHub fiókodhoz kapcsolni. A tényleges pushhoz szükséged lesz egy GitHub repóra és hitelesítésre (SSH-kulcs vagy token).

## 1) Új GitHub repo létrehozása
1. Jelentkezz be a GitHub fiókodba.
2. Hozz létre egy új repót (pl. `CRDom`).
3. **Ne** inicializáld README-vel, ha a helyi repo már létezik.

## 2) Távoli remote beállítása
SSH-t javaslok:
```bash
git remote add origin git@github.com:<FELHASZNALO_NEV>/CRDom.git
```

Vagy HTTPS-t:
```bash
git remote add origin https://github.com/<FELHASZNALO_NEV>/CRDom.git
```

## 3) Első push
```bash
git push -u origin main
```

## 4) Ha a branch neve nem `main`
```bash
git branch -M main
git push -u origin main
```

## 5) Ellenőrzés
```bash
git remote -v
git status
```

---
Ha szeretnéd, megírom a pontos parancsokat a GitHub felhasználóneved és a kívánt repo-név alapján.
