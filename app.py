from datetime import datetime
import json
import os
import pandas as pd
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Telephony Quotation Tool",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Sleek Custom CSS (Consistent Card Heights, Bulletproof Image Sizing, Clean Inputs)
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background-color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Container Spacing */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
        max-width: 1250px !important;
    }

    /* Hero / White Label Title */
    .brand-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #0F5A73;
        text-align: center;
        margin-bottom: 0.25rem;
        letter-spacing: -0.5px;
    }
    .brand-subtitle {
        font-size: 1.1rem;
        color: #64748B;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        justify-content: center;
        border-bottom: 2px solid #E2E8F0;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1rem;
        font-weight: 700;
        color: #64748B !important;
        padding: 10px 20px;
        background-color: transparent;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        color: #0F5A73 !important;
        border-bottom: 3px solid #0F5A73 !important;
    }

    /* Section Headers */
    .step-badge {
        display: inline-block;
        background: #E0F2FE;
        color: #0369A1;
        font-weight: 700;
        font-size: 0.8rem;
        padding: 4px 12px;
        border-radius: 9999px;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .step-heading {
        font-size: 1.5rem;
        font-weight: 800;
        color: #0F5A73;
        margin-bottom: 1.25rem;
    }

    /* Licence Card */
    .licence-banner {
        background: linear-gradient(135deg, #0F5A73 0%, #164E63 100%);
        border-radius: 14px;
        padding: 1.5rem;
        color: white;
        height: 100%;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .badge-price {
        background-color: #38BDF8;
        color: #0F172A;
        font-weight: 800;
        font-size: 1rem;
        padding: 0.35rem 0.75rem;
        border-radius: 8px;
    }
    .licence-feature-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.6rem;
        font-size: 0.88rem;
        color: #F1F5F9;
        margin-top: 1rem;
    }

    /* Hardware Product Cards */
    div[data-testid="column"] {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 1.1rem !important;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03);
        display: flex;
        flex-direction: column;
    }
    
    /* 🚨 CRITICAL FIX: Uniform Handset Image Sizing Across All Models 🚨 */
    div[data-testid="column"] img {
        height: 150px !important;
        max-height: 150px !important;
        width: 100% !important;
        object-fit: contain !important;
        margin: 0.5rem 0 !important;
        background-color: #FFFFFF !important;
    }

    .prod-header {
        text-align: center;
        min-height: 75px;
    }
    .prod-name {
        font-weight: 800;
        color: #0F5A73;
        font-size: 1.05rem;
        margin-bottom: 0.2rem;
    }
    .prod-desc {
        color: #64748B;
        font-size: 0.8rem;
        line-height: 1.25;
        margin-bottom: 0.5rem;
    }
    .prod-price {
        font-size: 1.25rem;
        font-weight: 800;
        color: #0F172A;
        text-align: center;
        margin: 0.25rem 0 0.5rem 0;
    }

    /* Buttons & Inputs */
    .stButton > button {
        background-color: #0F5A73 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        border: none !important;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #0c485c !important;
        color: #FFFFFF !important;
    }
    div[data-baseweb="input"] {
        background-color: #F8FAFC !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="input"] input {
        color: #0F172A !important;
    }

    /* Customer View Proposal Card */
    .proposal-card {
        background: #FFFFFF;
        border-radius: 16px;
        border: 2px solid #0F5A73;
        padding: 2rem;
        box-shadow: 0 10px 25px -5px rgba(15, 90, 115, 0.1);
    }
    .metric-pill {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
    }
    .metric-pill-val {
        font-size: 1.75rem;
        font-weight: 800;
        color: #0F5A73;
    }
    .metric-pill-lbl {
        font-size: 0.78rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.2rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 3. Product Catalogue & Constants
LICENCE_MONTHLY_RATE = 7.00
CATALOGUE_FILE = "catalogue.json"

_FALLBACK_PRODUCTS = [
    {
        "id": "v67",
        "name": "Executive V67",
        "desc": "Flagship 7-inch colour touch screen with HD video and Wi-Fi",
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

# 4. State Management
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


# 5. Header / Brand Bar
st.markdown(
    '<div class="brand-title">Telephony Quotation Tool</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="brand-subtitle">Interactive white-label quote builder: combine cloud user licences with desktop hardware</div>',
    unsafe_allow_html=True,
)

# 6. Tab Navigation
tab_builder, tab_customer_view = st.tabs(
    ["🛠️ Build Quotation", "💼 Customer Presentation View"]
)

with tab_builder:
    # --- Step 1: Hosted User Licences ---
    st.markdown(
        '<span class="step-badge">Step 1</span><div class="step-heading">Hosted User Licences (Monthly Opex)</div>',
        unsafe_allow_html=True,
    )

    lic_col1, lic_col2 = st.columns([3, 2], gap="large")

    with lic_col1:
        st.markdown(
            f"""
            <div class="licence-banner">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; color: #FFFFFF; font-size: 1.35rem; font-weight: 800;">Hosted Cloud User Licence</h3>
                    <span class="badge-price">£{LICENCE_MONTHLY_RATE:.2f} / user / mo</span>
                </div>
                <p style="color: #E2E8F0; font-size: 0.9rem; margin: 0.75rem 0 1rem 0;">
                    Complete unified communications package per seat with enterprise features included:
                </p>
                <div class="licence-feature-grid">
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

        # User Presets
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
            <div style="background: #F1F5F9; border-radius: 10px; padding: 0.85rem; margin-top: 0.75rem; text-align: center; border-left: 4px solid #0F5A73;">
                <div style="font-size: 0.8rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Total Licence Opex</div>
                <div style="font-size: 1.5rem; font-weight: 800; color: #0F5A73;">£{total_monthly_licences():.2f} <span style="font-size: 0.85rem; font-weight: normal; color: #475569;">/ month</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # --- Step 2: Handsets & Hardware ---
    st.markdown(
        '<span class="step-badge">Step 2</span><div class="step-heading">Optional Enterprise Handsets (Upfront Capex)</div>',
        unsafe_allow_html=True,
    )

    hw_cols = st.columns(4, gap="medium")
    for col, product in zip(hw_cols, PRODUCTS):
        with col:
            # Top card content
            st.markdown(
                f"""
                <div class="prod-header">
                    <div class="prod-name">{product["name"]}</div>
                    <div class="prod-desc">{product["desc"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Strict 150px normalized height image
            if os.path.exists(product["image"]):
                st.image(product["image"])
            else:
                st.caption("No image file found")

            st.markdown(
                f'<div class="prod-price">£{product["price"]:.2f} <span style="font-size: 0.8rem; font-weight: 500; color: #64748B;">each</span></div>',
                unsafe_allow_html=True,
            )

            # Bottom Controls
            qty = st.number_input(
                "Qty",
                min_value=1,
                max_value=100,
                value=1,
                step=1,
                key=f"qty_{product['id']}",
                label_visibility="collapsed",
            )
            if st.button(
                f"Add to Basket",
                key=f"btn_{product['id']}",
                use_container_width=True,
            ):
                add_to_basket(product["id"], qty)
                st.toast(f"Added {qty}x {product['name']}", icon="✅")
                st.rerun()

    # --- Basket Tray ---
    hardware_list = basket_items()
    if hardware_list:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander(
            f"🛒 Hardware Basket ({sum(i['qty'] for i in hardware_list)} items selected) — Total: £{total_hardware_capex():.2f}",
            expanded=True,
        ):
            for item in hardware_list:
                b1, b2, b3, b4 = st.columns([3, 1, 1.5, 1])
                b1.write(f"**{item['name']}**")
                b2.write(f"x{item['qty']}")
                b3.write(f"£{item['line_total']:.2f}")
                if b4.button("Remove", key=f"del_{item['id']}"):
                    remove_from_basket(item["id"])
                    st.rerun()

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # --- Step 3: Checkout Form ---
    st.markdown(
        '<span class="step-badge">Step 3</span><div class="step-heading">Client Details &amp; Quote Submission</div>',
        unsafe_allow_html=True,
    )

    f_col1, f_col2, f_col3 = st.columns([1, 2.5, 1])
    with f_col2:
        with st.form(key="telephony_quote_form"):
            c_name = st.text_input(
                "Company Name*", placeholder="e.g. Acme Corporation"
            )
            p_name = st.text_input(
                "Contact Name*", placeholder="e.g. John Doe"
            )
            c_email = st.text_input(
                "Business Email*", placeholder="john@acme.com"
            )
            c_phone = st.text_input("Contact Number", placeholder="01234 567890")

            needs_shipping = len(hardware_list) > 0
            if needs_shipping:
                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown(
                    "**Hardware Delivery Address** *(Required for dispatch)*"
                )
                a1 = st.text_input("Address Line 1*")
                city = st.text_input("Town / City*")
                postcode = st.text_input("Postcode*")
            else:
                a1 = city = postcode = ""

            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button(
                "Generate & Save Quotation", use_container_width=True
            )

            if submitted:
                if not c_name or not p_name or not c_email:
                    st.error("Please provide Company Name, Contact Name, and Email.")
                elif needs_shipping and (not a1 or not city or not postcode):
                    st.error("Please fill in the physical delivery address.")
                else:
                    ref = f"TQT-{datetime.now().strftime('%y%m%d%H%M')}"
                    hw_summary = (
                        "; ".join(
                            f"{i['name']} x{i['qty']}" for i in hardware_list
                        )
                        if hardware_list
                        else "No Hardware"
                    )

                    new_lead = {
                        "Quote Ref": [ref],
                        "Date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                        "Company": [c_name],
                        "Contact": [p_name],
                        "Email": [c_email],
                        "Phone": [c_phone],
                        "Licence Count": [st.session_state.num_licences],
                        "Monthly Licence Opex": [
                            f"£{total_monthly_licences():.2f}"
                        ],
                        "Hardware Summary": [hw_summary],
                        "Hardware Capex": [f"£{total_hardware_capex():.2f}"],
                        "Delivery Address": [
                            f"{a1}, {city}, {postcode}"
                            if needs_shipping
                            else "N/A"
                        ],
                    }
                    df = pd.DataFrame(new_lead)
                    csv_path = "quotes.csv"
                    if not os.path.isfile(csv_path):
                        df.to_csv(csv_path, index=False)
                    else:
                        df.to_csv(csv_path, mode="a", header=False, index=False)

                    st.success(
                        f"Quotation #{ref} generated and recorded successfully!"
                    )


with tab_customer_view:
    # --- Professional Client-Facing Presentation Card ---
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 4, 1])

    with c2:
        mrc = total_monthly_licences()
        capex = total_hardware_capex()
        month_1 = mrc + capex
        h_items = basket_items()

        st.markdown(
            f"""
            <div class="proposal-card">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #E2E8F0; padding-bottom: 1rem; margin-bottom: 1.5rem;">
                    <div>
                        <h2 style="color: #0F5A73; margin: 0; font-size: 1.8rem; font-weight: 800;">Telephony Solution Quotation</h2>
                        <div style="color: #64748B; font-size: 0.95rem;">Cloud VoIP &amp; Unified Communications Breakdown</div>
                    </div>
                    <div style="background: #E0F2FE; color: #0369A1; font-weight: 700; padding: 6px 14px; border-radius: 8px; font-size: 0.85rem;">
                        {datetime.now().strftime('%d %B %Y')}
                    </div>
                </div>

                <!-- Three Pillar Metric Cards -->
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-bottom: 2rem;">
                    <div class="metric-pill" style="border-left: 4px solid #0F5A73;">
                        <div class="metric-pill-val">£{mrc:.2f}</div>
                        <div class="metric-pill-lbl">Monthly Recurring (Ex VAT)</div>
                    </div>
                    <div class="metric-pill" style="border-left: 4px solid #38BDF8;">
                        <div class="metric-pill-val">£{capex:.2f}</div>
                        <div class="metric-pill-lbl">One-off Hardware (Ex VAT)</div>
                    </div>
                    <div class="metric-pill" style="border-left: 4px solid #10B981;">
                        <div class="metric-pill-val" style="color: #0F172A;">£{month_1:.2f}</div>
                        <div class="metric-pill-lbl">Total Month 1 Outlay</div>
                    </div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### 1. Monthly Recurring Services (Opex)")
        if st.session_state.num_licences > 0:
            st.markdown(
                f"""
                | Service Item | Quantity | Unit Price | Monthly Total |
                | :--- | :--- | :--- | :--- |
                | **Hosted VoIP User Licence** (Desktop & Mobile Apps, Call Recording, Inclusive UK Mins) | {st.session_state.num_licences} Users | £{LICENCE_MONTHLY_RATE:.2f} / mo | **£{mrc:.2f} / mo** |
                """
            )
        else:
            st.caption("No user licences currently selected.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 2. Hardware & Endpoints (Capex)")
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
            <div style="background-color: #F8FAFC; border: 1px dashed #CBD5E1; padding: 1rem; border-radius: 8px; font-size: 0.85rem; color: #64748B;">
                <strong>Commercial Notes:</strong> All quotations valid for 30 days. All prices exclude VAT. Pre-configured handsets include power supplies, desk stands, and lifetime manufacturer hardware warranties.
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
