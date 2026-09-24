import io
import json
import os
from datetime import datetime
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

# 2. Bulletproof Theme Overhaul (Direct Variable Override)
# By overriding CSS custom variables, Streamlit forces high-contrast dark text
# across tabs, inputs, cards, tables, and buttons in both light & dark modes.
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

    /* Force all text tags to render explicitly dark */
    p, span, label, h1, h2, h3, h4, h5, h6, li, td, th {
        color: #0F172A !important;
    }

    .brand-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #0F5A73 !important;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .brand-subtitle {
        font-size: 1.05rem;
        color: #475569 !important;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    /* TAB OVERRIDE: Clear visible tabs in all lighting/browser states */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        padding: 10px 24px !important;
    }
    button[data-baseweb="tab"] div, 
    button[data-baseweb="tab"] p {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        color: #475569 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        border-bottom: 3px solid #0F5A73 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] div,
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #0F5A73 !important;
    }

    /* Product Cards & Uniform Images */
    div[data-testid="column"] {
        background-color: #FFFFFF !important;
        border-radius: 12px;
        padding: 1.1rem !important;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
    }
    div[data-testid="column"] img {
        height: 140px !important;
        max-height: 140px !important;
        width: 100% !important;
        object-fit: contain !important;
        margin: 0.5rem auto !important;
        display: block !important;
        background: #FFFFFF !important;
    }

    /* Input & Stepper Field Contrast */
    div[data-baseweb="input"],
    div[data-baseweb="base-input"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="input"] input {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        background-color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* Form Card Container */
    .stForm {
        background-color: #FFFFFF !important;
        border-radius: 14px !important;
        border: 1px solid #E2E8F0 !important;
        padding: 2rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04) !important;
    }

    /* Primary Buttons */
    .stButton > button {
        background-color: #0F5A73 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        border: none !important;
    }
    .stButton > button * {
        color: #FFFFFF !important;
    }
    .stButton > button:hover {
        background-color: #0c485c !important;
    }

    /* Table Typography */
    table {
        color: #0F172A !important;
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

# 4. State Handlers
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


# 5. ReportLab PDF Generation Engine
def generate_quotation_pdf(quote_meta, reseller, customer, num_users, hw_items):
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

    c_primary = colors.HexColor("#0F5A73")
    c_slate = colors.HexColor("#475569")
    c_dark = colors.HexColor("#0F172A")
    c_bg = colors.HexColor("#F8FAFC")
    c_border = colors.HexColor("#CBD5E1")

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
    sec_head = ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=c_primary,
    )
    th_style = ParagraphStyle(
        "TH",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.white,
    )
    td_style = ParagraphStyle(
        "TD",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=c_dark,
    )
    td_bold = ParagraphStyle(
        "TDB",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=c_dark,
    )

    story = []

    # Title & Metadata
    hdr = Table(
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
    hdr.setStyle(
        TableStyle(
            [("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (1, 0), (1, 0), "RIGHT")]
        )
    )
    story.append(hdr)
    story.append(Spacer(1, 10))
    story.append(
        HRFlowable(
            width="100%", thickness=1.5, color=c_primary, spaceAfter=12, spaceBefore=0
        )
    )

    # Provider & Customer Panels
    parties = [
        [
            Paragraph("<b>SERVICE PROVIDER / PARTNER</b>", td_bold),
            Paragraph("<b>PROPOSED CUSTOMER</b>", td_bold),
        ],
        [
            Paragraph(
                f"<b>{reseller['company']}</b><br/>"
                f"Contact: {reseller['name']}<br/>"
                f"Email: {reseller['email']}<br/>"
                f"Phone: {reseller['phone']}",
                td_style,
            ),
            Paragraph(
                f"<b>{customer['company']}</b><br/>"
                f"Contact: {customer['name']}<br/>"
                f"Email: {customer['email']}<br/>"
                f"Phone: {customer['phone']}<br/>"
                f"Delivery: {customer['delivery']}",
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
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(t_party)
    story.append(Spacer(1, 15))

    # 1. Monthly Recurring Services Table
    story.append(Paragraph("1. Monthly Recurring Services (Opex)", sec_head))
    story.append(Spacer(1, 5))
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
                "<font color='#64748B' size=7.5>Includes PC/Mac softphone, iOS/Android mobile apps, cloud call recording, auto-attendant & inclusive UK landline/mobile calls.</font>",
                td_style,
            ),
            Paragraph(str(num_users), td_style),
            Paragraph(f"£{LICENCE_MONTHLY_RATE:.2f} / mo", td_style),
            Paragraph(f"£{mrc_total:.2f} / mo", td_bold),
        ],
        [
            Paragraph("<b>Total Monthly Recurring (Ex VAT)</b>", td_bold),
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
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(t_mrc)
    story.append(Spacer(1, 15))

    # 2. Hardware Table
    story.append(Paragraph("2. Hardware & Setup (Capex)", sec_head))
    story.append(Spacer(1, 5))
    capex_total = sum(i["line_total"] for i in hw_items)
    capex_data = [
        [
            Paragraph("Handset Model / Description", th_style),
            Paragraph("Qty", th_style),
            Paragraph("Unit Price", th_style),
            Paragraph("Line Total", th_style),
        ]
    ]

    if hw_items:
        for itm in hw_items:
            capex_data.append(
                [
                    Paragraph(
                        f"<b>{itm['name']}</b><br/><font color='#64748B' size=7.5>{itm['desc']}</font>",
                        td_style,
                    ),
                    Paragraph(str(itm["qty"]), td_style),
                    Paragraph(f"£{itm['price']:.2f}", td_style),
                    Paragraph(f"£{itm['line_total']:.2f}", td_bold),
                ]
            )
    else:
        capex_data.append(
            [
                Paragraph(
                    "App-only deployment selected (No physical desktop hardware)",
                    td_style,
                ),
                "0",
                "£0.00",
                "£0.00",
            ]
        )

    capex_data.append(
        [
            Paragraph("<b>Total Upfront Hardware (Ex VAT)</b>", td_bold),
            "",
            "",
            Paragraph(f"<b>£{capex_total:.2f}</b>", td_bold),
        ]
    )

    t_hw = Table(capex_data, colWidths=[290, 50, 100, 100])
    t_hw.setStyle(
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
    story.append(t_hw)
    story.append(Spacer(1, 15))

    # Summary Box
    first_month = mrc_total + capex_total
    summary_data = [
        [
            Paragraph("<b>COMMERCIAL SUMMARY</b>", td_bold),
            Paragraph(
                f"<b>Monthly Recurring (MRC):</b> £{mrc_total:.2f} + VAT / month<br/>"
                f"<b>Upfront Hardware (Capex):</b> £{capex_total:.2f} + VAT<br/>"
                f"<b>Total Month 1 Commitment:</b> £{first_month:.2f} + VAT",
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
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(t_sum)
    story.append(Spacer(1, 12))

    terms = (
        "<b>Commercial Notes:</b> Quotation valid for 30 calendar days. Prices exclude VAT. "
        "User licences operate on standard 30-day rolling terms. Physical hardware carries a standard 12-month "
        "manufacturer hardware warranty with pre-configuration included."
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

# 7. Main Tabs
tab_builder, tab_customer_view = st.tabs(["🛠️ Build Quotation", "💼 Customer Presentation View"])

# --- TAB 1: BUILD QUOTATION ---
with tab_builder:
    # Step 1: Licences
    st.markdown("### Step 1: Hosted User Licences (Monthly Opex)")

    lic_col1, lic_col2 = st.columns([3, 2], gap="large")
    with lic_col1:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #0F5A73 0%, #164E63 100%); border-radius: 12px; padding: 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 1.3rem; font-weight: 800; color: #FFFFFF !important;">Hosted Cloud User Licence</span>
                    <span style="background: #38BDF8; color: #0F172A !important; font-weight: 800; font-size: 0.95rem; padding: 4px 10px; border-radius: 6px;">
                        £{LICENCE_MONTHLY_RATE:.2f} / user / mo
                    </span>
                </div>
                <div style="color: #E2E8F0 !important; font-size: 0.9rem; margin: 0.75rem 0;">
                    Complete unified communications seat with enterprise features included:
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.85rem; color: #F8FAFC !important;">
                    <div style="color: #FFFFFF !important;">✓ Mobile App (iOS / Android)</div>
                    <div style="color: #FFFFFF !important;">✓ Cloud Call Recording</div>
                    <div style="color: #FFFFFF !important;">✓ Desktop PC Softphone</div>
                    <div style="color: #FFFFFF !important;">✓ Auto-Attendant & IVR</div>
                    <div style="color: #FFFFFF !important;">✓ Voicemail-to-Email</div>
                    <div style="color: #FFFFFF !important;">✓ Inclusive UK Landline/Mobile Calls</div>
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

        st.metric(
            label="Total Licence Opex (Per Month)",
            value=f"£{total_monthly_licences():.2f}/mo",
            delta=f"{st.session_state.num_licences} users @ £{LICENCE_MONTHLY_RATE:.2f}",
        )

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # Step 2: Handsets
    st.markdown("### Step 2: Optional Enterprise Handsets (Upfront Capex)")

    hw_cols = st.columns(4, gap="medium")
    for col, product in zip(hw_cols, PRODUCTS):
        with col:
            st.markdown(
                f"""
                <div style="text-align: center; min-height: 65px;">
                    <div style="font-weight: 800; color: #0F5A73; font-size: 1.05rem;">{product["name"]}</div>
                    <div style="color: #64748B; font-size: 0.8rem; line-height: 1.25; margin-top: 2px;">{product["desc"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if os.path.exists(product["image"]):
                st.image(product["image"])
            else:
                st.caption("Image unavailable")

            st.markdown(
                f"""
                <div style="text-align: center; font-size: 1.2rem; font-weight: 800; color: #0F172A; margin: 0.2rem 0 0.5rem 0;">
                    £{product["price"]:.2f} <span style="font-size: 0.8rem; font-weight: 500; color: #64748B;">each</span>
                </div>
                """,
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

    # Step 3: Reseller & Customer Quote Form
    st.markdown("### Step 3: Quotation Parties & PDF Generation")

    with st.form(key="telephony_quote_form"):
        col_reseller, col_customer = st.columns(2, gap="large")

        with col_reseller:
            st.markdown("#### 🏢 Your Company Details (Service Provider)")
            r_company = st.text_input("Your Company / Reseller Name*", value="Telecoms Partner Ltd")
            r_contact = st.text_input("Your Name / Account Manager*", value="Sam Myatt")
            r_email = st.text_input("Your Email Address*", value="sales@telecomspartner.co.uk")
            r_phone = st.text_input("Your Phone Number", value="0330 123 4567")

        with col_customer:
            st.markdown("#### 👤 Proposed Customer Details")
            c_company = st.text_input("Customer Company Name*", placeholder="e.g. Apex Logistics Ltd")
            c_contact = st.text_input("Customer Contact Name*", placeholder="e.g. Sarah Jenkins")
            c_email = st.text_input("Customer Email Address*", placeholder="sarah@apexlogistics.co.uk")
            c_phone = st.text_input("Customer Phone Number", placeholder="0161 123 4567")

        st.markdown("<hr style='margin: 1.25rem 0;'>", unsafe_allow_html=True)
        needs_delivery = len(hw_list) > 0
        if needs_delivery:
            st.markdown("#### 📦 Hardware Delivery Details")
            d1, d2, d3 = st.columns([2, 1, 1])
            with d1:
                del_addr1 = st.text_input("Delivery Address Line 1*")
            with d2:
                del_city = st.text_input("Town / City*")
            with d3:
                del_postcode = st.text_input("Postcode*")
        else:
            del_addr1 = del_city = del_postcode = ""

        generate_submitted = st.form_submit_button(
            "💾 Save Quotation & Generate PDF", use_container_width=True
        )

    if generate_submitted:
        if not r_company or not r_contact or not r_email:
            st.error("Please ensure your Service Provider details are complete.")
        elif not c_company or not c_contact or not c_email:
            st.error("Please fill in the Customer's Company, Contact Name, and Email.")
        elif needs_delivery and (not del_addr1 or not del_city or not del_postcode):
            st.error("Hardware is in the basket. Please provide the hardware delivery address.")
        else:
            quote_ref = f"TQT-{datetime.now().strftime('%y%m%d%H%M')}"
            quote_date = datetime.now().strftime("%d %B %Y")
            full_delivery = (
                f"{del_addr1}, {del_city}, {del_postcode}"
                if needs_delivery
                else "Softphone Deployment (No Delivery Required)"
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

    if "active_quote_pdf" in st.session_state:
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
        capex = total_hardware_capex()
        month_1 = mrc + capex
        h_items = basket_items()

        # Clean Proposal Container with explicit background & text colors
        st.markdown(
            f"""
            <div style="background-color: #FFFFFF; border-radius: 14px; border: 2px solid #0F5A73; padding: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.04);">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #E2E8F0; padding-bottom: 1rem; margin-bottom: 1.5rem;">
                    <div>
                        <div style="color: #0F5A73; font-size: 1.6rem; font-weight: 800;">Telephony Solution Quotation</div>
                        <div style="color: #64748B; font-size: 0.95rem;">Cloud VoIP &amp; Unified Communications Proposal</div>
                    </div>
                    <div style="background: #E0F2FE; color: #0369A1; font-weight: 700; padding: 6px 14px; border-radius: 8px; font-size: 0.85rem;">
                        {datetime.now().strftime('%d %B %Y')}
                    </div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        # 3 Pillar Summary using Native Columns (Guarantees visible text in all themes)
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric(
                label="Monthly Recurring (Ex VAT)",
                value=f"£{mrc:.2f}/mo",
            )
        with kpi2:
            st.metric(
                label="One-Off Hardware (Ex VAT)",
                value=f"£{capex:.2f}",
            )
        with kpi3:
            st.metric(
                label="Total Month 1 Outlay",
                value=f"£{month_1:.2f}",
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 1. Monthly Recurring Services (Opex)")
        if st.session_state.num_licences > 0:
            st.markdown(
                f"""
                | Service Description | Quantity | Unit Price | Monthly Total |
                | :--- | :---: | :---: | :---: |
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
                | :--- | :---: | :---: | :---: |
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
            <div style="background-color: #F8FAFC; border: 1px dashed #CBD5E1; padding: 1rem; border-radius: 8px; font-size: 0.85rem; color: #64748B;">
                <strong>Commercial Terms:</strong> Quotation valid for 30 days. All prices exclude VAT. Pre-configured handsets include power adapters, desk stands, and lifetime manufacturer hardware warranties.
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
