import base64
from datetime import datetime
import io
import json
import os
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Novalink Telephony Quotation",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Authentication Gate
def check_password():
    """Returns True if user enters the correct password."""
    if st.session_state.get("authenticated", False):
        return True

    configured_password = st.secrets.get("APP_PASSWORD", "araconnect")

    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="background: #FFFFFF; padding: 2.2rem; border-radius: 14px; border: 1px solid #CBD5E1; text-align: center; box-shadow: 0 4px 12px rgba(15,90,115,0.08);">
                <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">🔒</div>
                <h3 style="color: #0F5A73; margin: 0 0 0.5rem 0; font-weight: 800;">Authorised Access Only</h3>
                <p style="color: #64748B; font-size: 0.9rem; margin-bottom: 1.5rem;">Please enter your reseller access key to launch the Novalink Telephony Quotation tool.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            password_attempt = st.text_input("Access Password", type="password", placeholder="Enter password...")
            submitted = st.form_submit_button("Unlock Portal", use_container_width=True)

            if submitted:
                if password_attempt == configured_password:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Incorrect password. Please try again.")

    return False


if not check_password():
    st.stop()


# 3. Base64 Image Encoder
@st.cache_data
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode("utf-8")
            ext = os.path.splitext(image_path)[1].lower().replace(".", "")
            if ext == "jpg":
                ext = "jpeg"
            return f"data:image/{ext};base64,{encoded}"
    return None


