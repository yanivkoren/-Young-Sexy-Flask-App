# How to Send Changes from GitHub Codespaces to GitHub

This guide explains how to **commit and push** your changes from **GitHub Codespaces** to **GitHub**.

---

## **✅ Step 1: Check for Changes**
Run the following command inside your Codespaces terminal to see if there are modified files:
```bash
git status
```
- **If it says "nothing to commit, working tree clean"**, your files are already committed.
- **If you see modified files**, continue to Step 2.

---

## **✅ Step 2: Stage and Commit the Changes**
### **Stage all changes**:
```bash
git add .
```
This prepares all modified files to be committed.

### **Commit the changes**:
```bash
git commit -m "Your commit message here"
```
Replace `"Your commit message here"` with a meaningful description of your update.

---

## **✅ Step 3: Push Changes to GitHub**
Push the committed changes to GitHub using:
```bash
git push origin main
```
> **Note:** If your branch is not `main`, check the branch name:
```bash
git branch
```
Then push using:
```bash
git push origin <your-branch-name>
```

---

## **✅ Step 4: Verify the Changes in GitHub**
1. Go to your **GitHub repository**.
2. Check if the updated files appear in the repository.
3. If everything looks good, your changes are now live!

---

## **❗ Troubleshooting**
### **Changes are not appearing in GitHub?**
- Make sure you are on the correct branch (`git branch`).
- Try force pushing (only if necessary):
  ```bash
  git push origin main --force
  ```

### **Error: "fatal: not a git repository"?**
If you see this error, navigate to your repository folder:
```bash
cd /workspaces/your-repo-name
```
Then run:
```bash
git init
```

### **Error: "Permission denied"?**
Your GitHub credentials might be missing. Try:
```bash
git config --global user.email "your-email@example.com"
git config --global user.name "Your Name"
```
Then push again.

---

## **🚀 Summary**
| Action | Command |
|--------|---------|
| **Check for changes** | `git status` |
| **Stage changes** | `git add .` |
| **Commit changes** | `git commit -m "message"` |
| **Push to GitHub** | `git push origin main` |
| **Verify in GitHub** | Open GitHub repository |

---

🚀 **Now try these steps and send your changes to GitHub!** 🎉

