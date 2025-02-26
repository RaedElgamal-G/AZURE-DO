<br>
<p align="center">
 <img  src="AZURE-DO.png" align="center" alt="AZUREDOLogo" />
</h1>

---

## 📖 About AZURE-DO

AZURE-DO is an intelligent automation trigger for Azure DevOps, responsible for initiating workflows in other repositories. It seamlessly integrates with **our tools** (**AzureAnalysisAutomate** and **AzureTaskAutomate**), ensuring efficient work item processing, sprint analysis, and task automation.

## 🎯 Why AZURE-DO?

✔ **Acts as the Brain** – Triggers key workflows for automation.
✔ **Reduces Manual Effort** – Ensures seamless execution of tasks in multiple repos.
✔ **Improves Workflow Synchronization** – Keeps analysis and task automation in sync.
✔ **Seamless CI/CD Integration** – Works effortlessly with Azure Pipelines and GitHub Actions.

## 🚀 Features

- **🔗 Workflow Triggering** – Initiates automated workflows in linked repositories.
- **📊 Sprint Analysis Automation** – Triggers analysis for work items and backlog refinement.
- **✅ Task Creation Automation** – Triggers the generation of required tasks for user stories.
- **💬 Automated Commenting** – Ensures structured and well-formatted feedback on Azure DevOps work items.
- **🎨 Beautifully Formatted Comments** – Enhances readability with structured layouts and dynamic mentions.
- **⚡ CI/CD Ready** – Seamlessly integrates with GitHub Actions for workflow dispatch.

---

## 🔄 How to Set Up AZURE-DO

### 1️⃣ Fork the Repository
To start using **AZURE-DO**, fork this repository to your GitHub account.

### 2️⃣ Configure Your Secrets in GitHub
Go to your forked repository ➝ **Settings** ➝ **Secrets and Variables** ➝ **Actions** and add the following secrets:

| Secret Name       | Description                                               | Where to Get It                                                                                          |
| ----------------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `AZURE_PAT`       | Personal Access Token for Azure DevOps                    | 1. Go to [Azure DevOps](https://dev.azure.com/). 2. Click on your profile ➝ **Personal Access Tokens**. 3. Generate a token with Work Item Read & Write permissions. |
| `privateRepoAuth` | GitHub token to trigger workflows in private repositories | This token is **read-only** and will be added publicly in the repository settings. |

### 3️⃣ Set Up Repository Variables
Navigate to **Settings** ➝ **Environments** ➝ **Add Repository Variables**, then add the following:

| Variable Name           | Description                                 | Example                                |
| ----------------------- | ------------------------------------------- | -------------------------------------- |
| `ORGANIZATION`          | Your Azure DevOps organization name         | `GSIntegrationTeam`                    |
| `PROJECT_NAME`          | The project name in Azure DevOps            | `Scrap Management`                     |
| `STATE_REFLECT_KEYWORD` | Keyword for filtering work items            | `Ready For Review`                     |
| `PO_NAME`               | Product Owner's name for automated comments | `Ahmed Hisham`                         |
| `FRONTEND_IDS`          | Frontend team member IDs (comma-separated)  | `id1,id2,id3`                          |
| `BACKEND_IDS`           | Backend team member IDs (comma-separated)   | `id1,id2,id3`                          |
| `MOBILE_IDS`            | Mobile team member IDs (comma-separated)    | `id1,id2,id3`                          |

### 📌 How to Get Team Member IDs for Mentions

To mention team members in automated comments, you need their **Azure DevOps User IDs**:

1. **Go to Azure DevOps** ➝ **Organization Settings**.
2. **Select Users** and find the team member.
3. Click on the user profile and copy their **ID from the URL**.
4. Add multiple IDs separated by a comma `,`.

### 4️⃣ Trigger the Workflow

To manually trigger AZURE-DO workflows:

- Go to the **Actions** tab in your repository.
- Select **Trigger Workflow Dispatch**.
- Click **Run workflow**.

This will initiate workflow execution in the **AzureAnalysisAutomate** and **AzureTaskAutomate** repositories.

---

## 🔜 To Do

- [ ] Improve Workflow Synchronization 📌
- [ ] Enhance Debug Logging 🛠
- [x] Trigger Analysis Automation 📊
- [x] Automate Task Creation ✅
- [x] Implement Work Item State Updates 🔄
- [x] Handle Missing Tasks Automatically 📝
- [x] Extract and Update Effort Estimations ⚡

---

## 🤝 How to Contribute

🔥 Contributions are welcome! Follow these steps:

1. **Fork** the repository.
2. **Create a new branch** for your feature.
3. **Implement your changes** and test thoroughly.
4. **Open a pull request** for review.

Let's build something amazing together! 🚀

---

## ⚠️ License

AZURE-DO is open-source under the MIT License, encouraging collaboration and innovation.

---

## 🌟 Spread the Word!

If you find AZURE-DO helpful, **give it a ⭐ on GitHub!** Your support means a lot. 💙

📢 Follow us on **[LinkedIn](https://www.linkedin.com/in/mohamed-abdelrehem)** for updates!