# 4. High-Contrast Styles + Strict Card Boundaries
st.markdown(
    """
    <style>
    :root {
        --text-color: #0F172A !important;
        --background-color: #F8FAFC !important;
        --secondary-background-color: #FFFFFF !important;
        --primary-color: #0F5A73 !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    p, span, label, h1, h2, h3, h4, h5, h6, li, td, th {
        color: #0F172A !important;
    }

    /* Popup Toast Fix */
    div[data-testid="stToast"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #0F5A73 !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 25px -5px rgba(15, 90, 115, 0.25), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
        padding: 0.85rem 1.1rem !important;
    }
    div[data-testid="stToast"] * {
        color: #0F172A !important;
    }
    div[data-testid="stToast"] p {
        color: #0F172A !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }
    div[data-testid="stToast"] button {
        color: #64748B !important;
    }
    div[data-testid="stToast"] button:hover {
        color: #0F172A !important;
    }
    div[data-testid="stToast"] svg {
        fill: #0F172A !important;
        stroke: #0F172A !important;
    }

    /* Tabs Styling */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        padding: 12px 28px !important;
    }
    button[data-baseweb="tab"] div, 
    button[data-baseweb="tab"] p {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        color: #64748B !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        border-bottom: 3.5px solid #0F5A73 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] div,
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #0F5A73 !important;
    }

    /* Section Subheadings */
    .section-headline {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0F5A73 !important;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* 🚨 ROCK SOLID CARD CONTAINER FIX 🚨 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 14px !important;
        padding: 1.15rem !important;
        margin-bottom: 1.5rem !important;
        box-shadow: 0 4px 10px rgba(15, 90, 115, 0.06) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #0F5A73 !important;
        box-shadow: 0 8px 20px -2px rgba(15, 90, 115, 0.14) !important;
        transform: translateY(-2px);
    }

    /* Card Badge */
    .card-badge {
        font-size: 0.7rem;
        font-weight: 700;
        color: #0F5A73 !important;
        background: #F0F9FF;
        border: 1px solid #BAE6FD;
        padding: 3px 8px;
        border-radius: 6px;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Stepper Styling */
    .qty-display {
        font-size: 1.15rem;
        font-weight: 800;
        color: #0F172A !important;
        text-align: center;
        background: #F8FAFC;
        border: 1.5px solid #CBD5E1;
        border-radius: 8px;
        padding: 0.4rem 0;
        min-width: 44px;
    }

    /* Text Inputs */
    div[data-testid="stTextInput"] div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stTextInput"] input {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        background-color: #FFFFFF !important;
        font-weight: 500 !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: #94A3B8 !important;
        -webkit-text-fill-color: #94A3B8 !important;
    }

    /* Expander Container */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #0F5A73 !important;
        border-radius: 12px !important;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(15, 90, 115, 0.05);
    }
    div[data-testid="stExpander"] summary {
        background-color: #F8FAFC !important;
        padding: 0.85rem 1.25rem !important;
    }
    div[data-testid="stExpander"] summary svg {
        fill: #0F5A73 !important;
    }
    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] summary span {
        color: #0F5A73 !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
    }

    /* Action Buttons */
    .stButton > button,
    div[data-testid="stFormSubmitButton"] > button,
    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #0F5A73 0%, #164E63 100%) !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        border: none !important;
        padding: 0.45rem 1rem !important;
        box-shadow: 0 2px 6px rgba(15, 90, 115, 0.2) !important;
    }
    .stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover,
    div[data-testid="stDownloadButton"] > button:hover {
        box-shadow: 0 4px 10px rgba(15, 90, 115, 0.3) !important;
    }
    .stButton > button p,
    div[data-testid="stFormSubmitButton"] > button p,
    div[data-testid="stDownloadButton"] > button p,
    .stButton > button span,
    div[data-testid="stFormSubmitButton"] > button span,
    div[data-testid="stDownloadButton"] > button span {
        color: #FFFFFF !important;
    }

    /* Form Container */
    .stForm {
        background-color: #FFFFFF !important;
        border-radius: 16px !important;
        border: 1px solid #E2E8F0 !important;
        padding: 2.25rem !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.04) !important;
    }

    /* KPI Summary Cards */
    .vat-kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
    }
    .vat-kpi-title {
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748B;
        margin-bottom: 0.5rem;
    }
    .vat-kpi-ex {
        font-size: 1.7rem;
        font-weight: 800;
        color: #0F5A73;
        line-height: 1.1;
    }
    .vat-kpi-inc {
        font-size: 0.95rem;
        font-weight: 700;
        color: #334155;
        margin-top: 0.35rem;
    }

    /* Content Box */
    .section-box {
        background: #FFFFFF;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        padding: 1.75rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
    }

    /* Native Markdown Tables */
    table {
        width: 100% !important;
        border-collapse: collapse !important;
        margin: 0.75rem 0 1.5rem 0 !important;
        border-radius: 8px;
        overflow: hidden;
    }
    th {
        background-color: #0F5A73 !important;
        color: #FFFFFF !important;
        padding: 12px 14px !important;
        text-align: left !important;
        font-size: 0.9rem !important;
    }
    td {
        padding: 12px 14px !important;
        border-bottom: 1px solid #E2E8F0 !important;
        color: #0F172A !important;
        font-size: 0.9rem !important;
    }
    tr:nth-child(even) td {
        background-color: #F8FAFC !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 5. Full Hardware & Accessories Catalogue
LICENCE_MONTHLY_RATE = 7.00
ACTIVATION_FEE_PER_USER = 25.00
VAT_RATE = 0.20
CATALOGUE_FILE = "catalogue.json"

_FALLBACK_PRODUCTS = [
    # --- Fanvil Core Series ---
    {
        "id": "v67",
        "category": "Fanvil Phones",
        "tag": "Flagship Touch",
        "name": "Fanvil Executive V67",
        "desc": "7-inch adjustable touch screen with HD video, built-in Wi-Fi & Bluetooth",
        "image": "Fanvil V67.webp",
        "price": 189.00,
    },
    {
        "id": "v66pro",
        "category": "Fanvil Phones",
        "tag": "Executive Audio",
        "name": "Fanvil Premium V66 Pro",
        "desc": "Multi-line executive audio console with dual-screen colour display and Gigabit PoE",
        "image": "V66 Pro.webp",
        "price": 129.00,
    },
    {
        "id": "v62pro",
        "category": "Fanvil Phones",
        "tag": "Standard Desk",
        "name": "Fanvil Essential V62 Pro",
        "desc": "High-durability office desktop phone with 6 SIP lines and crystal-clear HD audio",
        "image": "Fanvil V62 Pro.png",
        "price": 89.00,
    },
    {
        "id": "w620w",
        "category": "Cordless DECT",
        "tag": "Rugged Cordless",
        "name": "Linkvil Rugged W620W",
        "desc": "IP67 waterproof & drop-proof wireless roaming handset with 15h talk time",
        "image": "Linkvil W620W Rugged.png",
        "price": 149.00,
    },
    # --- Yealink T-Series Prime Desk Phones ---
    {
        "id": "t73w",
        "category": "Yealink Phones",
        "tag": "Smart Business",
        "name": "Yealink T73W",
        "desc": "Entry-level executive IP desk phone with dual-band Wi-Fi and Bluetooth",
        "image": "Yealink T73W.png",
        "price": 78.00,
    },
    {
        "id": "t74w",
        "category": "Yealink Phones",
        "tag": "Colour Executive",
        "name": "Yealink T74W",
        "desc": "High-performance business phone with colour screen and integrated wireless",
        "image": "Yealink T74W.png",
        "price": 111.00,
    },
    {
        "id": "t85w",
        "category": "Yealink Phones",
        "tag": "Gigabit Console",
        "name": "Yealink T85W",
        "desc": "Advanced desktop console with colour display, Optima HD voice & USB expansion",
        "image": "Yealink T85W.png",
        "price": 115.00,
    },
    {
        "id": "t87w",
        "category": "Yealink Phones",
        "tag": "Executive Touch",
        "name": "Yealink T87W",
        "desc": "Large touchscreen IP phone engineered for managers and knowledge workers",
        "image": "Yealink T87W.png",
        "price": 155.00,
    },
    {
        "id": "t88w_pro",
        "category": "Yealink Phones",
        "tag": "Flagship Touch Pro",
        "name": "Yealink T88W Pro",
        "desc": "Premium smart media touch console with ultra-fast UI and full video support",
        "image": "Yealink T88W Pro.png",
        "price": 225.00,
    },
    # --- Yealink Cordless DECT & Roaming ---
    {
        "id": "w74p",
        "category": "Cordless DECT",
        "tag": "DECT Package",
        "name": "Yealink W74P",
        "desc": "High-performance DECT cordless phone system including base station & handset",
        "image": "Yealink W74P.png",
        "price": 87.00,
    },
    {
        "id": "ax83h",
        "category": "Cordless DECT",
        "tag": "Commercial DECT",
        "name": "Yealink AX83H",
        "desc": "Slim, modern cordless business handset for active office environments",
        "image": "Yealink AX83H.png",
        "price": 75.00,
    },
    {
        "id": "ax86r",
        "category": "Cordless DECT",
        "tag": "Rugged DECT",
        "name": "Yealink AX86R",
        "desc": "Heavy-duty shockproof and water-resistant rugged handset for site roaming",
        "image": "Yealink AX86R.png",
        "price": 113.00,
    },
    # --- Headsets & Accessories ---
    {
        "id": "uh36_mono",
        "category": "Headsets & Accessories",
        "tag": "UC Headset",
        "name": "Yealink UH36 Mono Headset UC",
        "desc": "Noise-cancelling professional USB/3.5mm wired mono headset with inline controller",
        "image": "Yealink UH36 Mono Headset UC.png",
        "price": 42.00,
    },
    {
        "id": "psu_10w",
        "category": "Headsets & Accessories",
        "tag": "Power Supply",
        "name": "Yealink 10W PSU",
        "desc": "Official UK 10W mains power adapter for non-PoE network deployments",
        "image": "Yealink 10W PSU.png",
        "price": 11.00,
    },
]


@st.cache_data(ttl=60)
def load_products():
    if os.path.isfile(CATALOGUE_FILE):
        try:
            with open(CATALOGUE_FILE, "r") as f:
                data = json.load(f)
            products = data.get("products", [])
            if products:
                for p in products:
                    if "tag" not in p or "category" not in p:
                        match = next((fb for fb in _FALLBACK_PRODUCTS if fb["id"] == p.get("id")), None)
                        if match:
                            p["tag"] = match["tag"]
                            p["category"] = match.get("category", "Hardware")
                return products
        except (json.JSONDecodeError, OSError):
            pass
    return _FALLBACK_PRODUCTS


PRODUCTS = load_products()

# 6. Session State Setup
if "basket" not in st.session_state:
    st.session_state.basket = {}

if "num_licences" not in st.session_state:
    st.session_state.num_licences = 0


def update_qty(product_id, delta):
    """Modifies the quantity of a product in the quotation."""
    current = st.session_state.basket.get(product_id, 0)
    new_val = max(0, current + delta)

    if new_val > 0:
        st.session_state.basket[product_id] = new_val
    else:
        st.session_state.basket.pop(product_id, None)


def remove_from_basket(product_id):
    st.session_state.basket.pop(product_id, None)


def basket_items():
    items = []
    for pid, qty in st.session_state.basket.items():
        prod = next((p for p in PRODUCTS if p["id"] == pid), None)
        if prod and qty > 0:
            items.append({**prod, "qty": qty, "line_total": prod["price"] * qty})
    return items


def total_hardware_capex():
    return sum(item["line_total"] for item in basket_items())


def total_monthly_licences():
    users = st.session_state.get("num_licences", 0)
    return float(users) * LICENCE_MONTHLY_RATE if users > 0 else 0.0


def total_activation_fee():
    users = st.session_state.get("num_licences", 0)
    return float(users) * ACTIVATION_FEE_PER_USER if users > 0 else 0.0


# 7. ReportLab PDF Generation Routine
def generate_quotation_pdf(quote_meta, reseller, customer, num_users, hw_items):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=32,
        bottomMargin=32,
    )
    styles = getSampleStyleSheet()

    c_primary = colors.HexColor("#0F5A73")
    c_slate = colors.HexColor("#475569")
    c_dark = colors.HexColor("#0F172A")
    c_bg = colors.HexColor("#F8FAFC")
    c_border = colors.HexColor("#CBD5E1")
    c_warning_bg = colors.HexColor("#FFFBEB")
    c_warning_border = colors.HexColor("#F59E0B")
    c_warning_text = colors.HexColor("#92400E")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=23,
        textColor=c_primary,
    )
    meta_style = ParagraphStyle(
        "MetaText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=c_slate,
    )
    sec_head = ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=c_primary,
    )
    th_style = ParagraphStyle(
        "TH",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    )
    td_style = ParagraphStyle(
        "TD",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=c_dark,
    )
    td_bold = ParagraphStyle(
        "TDB",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=c_dark,
    )

    story = []

    # Title & Metadata
    hdr = Table(
        [
            [
                Paragraph("<b>Novalink Telephony Quotation</b>", title_style),
                Paragraph(
                    f"<b>Reference:</b> {quote_meta['ref']}<br/>"
                    f"<b>Date:</b> {quote_meta['date']}<br/>"
                    f"<b>Contract Term:</b> <b>24 Months Minimum</b>",
                    meta_style,
                ),
            ]
        ],
        colWidths=[350, 190],
    )
    hdr.setStyle(
        TableStyle(
            [("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (1, 0), (1, 0), "RIGHT")]
        )
    )
    story.append(hdr)
    story.append(Spacer(1, 8))
    story.append(
        HRFlowable(
            width="100%", thickness=1.5, color=c_primary, spaceAfter=10, spaceBefore=0
        )
    )

    # Provider & Customer Panels
    addr_line = (
        f"Site/Delivery: {customer['delivery']}<br/>"
        if customer["delivery"] and customer["delivery"] != "N/A"
        else ""
    )
    parties = [
        [
            Paragraph("<b>SERVICE PROVIDER / PARTNER</b>", td_bold),
            Paragraph("<b>PROPOSED CUSTOMER</b>", td_bold),
        ],
        [
            Paragraph(
                f"<b>{reseller['company']}</b><br/>"
                f"Account Manager: {reseller['name']}<br/>"
                f"Email: {reseller['email']}<br/>"
                f"Telephone: {reseller['phone']}",
                td_style,
            ),
            Paragraph(
                f"<b>{customer['company']}</b><br/>"
                f"Contact Name: {customer['name']}<br/>"
                f"Email: {customer['email']}<br/>"
                f"Telephone: {customer['phone']}<br/>"
                f"{addr_line}",
                td_style,
            ),
        ],
    ]
    t_party = Table(parties, colWidths=[270, 270])
    t_party.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), c_bg),
                ("BOX", (0, 0), (-1, -1), 1, c_border),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(t_party)
    story.append(Spacer(1, 10))

    # 1. Ongoing Monthly Costs Table
    story.append(Paragraph("1. Ongoing Monthly Costs", sec_head))
    story.append(Spacer(1, 4))
    mrc_total = num_users * LICENCE_MONTHLY_RATE if num_users > 0 else 0.0
    mrc_vat = mrc_total * VAT_RATE
    mrc_inc_vat = mrc_total + mrc_vat

    mrc_data = [
        [
            Paragraph("Description", th_style),
            Paragraph("Users", th_style),
            Paragraph("Unit Price (Ex VAT)", th_style),
            Paragraph("Monthly Total (Ex VAT)", th_style),
        ],
        [
            Paragraph(
                "<b>Hosted VoIP Cloud User Licence</b><br/>"
                "<font color='#64748B' size=7>Includes PC/Mac softphone, iOS/Android mobile apps, cloud call recording, auto-attendant & inclusive UK landline/mobile calls.</font>",
                td_style,
            ),
            Paragraph(str(num_users), td_style),
            Paragraph(f"£{LICENCE_MONTHLY_RATE:.2f} / mo", td_style),
            Paragraph(f"£{mrc_total:.2f} / mo", td_bold),
        ],
        [
            Paragraph("<b>Total Ongoing Monthly Costs (Ex VAT)</b>", td_bold),
            "",
            "",
            Paragraph(f"<b>£{mrc_total:.2f} / mo</b>", td_bold),
        ],
        [
            Paragraph("VAT @ 20%", td_style),
            "",
            "",
            Paragraph(f"£{mrc_vat:.2f} / mo", td_style),
        ],
        [
            Paragraph("<b>Total Ongoing Monthly Costs (Inc VAT)</b>", td_bold),
            "",
            "",
            Paragraph(f"<b>£{mrc_inc_vat:.2f} / mo</b>", td_bold),
        ],
    ]
    t_mrc = Table(mrc_data, colWidths=[290, 50, 100, 100])
    t_mrc.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), c_primary),
                ("BOX", (0, 0), (-1, -1), 1, c_border),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
                ("BACKGROUND", (0, 2), (-1, 2), c_bg),
                ("BACKGROUND", (0, 4), (-1, 4), c_bg),
                ("TOPPADDING", (0, 0), (-1, -1), 4.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
            ]
        )
    )
    story.append(t_mrc)
    story.append(Spacer(1, 10))

    # 2. One-Off Upfront Costs Table
    story.append(Paragraph("2. One-Off Upfront Costs", sec_head))
    story.append(Spacer(1, 4))

    activation_total = num_users * ACTIVATION_FEE_PER_USER if num_users > 0 else 0.0
    hw_total = sum(i["line_total"] for i in hw_items)
    one_off_grand_total = activation_total + hw_total
    one_off_vat = one_off_grand_total * VAT_RATE
    one_off_inc_vat = one_off_grand_total + one_off_vat

    upfront_data = [
        [
            Paragraph("Item / Description", th_style),
            Paragraph("Qty", th_style),
            Paragraph("Unit Price (Ex VAT)", th_style),
            Paragraph("Line Total (Ex VAT)", th_style),
        ],
        [
            Paragraph(
                "<b>Initial User Setup &amp; Activation</b><br/>"
                "<font color='#64748B' size=7>System configuration, extension setup, user provisioning &amp; portal deployment.</font>",
                td_style,
            ),
            Paragraph(str(num_users), td_style),
            Paragraph(f"£{ACTIVATION_FEE_PER_USER:.2f}", td_style),
            Paragraph(f"£{activation_total:.2f}", td_bold),
        ]
    ]

    if hw_items:
        for itm in hw_items:
            upfront_data.append(
                [
                    Paragraph(
                        f"<b>{itm['name']}</b><br/><font color='#64748B' size=7>{itm['desc']}</font>",
                        td_style,
                    ),
                    Paragraph(str(itm["qty"]), td_style),
                    Paragraph(f"£{itm['price']:.2f}", td_style),
                    Paragraph(f"£{itm['line_total']:.2f}", td_bold),
                ]
            )

    upfront_data.append(
        [
            Paragraph("<b>Total One-Off Upfront Costs (Ex VAT)</b>", td_bold),
            "",
            "",
            Paragraph(f"<b>£{one_off_grand_total:.2f}</b>", td_bold),
        ]
    )
    upfront_data.append(
        [
            Paragraph("VAT @ 20%", td_style),
            "",
            "",
            Paragraph(f"£{one_off_vat:.2f}", td_style),
        ]
    )
    upfront_data.append(
        [
            Paragraph("<b>Total One-Off Upfront Costs (Inc VAT)</b>", td_bold),
            "",
            "",
            Paragraph(f"<b>£{one_off_inc_vat:.2f}</b>", td_bold),
        ]
    )

    t_upfront = Table(upfront_data, colWidths=[290, 50, 100, 100])
    t_upfront.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), c_primary),
                ("BOX", (0, 0), (-1, -1), 1, c_border),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
                ("BACKGROUND", (0, -3), (-1, -3), c_bg),
                ("BACKGROUND", (0, -1), (-1, -1), c_bg),
                ("TOPPADDING", (0, 0), (-1, -1), 4.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
            ]
        )
    )
    story.append(t_upfront)
    story.append(Spacer(1, 10))

    # Summary Box
    first_month_ex = mrc_total + one_off_grand_total
    first_month_inc = mrc_inc_vat + one_off_inc_vat

    summary_data = [
        [
            Paragraph("<b>FINANCIAL SUMMARY</b>", td_bold),
            Paragraph(
                f"<b>Ongoing Monthly Costs:</b> £{mrc_total:.2f} Ex VAT (£{mrc_inc_vat:.2f} Inc VAT / mo)<br/>"
                f"<b>Total One-Off Upfront Costs:</b> £{one_off_grand_total:.2f} Ex VAT (£{one_off_inc_vat:.2f} Inc VAT)<br/>"
                f"<b>Total Month 1 Investment:</b> <b>£{first_month_ex:.2f} Ex VAT (£{first_month_inc:.2f} Inc VAT)</b>",
                td_style,
            ),
        ]
    ]
    t_sum = Table(summary_data, colWidths=[180, 360])
    t_sum.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), c_bg),
                ("BOX", (0, 0), (-1, -1), 1.5, c_primary),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(t_sum)
    story.append(Spacer(1, 10))

    # Contract Termination Clause Box
    clause_text = (
        "<b>IMPORTANT CONTRACTUAL COMMITMENT &amp; TERMINATION TERMS:</b><br/>"
        "All hosted user licences quoted herein are strictly subject to a <b>minimum 24-month agreement term</b>. "
        "In the event of early termination or cancellation of services prior to the expiry of the initial 24-month term, "
        "<b>early termination charges will be applicable and payable in full</b> for all outstanding monthly licence fees "
        "remaining across the unexpired portion of the agreement.<br/>"
        "<b>Commercial Notes:</b> Quotation valid for 30 calendar days."
    )
    clause_para = Paragraph(
        clause_text,
        ParagraphStyle(
            "ContractClause",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.8,
            leading=11,
            textColor=c_warning_text,
        ),
    )
    t_clause = Table([[clause_para]], colWidths=[540])
    t_clause.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), c_warning_bg),
                ("BOX", (0, 0), (-1, -1), 1.2, c_warning_border),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(t_clause)
    story.append(Spacer(1, 10))

    # Customer Sign-Off Box
    sign_data = [
        [
            Paragraph("<b>CUSTOMER ACCEPTANCE &amp; AUTHORISATION:</b>", td_bold),
            Paragraph("<b>DATE:</b> ___________________________", td_style),
        ],
        [
            Paragraph("Authorised Signature: _________________________________", td_style),
            Paragraph("Print Name: __________________________", td_style),
        ],
    ]
    t_sign = Table(sign_data, colWidths=[330, 210])
    t_sign.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1, c_border),
                ("BACKGROUND", (0, 0), (-1, -1), c_bg),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(t_sign)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# 8. Navigation Tabs
tab_builder, tab_customer_view = st.tabs(["🛠️ Build Quotation", "💼 Customer Presentation View"])


# --- TAB 1: BUILD QUOTATION (Proportional, centered & live-calculated) ---
with tab_builder:
    st.markdown("<br>", unsafe_allow_html=True)
    b_col1, b_main, b_col3 = st.columns([1, 4, 1])

    with b_main:
        # Novalink Hero Brand Header Card
        st.markdown(
            f"""
            <div style="background-color: #FFFFFF; border-radius: 14px; border: 2px solid #0F5A73; padding: 2rem; box-shadow: 0 4px 12px rgba(15, 90, 115, 0.08); margin-bottom: 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #E2E8F0; padding-bottom: 1.25rem; margin-bottom: 1.5rem;">
                    <div>
                        <div style="color: #0F5A73; font-size: 1.7rem; font-weight: 800;">Novalink Telephony Quotation</div>
                        <div style="color: #64748B; font-size: 0.95rem; margin-top: 3px;">Interactive Quote Builder: Combine Cloud User Licences with Desktop Hardware</div>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: #E0F2FE; color: #0369A1; font-weight: 700; padding: 6px 14px; border-radius: 8px; font-size: 0.85rem; display: inline-block;">
                            {datetime.now().strftime('%d %B %Y')}
                        </span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Reactive live calculation container
        live_mrc_ex = total_monthly_licences()
        live_mrc_inc = live_mrc_ex * (1 + VAT_RATE)

        live_activation_ex = total_activation_fee()
        live_hw_ex = total_hardware_capex()
        live_one_off_ex = live_activation_ex + live_hw_ex
        live_one_off_inc = live_one_off_ex * (1 + VAT_RATE)

        live_month_1_ex = live_mrc_ex + live_one_off_ex
        live_month_1_inc = live_month_1_ex * (1 + VAT_RATE)

        # 3 Pillar Summary Cards
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.markdown(
                f"""
                <div class="vat-kpi-card" style="border-left: 4px solid #0F5A73;">
                    <div class="vat-kpi-title">Ongoing Monthly Costs</div>
                    <div class="vat-kpi-ex">£{live_mrc_ex:.2f} <span style="font-size: 0.9rem; font-weight: 600; color: #64748B;">Ex VAT</span></div>
                    <div class="vat-kpi-inc">£{live_mrc_inc:.2f} / mo <span style="font-size: 0.8rem; font-weight: 500; color: #64748B;">Inc VAT (20%)</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with kpi2:
            st.markdown(
                f"""
                <div class="vat-kpi-card" style="border-left: 4px solid #38BDF8;">
                    <div class="vat-kpi-title">Total One-Off Costs</div>
                    <div class="vat-kpi-ex">£{live_one_off_ex:.2f} <span style="font-size: 0.9rem; font-weight: 600; color: #64748B;">Ex VAT</span></div>
                    <div class="vat-kpi-inc">£{live_one_off_inc:.2f} <span style="font-size: 0.8rem; font-weight: 500; color: #64748B;">Inc VAT (20%)</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with kpi3:
            st.markdown(
                f"""
                <div class="vat-kpi-card" style="border-left: 4px solid #10B981;">
                    <div class="vat-kpi-title">Total Month 1 Investment</div>
                    <div class="vat-kpi-ex">£{live_month_1_ex:.2f} <span style="font-size: 0.9rem; font-weight: 600; color: #64748B;">Ex VAT</span></div>
                    <div class="vat-kpi-inc">£{live_month_1_inc:.2f} <span style="font-size: 0.8rem; font-weight: 500; color: #64748B;">Inc VAT (20%)</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Step 1: Licences
        st.markdown(
            """
            <div class="section-box">
                <div class="section-headline"><span>Step 1:</span> Hosted User Licences (Ongoing Monthly)</div>
            """,
            unsafe_allow_html=True,
        )

        lic_col1, lic_col2 = st.columns([3, 2], gap="large")
        with lic_col1:
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #0F5A73 0%, #164E63 100%); border-radius: 14px; padding: 1.5rem; box-shadow: 0 4px 10px rgba(15, 90, 115, 0.15);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 1.3rem; font-weight: 800; color: #FFFFFF !important;">Hosted Cloud User Licence</span>
                        <span style="background: #38BDF8; color: #0F172A !important; font-weight: 800; font-size: 0.95rem; padding: 4px 12px; border-radius: 9999px;">
                            £{LICENCE_MONTHLY_RATE:.2f} / user / mo
                        </span>
                    </div>
                    <div style="color: #E2E8F0 !important; font-size: 0.88rem; margin: 0.75rem 0;">
                        Complete unified communications seat with enterprise features included:
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; font-size: 0.85rem; color: #F8FAFC !important;">
                        <div style="color: #FFFFFF !important;">✓ Mobile App (iOS / Android)</div>
                        <div style="color: #FFFFFF !important;">✓ Cloud Call Recording</div>
                        <div style="color: #FFFFFF !important;">✓ Desktop PC Softphone</div>
                        <div style="color: #FFFFFF !important;">✓ Auto-Attendant & IVR</div>
                        <div style="color: #FFFFFF !important;">✓ Voicemail-to-Email</div>
                        <div style="color: #FFFFFF !important;">✓ Inclusive UK Landline/Mobile Calls</div>
                    </div>
                    <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid rgba(255,255,255,0.15); font-size: 0.82rem; color: #BAE6FD;">
                        ⚡ One-off user activation &amp; provisioning: <strong>£{ACTIVATION_FEE_PER_USER:.2f} per user</strong> (billed upfront in Month 1)
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with lic_col2:
            st.markdown("**Number of Hosted Users**")

            st.number_input(
                "Users",
                min_value=0,
                max_value=500,
                step=1,
                key="num_licences",
                label_visibility="collapsed",
            )

            current_users = st.session_state.num_licences
            current_mrc = float(current_users) * LICENCE_MONTHLY_RATE
            current_act = float(current_users) * ACTIVATION_FEE_PER_USER

            st.metric(
                label="Ongoing Monthly Costs (Ex VAT)",
                value=f"£{current_mrc:.2f}/mo",
                delta=f"£{current_mrc * (1 + VAT_RATE):.2f}/mo Inc VAT" if current_users > 0 else None,
                delta_color="off",
            )
            st.caption(f"Initial One-Off Activation ({current_users} users @ £{ACTIVATION_FEE_PER_USER:.2f}): **£{current_act:.2f} Ex VAT**")

        st.markdown("</div>", unsafe_allow_html=True)

        # Step 2: Handsets
        st.markdown(
            """
            <div class="section-box">
                <div class="section-headline"><span>Step 2:</span> Optional Handsets, Headsets &amp; Hardware (One-off Upfront)</div>
            """,
            unsafe_allow_html=True,
        )

        categories = ["All Hardware", "Yealink Phones", "Fanvil Phones", "Cordless DECT", "Headsets & Accessories"]
        selected_category = st.radio(
            "Filter Hardware Category",
            categories,
            horizontal=True,
            label_visibility="collapsed",
        )

        if selected_category == "All Hardware":
            filtered_products = PRODUCTS
        else:
            filtered_products = [p for p in PRODUCTS if p.get("category") == selected_category]

        # 🚨 Render products inside dedicated, bordered card enclosures 🚨
        for row_start in range(0, len(filtered_products), 4):
            row_slice = filtered_products[row_start : row_start + 4]
            cols = st.columns(4, gap="medium")

            for col, product in zip(cols, row_slice):
                with col:
                    with st.container(border=True):
                        # Top header row within card
                        st.markdown(
                            f"""
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                                <span class="card-badge">{product.get('tag', 'Handset')}</span>
                                <span style="font-weight: 800; color: #0F5A73; font-size: 1.15rem;">£{product['price']:.2f}</span>
                            </div>
                            <div style="min-height: 52px;">
                                <div style="font-weight: 800; color: #0F172A; font-size: 0.95rem;">{product["name"]}</div>
                                <div style="color: #64748B; font-size: 0.76rem; line-height: 1.2; margin-top: 2px;">{product["desc"]}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        # Rigid Base64 Image Stage
                        b64_uri = get_base64_image(product["image"])
                        if b64_uri:
                            st.markdown(
                                f"""
                                <div style="height: 150px; width: 100%; display: flex; align-items: center; justify-content: center; background-color: #FAFAFA; border-radius: 10px; margin: 0.65rem 0; padding: 6px; border: 1px solid #F1F5F9;">
                                    <img src="{b64_uri}" style="max-height: 135px; max-width: 90%; width: auto; height: auto; object-fit: contain; display: block; margin: 0 auto;" alt="{product['name']}">
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                f"""
                                <div style="height: 150px; width: 100%; display: flex; align-items: center; justify-content: center; background-color: #FAFAFA; border-radius: 10px; margin: 0.65rem 0; color: #94A3B8; font-size: 0.82rem; border: 1px solid #F1F5F9;">
                                    Image loading ({product['image']})
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        # Direct Reactive Stepper Controls
                        qty_in_quote = st.session_state.basket.get(product["id"], 0)

                        step_col1, step_col2, step_col3 = st.columns([1, 1.4, 1])
                        with step_col1:
                            if st.button("➖", key=f"minus_{product['id']}", use_container_width=True):
                                update_qty(product["id"], -1)
                                st.rerun()

                        with step_col2:
                            st.markdown(f"<div class='qty-display'>{qty_in_quote}</div>", unsafe_allow_html=True)

                        with step_col3:
                            if st.button("➕", key=f"plus_{product['id']}", use_container_width=True):
                                update_qty(product["id"], 1)
                                st.rerun()

                        # Status label
                        if qty_in_quote > 0:
                            st.markdown(
                                f"<div style='text-align: center; color: #0F5A73; font-weight: 700; font-size: 0.82rem; margin-top: 4px;'>Subtotal: £{qty_in_quote * product['price']:.2f} Ex VAT</div>",
                                unsafe_allow_html=True,
                            )
                        else:
                            st.caption("<div style='text-align: center; color: #94A3B8; font-size: 0.8rem;'>Not in quote</div>", unsafe_allow_html=True)

        # Hardware List Expander
        current_h_items = basket_items()
        if current_h_items:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander(
                f"📋 Selected Hardware in Quotation ({sum(i['qty'] for i in current_h_items)} items) — Subtotal: £{total_hardware_capex():.2f} Ex VAT",
                expanded=True,
            ):
                for item in current_h_items:
                    b1, b2, b3, b4 = st.columns([3, 1, 1.5, 1])
                    b1.write(f"**{item['name']}**")
                    b2.write(f"x{item['qty']}")
                    b3.write(f"£{item['line_total']:.2f} Ex VAT")
                    if b4.button("Remove", key=f"del_{item['id']}"):
                        remove_from_basket(item["id"])
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # Step 3: Quote Form & PDF
        st.markdown(
            """
            <div class="section-box">
                <div class="section-headline"><span>Step 3:</span> Quotation Details &amp; PDF Generation</div>
            """,
            unsafe_allow_html=True,
        )

        with st.form(key="telephony_quote_form"):
            col_reseller, col_customer = st.columns(2, gap="large")

            with col_reseller:
                st.markdown("#### 🏢 Your Company Details (Service Provider)")
                r_company = st.text_input("Your Company / Reseller Name*", placeholder="e.g. Acme Communications Ltd")
                r_contact = st.text_input("Your Name / Account Manager*", placeholder="e.g. John Doe")
                r_email = st.text_input("Your Email Address*", placeholder="e.g. sales@acmecomms.co.uk")
                r_phone = st.text_input("Your Phone Number", placeholder="e.g. 0330 123 4567")

            with col_customer:
                st.markdown("#### 👤 Proposed Customer Details")
                c_company = st.text_input("Customer Company Name*", placeholder="e.g. Apex Logistics Ltd")
                c_contact = st.text_input("Customer Contact Name*", placeholder="e.g. Sarah Jenkins")
                c_email = st.text_input("Customer Email Address*", placeholder="e.g. sarah@apexlogistics.co.uk")
                c_phone = st.text_input("Customer Phone Number", placeholder="e.g. 0161 123 4567")

            st.markdown("<hr style='margin: 1.25rem 0;'>", unsafe_allow_html=True)
            st.markdown("#### 📦 Delivery / Site Address *(Optional - can be left blank for initial quotes)*")
            d1, d2, d3 = st.columns([2, 1, 1])
            with d1:
                del_addr1 = st.text_input("Address Line 1", placeholder="Building name or street")
            with d2:
                del_city = st.text_input("Town / City", placeholder="Town / City")
            with d3:
                del_postcode = st.text_input("Postcode", placeholder="Postcode")

            generate_submitted = st.form_submit_button(
                "💾 Save Quotation & Generate Official PDF", use_container_width=True
            )

        if generate_submitted:
            if not r_company or not r_contact or not r_email:
                st.error("Please ensure your Service Provider details are complete.")
            elif not c_company or not c_contact or not c_email:
                st.error("Please fill in the Customer's Company, Contact Name, and Email.")
            else:
                quote_ref = f"NL-{datetime.now().strftime('%y%m%d%H%M')}"
                quote_date = datetime.now().strftime("%d %B %Y")
                
                addr_parts = [p.strip() for p in [del_addr1, del_city, del_postcode] if p.strip()]
                full_delivery = ", ".join(addr_parts) if addr_parts else "N/A"

                reseller_info = {
                    "company": r_company,
                    "name": r_contact,
                    "email": r_email,
                    "phone": r_phone,
                }
                customer_info = {
                    "company": c_company,
                    "name": c_contact,
                    "email": c_email,
                    "phone": c_phone,
                    "delivery": full_delivery,
                }
                quote_meta = {"ref": quote_ref, "date": quote_date}

                pdf_bytes = generate_quotation_pdf(
                    quote_meta,
                    reseller_info,
                    customer_info,
                    st.session_state.num_licences,
                    current_h_items,
                )

                st.session_state.active_quote_pdf = pdf_bytes
                st.session_state.active_quote_ref = quote_ref

                hw_summary = (
                    "; ".join(f"{i['name']} x{i['qty']}" for i in current_h_items)
                    if current_h_items
                    else "No Hardware (App/Licences Only)"
                )
                one_off_combined = total_activation_fee() + total_hardware_capex()
                record = {
                    "Quote Ref": [quote_ref],
                    "Date": [quote_date],
                    "Brand": ["Novalink Telephony"],
                    "Reseller": [r_company],
                    "Customer Company": [c_company],
                    "Customer Contact": [c_contact],
                    "Customer Email": [c_email],
                    "Licences": [st.session_state.num_licences],
                    "Ongoing Monthly Costs Ex VAT (£)": [f"{total_monthly_licences():.2f}"],
                    "Ongoing Monthly Costs Inc VAT (£)": [f"{total_monthly_licences() * (1 + VAT_RATE):.2f}"],
                    "Activation Fee Ex VAT (£)": [f"{total_activation_fee():.2f}"],
                    "Hardware Total Ex VAT (£)": [f"{total_hardware_capex():.2f}"],
                    "Total One-Off Costs Ex VAT (£)": [f"{one_off_combined:.2f}"],
                    "Total One-Off Costs Inc VAT (£)": [f"{one_off_combined * (1 + VAT_RATE):.2f}"],
                    "Hardware Summary": [hw_summary],
                    "Delivery Address": [full_delivery],
                }
                df = pd.DataFrame(record)
                if not os.path.isfile("quotes.csv"):
                    df.to_csv("quotes.csv", index=False)
                else:
                    df.to_csv("quotes.csv", mode="a", header=False, index=False)

                st.success(f"Quotation #{quote_ref} generated successfully under Novalink Telephony!")

        # Download action button
        if "active_quote_pdf" in st.session_state:
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                label=f"⬇️ Download Official PDF Document ({st.session_state.active_quote_ref}.pdf)",
                data=st.session_state.active_quote_pdf,
                file_name=f"{st.session_state.active_quote_ref}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)


# --- TAB 2: CUSTOMER PRESENTATION VIEW ---
with tab_customer_view:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 4, 1])

    with c2:
        cust_users = st.session_state.get("num_licences", 0)
        cust_mrc_ex = total_monthly_licences()
        cust_mrc_vat = cust_mrc_ex * VAT_RATE
        cust_mrc_inc = cust_mrc_ex + cust_mrc_vat

        cust_activation_ex = total_activation_fee()
        cust_hw_ex = total_hardware_capex()
        cust_one_off_ex = cust_activation_ex + cust_hw_ex
        cust_one_off_vat = cust_one_off_ex * VAT_RATE
        cust_one_off_inc = cust_one_off_ex + cust_one_off_vat

        cust_month_1_ex = cust_mrc_ex + cust_one_off_ex
        cust_month_1_vat = cust_mrc_vat + cust_one_off_vat
        cust_month_1_inc = cust_month_1_ex + cust_month_1_vat

        cust_h_items = basket_items()

        # Proposal Header Card
        st.markdown(
            f"""
            <div style="background-color: #FFFFFF; border-radius: 14px; border: 2px solid #0F5A73; padding: 2rem; box-shadow: 0 4px 12px rgba(15, 90, 115, 0.08);">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #E2E8F0; padding-bottom: 1.25rem; margin-bottom: 1.5rem;">
                    <div>
                        <div style="color: #0F5A73; font-size: 1.7rem; font-weight: 800;">Novalink Telephony Quotation</div>
                        <div style="color: #64748B; font-size: 0.95rem; margin-top: 3px;">Unified Communications &amp; Cloud Telephony Solution</div>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: #E0F2FE; color: #0369A1; font-weight: 700; padding: 6px 14px; border-radius: 8px; font-size: 0.85rem; display: inline-block;">
                            {datetime.now().strftime('%d %B %Y')}
                        </span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # 3 Pillar Summary Cards showing Ex VAT & Inc VAT (20%)
        ckpi1, ckpi2, ckpi3 = st.columns(3)
        with ckpi1:
            st.markdown(
                f"""
                <div class="vat-kpi-card" style="border-left: 4px solid #0F5A73;">
                    <div class="vat-kpi-title">Ongoing Monthly Costs</div>
                    <div class="vat-kpi-ex">£{cust_mrc_ex:.2f} <span style="font-size: 0.9rem; font-weight: 600; color: #64748B;">Ex VAT</span></div>
                    <div class="vat-kpi-inc">£{cust_mrc_inc:.2f} / mo <span style="font-size: 0.8rem; font-weight: 500; color: #64748B;">Inc VAT (20%)</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with ckpi2:
            st.markdown(
                f"""
                <div class="vat-kpi-card" style="border-left: 4px solid #38BDF8;">
                    <div class="vat-kpi-title">Total One-Off Costs</div>
                    <div class="vat-kpi-ex">£{cust_one_off_ex:.2f} <span style="font-size: 0.9rem; font-weight: 600; color: #64748B;">Ex VAT</span></div>
                    <div class="vat-kpi-inc">£{cust_one_off_inc:.2f} <span style="font-size: 0.8rem; font-weight: 500; color: #64748B;">Inc VAT (20%)</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with ckpi3:
            st.markdown(
                f"""
                <div class="vat-kpi-card" style="border-left: 4px solid #10B981;">
                    <div class="vat-kpi-title">Total Month 1 Investment</div>
                    <div class="vat-kpi-ex">£{cust_month_1_ex:.2f} <span style="font-size: 0.9rem; font-weight: 600; color: #64748B;">Ex VAT</span></div>
                    <div class="vat-kpi-inc">£{cust_month_1_inc:.2f} <span style="font-size: 0.8rem; font-weight: 500; color: #64748B;">Inc VAT (20%)</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 1. Ongoing Monthly Costs")
        if cust_users > 0:
            st.markdown(
                f"""
| Service Description | Quantity | Unit Price (Ex VAT) | Monthly Total (Ex VAT) |
| :--- | :---: | :---: | :---: |
| **Hosted VoIP Cloud User Licence** (Apps, Call Recording, Inclusive UK Mins) | {cust_users} Users | £{LICENCE_MONTHLY_RATE:.2f} / mo | **£{cust_mrc_ex:.2f} / mo** |
| **Monthly Subtotal (Ex VAT)** | | | **£{cust_mrc_ex:.2f} / mo** |
| **VAT @ 20%** | | | **£{cust_mrc_vat:.2f} / mo** |
| **Total Ongoing Monthly Costs (Inc VAT)** | | | **£{cust_mrc_inc:.2f} / mo** |
"""
            )
        else:
            st.caption("No user licences currently selected.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 2. One-Off Upfront Costs")
        table_lines = [
            "| Item Description | Qty | Unit Price (Ex VAT) | Line Total (Ex VAT) |",
            "| :--- | :---: | :---: | :---: |",
            f"| **Initial User Setup & Activation** - Provisioning, portal setup, and licence deployment | {cust_users} | £{ACTIVATION_FEE_PER_USER:.2f} | £{cust_activation_ex:.2f} |"
        ]

        if cust_h_items:
            for item in cust_h_items:
                table_lines.append(f"| **{item['name']}** ({item.get('tag', 'Item')}) - {item['desc']} | {item['qty']} | £{item['price']:.2f} | £{item['line_total']:.2f} |")

        table_lines.append(f"| **Subtotal (Ex VAT)** | | | **£{cust_one_off_ex:.2f}** |")
        table_lines.append(f"| **VAT @ 20%** | | | **£{cust_one_off_vat:.2f}** |")
        table_lines.append(f"| **Total One-Off Costs (Inc VAT)** | | | **£{cust_one_off_inc:.2f}** |")
        st.markdown("\n".join(table_lines))

        # Simplified Commercial Note
        st.markdown(
            """
            <div style="background-color: #F8FAFC; border: 1px dashed #CBD5E1; padding: 1rem 1.25rem; border-radius: 8px; font-size: 0.9rem; color: #475569; margin-top: 1rem;">
                <strong>Commercial Notes:</strong> Quotation valid for 30 calendar days.
            </div>
            """,
            unsafe_allow_html=True,
        )
