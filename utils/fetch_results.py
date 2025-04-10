import requests
import fitz  # PyMuPDF
import re
import concurrent.futures
from io import BytesIO

def fetch_pdf(usn, branch, year):
    formatted_usn = f"{int(usn):03d}"
    usn_full = f"1ds{year}{branch}{formatted_usn}"
    url = f"http://14.99.184.178:8080/birt/frameset?__report=mydsi/exam/Exam_Result_Sheet_dsce.rptdesign&__format=pdf&USN={usn_full}"

    response = requests.get(url)
    if response.status_code == 200:
        pdf_stream = BytesIO(response.content)
        text = extract_text_from_pdf(pdf_stream)
        usn, name, sgpa = parse_details(text)
        return (usn_full, name, sgpa) if usn != "N/A" else None
    return None

def extract_text_from_pdf(pdf_stream):
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    text = "\n".join(page.get_text("text") for page in doc)
    return text if text.strip() else "N/A"

def parse_details(text):
    if text == "N/A":
        return "N/A", "N/A", "N/A"

    usn_match = re.search(r"USN / Roll No:\s*(\S+)", text, re.IGNORECASE)
    name_match = re.search(r"Name of the Student:\s*(.*?)\n", text, re.IGNORECASE)
    sgpa_match = re.search(r"SGPA\s*[:=-]?\s*(\d+(?:\.\d+)?)", text, re.IGNORECASE)

    usn = usn_match.group(1) if usn_match else "N/A"
    name = name_match.group(1).strip() if name_match else "N/A"
    sgpa = sgpa_match.group(1) if sgpa_match else "N/A"

    return usn, name, sgpa

def process_usn(usn, year, branches):
    results = []
    for branch in branches:
        result = fetch_pdf(usn, branch, year)
        if result:
            results.append(result)
    return results

def fetch_results(year, selected_branches, usn_range, diploma_usn_range, progress_bar, progress_text):
    usn_list = [f"{i:03d}" for i in range(usn_range[0], usn_range[1] + 1)]
    diploma_usn_list = [f"{i:03d}" for i in range(diploma_usn_range[0], diploma_usn_range[1] + 1)]
    total_tasks = len(usn_list) * len(selected_branches) + len(diploma_usn_list) * len(selected_branches)
    all_results = {}
    completed_tasks = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(process_usn, usn, year, selected_branches): usn for usn in usn_list}
        futures.update({executor.submit(process_usn, usn, year + 1, selected_branches): usn for usn in diploma_usn_list})

        for future in concurrent.futures.as_completed(futures):
            usn = futures[future]
            result = future.result()
            
            if result:
                for result_tuple in result:
                    if usn not in all_results:
                        all_results[usn] = []
                    all_results[usn].append(result_tuple)
            completed_tasks += len(selected_branches)
            progress = completed_tasks / total_tasks
            progress_bar.progress(progress)
            progress_text.text(f"Progress: {int(progress * 100)}%")

    merged_data = []
    for usn, results in all_results.items():
        if results:
            name = ""
            sgpa = ""
            usn_full = ""
            for result_tuple in results:
                usn_full = result_tuple[0]
                if name == "":
                    name = result_tuple[1]
                if result_tuple[2] != "N/A":
                    sgpa = result_tuple[2]

            merged_data.append([usn_full, name, sgpa])

    all_results = sorted(merged_data, key=lambda x: int(re.search(r'\d+$', x[0]).group()))
    return all_results