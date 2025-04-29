import streamlit as st
import pdfplumber
import pyodbc
import json
import os
from io import BytesIO
import re

# --- Streamlit Page Setup ---
st.set_page_config(page_title="AVIS Invoice Processor", layout="centered")
st.title("AVIS Invoice Processor")
st.markdown("Extract data from PDFs ➡️ Insert customer/supplier info into SQL Server.")

# --- Helper Functions ---
def find_gstin(text):
    gst_patterns = [
        r"GSTIN\s*\(.*?\)\s*:\s*([0-9A-Z]{15})",
        r"GSTIN\s*:\s*([0-9A-Z]{15})",
        r"GST\s*NO\s*:\s*([0-9A-Z]{15})",
    ]
    for pattern in gst_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def parse_address_block(block_text, is_customer=True):
    lines = [line.strip() for line in block_text.strip().split("\n") if line.strip()]
    
    name = lines[1] if len(lines) > 1 else None
    name = name.strip() if name else None

    if name:
        address_text = "\n".join(lines[2:])
        address_text = re.sub(f"^{re.escape(name)}", "", address_text).strip()

    state_line = next((line for line in lines if "STATE CODE" in line.upper()), None)
    state_code = None
    if state_line:
        if ":" in state_line:
            state_code = state_line.split(":")[-1].strip()
        elif "." in state_line:
            state_code = state_line.split(".")[-1].strip()
        else:
            state_code = state_line.strip().replace("STATE CODE", "").strip()

    start = 2
    end = next((i for i, line in enumerate(lines) if "STATE CODE" in line.upper()), len(lines))
    address = ", ".join(lines[start:end])

    if not is_customer and "AVIS" in address:
        return None

    return {
        "CUST_NAME": name,
        "ADDRESS": address,
        "STATE_CODE_NO": state_code
    }

def extract_pdf_data(uploaded_pdf):
    all_data = []

    try:
        with pdfplumber.open(uploaded_pdf) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_data = {}
                text = page.extract_text()

                bill_to_block = None
                ship_to_block = None
                gst_no = None

                if text:
                    gst_no = find_gstin(text)
                    lines = text.split('\n')
                    current_block = ""
                    is_bill_to = False
                    is_ship_to = False

                    for line in lines:
                        if "BILL TO" in line.upper():
                            is_bill_to = True
                            is_ship_to = False
                            current_block = line + "\n"
                        elif "SHIP TO" in line.upper():
                            is_ship_to = True
                            is_bill_to = False
                            current_block = line + "\n"
                        elif is_bill_to:
                            current_block += line + "\n"
                        elif is_ship_to:
                            current_block += line + "\n"

                        if "STATE CODE" in line.upper():
                            if is_bill_to:
                                bill_to_block = current_block
                                is_bill_to = False
                            elif is_ship_to:
                                ship_to_block = current_block
                                is_ship_to = False

                if bill_to_block:
                    bill_to = parse_address_block(bill_to_block, is_customer=True)
                    if bill_to:
                        bill_to["GST_NO"] = gst_no
                    page_data["BILL_TO"] = bill_to

                if ship_to_block:
                    ship_to = parse_address_block(ship_to_block, is_customer=False)
                    page_data["SHIP_TO"] = ship_to

                if not ship_to_block:
                    page_data["SHIP_TO"] = None

                if page_data:
                    all_data.append(page_data)

                st.write(f"📄 Page {page_num + 1}: Extracted Data - {page_data}")

    except Exception as e:
        st.error(f"❌ Error processing PDF: {e}")

    return all_data

