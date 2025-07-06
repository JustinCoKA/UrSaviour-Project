# Git Command Manual

## 📦 Clone a repository (first time only)

```bash
git clone https://github.com/JustinCoKA/UrSaviour-Project.git
```

> Copy a GitHub project to your local folder.  
> Only run this once when starting.

---

## 🔄 Get the latest changes from GitHub

```bash
git pull origin main
```

> Download updates from the remote `main` branch.

---

## ➕ Add changes (3 steps)

### 1. Add all files

```bash
git add .
```

> Add all changed files to the staging area.

### Or 1. Add one file (example)

```bash
git add frontend/default.conf
```

> Add only the selected file.

⚠️ **Don't use `git add.`** — a space is required.

---

## 2. Save changes with a message (commit)

```bash
git commit -m "Write a massage for uploading (e.g. Set up minimal routers and confirmed Docker runs)"
```

> Save your changes with a short message.

---

## 3. Upload (push) changes to GitHub

```bash
git push origin main
```

> Send your local commits to the remote `main` branch.

---

## ❗ If push fails with a warning

If you see:

```
Updates were rejected because the remote contains work that you do not have locally.
```

Run this:

```bash
git pull origin main --rebase
```

> This downloads updates from GitHub and adds your changes after them.

Then push again:

```bash
git push origin main
```
