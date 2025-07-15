import customtkinter as ctk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")

class FrecellApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Frecell — Desktop Data Tool")
        self.geometry("1000x650")
        self.df = None

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_import = self.tabview.add("📥 Import Data")
        self.tab_query = self.tabview.add("🧪 Query Editor")
        self.tab_plot = self.tabview.add("📈 Plot Designer")

        self.build_tab_import()
        self.build_tab_query()
        self.build_tab_plot()

    def build_tab_import(self):
        self.upload_button = ctk.CTkButton(self.tab_import, text="Upload CSV", command=self.upload_csv)
        self.upload_button.pack(pady=10)

        self.row_slider = ctk.CTkSlider(self.tab_import, from_=1, to=10, number_of_steps=9, command=self.preview_rows)
        self.row_slider.set(5)
        self.row_slider.pack(pady=10)

        self.preview_text = ctk.CTkTextbox(self.tab_import, width=900, height=400)
        self.preview_text.pack(padx=10, pady=10)

    def upload_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                messagebox.showinfo("Success", "CSV loaded successfully!")
                self.preview_rows()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read CSV: {e}")

    def preview_rows(self, _=None):
        if self.df is not None:
            n = int(self.row_slider.get())
            preview = self.df.head(n).to_string()
            self.preview_text.delete("0.0", "end")
            self.preview_text.insert("0.0", preview)

    def build_tab_query(self):
        self.query_entry = ctk.CTkTextbox(self.tab_query, width=900, height=100)
        self.query_entry.pack(padx=10, pady=10)
        self.query_entry.insert("0.0", "df[df['Age'] > 30]")

        self.run_button = ctk.CTkButton(self.tab_query, text="▶ Run Query", command=self.run_query)
        self.run_button.pack()

        self.query_result = ctk.CTkTextbox(self.tab_query, width=900, height=400)
        self.query_result.pack(padx=10, pady=10)

    def run_query(self):
        if self.df is None:
            messagebox.showwarning("No Data", "Please upload a CSV first.")
            return

        code = self.query_entry.get("0.0", "end").strip()
        try:
            local_env = {"df": self.df.copy(), "pd": pd}
            result = eval(code, {}, local_env)

            self.query_result.delete("0.0", "end")
            if isinstance(result, pd.DataFrame):
                self.query_result.insert("0.0", result.to_string())
            else:
                self.query_result.insert("0.0", str(result))
        except Exception as e:
            self.query_result.delete("0.0", "end")
            self.query_result.insert("0.0", f"❌ Error: {e}")

    def build_tab_plot(self):
        self.x_col_menu = ctk.CTkOptionMenu(self.tab_plot, values=[""], command=self.update_default_code)
        self.x_col_menu.pack(pady=5)

        self.y_col_menu = ctk.CTkOptionMenu(self.tab_plot, values=[""], command=self.update_default_code)
        self.y_col_menu.pack(pady=5)

        self.plot_code_box = ctk.CTkTextbox(self.tab_plot, width=900, height=160)
        self.plot_code_box.pack(padx=10, pady=10)

        self.plot_button = ctk.CTkButton(self.tab_plot, text="📊 Generate Plot", command=self.generate_plot)
        self.plot_button.pack(pady=5)

        self.canvas_frame = ctk.CTkFrame(self.tab_plot)
        self.canvas_frame.pack(padx=10, pady=10, fill="both", expand=True)

    def update_default_code(self, _=None):
        if self.df is None:
            return

        x = self.x_col_menu.get()
        y = self.y_col_menu.get()
        default_code = f"""fig, ax = plt.subplots()
ax.plot(df["{x}"], df["{y}"])
ax.set_xlabel("{x}")
ax.set_ylabel("{y}")
ax.set_title("{y} vs {x}")
ax.grid(True)
"""
        self.plot_code_box.delete("0.0", "end")
        self.plot_code_box.insert("0.0", default_code)

    def generate_plot(self):
        if self.df is None:
            messagebox.showwarning("No Data", "Please upload a CSV first.")
            return

        code = self.plot_code_box.get("0.0", "end")
        try:
            fig_env = {"df": self.df, "pd": pd, "plt": plt}
            exec(code, fig_env)
            fig = fig_env.get("fig", plt.gcf())

            for widget in self.canvas_frame.winfo_children():
                widget.destroy()

            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Plot Error", f"{e}")

    def update_column_menus(self):
        if self.df is not None:
            numeric_cols = self.df.select_dtypes(include="number").columns.tolist()
            if numeric_cols:
                self.x_col_menu.configure(values=numeric_cols)
                self.y_col_menu.configure(values=numeric_cols)
                self.x_col_menu.set(numeric_cols[0])
                self.y_col_menu.set(numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0])
                self.update_default_code()

    def mainloop_with_update(self):
        def check_csv_loaded():
            self.update_column_menus()
            self.after(1000, check_csv_loaded)

        check_csv_loaded()
        self.mainloop()

if __name__ == "__main__":
    app = FrecellApp()
    app.mainloop_with_update()
