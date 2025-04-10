import tempfile
import os
import csv
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# def save_to_csv(data):
#     """
#     Saves the fetched data to a temporary CSV file.
#     Returns the path to the temporary file.
#     """
#     # Create a temporary file
#     # temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode='w', newline='')
#     # temp_csv_path = temp_file.name
#     temp_csv_path = r"C:\Users\vicky\OneDrive\Pictures\Result Chatbot\TempCSV"

#     # Write data to the CSV file
#     writer = csv.writer(temp_file)
#     writer.writerow(["USN", "Name", "SGPA"])
#     writer.writerows(data)

#     # Close the file to release the handle
#     # temp_file.close()

#     print(f"✅ Temporary CSV file saved at: {temp_csv_path}")
#     return temp_csv_path


def save_to_csv(data, filename="temp_data.csv"):
    """
    Saves the fetched data to a CSV file.
    """
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["USN", "Name", "SGPA"])
        writer.writerows(data)

    print(f"✅ Temporary CSV file saved at: {filename}")
    return filename



def create_pdf_from_dataframe(df):
    """
    Creates a PDF from a pandas DataFrame using reportlab.
    """
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    table_data = [df.columns.tolist()] + df.values.tolist()
    table = Table(table_data, colWidths=[2.5 * inch, 4 * inch, 1 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))

    elements.append(table)
    pdf.build(elements)
    buffer.seek(0)
    return buffer

def delete_temp_file(file_path):
    """
    Deletes the temporary file.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"✅ Temporary file {file_path} deleted successfully!")
    else:
        print(f"❌ Temporary file {file_path} does not exist.")