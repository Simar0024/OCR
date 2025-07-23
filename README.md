# Azure OCR Automation
Project - Extract the handwritten or printed text from images in format that can be useful to get insights from or perform enhancements on top of it. Images should be fetched from input Azure Blob container. Language to be used: Python. JSON Output file should be uploaded to blob in output container. Application should be accessible only on private network. Automate the task that whenever new input image has been uploaded it automatically processes it and generates email alerts after output file has been generated.
This project automates the process of extracting **handwritten or printed text** from images using **Azure AI Vision OCR**. It monitors an Azure Blob Storage container, processes newly uploaded images, stores the extracted text as JSON, and sends email alerts—all within a **private network environment**.

---

## 📦 Features

- ✅ Automatically trigger OCR on new image uploads (JPG, PNG, etc.)
- ✅ Extract printed or handwritten text using Azure AI Vision
- ✅ Upload structured JSON output to an output blob container
- ✅ Send email alerts upon successful processing
- ✅ All resources accessible only from **private networks (VNet)**
- ✅ Written in clean, modular **Python**
- ✅ Scalable via **Azure Functions (Blob Trigger)**

---

## 🧰 Technologies Used

- Python 3.10+
- Azure Functions
- Azure Blob Storage
- Azure AI Vision SDK
- SMTP (Email notifications)
- Azure VNet + Private Endpoints (for security)

---

