# GitHub Actions Telepítőkészítő Útmutató

Ez az útmutató részletezi, hogyan használhatja a GitHub Actions workflow-t a Windows telepítő automatikus létrehozásához és közzétételéhez.

## A GitHub Actions Workflow

A `.github/workflows/build-and-publish-installer.yml` fájlban található workflow automatikusan elkészíti a Windows telepítőt és terjeszti a következő esetekben:

1. **Kód push** - Amikor kódot küld a `main` vagy `master` ágra
2. **Version tag** - Amikor `v` kezdetű tag-et ad ki (pl. `v1.0.0`, `v2.3.1`)
3. **Manuális indítás** - A GitHub felületen a "workflow_dispatch" esemény segítségével

## Használati útmutató

### Telepítő létrehozása és közzététele

1. **Készítse elő a projektet GitHubra**
   - Hozzon létre egy új GitHub repository-t
   - Töltse fel a teljes projektet, beleértve a `.github` mappát és annak tartalmát

2. **Telepítő építése (Automatikus)**
   - A workflow automatikusan lefut, amikor kódot küld a `main` vagy `master` ágra
   - A kész telepítő elérhető lesz a GitHub Actions "Artifacts" szekciójában letöltéshez

3. **Hivatalos kiadás (Release) készítése**
   - Készítsen egy új tag-et a Git-ben, amely "v" kezdetű:
     ```
     git tag v1.0.0
     git push origin v1.0.0
     ```
   - A workflow automatikusan létrehoz egy új GitHub Release-t a tag nevével
   - A telepítő (.exe) fájl csatolva lesz a Release-hez
   - A Release tartalmaz automatikusan generált release jegyzeteket

### A workflow manuális indítása

1. Látogasson el a GitHub repository oldalára
2. Kattintson az "Actions" fülre
3. A bal oldali listából válassza a "Build and Publish Windows Installer" workflow-t
4. Kattintson a "Run workflow" gombra
5. Válassza ki az ágat, amin futtatni szeretné
6. Kattintson a "Run workflow" gombra

## Mit kínál ez a megoldás?

- **Automatizált építés**: Nem kell manuálisan Windows környezetet felállítania
- **Verziókezelés**: A kiadásokat Git tag-ek segítségével kezelheti
- **Release-ek**: Automatikus GitHub Release-ek a telepítővel
- **Egyszerű letöltés**: A felhasználók könnyen elérhetik a telepítőt a GitHub-on

## Hogyan működik ez a háttérben?

A workflow a következő lépéseket hajtja végre:

1. Windows környezet létrehozása a felhőben
2. Python és szükséges függőségek telepítése
3. Inno Setup telepítése
4. Alkalmazás ikon létrehozása, ha nem létezik
5. A Python alkalmazás "befagyasztása" EXE fájllá a PyInstaller segítségével
6. A telepítő létrehozása az Inno Setup-pal
7. A telepítő feltöltése Artifact-ként és (tag esetén) Release-ként

## Hibaelhárítás

Ha problémát tapasztal a workflow során:

1. Ellenőrizze a workflow futási naplóját a GitHub Actions felületen
2. Győződjön meg róla, hogy a `build_exe.py` és `installer.iss` fájlok helyesek
3. Ha az ikon létrehozásnál van probléma, csináljon manuálisan egy `app_icon.ico` fájlt és adja hozzá a projekthez