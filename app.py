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
    page_title="Telephony Quotation Tool",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Strict CSS: Fixes Light/Dark Tab Visibility & Cleans up Cards
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Container Spacing */
    .block-container {
        padding-top: 1.75rem !important;
        padding-bottom: 4rem !important;
        max-width: 1250px !important;
    }

    /* Hero */
    .brand-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #0F5A73;
        text-align: center;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    .brand-subtitle {
        font-size: 1.05rem;
        color: #475569;
        text-align: center;
        margin-bottom: 1.75rem;
    }

    /* Force Visible Tab Typography in ALL Modes */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        justify-content: center;
        border-bottom: 2px solid #CBD5E1;
        margin-bottom: 1.75rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        color: #334155 !important;
        padding: 10px 24px !important;
        background-color: transparent !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        color: #0F5A73 !important;
        border-bottom: 3px solid #0F5A73 !important;
    }

    /* Step Badges & Typography */
    .step-badge {
        display: inline-block;
        background: #E0F2FE;
        color: #0369A1;
        font-weight: 700;
        font-size: 0.75rem;
        padding: 4px 10px;
        border-radius: 9999px;
        margin-bottom: 0.35rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .step-heading {
        font-size: 1.4rem;
        font-weight: 800;
        color: #0F5A73;
        margin-bottom: 1rem;
    }

    /* Hardware Cards & Fixed Image Sizing */
    div[data-testid="column"] {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 1rem !important;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03);
    }
    div[data-testid="column"] img {
        height: 145px !important;
        max-height: 145px !important;
        width: 100% !important;
        object-fit: contain !important;
        margin: 0.5rem 0 !important;
        background-color: #FFFFFF !important;
    }

    .prod-header {
        text-align: center;
        min-height: 70px;
    }
    .prod-name {
        font-weight: 800;
        color: #0F5A73;
        font-size: 1rem;
        margin-bottom: 0.2rem;
    }
    .prod-desc {
        color: #64748B;
        font-size: 0.78rem;
        line-height: 1.25;
    }
    .prod-price {
        font-size: 1.2rem;
        font-weight: 800;
        color: #0F172A;
        text-align: center;
        margin: 0.25rem 0 0.5rem 0;
    }

    /* Primary Buttons */
    .stButton > button {
        background-color: #0F5A73 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        border: none !important;
    }
    .stButton > button:hover {
        background-color: #0c485c !important;
    }

    /* Clean Input Fields */
    div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="input"] input {
        color: #0F172A !important;
    }
    label {
        color: #1E293B !important;
        font-weight: 600 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 3. Product Catalogue & Defaults
LICENCE_MONTHLY_RATE = 7.00
CATALOGUE_FILE = "catalogue.json"

_FALLBACK_PRODUCTS = [
    {
        "id": "v67",
        "name": "Executive V67",
        "desc": "Flagship 7-inch touch console with HD video and Wi-Fi",
        "image": "Fanvil V67.webp",
        "price": 189.00,
    },
    {
        "id": "v66pro",
        "name": "Premium V66 Pro",
        "desc": "Multi-line audio console with adjustable colour display",
        "image": "V66 Pro.webp",
        "price": 129.00,
    },
    {
        "id": "v62pro",
        "name": "Essential V62 Pro",
        "desc": "Standard desktop phone with Gigabit PoE and 6 SIP lines",
        "image": "Fanvil V62 Pro.png",
        "price": 89.00,
    },
    {
        "id": "w620w",
        "name": "Linkvil Rugged",
        "desc": "Heavy-duty drop-proof roaming handset with Wi-Fi 6",
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
                return products
        except (json.JSONDecodeError, OSError):
            pass
    return _FALLBACK_PRODUCTS


PRODUCTS = load_products()

# 4. Session State Setup
if "basket" not in st.session_state:
    st.session_state.basket = {}

if "num_licences" not in st.session_state:
    st.session_state.num_licences = 5


def add_to_basket(product_id, qty):
    st.session_state.basket[product_id] = (
        st.session_state.basket.get(product_id, 0) + qty
    )


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


# 5. PDF Generation Routine (ReportLab)
def generate_quotation_pdf(quote_meta, reseller_data, customer_data, licences_qty, hw_items):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    # Palette
    c_primary = colors.HexColor("#0F5A73")
    c_slate = colors.HexColor("#475569")
    c_dark = colors.HexColor("#0F172A")
    c_bg = colors.HexColor("#F8FAFC")
    c_border = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=c_primary,
    )
    meta_style = ParagraphStyle(
        "MetaText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=c_slate,
    )
    head_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=c_primary,
    )
    cell_bold = ParagraphStyle(
        "CellB",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=c_dark,
    )
    cell_norm = ParagraphStyle(
        "CellN",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=c_dark,
    )

    story = []

    # Header Row (Title on Left, Quote Ref/Date on Right)
    hdr_table = Table(
        [
            [
                Paragraph("<b>Telephony Solution Quotation</b>", title_style),
                Paragraph(
                    f"<b>Reference:</b> {quote_meta['ref']}<br/><b>Date:</b> {quote_meta['date']}",
                    meta_style,
                ),
            ]
        ],
        colWidths=[360, 180],
    )
    hdr_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ]
        )
    )
    story.append(hdr_table)
    story.append(Spacer(1, 15))
    story.append(
        HRFlowable(
            width="100%", thickness=1.5, color=c_primary, spaceAfter=15, spaceBefore=0
        )
    )

    # Reseller (Prepared By) vs Customer (Prepared For) Table
    party_data = [
        [
            Paragraph("<b>SERVICE PROVIDER / PARTNER</b>", cell_bold),
            Paragraph("<b>CUSTOMER / PROPOSED FOR</b>", cell_bold),
        ],
        [
            Paragraph(
                f"<b>{reseller_data['company']}</b><br/>"
                f"Contact: {reseller_data['name']}<br/>"
                f"Email: {reseller_data['email']}<br/>"
                f"Phone: {reseller_data['phone']}",
                cell_norm,
            ),
            Paragraph(
                f"<b>{customer_data['company']}</b><br/>"
                f"Contact: {customer_data['name']}<br/>"
                f"Email: {customer_data['email']}<br/>"
                f"Phone: {customer_data['phone']}<br/>"
                f"Delivery: {customer_data['delivery']}",
                cell_norm,
            ),
        ],
    ]
    party_table = Table(party_data, colWidths=[270, 270])
    party_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), c_bg),
                ("BOX", (0, 0), (-1, -1), 1, c_border),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(party_table)
    story.append(Spacer(1, 15))

    # Section 1: Monthly Recurring Services (Opex)
    story.append(Paragraph("1. Monthly Recurring Services (Opex)", head_style))
    story.append(Spacer(1, 6))

    mrc_total = licences_qty * LICENCE_MONTHLY_RATE
    mrc_table_data = [
        [
            Paragraph("<b>Description</b>", cell_bold),
            Paragraph("<b>Qty</b>", cell_bold),
            Paragraph("<b>Unit Price</b>", cell_bold),
            Paragraph("<b>Monthly Total</b>", cell_bold),
        ],
        [
            Paragraph(
                "<b>Hosted VoIP Cloud User Licence</b><br/>"
                "<font color='#64748B' size=7.5>Includes PC/Mac softphone, iOS/Android mobile apps, cloud call recording, auto-attendant, & UK landline/mobile minutes.</font>",
                cell_norm,
            ),
            Paragraph(str(licences_qty), cell_norm),
            Paragraph(f"£{LICENCE_MONTHLY_RATE:.2f} / mo", cell_norm),
            Paragraph(f"£{mrc_total:.2f} / mo", cell_bold),
        ],
        [
            Paragraph("<b>Total Monthly Recurring (Ex VAT)</b>", cell_bold),
            "",
            "",
            Paragraph(f"<b>£{mrc_total:.2f} / mo</b>", cell_bold),
        ],
    ]
    t_mrc = Table(mrc_table_data, colWidths=[290, 50, 100, 100])
    t_mrc.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), c_primary),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BOX", (0, 0), (-1, -1), 1, c_border),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
                ("BACKGROUND", (0, -1), (-1, -1), c_bg),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    # Fix header text color for the PDF table
    for i in range(4):
        mrc_table_data[0][i].style.textColor = colors.white
    story.append(t_mrc)
    story.append(Spacer(1, 15))

    # Section 2: Hardware & Capex
    story.append(Paragraph("2. Hardware & Setup (Capex)", head_style))
    story.append(Spacer(1, 6))

    capex_total = sum(i["line_total"] for i in hw_items)
    capex_rows = [
        [
            Paragraph("<b>Handset Model / Description</b>", cell_bold),
            Paragraph("<b>Qty</b>", cell_bold),
            Paragraph("<b>Unit Price</b>", cell_bold),
            Paragraph("<b>Line Total</b>", cell_bold),
        ]
    ]

    if hw_items:
        for item in hw_items:
            capex_rows.append(
                [
                    Paragraph(
                        f"<b>{item['name']}</b><br/><font color='#64748B' size=7.5>{item['desc']}</font>",
                        cell_norm,
                    ),
                    Paragraph(str(item["qty"]), cell_norm),
                    Paragraph(f"£{item['price']:.2f}", cell_norm),
                    Paragraph(f"£{item['line_total']:.2f}", cell_bold),
                ]
            )
    else:
        capex_rows.append(
            [
                Paragraph("No desktop hardware requested (App/Softphone Deployment)", cell_norm),
                "0",
                "£0.00",
                "£0.00",
            ]
        )

    capex_rows.append(
        [
            Paragraph("<b>Total Upfront Hardware (Ex VAT)</b>", cell_bold),
            "",
            "",
            Paragraph(f"<b>£{capex_total:.2f}</b>", cell_bold),
        ]
    )

    t_capex = Table(capex_rows, colWidths=[290, 50, 100, 100])
    for i in range(4):
        capex_rows[0][i].style.textColor = colors.white

    t_capex.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), c_primary),
                ("BOX", (0, 0), (-1, -1), 1, c_border),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
                ("BACKGROUND", (0, -1), (-1, -1), c_bg),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(t_capex)
    story.append(Spacer(1, 15))

    # Grand Totals Box
    first_month = mrc_total + capex_total
    summary_box_data = [
        [
            Paragraph("<b>COMMERCIAL SUMMARY</b>", cell_bold),
            Paragraph(
                f"<b>Total Ongoing Monthly (MRC):</b> £{mrc_total:.2f} + VAT / month<br/>"
                f"<b>Total One-off Hardware (Capex):</b> £{capex_total:.2f} + VAT<br/>"
                f"<b>Initial Month 1 Commitment:</b> £{first_month:.2f} + VAT",
                cell_norm,
            ),
        ]
    ]
    t_summary = Table(summary_box_data, colWidths=[180, 360])
    t_summary.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), c_bg),
                ("BOX", (0, 0), (-1, -1), 1.5, c_primary),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(t_summary)
    story.append(Spacer(1, 15))

    # Terms
    terms = (
        "<b>Standard Telecoms Terms:</b> Quotation valid for 30 calendar days. Prices exclude VAT. "
        "User licences run on 30-day rolling terms unless otherwise specified. Physical hardware carries a 12-month "
        "manufacturer hardware warranty. Delivery subject to standard UK carrier lead times."
    )
    story.append(Paragraph(terms, meta_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# 6. Hero Brand Header
st.markdown('<div class="brand-title">Telephony Quotation Tool</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="brand-subtitle">Interactive white-label quote builder: combine cloud user licences with desktop hardware</div>',
    unsafe_allow_html=True,
)

# 7. Tabs
tab_builder, tab_customer_view = st.tabs(["🛠️ Build Quotation", "💼 Customer Presentation View"])

# --- TAB 1: BUILD QUOTATION ---
with tab_builder:
    # --- Step 1: Licences ---
    st.markdown(
        '<span class="step-badge">Step 1</span><div class="step-heading">Hosted User Licences (Monthly Opex)</div>',
        unsafe_allow_html=True,
    )

    lic_col1, lic_col2 = st.columns([3, 2], gap="large")
    with lic_col1:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #0F5A73 0%, #164E63 100%); border-radius: 12px; padding: 1.5rem; color: #FFFFFF;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; color: #FFFFFF; font-size: 1.3rem; font-weight: 800;">Hosted Cloud User Licence</h3>
                    <span style="background: #38BDF8; color: #0F172A; font-weight: 800; font-size: 0.95rem; padding: 0.3rem 0.75rem; border-radius: 6px;">
                        £{LICENCE_MONTHLY_RATE:.2f} / user / mo
                    </span>
                </div>
                <p style="color: #E2E8F0; font-size: 0.88rem; margin: 0.75rem 0 0.75rem 0;">
                    Complete unified communications package per seat with enterprise features included:
                </p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.85rem; color: #F8FAFC;">
                    <div>✓ Mobile App (iOS / Android)</div>
                    <div>✓ Cloud Call Recording</div>
                    <div>✓ Desktop PC Softphone</div>
                    <div>✓ Auto-Attendant & IVR</div>
                    <div>✓ Voicemail-to-Email</div>
                    <div>✓ Inclusive UK Landline/Mobile Calls</div>
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
            label_visibility="collapsed",
        )
        st.session_state.num_licences = selected_licences

        p1, p2, p3, p4 = st.columns(4)
        if p1.button("5 Users"):
            st.session_state.num_licences = 5
            st.rerun()
        if p2.button("10 Users"):
            st.session_state.num_licences = 10
            st.rerun()
        if p3.button("20 Users"):
            st.session_state.num_licences = 20
            st.rerun()
        if p4.button("50 Users"):
            st.session_state.num_licences = 50
            st.rerun()

        st.markdown(
            f"""
            <div style="background: #FFFFFF; border-radius: 10px; padding: 0.85rem; margin-top: 0.75rem; text-align: center; border: 1px solid #CBD5E1; border-left: 4px solid #0F5A73;">
                <div style="font-size: 0.75rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Total Licence Opex</div>
                <div style="font-size: 1.45rem; font-weight: 800; color: #0F5A73;">£{total_monthly_licences():.2f} <span style="font-size: 0.85rem; font-weight: normal; color: #475569;">/ month</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # --- Step 2: Handsets ---
    st.markdown(
        '<span class="step-badge">Step 2</span><div class="step-heading">Optional Enterprise Handsets (Upfront Capex)</div>',
        unsafe_allow_html=True,
    )

    hw_cols = st.columns(4, gap="medium")
    for col, product in zip(hw_cols, PRODUCTS):
        with col:
            st.markdown(
                f"""
                <div class="prod-header">
                    <div class="prod-name">{product["name"]}</div>
                    <div class="prod-desc">{product["desc"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if os.path.exists(product["image"]):
                st.image(product["image"])
            else:
                st.caption("No image file found")

            st.markdown(
                f'<div class="prod-price">£{product["price"]:.2f} <span style="font-size: 0.8rem; font-weight: 500; color: #64748B;">each</span></div>',
                unsafe_allow_html=True,
            )

            qty = st.number_input(
                "Qty",
                min_value=1,
                max_value=100,
                value=1,
                step=1,
                key=f"qty_{product['id']}",
                label_visibility="collapsed",
            )
            if st.button(f"Add to Basket", key=f"btn_{product['id']}", use_container_width=True):
                add_to_basket(product["id"], qty)
                st.toast(f"Added {qty}x {product['name']}", icon="✅")
                st.rerun()

    # Hardware Basket Expander
    hw_list = basket_items()
    if hw_list:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander(
            f"🛒 Hardware Basket ({sum(i['qty'] for i in hw_list)} items) — Total: £{total_hardware_capex():.2f}",
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

    # --- Step 3: Reseller & Customer Quote Form ---
    st.markdown(
        '<span class="step-badge">Step 3</span><div class="step-heading">Quotation Parties &amp; PDF Export</div>',
        unsafe_allow_html=True,
    )

    with st.form(key="telephony_quote_form"):
        col_reseller, col_customer = st.columns(2, gap="large")

        with col_reseller:
            st.markdown("##### 🏢 Your Company Details (Service Provider)")
            r_company = st.text_input("Your Company / Reseller Name*", value="Telecoms Partner Ltd")
            r_contact = st.text_input("Your Name / Account Manager*", value="Sam Myatt")
            r_email = st.text_input("Your Email Address*", value="sales@telecomspartner.co.uk")
            r_phone = st.text_input("Your Phone Number", value="0330 123 4567")

        with col_customer:
            st.markdown("##### 👤 Customer Details (Proposed For)")
            c_company = st.text_input("Customer Company Name*", placeholder="e.g. Apex Logistics Ltd")
            c_contact = st.text_input("Customer Contact Name*", placeholder="e.g. Sarah Jenkins")
            c_email = st.text_input("Customer Email Address*", placeholder="sarah@apexlogistics.co.uk")
            c_phone = st.text_input("Customer Phone Number", placeholder="0161 123 4567")

        st.markdown("<hr style='margin: 1.25rem 0;'>", unsafe_allow_html=True)
        needs_delivery = len(hw_list) > 0
        if needs_delivery:
            st.markdown("##### 📦 Hardware Delivery Details")
            d_col1, d_col2, d_col3 = st.columns([2, 1, 1])
            with d_col1:
                del_addr1 = st.text_input("Delivery Address Line 1*")
            with d_col2:
                del_city = st.text_input("Town / City*")
            with d_col3:
                del_postcode = st.text_input("Postcode*")
        else:
            del_addr1 = del_city = del_postcode = ""

        generate_submitted = st.form_submit_button(
            "💾 Save Quotation & Prepare PDF", use_container_width=True
        )

    # When form is submitted, validate, save locally and offer instant download
    if generate_submitted:
        if not r_company or not r_contact or not r_email:
            st.error("Please ensure your Service Provider details are complete.")
        elif not c_company or not c_contact or not c_email:
            st.error("Please fill in the Customer's Company, Contact Name, and Email.")
        elif needs_delivery and (not del_addr1 or not del_city or not del_postcode):
            st.error("Handsets are in the basket. Please provide the hardware delivery address.")
        else:
            quote_ref = f"TQT-{datetime.now().strftime('%y%m%d%H%M')}"
            quote_date = datetime.now().strftime("%d %B %Y")
            full_delivery = (
                f"{del_addr1}, {del_city}, {del_postcode}" if needs_delivery else "Softphone Deployment (No Delivery Required)"
            )

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

            # Generate PDF
            pdf_bytes = generate_quotation_pdf(
                quote_meta,
                reseller_info,
                customer_info,
                st.session_state.num_licences,
                hw_list,
            )

            # Store in session state for downloading outside the form
            st.session_state.active_quote_pdf = pdf_bytes
            st.session_state.active_quote_ref = quote_ref

            # Also persist to CSV
            hw_summary = (
                "; ".join(f"{i['name']} x{i['qty']}" for i in hw_list)
                if hw_list
                else "No Hardware"
            )
            record = {
                "Quote Ref": [quote_ref],
                "Date": [quote_date],
                "Reseller": [r_company],
                "Customer Company": [c_company],
                "Customer Contact": [c_contact],
                "Customer Email": [c_email],
                "Licences": [st.session_state.num_licences],
                "Monthly Opex (£)": [f"{total_monthly_licences():.2f}"],
                "Hardware Summary": [hw_summary],
                "Hardware Capex (£)": [f"{total_hardware_capex():.2f}"],
                "Delivery Address": [full_delivery],
            }
            df = pd.DataFrame(record)
            if not os.path.isfile("quotes.csv"):
                df.to_csv("quotes.csv", index=False)
            else:
                df.to_csv("quotes.csv", mode="a", header=False, index=False)

            st.success(f"Quotation #{quote_ref} generated successfully!")

    # If a quote has just been compiled, offer the download button
    if "active_quote_pdf" in st.session_state:
        st.download_button(
            label=f"⬇️ Download Quotation PDF ({st.session_state.active_quote_ref}.pdf)",
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
        capex = total_hardware_capex()
        month_1 = mrc + capex
        h_items = basket_items()

        # FIXED: Pure, clean HTML with 0 indentation so Streamlit does NOT treat it as a code block!
        card_html = f"""<div style="background: #FFFFFF; border-radius: 14px; border: 2px solid #0F5A73; padding: 2rem; box-shadow: 0 10px 25px -5px rgba(15, 90, 115, 0.08);">
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #E2E8F0; padding-bottom: 1rem; margin-bottom: 1.5rem;">
<div>
<h2 style="color: #0F5A73; margin: 0; font-size: 1.7rem; font-weight: 800;">Telephony Solution Quotation</h2>
<div style="color: #64748B; font-size: 0.95rem;">Cloud VoIP &amp; Unified Communications Proposal</div>
</div>
<div style="background: #E0F2FE; color: #0369A1; font-weight: 700; padding: 6px 14px; border-radius: 8px; font-size: 0.85rem;">
{datetime.now().strftime('%d %B %Y')}
</div>
</div>
<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
<div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #0F5A73; border-radius: 10px; padding: 1.2rem; text-align: center;">
<div style="font-size: 1.7rem; font-weight: 800; color: #0F5A73;">£{mrc:.2f}</div>
<div style="font-size: 0.78rem; font-weight: 700; color: #64748B; text-transform: uppercase;">Monthly Recurring (Ex VAT)</div>
</div>
<div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #38BDF8; border-radius: 10px; padding: 1.2rem; text-align: center;">
<div style="font-size: 1.7rem; font-weight: 800; color: #0F5A73;">£{capex:.2f}</div>
<div style="font-size: 0.78rem; font-weight: 700; color: #64748B; text-transform: uppercase;">One-off Hardware (Ex VAT)</div>
</div>
<div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #10B981; border-radius: 10px; padding: 1.2rem; text-align: center;">
<div style="font-size: 1.7rem; font-weight: 800; color: #0F172A;">£{month_1:.2f}</div>
<div style="font-size: 0.78rem; font-weight: 700; color: #64748B; text-transform: uppercase;">Total Month 1 Outlay</div>
</div>
</div>
</div>"""
        st.markdown(card_html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 1. Monthly Recurring Services (Opex)")
        if st.session_state.num_licences > 0:
            st.markdown(
                f"""
                | Service Item | Quantity | Unit Price | Monthly Total |
                | :--- | :--- | :--- | :--- |
                | **Hosted VoIP User Licence** (Apps, Call Recording, Inclusive UK Mins) | {st.session_state.num_licences} Users | £{LICENCE_MONTHLY_RATE:.2f} / mo | **£{mrc:.2f} / mo** |
                """
            )
        else:
            st.caption("No user licences currently selected.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 2. Physical Handsets & Hardware (Capex)")
        if h_items:
            table_rows = "\n".join(
                f"| **{i['name']}** - {i['desc']} | {i['qty']} | £{i['price']:.2f} | £{i['line_total']:.2f} |"
                for i in h_items
            )
            st.markdown(
                f"""
                | Hardware Description | Qty | Unit Price | Total |
                | :--- | :--- | :--- | :--- |
                {table_rows}
                | **Hardware Subtotal** | | | **£{capex:.2f}** |
                """
            )
        else:
            st.info(
                "App-only deployment selected (No physical desktop hardware). Users will utilise PC/Mac and mobile smartphone apps."
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="background-color: #FFFFFF; border: 1px dashed #CBD5E1; padding: 1rem; border-radius: 8px; font-size: 0.85rem; color: #64748B;">
                <strong>Commercial Terms:</strong> Quotation valid for 30 days. All prices exclude VAT. Pre-configured handsets include power adapters, desk stands, and lifetime manufacturer hardware warranties.
            </div>
            """,
            unsafe_allow_html=True,
        )