def insert_customer_data(customer_data):
    try:
        conn = pyodbc.connect('DSN=AVIS_MAIN_DSN;DATABASE=AVIS_MAIN;Trusted_Connection=yes')
        cursor = conn.cursor()

        cursor.execute("SELECT MAX(CUST_ID) FROM [dbo].[cust_details]")
        latest_id = cursor.fetchone()[0]

        if latest_id:
            latest_num = int(latest_id.replace("C_", "")) + 1
        else:
            latest_num = 100

        new_cust_id = f"C_{latest_num:08d}"

        insert_query = """
        INSERT INTO [dbo].[cust_details] (
            CUST_ID, CUST_NAME, CUST_BILL_ADD, CUST_SHIP_ADD,
            CUST_CONTACT, CUST_EMAIL_ID, CUST_GST_NO, CUST_STATE_CODE_NO
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(
            insert_query,
            new_cust_id,
            customer_data.get("CUST_NAME"),
            customer_data.get("CUST_BILL_ADD"),
            customer_data.get("CUST_SHIP_ADD"),
            None,
            None,
            customer_data.get("CUST_GST_NO"),
            customer_data.get("CUST_STATE_CODE_NO")
        )

        conn.commit()
        conn.close()

        return new_cust_id

    except Exception as e:
        st.error(f"❌ Database Error: {e}")
        return None

def extract_all_text_from_pdf(uploaded_pdf):
    all_text = []

    try:
        with pdfplumber.open(uploaded_pdf) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_data = {}
                text = page.extract_text()

                if text:
                    page_data["page_number"] = page_num + 1
                    page_data["text"] = text.strip()
                else:
                    page_data["page_number"] = page_num + 1
                    page_data["text"] = "No text found on this page."

                all_text.append(page_data)
                st.write(f"📄 Page {page_num + 1}: Extracted Text - {text[:300]}...")

    except Exception as e:
        st.error(f"❌ Error processing PDF: {e}")

    return all_text

def insert_supplier_data(supplier_data):
    try:
        conn = pyodbc.connect('DSN=AVIS_MAIN_DSN;DATABASE=AVIS_MAIN;Trusted_Connection=yes')
        cursor = conn.cursor()

        cursor.execute("SELECT MAX(SUP_ID) FROM [dbo].[sup_details]")
        latest_id = cursor.fetchone()[0]

        if latest_id:
            latest_num = int(latest_id.replace("S_", "")) + 1
        else:
            latest_num = 100

        new_sup_id = f"S_{latest_num:08d}"

        insert_query = """
        INSERT INTO [dbo].[sup_details] (
            SUP_ID, SUP_NAME, SUP_BILL_ADD, SUP_SHIP_ADD,
            SUP_CONTACT, SUP_EMAIL_ID, SUP_GST_NO, SUP_STATE_CODE_NO
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(
            insert_query,
            new_sup_id,
            supplier_data.get("SUP_NAME"),
            supplier_data.get("SUP_BILL_ADD"),
            supplier_data.get("SUP_SHIP_ADD"),
            None,
            None,
            supplier_data.get("SUP_GST_NO"),
            supplier_data.get("SUP_STATE_CODE_NO")
        )

        conn.commit()
        conn.close()

        return new_sup_id

    except Exception as e:
        st.error(f"❌ Database Error: {e}")
        return None

# --- NEW Supplier Parsing ---
def parse_supplier_from_text(raw_text):
    supplier_data = {
        "SUP_NAME": None,
        "SUP_BILL_ADD": None,
        "SUP_SHIP_ADD": None,
        "SUP_CONTACT": None,
        "SUP_EMAIL_ID": None,
        "SUP_GST_NO": None,
        "SUP_STATE_CODE_NO": None
    }

    lines = raw_text.split('\n')
    capture = False
    supplier_lines = []

    for line in lines:
        if 'Supplier (Bill from)' in line:
            capture = True
            continue
        if capture:
            if 'State Name' in line or 'Description of Goods' in line or 'Sl Description' in line:
                break
            supplier_lines.append(line.strip())

    if supplier_lines:
        if len(supplier_lines) >= 1:
            supplier_data["SUP_NAME"] = supplier_lines[0]
        if len(supplier_lines) > 1:
            supplier_data["SUP_BILL_ADD"] = ", ".join(supplier_lines[1:])

    gst_match = re.search(r'GSTIN\s*[:\-]?\s*([0-9A-Z]{15})', raw_text)
    if gst_match:
        supplier_data["SUP_GST_NO"] = gst_match.group(1)

    return supplier_data

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(
    ["📄 Extract PDF to JSON", "🛢️ Insert JSON to SQL Server", "📄 Extract All Text from Purchase Invoice PDF", "🛢️ Insert Supplier Data from JSON"]
)

# ------------------ TAB 1 ------------------
with tab1:
    st.header("📄 Extract PDF Invoice to JSON File")
    uploaded_pdfs = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

    if uploaded_pdfs:
        for uploaded_pdf in uploaded_pdfs:
            file_name = uploaded_pdf.name
            base_name, _ = os.path.splitext(file_name)
            st.write(f"📄 Processing: `{file_name}`")

            extracted_data = extract_pdf_data(uploaded_pdf)

            if extracted_data:
                output = BytesIO()
                output.write(json.dumps(extracted_data, indent=4).encode('utf-8'))
                output.seek(0)
                json_file_name = f"{base_name}.json"

                st.success(f"✅ Extracted data from `{file_name}`")
                st.download_button(
                    label=f"📥 Download JSON for {file_name}",
                    data=output,
                    file_name=json_file_name,
                    mime="application/json"
                )
            else:
                st.warning(f"⚠️ No data extracted from `{file_name}`.")

# ------------------ TAB 2 ------------------
with tab2:
    st.header("🛢️ Insert Customer Data from JSON to SQL Server")
    uploaded_json = st.file_uploader("Upload JSON File", type=["json"], key="json_upload")

    if uploaded_json:
        try:
            extracted_data = json.load(uploaded_json)

            if isinstance(extracted_data, list):
                for page_data in extracted_data:
                    bill_to = page_data.get("BILL_TO")
                    ship_to = page_data.get("SHIP_TO")

                    if bill_to:
                        customer_data = {
                            "CUST_NAME": bill_to.get("CUST_NAME"),
                            "CUST_BILL_ADD": bill_to.get("ADDRESS"),
                            "CUST_SHIP_ADD": ship_to.get("ADDRESS") if ship_to else None,
                            "CUST_GST_NO": bill_to.get("GST_NO"),
                            "CUST_STATE_CODE_NO": bill_to.get("STATE_CODE_NO")
                        }

                        st.subheader(f"📌 Customer Details")
                        st.write(customer_data)

                        if st.button(f"🚀 Insert {customer_data['CUST_NAME']}", key=customer_data['CUST_NAME']):
                            inserted_id = insert_customer_data(customer_data)
                            if inserted_id:
                                st.success(f"✅ Inserted with CUST_ID: `{inserted_id}`")

            else:
                st.error("❌ Invalid JSON structure.")

        except Exception as e:
            st.error(f"❌ Error reading JSON: {e}")

# ------------------ TAB 3 ------------------
with tab3:
    st.header("📄 Extract All Text from Purchase Invoice PDF")
    uploaded_purchase_pdf = st.file_uploader("Upload Purchase Invoice PDF", type=["pdf"], key="purchase_pdf")

    if uploaded_purchase_pdf:
        extracted_text_data = extract_all_text_from_pdf(uploaded_purchase_pdf)

        if extracted_text_data:
            output = BytesIO()
            output.write(json.dumps(extracted_text_data, indent=4).encode('utf-8'))
            output.seek(0)
            purchase_json_file_name = f"{os.path.splitext(uploaded_purchase_pdf.name)[0]}_purchase_text.json"

            st.success(f"✅ Extracted all text from purchase invoice")
            st.download_button(
                label=f"📥 Download Purchase Invoice Text JSON",
                data=output,
                file_name=purchase_json_file_name,
                mime="application/json"
            )
        else:
            st.warning("⚠️ No text extracted from the uploaded purchase invoice PDF.")

# ------------------ TAB 4 ------------------
with tab4:
    st.header("🛢️ Insert Supplier Data from JSON to SQL Server")
    uploaded_supplier_json = st.file_uploader("Upload Supplier JSON File", type=["json"], key="supplier_json_upload")

    if uploaded_supplier_json:
        try:
            extracted_data = json.load(uploaded_supplier_json)

            if isinstance(extracted_data, list):
                for page_data in extracted_data:
                    text = page_data.get("text")

                    if text:
                        supplier_info = parse_supplier_from_text(text)

                        st.subheader(f"📌 Supplier Details")
                        st.write(supplier_info)

                        if supplier_info["SUP_NAME"]:
                            if st.button(f"🚀 Insert {supplier_info['SUP_NAME']}", key=f"insert_{supplier_info['SUP_NAME']}_{page_data['page_number']}"):
                                inserted_id = insert_supplier_data(supplier_info)
                                if inserted_id:
                                    st.success(f"✅ Inserted with SUP_ID: `{inserted_id}`")
                        else:
                            st.warning("⚠️ Supplier Name not found.")

            else:
                st.error("❌ Invalid JSON structure.")

        except Exception as e:
            st.error(f"❌ Error reading JSON: {e}")
