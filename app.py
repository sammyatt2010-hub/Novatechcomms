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


# 4. High-Contrast Styles + Toast Popup Styling
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

    /* 🚨 POPUP TOAST FIX: Clean White Box, High-Contrast Text & Visible Close Button 🚨 */
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

    /* Novalink Brand Banner Card */
    .novalink-banner {
        background: linear-gradient(135deg, #0F5A73 0%, #164E63 100%);
        border-radius: 16px;
        padding: 2.2rem 1.75rem;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 20px -4px rgba(15, 90, 115, 0.25);
    }
    .brand-tag {
        display: inline-block;
        background-color: rgba(255, 255, 255, 0.18);
        color: #38BDF8 !important;
        font-size: 0.8rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 5px 16px;
        border-radius: 9999px;
        margin-bottom: 0.6rem;
        border: 1px solid rgba(56, 189, 248, 0.35);
    }
    .brand-title {
        font-size: 2.6rem;
        font-weight: 800;
        color: #FFFFFF !important;
        letter-spacing: -0.5px;
        margin: 0 0 0.4rem 0;
    }
    .brand-subtitle {
        font-size: 1.1rem;
        color: #E2E8F0 !important;
        margin: 0;
        font-weight: 400;
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

    /* Hardware Column Containers */
    div[data-testid="column"] {
        background-color: #FFFFFF !important;
        border-radius: 14px;
        padding: 1.25rem !important;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="column"]:hover {
        border-color: #CBD5E1;
        box-shadow: 0 10px 15px -3px rgba(15, 90, 115, 0.08);
    }

    /* Card Badge */
    .card-badge {
        font-size: 0.72rem;
        font-weight: 700;
        color: #0F5A73 !important;
        background: #F0F9FF;
        border: 1px solid #BAE6FD;
        padding: 3px 10px;
        border-radius: 6px;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Number Steppers & Inputs */
    div[data-testid="stNumberInput"] div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #94A3B8 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stNumberInput"] input {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        background-color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        text-align: center !important;
    }
    div[data-testid="stNumberInput"] button {
        background-color: #F1F5F9 !important;
        border: 1px solid #CBD5E1 !important;
        color: #0F172A !important;
    }
    div[data-testid="stNumberInput"] button:hover {
        background-color: #E2E8F0 !important;
    }
    div[data-testid="stNumberInput"] button svg {
        fill: #0F172A !important;
        stroke: #0F172A !important;
        color: #0F172A !important;
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
        border-radius: 10px !important;
        font-weight: 700 !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        box-shadow: 0 4px 10px rgba(15, 90, 115, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover,
    div[data-testid="stDownloadButton"] > button:hover {
        box-shadow: 0 6px 14px rgba(15, 90, 115, 0.35) !important;
        transform: translateY(-1px);
    }
    .stButton > button p,
    div[data-testid="stFormSubmitButton"] > button p,
    div[data-testid="stDownloadButton"] > button p,
    .stButton > button span,
    div[data-testid="stFormSubmitButton"] > button span,
    div[data-testid="stDownloadButton"] > button span {
        color: #FFFFFF !important;
    }

    /* Preset User Quick-Select Pills */
    .preset-btn > div > button {
        background: #F1F5F9 !important;
        color: #0F5A73 !important;
        border: 1px solid #CBD5E1 !important;
        font-weight: 700 !important;
        box-shadow: none !important;
        padding: 0.4rem 0.6rem !important;
    }
    .preset-btn > div > button p {
        color: #0F5A73 !important;
    }
    .preset-btn > div > button:hover {
        background: #E0F2FE !important;
        border-color: #38BDF8 !important;
    }

    /* Form Container */
    .stForm {
        background-color: #FFFFFF !important;
        border-radius: 16px !important;
        border: 1px solid #E2E8F0 !important;
        padding: 2.25rem !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.04) !important;
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

# 5. Rates & Product Catalogue
LICENCE_MONTHLY_RATE = 7.00
ACTIVATION_FEE_PER_USER = 25.00
CATALOGUE_FILE = "catalogue.json"

_FALLBACK_PRODUCTS = [
    {
        "id": "v67",
        "tag": "Flagship Touch",
        "name": "Executive V67",
        "desc": "7-inch adjustable touch screen with HD video and built-in Wi-Fi / Bluetooth",
        "image": "Fanvil V67.webp",
        "price": 189.00,
    },
    {
        "id": "v66pro",
        "tag": "Executive Audio",
        "name": "Premium V66 Pro",
        "desc": "Multi-line executive audio console with dual-screen colour display and Gigabit PoE",
        "image": "V66 Pro.webp",
        "price": 129.00,
    },
    {
        "id": "v62pro",
        "tag": "Standard Desk",
        "name": "Essential V62 Pro",
        "desc": "High-durability office desktop phone with 6 SIP lines and crystal-clear HD audio",
        "image": "Fanvil V62 Pro.png",
        "price": 89.00,
    },
    {
        "id": "w620w",
        "tag": "Rugged Cordless",
        "name": "Linkvil Rugged",
        "desc": "IP67 waterproof & drop-proof wireless roaming handset with 15h talk time",
        "image": "Linkvil W620W Rugged.png",
        "price": 149.00,
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
                    if "tag" not in p:
                        match = next((fb for fb in _FALLBACK_PRODUCTS if fb["id"] == p.get("id")), None)
                        p["tag"] = match["tag"] if match else "Handset"
                return products
        except (json.JSONDecodeError, OSError):
            pass
    return _FALLBACK_PRODUCTS


PRODUCTS = load_products()

# 6. Session State Setup (Defaults to 0 on reload)
if "basket" not in st.session_state:
    st.session_state.basket = {}

if "num_licences" not in st.session_state:
    st.session_state.num_licences = 0


def set_hardware_qty(product_id, qty):
    if qty > 0:
        st.session_state.basket[product_id] = qty
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
    return st.session_state.num_licences * LICENCE_MONTHLY_RATE


def total_activation_fee():
    return st.session_state.num_licences * ACTIVATION_FEE_PER_USER


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
    mrc_total = num_users * LICENCE_MONTHLY_RATE
    mrc_data = [
        [
            Paragraph("Description", th_style),
            Paragraph("Users", th_style),
            Paragraph("Unit Price", th_style),
            Paragraph("Monthly Total", th_style),
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
    ]
    t_mrc = Table(mrc_data, colWidths=[290, 50, 100, 100])
    t_mrc.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), c_primary),
                ("BOX", (0, 0), (-1, -1), 1, c_border),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
                ("BACKGROUND", (0, -1), (-1, -1), c_bg),
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

    activation_total = num_users * ACTIVATION_FEE_PER_USER
    hw_total = sum(i["line_total"] for i in hw_items)
    one_off_grand_total = activation_total + hw_total

    upfront_data = [
        [
            Paragraph("Item / Description", th_style),
            Paragraph("Qty", th_style),
            Paragraph("Unit Price", th_style),
            Paragraph("Line Total", th_style),
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

    t_upfront = Table(upfront_data, colWidths=[290, 50, 100, 100])
    t_upfront.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), c_primary),
                ("BOX", (0, 0), (-1, -1), 1, c_border),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
                ("BACKGROUND", (0, -1), (-1, -1), c_bg),
                ("TOPPADDING", (0, 0), (-1, -1), 4.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
            ]
        )
    )
    story.append(t_upfront)
    story.append(Spacer(1, 10))

    # Summary Box
    first_month = mrc_total + one_off_grand_total
    summary_data = [
        [
            Paragraph("<b>FINANCIAL SUMMARY</b>", td_bold),
            Paragraph(
                f"<b>Ongoing Monthly Costs:</b> £{mrc_total:.2f} + VAT / month<br/>"
                f"<b>Total One-Off Upfront Costs:</b> £{one_off_grand_total:.2f} + VAT "
                f"<font color='#64748B' size=7.5>(Includes £{activation_total:.2f} Activation + £{hw_total:.2f} Hardware)</font><br/>"
                f"<b>Total Month 1 Investment:</b> £{first_month:.2f} + VAT",
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
        "remaining across the unexpired portion of the agreement."
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
                ("BACKGROUND", (0, 0), (-1, 0), c_warning_bg),
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


# 8. Novalink Hero Brand Header Card
st.markdown(
    """
    <div class="novalink-banner">
        <span class="brand-tag">Novalink Communications</span>
        <h1 class="brand-title">Novalink Telephony Quotation</h1>
        <p class="brand-subtitle">Official Partner Portal: Cloud VoIP User Licences &amp; Enterprise Hardware</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# 9. Navigation Tabs
tab_builder, tab_customer_view = st.tabs(["🛠️ Build Quotation", "💼 Customer Presentation View"])

# --- TAB 1: BUILD QUOTATION ---
with tab_builder:
    # Step 1: Licences
    st.markdown('<div class="section-headline"><span>Step 1:</span> Hosted User Licences (Ongoing Monthly)</div>', unsafe_allow_html=True)

    lic_col1, lic_col2 = st.columns([3, 2], gap="large")
    with lic_col1:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #0F5A73 0%, #164E63 100%); border-radius: 14px; padding: 1.6rem; box-shadow: 0 4px 10px rgba(15, 90, 115, 0.15);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 1.35rem; font-weight: 800; color: #FFFFFF !important;">Hosted Cloud User Licence</span>
                    <span style="background: #38BDF8; color: #0F172A !important; font-weight: 800; font-size: 0.95rem; padding: 4px 12px; border-radius: 9999px;">
                        £{LICENCE_MONTHLY_RATE:.2f} / user / mo
                    </span>
                </div>
                <div style="color: #E2E8F0 !important; font-size: 0.88rem; margin: 0.85rem 0 1rem 0;">
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
        selected_licences = st.number_input(
            "Users",
            min_value=0,
            max_value=500,
            value=st.session_state.num_licences,
            step=1,
            key="licence_counter",
            label_visibility="collapsed",
        )
        st.session_state.num_licences = selected_licences

        p1, p2, p3, p4 = st.columns(4)
        with p1:
            st.markdown('<div class="preset-btn">', unsafe_allow_html=True)
            if st.button("5 Users", key="preset_5"):
                st.session_state.num_licences = 5
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with p2:
            st.markdown('<div class="preset-btn">', unsafe_allow_html=True)
            if st.button("10 Users", key="preset_10"):
                st.session_state.num_licences = 10
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with p3:
            st.markdown('<div class="preset-btn">', unsafe_allow_html=True)
            if st.button("20 Users", key="preset_20"):
                st.session_state.num_licences = 20
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with p4:
            st.markdown('<div class="preset-btn">', unsafe_allow_html=True)
            if st.button("50 Users", key="preset_50"):
                st.session_state.num_licences = 50
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.metric(
            label="Ongoing Monthly Costs",
            value=f"£{total_monthly_licences():.2f}/mo",
            delta=f"{st.session_state.num_licences} users @ £{LICENCE_MONTHLY_RATE:.2f}",
        )

        st.caption(f"Initial One-Off Activation ({st.session_state.num_licences} users @ £{ACTIVATION_FEE_PER_USER:.2f}): **£{total_activation_fee():.2f}**")

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # Step 2: Handsets with Base64 Images
    st.markdown('<div class="section-headline"><span>Step 2:</span> Optional Handsets &amp; Hardware (One-off Upfront)</div>', unsafe_allow_html=True)

    hw_cols = st.columns(4, gap="medium")
    for col, product in zip(hw_cols, PRODUCTS):
        with col:
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span class="card-badge">{product.get('tag', 'Handset')}</span>
                    <span style="font-weight: 800; color: #0F5A73; font-size: 1.15rem;">£{product['price']:.2f}</span>
                </div>
                <div style="min-height: 55px;">
                    <div style="font-weight: 800; color: #0F172A; font-size: 1rem;">{product["name"]}</div>
                    <div style="color: #64748B; font-size: 0.78rem; line-height: 1.25; margin-top: 2px;">{product["desc"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Rigid Base64 Image Stage
            b64_uri = get_base64_image(product["image"])
            if b64_uri:
                st.markdown(
                    f"""
                    <div style="height: 155px; width: 100%; display: flex; align-items: center; justify-content: center; background-color: #FAFAFA; border-radius: 10px; margin: 0.65rem 0; padding: 6px;">
                        <img src="{b64_uri}" style="max-height: 140px; max-width: 90%; width: auto; height: auto; object-fit: contain; display: block; margin: 0 auto;" alt="{product['name']}">
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div style="height: 155px; width: 100%; display: flex; align-items: center; justify-content: center; background-color: #FAFAFA; border-radius: 10px; margin: 0.65rem 0; color: #94A3B8; font-size: 0.85rem;">
                        Image unavailable
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            current_qty = st.session_state.basket.get(product["id"], 0)
            qty = st.number_input(
                "Qty",
                min_value=0,
                max_value=100,
                value=current_qty,
                step=1,
                key=f"qty_{product['id']}",
                label_visibility="collapsed",
            )

            if st.button(f"Add to Quotation", key=f"btn_{product['id']}", use_container_width=True):
                set_hardware_qty(product["id"], qty)
                if qty > 0:
                    st.toast(f"Updated {qty}x {product['name']} in quotation!", icon="✅")
                else:
                    st.toast(f"Removed {product['name']} from quotation.", icon="ℹ️")
                st.rerun()

    # Hardware List Expander
    hw_list = basket_items()
    if hw_list:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander(
            f"📋 Selected Hardware in Quotation ({sum(i['qty'] for i in hw_list)} items) — Hardware Subtotal: £{total_hardware_capex():.2f}",
            expanded=True,
        ):
            for item in hw_list:
                b1, b2, b3, b4 = st.columns([3, 1, 1.5, 1])
                b1.write(f"**{item['name']}**")
                b2.write(f"x{item['qty']}")
                b3.write(f"£{item['line_total']:.2f}")
                if b4.button("Remove", key=f"del_{item['id']}"):
                    remove_from_basket(item["id"])
                    st.rerun()

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # Step 3: Blank Quote Form
    st.markdown('<div class="section-headline"><span>Step 3:</span> Quotation Details & PDF Generation</div>', unsafe_allow_html=True)

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
                hw_list,
            )

            st.session_state.active_quote_pdf = pdf_bytes
            st.session_state.active_quote_ref = quote_ref

            hw_summary = (
                "; ".join(f"{i['name']} x{i['qty']}" for i in hw_list)
                if hw_list
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
                "Ongoing Monthly Costs (£)": [f"{total_monthly_licences():.2f}"],
                "Activation Fee (£)": [f"{total_activation_fee():.2f}"],
                "Hardware Summary": [hw_summary],
                "Hardware Total (£)": [f"{total_hardware_capex():.2f}"],
                "Total One-Off Costs (£)": [f"{one_off_combined:.2f}"],
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


# --- TAB 2: CUSTOMER PRESENTATION VIEW ---
with tab_customer_view:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 4, 1])

    with c2:
        mrc = total_monthly_licences()
        activation = total_activation_fee()
        hw_total = total_hardware_capex()
        one_off_total = activation + hw_total
        month_1 = mrc + one_off_total
        h_items = basket_items()

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

        # 3 Pillar Summary: Ongoing Monthly vs One-Off Upfront vs Month 1 Total
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric(
                label="Ongoing Monthly Costs",
                value=f"£{mrc:.2f}/mo",
            )
        with kpi2:
            st.metric(
                label="Total One-Off Costs",
                value=f"£{one_off_total:.2f}",
                delta=f"Activation: £{activation:.2f} | Handsets: £{hw_total:.2f}",
                delta_color="off",
            )
        with kpi3:
            st.metric(
                label="Total Month 1 Investment",
                value=f"£{month_1:.2f}",
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 1. Ongoing Monthly Costs")
        if st.session_state.num_licences > 0:
            st.markdown(
                f"""
| Service Description | Quantity | Unit Price | Monthly Total |
| :--- | :---: | :---: | :---: |
| **Hosted VoIP Cloud User Licence** (Apps, Call Recording, Inclusive UK Mins) | {st.session_state.num_licences} Users | £{LICENCE_MONTHLY_RATE:.2f} / mo | **£{mrc:.2f} / mo** |
"""
            )
        else:
            st.caption("No user licences currently selected.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 2. One-Off Upfront Costs")
        table_lines = [
            "| Item Description | Qty | Unit Price | Total |",
            "| :--- | :---: | :---: | :---: |",
            f"| **Initial User Setup & Activation** - Provisioning, portal setup, and licence deployment | {st.session_state.num_licences} | £{ACTIVATION_FEE_PER_USER:.2f} | £{activation:.2f} |"
        ]

        if h_items:
            for item in h_items:
                table_lines.append(f"| **{item['name']}** ({item.get('tag', 'Handset')}) - {item['desc']} | {item['qty']} | £{item['price']:.2f} | £{item['line_total']:.2f} |")

        table_lines.append(f"| **Total One-Off Upfront Costs** | | | **£{one_off_total:.2f}** |")
        st.markdown("\n".join(table_lines))

        st.markdown(
            """
            <div style="background-color: #F8FAFC; border: 1px dashed #CBD5E1; padding: 1rem 1.25rem; border-radius: 8px; font-size: 0.85rem; color: #64748B; margin-top: 1rem;">
                <strong>Commercial Notes:</strong> Quotation valid for 30 calendar days. All prices exclude VAT. Pre-configured handsets include power adapters, desk stands, and lifetime manufacturer hardware warranties. Formal terms and contractual commitments are detailed on the generated agreement paperwork.
            </div>
            """,
            unsafe_allow_html=True,
        )
