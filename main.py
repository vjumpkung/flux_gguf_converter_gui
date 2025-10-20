import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import shlex
import os
import sys
import wget
import zipfile

PYTHON = sys.executable
zip_file_name = "sd-master-64a7698-bin-win-noavx-x64.zip"
folder_name = "sd-master-64a7698-bin-win-noavx-x64"


def extract_zip(zip_path, extract_to=None):
    """
    Extract a zip file to the specified directory.
    If no directory is specified, extract to the same location as the zip file.
    """
    # If no extraction path is provided, extract to a folder with the same name as the zip
    if extract_to is None:
        extract_to = os.path.splitext(zip_path)[0]

    # Create the extraction directory if it doesn't exist
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    # Extract the zip file
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        print(f"Extracting {zip_path} to {extract_to}...")
        zip_ref.extractall(extract_to)
        print(f"Extraction complete. Files extracted to: {extract_to}")


class GGUFConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Convert .safetensors to .gguf")
        self.root.geometry("600x300")
        self.root.resizable(False, False)

        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=5)

        # Create tabs
        self.convert_tab = ttk.Frame(self.notebook)
        self.quantize_tab = ttk.Frame(self.notebook)

        # Add tabs to notebook
        self.notebook.add(self.quantize_tab, text="Quantization to GGUF")

        # Initialize tabs
        self.setup_quantize_tab()

        # Processing flags
        self.is_converting = False
        self.is_quantizing = False

        # Filestate
        self.sft_file = ""
        self.gguf_file = ""
        self.output_path = ""

    def setup_quantize_tab(self):
        # .safetensors file selection
        ttk.Label(self.quantize_tab, text="Source File (.safetensors):").pack(pady=5)
        self.source_frame = ttk.Frame(self.quantize_tab)
        self.source_frame.pack(fill="x", padx=5)

        self.source_entry = ttk.Entry(self.source_frame)
        self.source_entry.pack(side="left", expand=True, fill="x", padx=(0, 5))

        ttk.Button(self.source_frame, text="Browse", command=self.browse_source).pack(
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
                "f32",
                "f16",
                "q4_0",
                "q4_1",
                "q5_0",
                "q5_1",
                "q8_0",
                "q2_K",
                "q3_K",
                "q4_K",
                "q5_K",
                "q6_K",
                "iq2_xxs",
                "iq2_xs",
                "iq3_xxs",
                "iq1_s",
                "iq4_nl",
                "iq3_s",
                "iq2_s",
                "iq4_xs",
                "iq1_m",
                "bf16",
                "tq1_0",
                "tq2_0",
            ],
        )
        self.quant_method.set("q4_0")  # Default value
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

    def finish_conversion(self):
        self.convert_button.config(text="Convert", state="normal")
        self.convert_progress.stop()
        self.is_converting = False
        messagebox.showinfo("Success", "Conversion completed!")

    def start_quantization(self):
        if not self.source_entry.get() or not self.quant_dest_entry.get():
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
        outputfile = os.path.basename(self.sft_file).replace(
            ".safetensors", f"-{self.quant_method.get()}.gguf"
        )
        command = rf'"./{folder_name}/sd.exe" -M convert -m "{self.sft_file}" -o "{os.path.join(self.output_path,outputfile)}" -v --type {self.quant_method.get()}'

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

    def error_conversion(self):
        self.convert_button.config(text="Convert", state="normal")
        self.convert_progress.stop()
        self.is_converting = False
        messagebox.showerror(
            "Error", "An Error has been occur when converting model to GGUF."
        )
        self.convert_progress.forget()

    def finish_quantization(self):
        self.quantize_progress.pack(fill="x", padx=5, pady=5)
        self.quantize_button.config(text="Quantize", state="normal")
        self.quantize_progress.stop()
        self.is_quantizing = False
        self.quantize_progress.forget()
        messagebox.showinfo("Success", "Quantization completed!")


if __name__ == "__main__":

    try:
        if not os.path.exists(folder_name):
            filename = wget.download(
                "https://github.com/leejet/stable-diffusion.cpp/releases/download/master-333-64a7698/sd-master-64a7698-bin-win-noavx-x64.zip"
            )
            # extract here
            zip_file = zip_file_name
            extract_zip(zip_file)
            os.remove(zip_file)
    except FileNotFoundError:
        print("skip downloading")

    root = tk.Tk()
    app = GGUFConverterApp(root)
    root.mainloop()
