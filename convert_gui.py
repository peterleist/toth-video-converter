import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import time
from video_converter import convert_to_mpg, check_ffmpeg
from tkinter import ttk

class VideoConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Videó MPG konvertáló")
        self.root.geometry("800x800")
        self.files = []
        self.output_dir = os.getcwd()
        self.current_file_index = 0
        self.conversion_running = False

        # Modern téma beállítása
        self.set_modern_theme()
        
        # Főkeret létrehozása
        main_frame = ttk.Frame(root, padding="20 15 20 15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Cím létrehozása
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        title_label = ttk.Label(title_frame, text="Videó Konvertáló", 
                               font=("Helvetica", 16, "bold"))
        title_label.pack()
        subtitle = ttk.Label(title_frame, text="Konvertálás MPG formátumba")
        subtitle.pack()

        # Fájl kiválasztás keret
        file_frame = ttk.LabelFrame(main_frame, text="Fájlok", padding=10)
        file_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Fájl kiválasztás gomb
        self.select_btn = ttk.Button(
            file_frame, 
            text="Videófájl(ok) kiválasztása", 
            command=self.select_files,
            style="Accent.TButton"
        )
        self.select_btn.pack(pady=5, fill=tk.X)
        
        # Tooltip készítése a gombhoz
        self.create_tooltip(self.select_btn, "MP4, AVI, MOV, MKV formátumú videófájlok kiválasztása")

        # Kiválasztott fájlok listája (Treeview)
        tree_frame = ttk.Frame(file_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollbar a Treeview-hoz
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_tree = ttk.Treeview(
            tree_frame, 
            columns=('file', 'status'), 
            show='headings', 
            height=5,
            yscrollcommand=scrollbar.set
        )
        self.file_tree.heading('file', text='Fájlok')
        self.file_tree.heading('status', text='Állapot')
        self.file_tree.column('file', width=400)
        self.file_tree.column('status', width=100)
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_tree.yview)

        # Beállítások keret
        settings_frame = ttk.LabelFrame(main_frame, text="Beállítások", padding=10)
        settings_frame.pack(fill=tk.X, pady=10)
        
        # Célmappa kiválasztás
        dir_frame = ttk.Frame(settings_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        
        self.dir_btn = ttk.Button(
            dir_frame, 
            text="Célmappa kiválasztása", 
            command=self.select_output_dir
        )
        self.dir_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.dir_label = ttk.Label(dir_frame, text=f"Célmappa: {self.output_dir}")
        self.dir_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Felbontás kiválasztó
        self.resolutions = [
            "1920x1080", "720x576", "1280x720", "640x480", 
            "3840x2160", "854x480", "320x240",
            # 8:7 képarányú felbontások
            "1024x896", "800x700", "640x560", "512x448", "384x336"
        ]
        self.selected_resolution = tk.StringVar(value=self.resolutions[0])
        
        res_frame = ttk.Frame(settings_frame)
        res_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(res_frame, text="Felbontás:").pack(side=tk.LEFT, padx=(0, 10))
        self.res_menu = ttk.Combobox(
            res_frame, 
            textvariable=self.selected_resolution, 
            values=self.resolutions, 
            state='readonly',
            width=15
        )
        self.res_menu.pack(side=tk.LEFT)
        self.create_tooltip(self.res_menu, "Válassza ki a kimeneti videó felbontását")
        
        # Minőség kiválasztó
        self.qualities = {
            "Alacsony": "low",
            "Közepes": "medium",
            "Magas": "high",
            "Nagyon magas": "veryhigh",
            "Ultra": "ultra",
            "Maximum": "maximum"
        }
        self.selected_quality = tk.StringVar(value="Közepes")
        
        quality_frame = ttk.Frame(settings_frame)
        quality_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(quality_frame, text="Videóminőség:").pack(side=tk.LEFT, padx=(0, 10))
        self.quality_menu = ttk.Combobox(
            quality_frame,
            textvariable=self.selected_quality,
            values=list(self.qualities.keys()),
            state='readonly',
            width=15
        )
        self.quality_menu.pack(side=tk.LEFT)
        self.create_tooltip(self.quality_menu, "Válassza ki a kimeneti videó minőségét:\n"
                                             "- Alacsony: kisebb fájlméret\n"
                                             "- Közepes: általános használatra\n"
                                             "- Magas: jobb minőség, élesebb kép\n"
                                             "- Nagyon magas: kiváló minőség\n"
                                             "- Ultra: professzionális minőség zajszűréssel\n"
                                             "- Maximum: maximális részletesség, nagyobb fájlméret")

        # Konvertálás keret
        convert_frame = ttk.Frame(main_frame)
        convert_frame.pack(fill=tk.X, pady=10)
        
        # Konvertálás gomb
        self.convert_btn = ttk.Button(
            convert_frame, 
            text="Konvertálás indítása", 
            command=self.start_conversion,
            style="Accent.TButton"
        )
        self.convert_btn.pack(fill=tk.X, pady=5)
        self.create_tooltip(self.convert_btn, "A kiválasztott fájlok konvertálása MPG formátumba")

        # Progress frame - Teljes folyamat
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(progress_frame, text="Összes folyamat:").pack(anchor=tk.W)
        
        self.progress = ttk.Progressbar(
            progress_frame, 
            orient='horizontal', 
            length=400, 
            mode='determinate',
            style="TProgressbar"
        )
        self.progress.pack(fill=tk.X, pady=5)

        # Állapotjelző
        self.status_label = ttk.Label(
            progress_frame, 
            text="Készen áll a konvertálásra",
            anchor=tk.CENTER
        )
        self.status_label.pack(fill=tk.X, pady=5)

        # Aktuális fájl progress frame
        current_progress_frame = ttk.Frame(main_frame)
        current_progress_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(current_progress_frame, text="Aktuális fájl:").pack(anchor=tk.W)
        
        self.current_file_progress = ttk.Progressbar(
            current_progress_frame, 
            orient='horizontal', 
            length=400, 
            mode='determinate',
            style="TProgressbar"
        )
        self.current_file_progress.pack(fill=tk.X, pady=5)
        
        # Hátralévő idő jelző
        self.time_label = ttk.Label(
            current_progress_frame, 
            text="Becsült hátralévő idő: --:--",
            anchor=tk.CENTER
        )
        self.time_label.pack(fill=tk.X, pady=5)

    def set_modern_theme(self):
        """Modern téma beállítása a felületen"""
        style = ttk.Style()
        
        # Alapvető témák közül a "clam" a legmodernebb alapértelmezett téma macOS-en
        style.theme_use('clam')
        
        # Főszínek definiálása
        bg_color = '#f5f5f7'
        accent_color = '#007aff'  # iOS/macOS kék
        text_color = '#333333'
        hover_color = '#0069d9'
        
        # Alap háttérszín beállítása
        self.root.configure(background=bg_color)
        
        # Általános stílusok
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=text_color)
        style.configure('TLabelframe', background=bg_color, foreground=text_color)
        style.configure('TLabelframe.Label', background=bg_color, foreground=text_color)
        
        # Normál gombok
        style.configure('TButton', 
                        background=bg_color, 
                        foreground=text_color,
                        borderwidth=1)
        
        # Kiemelt gombok                
        style.configure('Accent.TButton', 
                        background=accent_color, 
                        foreground='white',
                        borderwidth=0)
        
        style.map('Accent.TButton', 
                 background=[('active', hover_color), 
                             ('pressed', hover_color)])
                             
        # Progressbar testreszabása
        style.configure('TProgressbar', 
                        background=accent_color,
                        troughcolor='#e0e0e0', 
                        borderwidth=0, 
                        thickness=10)
        
        # Treeview testreszabása
        style.configure('Treeview', 
                        background='white',
                        fieldbackground='white',
                        foreground=text_color)
        
        style.configure('Treeview.Heading', 
                        background='#eaeaea',
                        foreground=text_color)
        
        # Combobox testreszabása
        style.configure('TCombobox',
                        background=bg_color,
                        fieldbackground='white')

    def create_tooltip(self, widget, text):
        """Tooltip funkció hozzáadása egy widgethez"""
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20
            
            # Tooltip ablak létrehozása
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = ttk.Label(self.tooltip, text=text, background="#ffffe0", 
                             relief="solid", borderwidth=1, padding=2)
            label.pack()
            
        def leave(event):
            if hasattr(self, "tooltip"):
                self.tooltip.destroy()
                
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Videófájlok kiválasztása",
            filetypes=[("Videófájlok", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm *.MP4 *.AVI *.MOV *.MKV *.WMV *.FLV *.WEBM")]
        )
        if files:
            self.files = list(files)
            # Frissítse a fájllistát
            self.file_tree.delete(*self.file_tree.get_children())
            for f in self.files:
                self.file_tree.insert('', tk.END, values=(f, "Várakozás"))

    def select_output_dir(self):
        dir_selected = filedialog.askdirectory(title="Célmappa kiválasztása")
        if dir_selected:
            self.output_dir = dir_selected
            self.dir_label.config(text=f"Célmappa: {self.output_dir}")

    def format_time(self, seconds):
        """Másodperceket formázza olvasható idővé"""
        if seconds < 60:
            return f"{int(seconds)} másodperc"
        
        minutes = int(seconds / 60)
        sec = int(seconds % 60)
        
        if minutes < 60:
            return f"{minutes} perc {sec} másodperc"
        
        hours = int(minutes / 60)
        min_rem = int(minutes % 60)
        
        return f"{hours} óra {min_rem} perc {sec} másodperc"

    def update_progress(self, percent, remaining_seconds, _):
        """Frissíti az aktuális fájl előrehaladását és a becsült hátralévő időt"""
        if not self.conversion_running:
            return
        
        self.current_file_progress['value'] = percent
        
        # Hátralévő idő frissítése
        formatted_time = self.format_time(remaining_seconds)
        self.time_label.config(text=f"Becsült hátralévő idő: {formatted_time}")
        
        # Állapot frissítése a fájllistában
        if self.current_file_index < len(self.files):
            item_id = self.file_tree.get_children()[self.current_file_index]
            self.file_tree.item(item_id, values=(self.files[self.current_file_index], f"{percent:.1f}%"))

    def start_conversion(self):
        if not self.files:
            messagebox.showwarning("Nincs fájl kiválasztva", "Először válassz ki legalább egy videófájlt!")
            return
        if not check_ffmpeg():
            messagebox.showerror("FFmpeg hiányzik", "Az FFmpeg nincs telepítve vagy nincs az elérési úton!")
            return
            
        # Progress és state inicializálása
        self.progress['value'] = 0
        self.progress['maximum'] = len(self.files)
        self.current_file_progress['value'] = 0
        self.status_label.config(text="Konvertálás folyamatban...")
        self.time_label.config(text="Becsült hátralévő idő: számítás alatt...")
        self.convert_btn.config(state=tk.DISABLED)
        self.conversion_running = True
        self.current_file_index = 0
        
        # Minden fájl állapotának frissítése "Várakozás"-ra
        for i, _ in enumerate(self.files):
            item_id = self.file_tree.get_children()[i]
            self.file_tree.item(item_id, values=(self.files[i], "Várakozás"))
        
        threading.Thread(target=self.convert_files, daemon=True).start()

    def convert_files(self):
        success = 0
        fail = 0
        resolution = self.selected_resolution.get()
        quality = self.qualities[self.selected_quality.get()]
        
        for idx, file in enumerate(self.files):
            self.current_file_index = idx
            base = os.path.splitext(os.path.basename(file))[0]
            out_path = os.path.join(self.output_dir, base + ".mpg")
            
            # Állapot frissítése az aktuális fájllal
            self.root.after(0, lambda file=file: self.status_label.config(
                text=f"Konvertálás: {os.path.basename(file)}..."
            ))
            
            item_id = self.file_tree.get_children()[idx]
            self.root.after(0, lambda id=item_id, f=file: self.file_tree.item(id, values=(f, "Konvertálás...")))
            
            # Progress bar és hátralévő idő visszaállítása
            self.root.after(0, lambda: self.current_file_progress.config(value=0))
            self.root.after(0, lambda: self.time_label.config(text="Becsült hátralévő idő: számítás alatt..."))
            
            # Konvertálás az előrehaladás-visszajelzéssel és minőségbeállítással
            result = convert_to_mpg(
                file, 
                out_path, 
                overwrite=True, 
                resolution=resolution, 
                progress_callback=self.update_progress,
                quality=quality
            )
            
            if result:
                success += 1
                self.root.after(0, lambda id=item_id, f=file: self.file_tree.item(id, values=(f, "Kész")))
            else:
                fail += 1
                self.root.after(0, lambda id=item_id, f=file: self.file_tree.item(id, values=(f, "Sikertelen")))
                
            # Frissítse a teljes folyamat progress bar-t
            self.root.after(0, self.progress.step)
        
        self.conversion_running = False
        self.root.after(0, self.show_result, success, fail)

    def show_result(self, success, fail):
        msg = f"Sikeres: {success}, Sikertelen: {fail}"
        self.status_label.config(text=msg)
        self.time_label.config(text="Becsült hátralévő idő: --:--")
        self.convert_btn.config(state=tk.NORMAL)
        if fail == 0 and success > 0:
            messagebox.showinfo("Kész", "Minden fájl sikeresen konvertálva!")
        elif fail > 0:
            messagebox.showwarning("Hiba", f"{fail} fájl konvertálása sikertelen volt.")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoConverterGUI(root)
    root.mainloop()
