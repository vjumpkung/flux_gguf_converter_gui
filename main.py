import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import shlex
import os
import sys

PYTHON = sys.executable


class GGUFConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flux GGUF Converter and Quantizer")
        self.root.geometry("600x300")
        self.root.resizable(False, False)

        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=5)

        # Create tabs
        self.convert_tab = ttk.Frame(self.notebook)
        self.quantize_tab = ttk.Frame(self.notebook)

        # Add tabs to notebook
        self.notebook.add(self.convert_tab, text="Convert to GGUF")
        self.notebook.add(self.quantize_tab, text="Quantization")

        # Initialize tabs
        self.setup_convert_tab()
        self.setup_quantize_tab()

        # Processing flags
        self.is_converting = False
        self.is_quantizing = False

        # Filestate
        self.sft_file = ""
        self.gguf_file = ""
        self.output_path = ""

    def setup_convert_tab(self):
        # Source file selection
        ttk.Label(self.convert_tab, text="Source File:").pack(pady=5)
        self.source_frame = ttk.Frame(self.convert_tab)
        self.source_frame.pack(fill="x", padx=5)

        self.source_entry = ttk.Entry(self.source_frame)
        self.source_entry.pack(side="left", expand=True, fill="x", padx=(0, 5))

        ttk.Button(self.source_frame, text="Browse", command=self.browse_source).pack(
            side="right"
        )

        # Destination selection
        ttk.Label(self.convert_tab, text="Destination:").pack(pady=5)
        self.dest_frame = ttk.Frame(self.convert_tab)
        self.dest_frame.pack(fill="x", padx=5)

        self.dest_entry = ttk.Entry(self.dest_frame)
        self.dest_entry.pack(side="left", expand=True, fill="x", padx=(0, 5))

        ttk.Button(
            self.dest_frame, text="Browse", command=self.browse_destination
        ).pack(side="right")

        # Convert button
        self.convert_button = ttk.Button(
            self.convert_tab, text="Convert", command=self.start_conversion
        )
        self.convert_button.pack(pady=20)

        # Progress bar
        self.convert_progress = ttk.Progressbar(self.convert_tab, mode="indeterminate")
        self.convert_progress.forget()

    def setup_quantize_tab(self):
        # GGUF file selection
        ttk.Label(self.quantize_tab, text="GGUF FP16/BF16 File:").pack(pady=5)
        self.gguf_frame = ttk.Frame(self.quantize_tab)
        self.gguf_frame.pack(fill="x", padx=5)

        self.gguf_entry = ttk.Entry(self.gguf_frame)
        self.gguf_entry.pack(side="left", expand=True, fill="x", padx=(0, 5))

        ttk.Button(self.gguf_frame, text="Browse", command=self.browse_gguf).pack(
            side="right"
        )

        # Destination selection for quantization
        ttk.Label(self.quantize_tab, text="Destination:").pack(pady=5)
        self.quant_dest_frame = ttk.Frame(self.quantize_tab)
        self.quant_dest_frame.pack(fill="x", padx=5)

        self.quant_dest_entry = ttk.Entry(self.quant_dest_frame)
        self.quant_dest_entry.pack(side="left", expand=True, fill="x", padx=(0, 5))

        ttk.Button(
            self.quant_dest_frame, text="Browse", command=self.browse_quant_destination
        ).pack(side="right")

        # Quantization method selection
        ttk.Label(self.quantize_tab, text="Quantization Method:").pack(pady=5)
        self.quant_method = ttk.Combobox(
            self.quantize_tab,
            values=[
                "Q2_K",
                "Q3_K_S",
                "Q4_0",
                "Q4_1",
                "Q4_K_S",
                "Q5_0",
                "Q5_1",
                "Q5_K_S",
                "Q6_K",
                "Q8_0",
            ],
        )
        self.quant_method.set("Q4_K_S")  # Default value
        self.quant_method.pack(pady=5)

        # Quantize button
        self.quantize_button = ttk.Button(
            self.quantize_tab, text="Quantize", command=self.start_quantization
        )
        self.quantize_button.pack(pady=20)

        # Progress bar
        self.quantize_progress = ttk.Progressbar(
            self.quantize_tab, mode="indeterminate"
        )

    def browse_source(self):
        filename = filedialog.askopenfilename(
            filetypes=[("safetensors files", "*.safetensors")]
        )
        if filename:
            print("Safetensors file detected :", os.path.basename(filename))
            self.sft_file = filename
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, filename)

    def browse_destination(self):
        dest = filedialog.askdirectory()
        if dest:
            self.output_path = dest
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, dest)

    def browse_quant_destination(self):
        dest = filedialog.askdirectory()
        if dest:
            self.output_path = dest
            self.quant_dest_entry.delete(0, tk.END)
            self.quant_dest_entry.insert(0, dest)

    def browse_gguf(self):
        filename = filedialog.askopenfilename(filetypes=[("GGUF files", "*.gguf")])
        if filename:
            print("GGUF file detected :", os.path.basename(filename))
            self.gguf_file = filename
            self.gguf_entry.delete(0, tk.END)
            self.gguf_entry.insert(0, filename)

    def start_conversion(self):
        if not self.source_entry.get() or not self.dest_entry.get():
            messagebox.showerror("Error", "Please select both source and destination")
            return

        self.convert_button.config(text="Processing...", state="disabled")
        self.convert_progress.start()
        self.is_converting = True

        # Simulate conversion in a separate thread
        self.convert_progress.pack(fill="x", padx=5, pady=5)
        thread = threading.Thread(target=self.convert_process)
        thread.start()

    def convert_process(self):
        outputfile = os.path.basename(self.sft_file).replace(
            ".safetensors", "-F16.gguf"
        )
        command = rf'"{PYTHON}" convert.py --src "{self.sft_file}" --dst "{os.path.join(self.output_path,outputfile)}"'

        print("RUNNING : \n" + command)

        with subprocess.Popen(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        ) as sp:
            for line in sp.stdout:
                print(line.strip())
            if sp.poll():
                self.root.after(0, self.error_conversion)
                return

        print("Convert to GGUF completed")

        self.root.after(0, self.finish_conversion)

    def finish_conversion(self):
        self.convert_button.config(text="Convert", state="normal")
        self.convert_progress.stop()
        self.is_converting = False
        messagebox.showinfo("Success", "Conversion completed!")

    def error_conversion(self):
        self.convert_button.config(text="Convert", state="normal")
        self.convert_progress.stop()
        self.is_converting = False
        messagebox.showerror(
            "Error", "An Error has been occur when converting model to GGUF."
        )
        self.convert_progress.forget()

    def start_quantization(self):
        if not self.gguf_entry.get() or not self.quant_dest_entry.get():
            messagebox.showerror(
                "Error", "Please select both GGUF file and destination"
            )
            return

        print("convert to", self.quant_method.get())

        self.quantize_button.config(text="Processing...", state="disabled")
        self.quantize_progress.start()
        self.is_quantizing = True

        # Simulate quantization in a separate thread
        self.quantize_progress.pack(fill="x", padx=5, pady=5)
        thread = threading.Thread(target=self.quantize_process)
        thread.start()

    def quantize_process(self):
        outputfile = os.path.basename(self.gguf_file).replace(
            ".gguf", f"-{self.quant_method.get()}.gguf"
        )
        command = rf'"./llama-quantize/llama-quantize.exe" "{self.gguf_file}" "{os.path.join(self.output_path,outputfile)}" {self.quant_method.get()}'

        print("RUNNING : \n" + command)

        with subprocess.Popen(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        ) as sp:
            for line in sp.stdout:
                print(line.strip())
            if sp.poll():
                self.root.after(0, self.error_conversion)
                return
        print(f"Quantization to {self.quant_method.get()} completed")

        self.root.after(0, self.finish_quantization)

    def finish_quantization(self):
        self.quantize_progress.pack(fill="x", padx=5, pady=5)
        self.quantize_button.config(text="Quantize", state="normal")
        self.quantize_progress.stop()
        self.is_quantizing = False
        self.quantize_progress.forget()
        messagebox.showinfo("Success", "Quantization completed!")


if __name__ == "__main__":
    root = tk.Tk()
    app = GGUFConverterApp(root)
    root.mainloop()
