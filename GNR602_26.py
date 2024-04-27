import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from skimage import io, color
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering
import os

class ImageSegmentationApp:
    def __init__(self, root):
        # setting up environment of GUI including all buttons, labels and progress bar 
        self.upload_path = ' '
        self.save_path = ' '
        self.root = root
        self.root.title("Image Segmentation GUI")
        self.clusters_number = 5

        # labels in GUI
        self.label = tk.Label(root, text="Image Segmentation using Hierarchical Clustering", font=("Arial", 16, "bold"), pady=10) 
        self.label.grid(row = 1, column= 2, columnspan= 8)

        # Buttons in GUI
        self.upload_button = tk.Button(root, text="Upload Image", command=self.upload_image)
        self.upload_button.grid(row = 2, column = 2)

        self.save_button = tk.Button(root, text="Save Output", command=self.save_output, state=tk.NORMAL)
        self.save_button.grid(row = 3, column = 2)

        self.cluster_label = tk.Label(root, text="Enter number of clusters (default 5)")
        self.cluster_label.grid(row = 4, column = 2)

        self.start_button = tk.Button(root, text="Start Segmentation", command=self.start_segmentation, state=tk.DISABLED)
        self.start_button.grid(row = 5, column = 2)

        # progress bar in GUI
        self.progress = ttk.Progressbar(root, mode = 'determinate', length=200)
        self.progress.grid(row = 8, column = 2)

        # input for number of clusters with default 
        self.display_cluster_number = tk.Label(self.root)
        self.display_cluster_number.grid(row = 6, column = 2)
        self.ent = tk.Label(root, text="Upload image")
        self.ent.grid(row = 7, column = 2)

        self.clusters = tk.Entry(root)
        self.clusters.grid(row = 4, column = 4)

        # Image display as thumbnail in GUI
        self.original_image = tk.Label(self.root)
        self.original_image.grid(row = 2, column = 6, rowspan=5)

        self.segmented_image = tk.Label(self.root)
        self.segmented_image.grid(row = 2, column = 8, rowspan=5)

        self.original_image_label = tk.Label(self.root)
        self.original_image_label.grid(row = 7, column = 6)

        self.segmented_image_label = tk.Label(self.root)
        self.segmented_image_label.grid(row = 7, column = 8)

    def upload_image(self):
        # function to uploa image
        file_path = filedialog.askopenfilename(title="Select Image File",
                                               filetypes=(("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")))
        if file_path:
            self.image = Image.open(file_path)
            self.upload_path = file_path

            # display feedback thumbnail of image
            self.image.thumbnail((400, 400))
            self.image_tk = ImageTk.PhotoImage(self.image)
            self.original_image.config(image=self.image_tk)
            self.original_image_label.config(text='Original image')

            # updating progress label
            self.ent.config(text='Select output location')

            # self.save_button.config(state=tk.NORMAL)

    def save_output(self):
            # function to save file location with reference name as intput file name
            file_path = filedialog.asksaveasfilename(title="Save Segmented Image As", initialfile= os.path.basename(self.upload_path)[0:-4] + "_segmented.png", filetypes=(("PNG files", "*.png"), ("All files", "*.*")))
            if file_path:
                self.save_path = file_path

                #updating labels and Enabling sstart button
                self.ent.config(text='Ready to start')
                self.start_button.config(state=tk.NORMAL)
    
    def start_segmentation(self):
        if hasattr(self, 'image'):
            # try except loop to check for rrors
            try:
                #checking for input of cluster numbe
                if len(self.clusters.get()) > 0:
                    self.clusters_number = int(self.clusters.get())

                # displaying cluster number
                self.display_cluster_number.config(text='Number of clusters: ' + str(self.clusters_number))

                # disabling buttons while processing image
                self.save_button.config(state=tk.DISABLED)
                self.upload_button.config(state=tk.DISABLED)

                #updating label
                self.ent.config(text='Processing image ...')

                # reading input image and converting to 2d array using reshape
                image_array = io.imread(self.upload_path)
                height, width, channels = image_array.shape
                image_2d = image_array.reshape((height * width, channels))

                # updating progress bar
                self.progress['value'] = 30
                self.root.update_idletasks()
                self.ent.config(text='Segmenting...')
                n_clusters = self.clusters_number 

                # agglo = model.AgglomerativeClustering(k=n_clusters, initial_k=25)
                # agglo.fit(image_2d)
                # seg_img = [[agglo.predict_center(list(pixel)) for pixel in row] for row in image_array]
                # seg_img = np.array(seg_img, np.uint8)

                # performing clustering using Sklearn
                clustering = AgglomerativeClustering(n_clusters=n_clusters).fit(image_2d)

                # extracting labels of clusters
                labels = clustering.labels_.reshape((height, width))

                # converting original image to extract colours of clusters
                image_lab = color.rgb2lab(image_array)
                segmented_image_lab = np.zeros_like(image_lab)

                # assigning color to each cluster
                for label in np.unique(labels):
                    mask = labels == label
                    mean_color = np.mean(image_lab[mask], axis=0)
                    segmented_image_lab[mask] = mean_color

                # Convert the segmented image back to RGB color space
                segmented_image_rgb = color.lab2rgb(segmented_image_lab)

                # plotting results
                plt.figure(figsize=(8, 6))
                # plt.imshow(seg_img)
                # plt.imshow(labels, cmap='viridis')
                plt.imshow(segmented_image_rgb)
                plt.axis('off')
                plt.title('Segmented Image')
                # plt.colorbar()
                plt.savefig(self.save_path)

                # plotting segmented image thumbnanil in GUI
                self.segmented_image_read = Image.open(self.save_path)
                self.segmented_image_read.thumbnail((400, 400))
                self.segmented_image_tk = ImageTk.PhotoImage(self.segmented_image_read)
                self.segmented_image.config(image=self.segmented_image_tk)
                self.segmented_image_label.config(text="Segmented image")

                # updating labels, eabling buttons
                self.progress['value'] = 100
                self.root.update_idletasks()
                self.save_button.config(state=tk.NORMAL)
                self.upload_button.config(state=tk.NORMAL)
                self.ent.config(text='Completed!')
                messagebox.showinfo("Success", "Segmented image saved successfully!")
            except:
                messagebox.showinfo("ERROR", "Check terminal")
                self.save_button.config(state=tk.NORMAL)
                self.upload_button.config(state=tk.NORMAL)
                self.ent.config(text='Error!')

root = tk.Tk()
root.geometry("1000x500")
app = ImageSegmentationApp(root)
root.mainloop()
