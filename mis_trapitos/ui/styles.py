from tkinter import font, ttk


UI_COLORS = {
    "background": "#F4F7FA", "surface": "#FFFFFF", "surface_alt": "#E9EFF5",
    "text": "#223247", "muted": "#53677E", "border": "#C8D4E0",
    "primary": "#1D3854", "primary_active": "#294C6B",
    "accent": "#147D73", "accent_active": "#10665E",
    "danger": "#AC3549", "danger_active": "#8D293B", "selection": "#D9ECE9",
}


def configure_styles(root):
    c = UI_COLORS
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont"):
        font.nametofont(name, root=root).configure(family="Segoe UI", size=10)
    style.configure(".", font=("Segoe UI", 10), foreground=c["text"])
    for name in ("TFrame", "Workspace.TFrame", "Content.TFrame", "Login.TFrame"):
        style.configure(name, background=c["background"])
    style.configure("Surface.TFrame", background=c["surface"])
    style.configure("WorkspaceHeader.TFrame", background=c["surface"])
    style.configure("Sidebar.TFrame", background=c["primary"])
    style.configure("TLabel", background=c["background"], foreground=c["text"])
    style.configure("Muted.TLabel", foreground=c["muted"], font=("Segoe UI", 9))
    style.configure("Field.TLabel", foreground=c["muted"], font=("Segoe UI", 9))
    style.configure("Card.TLabel", background=c["surface"])
    style.configure("Brand.TLabel", foreground=c["primary"], font=("Segoe UI", 27, "bold"))
    style.configure("WorkspaceTitle.TLabel", background=c["surface"], font=("Segoe UI", 19, "bold"))
    style.configure("WorkspaceMuted.TLabel", background=c["surface"], foreground=c["muted"], font=("Segoe UI", 9))
    for name, size, weight, color in (
        ("SidebarBrand.TLabel", 14, "bold", "#FFFFFF"),
        ("SidebarUser.TLabel", 10, "bold", "#FFFFFF"),
        ("SidebarMuted.TLabel", 9, "normal", "#B7CBDD"),
        ("SidebarSection.TLabel", 8, "bold", "#B7CBDD"),
    ):
        style.configure(name, background=c["primary"], foreground=color, font=("Segoe UI", size, weight))
    style.configure("Sidebar.TSeparator", background="#3B5670")
    style.configure("TLabelframe", background=c["background"], borderwidth=0, relief="flat")
    style.layout("TLabelframe", [("Labelframe.padding", {"sticky": "nswe"})])
    style.configure("TLabelframe.Label", background=c["background"], foreground=c["primary"], font=("Segoe UI", 11, "bold"))
    style.configure("TButton", padding=(14, 8), width=0, font=("Segoe UI", 9, "bold"), relief="flat", borderwidth=0, anchor="center")
    for name, bg, fg, active in (
        ("TButton", c["surface_alt"], c["primary"], "#D9E4EE"),
        ("Accent.TButton", c["accent"], "#FFFFFF", c["accent_active"]),
        ("Danger.TButton", c["danger"], "#FFFFFF", c["danger_active"]),
        ("Sidebar.TButton", c["primary"], "#DDE8F2", c["primary_active"]),
        ("SidebarActive.TButton", c["accent"], "#FFFFFF", c["accent_active"]),
        ("SidebarLogout.TButton", c["primary"], "#DDE8F2", c["primary_active"]),
    ):
        style.configure(name, background=bg, foreground=fg, bordercolor=bg, lightcolor=bg, darkcolor=bg)
        style.map(name, background=[("disabled", "#E1E7ED"), ("pressed", active), ("active", active)],
                  foreground=[("disabled", "#758394"), ("!disabled", fg)],
                  bordercolor=[("focus", c["accent"]), ("!focus", bg)])
    for name in ("Sidebar.TButton", "SidebarActive.TButton", "SidebarLogout.TButton"):
        style.configure(name, anchor="w", padding=(12, 7), font=("Segoe UI", 10))
    style.configure("SidebarActive.TButton", font=("Segoe UI", 10, "bold"))
    style.configure("TEntry", fieldbackground=c["surface"], foreground=c["text"],
                    bordercolor=c["border"], lightcolor=c["border"], darkcolor=c["border"], padding=(9, 6))
    style.map("TEntry", bordercolor=[("focus", c["accent"])])
    style.configure("TCombobox", padding=(9, 6), fieldbackground=c["surface"], bordercolor=c["border"])
    style.map("TCombobox", fieldbackground=[("readonly", c["surface"])],
              selectbackground=[("readonly", c["surface"])], selectforeground=[("readonly", c["text"])],
              bordercolor=[("focus", c["accent"])])
    style.configure("TNotebook", background=c["background"], borderwidth=0, tabmargins=(0, 0, 0, 12))
    style.layout("TNotebook", [("Notebook.padding", {"sticky": "nswe"})])
    style.configure("TNotebook.Tab", padding=(18, 9), background=c["surface_alt"], foreground=c["muted"], font=("Segoe UI", 10, "bold"))
    style.map("TNotebook.Tab", background=[("selected", c["surface"]), ("active", "#D9E4EE")],
              foreground=[("selected", c["accent"]), ("active", c["primary"])],
              padding=[("selected", (18, 9)), ("!selected", (18, 9))],
              expand=[("selected", (0, 0, 0, 0))])
    style.configure("Hidden.TNotebook", padding=0, tabmargins=0)
    style.layout("Hidden.TNotebook.Tab", [])
    line_height = font.Font(root=root, family="Segoe UI", size=10).metrics("linespace")
    style.configure("Treeview", background=c["surface"], fieldbackground=c["surface"],
                    foreground=c["text"], rowheight=line_height + 14, borderwidth=0, relief="flat", font=("Segoe UI", 10))
    style.configure("Treeview.Heading", background=c["surface_alt"], foreground=c["primary"],
                    padding=(10, 9), relief="flat", font=("Segoe UI", 9, "bold"))
    style.map("Treeview", background=[("selected", c["selection"])], foreground=[("selected", c["primary"])])
    style.map("Treeview.Heading", background=[("active", "#D9E4EE")])
    for direction in ("Vertical", "Horizontal"):
        style.configure(f"{direction}.TScrollbar", background="#CEDAE5", troughcolor=c["background"],
                        borderwidth=0, bordercolor=c["background"], arrowcolor=c["muted"])
