import json
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.tooltip import ToolTip
import requests
import urllib.parse
import os

CONFIG_FILE = "config.json"

# URLs for API calls
TASK_URL = "https://api.github.com/repos/MohamedAbdelrehem/AzureTaskAutomate/actions/workflows/Actions_Schedule_check_updates.yml/dispatches"
ANALYSIS_URL = "https://api.github.com/repos/MohamedAbdelrehem/AzureAnalysisAutomate/actions/workflows/Actions_Schedule_check_updates.yml/dispatches"

class ScrollableFrame(tk.Frame):
    """
    A custom scrollable frame using a Canvas and vertical scrollbar.
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas)
        self.inner_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Bind mouse wheel events for scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        self.inner.bind("<MouseWheel>", self._on_mousewheel)
        self.inner.bind("<Button-4>", self._on_mousewheel)
        self.inner.bind("<Button-5>", self._on_mousewheel)



    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.inner_id, width=event.width)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling for Windows and Linux"""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")



def get_github_token():
    obfuscated = "JRX05TVYHMS3DVEx7juapBHLX8hPKxL4UlFeo4LZfbe2CA_AwvPqtkwPhFeWPGWFA11tap_buhtig"
    return "".join(reversed(obfuscated))


class App(tb.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        self.github_entry = None
        self.current_theme = "superhero"
        self.title("Azure-DO")
        self.geometry("900x750")

        # Set window icon (make sure AZURE-DO.ico exists)
        try:
            self.iconbitmap('assets/logo/AZURE-DO.ico')
        except Exception as e:
            print("Icon file not found. Please check the path.", e)

        self.config_data = self.load_config()

        # Load icon images for buttons (adjust file names and subsample factors as needed)
        try:
            self.save_icon = tk.PhotoImage(file="assets/images/save_icon.png").subsample(2, 2)
        except Exception as e:
            print("Save icon not found.", e)
            self.save_icon = None

        try:
            self.about_icon = tk.PhotoImage(file="assets/images/about_icon.png").subsample(2, 2)
        except Exception as e:
            print("About icon not found.", e)
            self.about_icon = None

        # Top frame for banner, save button, and About Me button
        top_frame = tb.Frame(self)
        top_frame.pack(fill="x", padx=0, pady=5)

        # Banner image placed at top left and made smaller using subsample
        try:
            original_banner = tk.PhotoImage(file="assets/logo/AZURE-DO.png")
            self.banner_img = original_banner.subsample(2, 2)
            banner_label = tk.Label(top_frame, image=self.banner_img)
            banner_label.pack(side="left", padx=0, pady=5)
        except Exception as e:
            print("Banner image not found. Please check the path.", e)

        # Right side controls in top_frame: Save Settings and About Me buttons with icons
        controls_frame = tb.Frame(top_frame)
        controls_frame.pack(side="right", padx=5)
        save_header_btn = tb.Button(
            controls_frame,
            text=" Save Settings",
            command=self.save_settings,
            bootstyle="success",
            compound="left",
            image=self.save_icon
        )
        save_header_btn.pack(side="right", padx=5)
        about_btn = tb.Button(
            controls_frame,
            text=" About Me",
            command=self.show_about_popup,
            bootstyle="info",
            compound="left",
            image=self.about_icon
        )
        about_btn.pack(side="right", padx=5)

        # Notebook for tabs (Task, Analysis, Settings)
        self.notebook = tb.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=15, pady=0)

        # Task Tab (scrollable)
        self.task_scrolled = ScrollableFrame(self.notebook)
        self.task_scrolled.inner.configure(padx=10, pady=10)
        self.create_task_tab(self.task_scrolled.inner)
        self.notebook.add(self.task_scrolled, text="Task")

        # Analysis Tab (scrollable)
        self.analysis_scrolled = ScrollableFrame(self.notebook)
        self.analysis_scrolled.inner.configure(padx=10, pady=10)
        self.create_analysis_tab(self.analysis_scrolled.inner)
        self.notebook.add(self.analysis_scrolled, text="Analysis")

        # Settings Tab with App Settings section for theme selection
        self.settings_frame = tb.Frame(self.notebook, padding=10)
        self.create_settings_tab(self.settings_frame)
        self.notebook.add(self.settings_frame, text="Settings")

        # Log Output at the bottom
        log_labelframe = tb.Labelframe(self, text="Log Output", padding=10)
        log_labelframe.pack(fill="both", padx=15, pady=(0,15))
        self.log_text = tk.Text(log_labelframe, height=8, bg="white", relief="flat")
        self.log_text.pack(fill="both", expand=True)

        # Footer with copyright information
        footer = tb.Frame(self)
        footer.pack(fill="x", padx=10, pady=(0,10))
        copyright_label = tb.Label(footer, text="© 2025 Mohamed Abdelrehem", font=("Helvetica", 10))
        copyright_label.pack(side="right")

    def on_theme_change(self, event):
        new_theme = self.theme_combo.get()
        self.style.theme_use(new_theme)
        self.current_theme = new_theme
        self.log(f"Theme changed to {new_theme}.")

    def create_settings_tab(self, parent):
        # General Settings
        form_frame = tb.Frame(parent)
        form_frame.pack(fill="x", padx=5, pady=5)
        # Organization
        org_label = tb.Label(form_frame, text="Organization:")
        org_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.org_entry = tb.Entry(form_frame)
        self.org_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        # Project Name
        proj_label = tb.Label(form_frame, text="Project Name:")
        proj_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.proj_entry = tb.Entry(form_frame)
        self.proj_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        # Azure Token
        azure_label = tb.Label(form_frame, text="Azure Token:")
        azure_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.azure_entry = tb.Entry(form_frame, show="*")
        self.azure_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        # GitHub Token
        github_label = tb.Label(form_frame, text="GitHub Token:")
        github_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.github_entry = tb.Entry(form_frame,show="*")
        self.github_entry.insert(0, get_github_token())
        self.github_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        # Email for reports
        email_label = tb.Label(form_frame, text="Email:")
        email_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.email_entry = tb.Entry(form_frame)
        self.email_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        ToolTip(self.email_entry, "This email will be used to send a report after running")

        form_frame.columnconfigure(1, weight=1)

        # App Settings Section
        app_settings_frame = tb.Labelframe(parent, text="App Settings", padding=10)
        app_settings_frame.pack(fill="x", padx=5, pady=10)

        theme_label = tb.Label(app_settings_frame, text="Theme:", font=("Helvetica", 12))
        theme_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.available_themes = ["litera", "darkly", "superhero"]
        self.theme_combo = tb.Combobox(app_settings_frame, values=self.available_themes, state="readonly")
        self.theme_combo.set(self.current_theme)
        self.theme_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_change)
        app_settings_frame.columnconfigure(1, weight=1)

        # Save Settings button (manual save if needed)
        save_btn = tb.Button(parent, text="Save Settings", command=self.save_settings, bootstyle="success")
        save_btn.pack(pady=10)

        self.populate_settings()

    def show_about_popup(self):
        # Create a popup window for the About Me information
        popup = tk.Toplevel(self)
        popup.title("About Me")
        popup.geometry("600x300")
        popup.transient(self)
        popup.grab_set()

        # Section title
        title = tb.Label(popup, text="About Me", font=("Helvetica", 18, "bold"))
        title.pack(pady=(10, 5))

        # Introduction
        intro = tb.Label(popup, text="Hi, I'm Mohamed Abdelrehem.", font=("Helvetica", 16))
        intro.pack(pady=(5, 5))

        # Professional Title
        subtitle = tb.Label(popup, text="Software Test Engineer | ISTQB Certified", font=("Helvetica", 16))
        subtitle.pack(pady=(5, 5))

        # Connection prompt
        connect_label = tb.Label(popup, text="Connect with me:", font=("Helvetica", 16, "bold"))
        connect_label.pack(pady=(10, 2))

        # Connection details as a bullet list
        connections = (
            "• GitHub: www.github.com/MohamedAbdelrehem\n"
            "• LinkedIn: www.linkedin.com/in/mohamed-abdelrehem"
        )
        connect_details = tb.Label(popup, text=connections, font=("Helvetica", 16), justify="left", wraplength=550)
        connect_details.pack(padx=10, pady=(5, 10))

        # Close button
        close_btn = tb.Button(popup, text="Close", command=popup.destroy, bootstyle="secondary")
        close_btn.pack(pady=5)

    def create_task_tab(self, parent):
        instr = tb.Label(parent, text="Select Task Types:", font=("Helvetica", 12, "bold"))
        instr.pack(anchor="w", padx=5, pady=5)
        teams_frame = tb.Frame(parent)
        teams_frame.pack(fill="x", padx=5, pady=5)
        # Define teams: FrontEnd, BackEnd, and Testing (with two groups)
        self.task_types = {
            "FrontEnd": ["FE-CreatUI", "FE-Review", "FE-APIIntegration", "FE-ReviewStory"],
            "BackEnd": ["[BE][Supplier][Design]", "[BE] [Supplier][Implementation]", "[BE] [Supplier][UnitTest]", "[BE] [Supplier][Review]"],
            "Testing": {
                "General Testing": ["Test Analysis", "Test Case Preparation", "Test Execution", "Retesting"],
                "Mobile Specific Testing": ["Android - Test Execution", "IOS - Test Execution", "Android - Retesting", "IOS - Retesting"]
            }
        }
        self.task_vars = {}
        for team, tasks in self.task_types.items():
            if team != "Testing":
                team_frame = tb.Labelframe(teams_frame, text=f"{team} Team", padding=10)
                team_frame.pack(fill="x", padx=5, pady=5)
                for t in tasks:
                    var = tk.IntVar()
                    chk = tb.Checkbutton(team_frame, text=t, variable=var)
                    chk.pack(side="left", padx=5, pady=5)
                    self.task_vars[t] = var
            else:
                # For Testing, create two sub-groups within the same Testing team frame
                testing_frame = tb.Labelframe(teams_frame, text="Testing Team", padding=10)
                testing_frame.pack(fill="x", padx=5, pady=5)
                for subgroup, sub_tasks in tasks.items():
                    subgroup_frame = tb.Labelframe(testing_frame, text=subgroup, padding=10)
                    subgroup_frame.pack(fill="x", padx=5, pady=5)
                    for t in sub_tasks:
                        var = tk.IntVar()
                        chk = tb.Checkbutton(subgroup_frame, text=t, variable=var)
                        chk.pack(side="left", padx=5, pady=5)
                        self.task_vars[t] = var
        custom_frame = tb.Frame(parent)
        custom_frame.pack(fill="x", padx=5, pady=10)
        custom_label = tb.Label(custom_frame, text="Additional Task Types (comma separated):")
        custom_label.pack(anchor="w", padx=5, pady=5)
        self.custom_task_entry = tb.Entry(custom_frame)
        self.custom_task_entry.pack(fill="x", padx=5, pady=5)
        additional_frame = tb.Labelframe(parent, text="Additional Task Settings", padding=10)
        additional_frame.pack(fill="x", padx=5, pady=10)
        self.auto_close_var = tk.IntVar()
        auto_close_chk = tb.Checkbutton(additional_frame, text="Activate AutoClose", variable=self.auto_close_var)
        auto_close_chk.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tscope_label = tb.Label(additional_frame, text="Scope of the Task:")
        tscope_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.tscope_combo = tb.Combobox(additional_frame, values=["Current Sprint", "All Sprints"], state="readonly")
        self.tscope_combo.current(0)
        self.tscope_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        uscope_label = tb.Label(additional_frame, text="User Story Scope:")
        uscope_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.uscope_combo = tb.Combobox(additional_frame, values=["Web", "Mobile", "All"], state="readonly")
        self.uscope_combo.current(0)
        self.uscope_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ttags_label = tb.Label(additional_frame, text="Tags (comma separated):")
        ttags_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.ttags_entry = tb.Entry(additional_frame)
        self.ttags_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        additional_frame.columnconfigure(1, weight=1)
        btn_frame = tb.Frame(parent)
        btn_frame.pack(fill="x", padx=5, pady=10)
        preview_btn = tb.Button(btn_frame, text="Preview Payload", command=self.preview_task_payload, bootstyle="info")
        preview_btn.pack(side="left", padx=5)
        run_task_btn = tb.Button(btn_frame, text="Run Task Workflow", command=self.run_task_workflow, bootstyle="success")
        run_task_btn.pack(side="right", padx=5)

    def create_analysis_tab(self, parent):
        form_frame = tb.Frame(parent)
        form_frame.pack(fill="x", padx=5, pady=5)
        labels = ["POName", "FrontEndIDs", "BackEndIDs", "MobileIDs", "StateReflectKeyword"]
        self.analysis_entries = {}
        for i, field in enumerate(labels):
            lbl = tb.Label(form_frame, text=f"{field}:")
            lbl.grid(row=i, column=0, sticky="w", padx=5, pady=5)
            entry = tb.Entry(form_frame)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
            self.analysis_entries[field] = entry
        form_frame.columnconfigure(1, weight=1)
        btn_frame = tb.Frame(parent)
        btn_frame.pack(fill="x", padx=5, pady=10)
        preview_btn = tb.Button(btn_frame, text="Preview Payload", command=self.preview_analysis_payload, bootstyle="info")
        preview_btn.pack(side="left", padx=5)
        run_analysis_btn = tb.Button(btn_frame, text="Run Analysis Workflow", command=self.run_analysis_workflow, bootstyle="success")
        run_analysis_btn.pack(side="right", padx=5)

    def preview_payload_popup(self, payload):
        popup = tk.Toplevel(self)
        popup.title("Payload Preview")
        text = tk.Text(popup, wrap="none", width=100, height=20)
        text.pack(fill="both", expand=True)
        formatted = json.dumps(payload, indent=4)
        text.insert("1.0", formatted)
        text.configure(state="disabled")
        popup.transient(self)
        popup.grab_set()
        self.wait_window(popup)

    def preview_task_payload(self):
        selected = [t for t, var in self.task_vars.items() if var.get() == 1]
        custom = self.custom_task_entry.get()
        if custom.strip():
            custom_items = [item.strip() for item in custom.split(",") if item.strip()]
            selected.extend(custom_items)
        task_types_title = ",".join(selected)
        payload = {
            "ref": "master",
            "inputs": {
                "AzureToken": self.azure_entry.get().strip(),
                "Organization": self.org_entry.get(),
                "ProjectName": urllib.parse.quote(self.proj_entry.get()),
                "ActivateAutoClose": bool(self.auto_close_var.get()),
                "TaskTypesTitle": task_types_title,
                "TaskScope": self.tscope_combo.get(),
                "TaskUSScope": self.uscope_combo.get(),
                "TaskTags": self.ttags_entry.get().strip()
            }
        }
        self.preview_payload_popup(payload)

    def preview_analysis_payload(self):
        inputs = {
            "AzureToken": self.azure_entry.get().strip(),
            "Organization": self.org_entry.get(),
            "ProjectName": urllib.parse.quote(self.proj_entry.get())
        }
        for field, entry in self.analysis_entries.items():
            inputs[field] = entry.get().strip()
        payload = {
            "ref": "master",
            "inputs": inputs
        }
        self.preview_payload_popup(payload)

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def populate_settings(self):
        if self.config_data:
            self.org_entry.insert(0, self.config_data.get("organization", ""))
            self.proj_entry.insert(0, self.config_data.get("project_name", ""))
            self.azure_entry.insert(0, self.config_data.get("azure_token", ""))
            self.github_entry.insert(0, self.config_data.get("github_token", ""))
            self.email_entry.insert(0, self.config_data.get("email", ""))
            self.custom_task_entry.insert(0, self.config_data.get("task_custom", ""))
            self.auto_close_var.set(self.config_data.get("auto_close", 0))
            self.tscope_combo.set(self.config_data.get("task_scope", "Current Sprint"))
            self.uscope_combo.set(self.config_data.get("uscope", "Web"))
            self.ttags_entry.insert(0, self.config_data.get("task_tags", ""))
            analysis_config = self.config_data.get("analysis", {})
            for field, entry in self.analysis_entries.items():
                entry.insert(0, analysis_config.get(field, ""))

    def save_settings(self):
        self.config_data = {
            "organization": self.org_entry.get(),
            "project_name": self.proj_entry.get(),
            "azure_token": self.azure_entry.get(),
            # "github_token": self.github_entry.get(),
            "email": self.email_entry.get(),
            "task_custom": self.custom_task_entry.get(),
            "auto_close": self.auto_close_var.get(),
            "task_scope": self.tscope_combo.get(),
            "uscope": self.uscope_combo.get(),
            "task_tags": self.ttags_entry.get(),
            "analysis": {}
        }
        for field, entry in self.analysis_entries.items():
            self.config_data["analysis"][field] = entry.get()
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config_data, f, indent=4)
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully!")
            self.log("Settings saved.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            self.log(f"Error saving settings: {e}")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except Exception as e:
                self.log(f"Error loading config: {e}")
        return {}

    def run_task_workflow(self):
        threading.Thread(target=self._run_task_workflow, daemon=True).start()

    def _run_task_workflow(self):
        if not self.config_data:
            self.log("Please save your settings first.")
            return
        selected = [t for t, var in self.task_vars.items() if var.get() == 1]
        custom = self.custom_task_entry.get()
        if custom.strip():
            custom_items = [item.strip() for item in custom.split(",") if item.strip()]
            selected.extend(custom_items)
        task_types_title = ",".join(selected)
        payload = {
            "ref": "master",
            "inputs": {
                "AzureToken": self.azure_entry.get().strip(),
                "Organization": self.org_entry.get(),
                "ProjectName": urllib.parse.quote(self.proj_entry.get()),
                "ActivateAutoClose": bool(self.auto_close_var.get()),
                "TaskTypesTitle": task_types_title,
                "TaskScope": self.tscope_combo.get(),
                "TaskUSScope": self.uscope_combo.get(),
                "TaskTags": self.ttags_entry.get().strip()
            }
        }
        self.log("Triggering Task Workflow...")
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.github_entry.get().strip()}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(TASK_URL, json=payload, headers=headers)
            if response.ok:
                self.log("Task Workflow triggered successfully.")
            else:
                self.log(f"Task Workflow trigger failed: {response.status_code} {response.text}")
        except Exception as e:
            self.log(f"Error triggering Task Workflow: {e}")

    def run_analysis_workflow(self):
        threading.Thread(target=self._run_analysis_workflow, daemon=True).start()

    def _run_analysis_workflow(self):
        if not self.config_data:
            self.log("Please save your settings first.")
            return
        inputs = {
            "AzureToken": self.azure_entry.get().strip(),
            "Organization": self.org_entry.get(),
            "ProjectName": urllib.parse.quote(self.proj_entry.get())
        }
        for field, entry in self.analysis_entries.items():
            inputs[field] = entry.get().strip()
        payload = {
            "ref": "master",
            "inputs": inputs
        }
        self.log("Triggering Analysis Workflow...")
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.github_entry.get().strip()}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(ANALYSIS_URL, json=payload, headers=headers)
            if response.ok:
                self.log("Analysis Workflow triggered successfully.")
            else:
                self.log(f"Analysis Workflow trigger failed: {response.status_code} {response.text}")
        except Exception as e:
            self.log(f"Error triggering Analysis Workflow: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
