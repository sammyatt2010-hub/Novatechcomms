import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# 1. Page Configuration (White-labelled)
st.set_page_config(
    page_title="Telephony Quotation Tool",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Modern Design CSS (Dark text, clean cards, customer summary styling)
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

    /* Hero & Headers */
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #0F5A73;
        text-align: center;
        margin-bottom: 0.4rem;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 1.25rem;
        color: #475569;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    .section-title {
        font-size: 1.85rem;
        font-weight: 700;
        color: #0F5A73;
        text-align: center;
        padding-top: 2.5rem;
        padding-bottom: 1rem;
    }

    /* Feature & Config Cards */
    .licence-card {
        background: linear-gradient(135deg, #0F5A73 0%, #164E63 100%);
        color: #FFFFFF;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(15, 90, 115, 0.25);
        margin-bottom: 1.5rem;
    }
    .licence-price-badge {
        background-color: #38BDF8;
        color: #0F172A;
        font-weight: 800;
        font-size: 1.15rem;
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        display: inline-block;
    }

    /* Product Cards */
    .product-card {
        background-color: #FFFFFF;
        padding: 1.25rem;
        border-radius: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .product-name {
        text-align: center;
        color: #0F5A73;
        font-weight: 700;
        font-size: 1.15rem;
        margin-top: 0.5rem;
        margin-bottom: 0.2rem;
    }
    .product-desc {
        text-align: center;
        color: #64748B;
        font-size: 0.85rem;
        min-height: 38px;
        margin-bottom: 0.5rem;
    }
    .product-price {
        text-align: center;
        color: #0F172A;
        font-weight: 800;
        font-size: 1.25rem;
        margin-bottom: 0.5rem;
    }

    /* Customer View Panel */
    .quote-box {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 2rem;
        border: 2px solid #0F5A73;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.07);
    }
    .quote-stat-box {
        background: #F1F5F9;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        border-left: 4px solid #0F5A73;
    }
    .quote-stat-num {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0F5A73;
    }
    .quote-stat-label {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Form & Input Overhauls */
    div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        color: #0F172A !important;
    }
    div[data-baseweb="input"] input {
        color: #0F172A !important;
        background-color: #FFFFFF !important;
    }
    label {
        color: #1E293B !important;
        font-weight: 600 !important;
    }
    .stForm {
        background-color: #FFFFFF !important;
        padding: 2rem !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid #E2E8F0 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 3. Product Catalogue & Licence Rates
LICENCE_MONTHLY_RATE = 7.00  # £7.00 / user / month
CATALOGUE_FILE = "catalogue.json"

_FALLBACK_PRODUCTS = [
    {
        "id": "v67",
        "name": "Executive V67",
        "desc": "Flagship smart touch console with HD video",
        "image": "Fanvil V67.webp",
        "price": 189.00,
    },
    {
        "id": "v66pro",
        "name": "Premium V66 Pro",
        "desc": "Multi-line executive audio console with colour display",
        "image": "V66 Pro.webp",
        "price": 129.00,
    },
    {
        "id": "v62pro",
        "name": "Essential V62 Pro",
        "desc": "Standard office desktop phone with Gigabit PoE",
        "image": "Fanvil V62 Pro.png",
        "price": 89.00,
    },
    {
        "id": "w620w",
        "name": "Linkvil Rugged",
        "desc": "Heavy-duty drop-proof Wi-Fi roaming handset",
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

# 4. Session State Management
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
        product = next((p for p in PRODUCTS if p["id"] == pid), None)
        if product and qty > 0:
            items.append({**product, "qty": qty, "line_total": product["price"] * qty})
    return items


def total_hardware_capex():
    return sum(item["line_total"] for item in basket_items())


def total_monthly_licences():
    return st.session_state.num_licences * LICENCE_MONTHLY_RATE


# 5. Header / Brand Bar
head_col1, head_col2, head_col3 = st.columns([1, 4, 1])
with head_col2:
    st.markdown(
        '<p class="hero-title">Telephony Quotation Tool</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="hero-subtitle">Interactive white-label quote builder: combine cloud user licences with desktop hardware</p>',
        unsafe_allow_html=True,
    )

# 6. Tab Navigation: Quote Builder vs. Customer Presentation View
tab_builder, tab_customer_view = st.tabs(
    ["🛠️ Build Quotation", "💼 Customer Presentation View"]
)

with tab_builder:
    # --- SECTION A: Hosted User Licences ---
    st.markdown(
        '<p class="section-title">Step 1: Hosted User Licences (Monthly Opex)</p>',
        unsafe_allow_html=True,
    )

    col_lic_info, col_lic_ctrl = st.columns([3, 2])

    with col_lic_info:
        st.markdown(
            f"""
            <div class="licence-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                    <h3 style="margin: 0; font-size: 1.5rem; color: #FFFFFF;">Hosted VoIP Cloud User Licence</h3>
                    <span class="licence-price-badge">£{LICENCE_MONTHLY_RATE:.2f} / user / mo</span>
                </div>
                <p style="color: #E2E8F0; font-size: 0.95rem; margin-bottom: 1rem;">
                    Full-featured cloud extension licence with enterprise capabilities:
                </p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; color: #F1F5F9; font-size: 0.9rem;">
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

    with col_lic_ctrl:
        st.markdown("#### Select Required Licences")
        selected_licences = st.number_input(
            "Total Hosted Users",
            min_value=0,
            max_value=1000,
            value=st.session_state.num_licences,
            step=1,
            key="licence_input",
            help="Every team member needing a direct dial, extension, or app access requires 1 user licence.",
        )
        st.session_state.num_licences = selected_licences

        preset_cols = st.columns(4)
        if preset_cols[0].button("5 Users"):
            st.session_state.num_licences = 5
            st.rerun()
        if preset_cols[1].button("10 Users"):
            st.session_state.num_licences = 10
            st.rerun()
        if preset_cols[2].button("20 Users"):
            st.session_state.num_licences = 20
            st.rerun()
        if preset_cols[3].button("50 Users"):
            st.session_state.num_licences = 50
            st.rerun()

        st.metric(
            label="Total Licence Cost (Per Month)",
            value=f"£{total_monthly_licences():.2f}/mo",
            delta=f"{st.session_state.num_licences} users @ £{LICENCE_MONTHLY_RATE:.2f}",
        )

    # --- SECTION B: Hardware Selection ---
    st.markdown(
        '<p class="section-title">Step 2: Optional Handsets &amp; Hardware (Upfront Capex)</p>',
        unsafe_allow_html=True,
    )

    hw_cols = st.columns(4)
    for col, product in zip(hw_cols, PRODUCTS):
        with col:
            st.markdown(
                f"""
                <div class="product-card">
                    <div>
                        <p class="product-name">{product["name"]}</p>
                        <p class="product-desc">{product["desc"]}</p>
                        <p class="product-price">£{product["price"]:.2f} <span style="font-size: 0.8rem; color: #64748B;">each</span></p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if os.path.exists(product["image"]):
                st.image(product["image"], use_container_width=True)

            qty = st.number_input(
                "Qty",
                min_value=1,
                max_value=250,
                value=1,
                step=1,
                key=f"qty_{product['id']}",
                label_visibility="collapsed",
            )
            if st.button(
                f"Add {product['name']}",
                key=f"btn_{product['id']}",
                use_container_width=True,
            ):
                add_to_basket(product["id"], qty)
                st.toast(f"Added {qty}x {product['name']} to quote!", icon="✅")
                st.rerun()

    # --- Live Builder Basket Bar ---
    hardware_list = basket_items()
    if hardware_list:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander(
            f"🛒 Hardware Basket ({sum(i['qty'] for i in hardware_list)} items) — Subtotal: £{total_hardware_capex():.2f}",
            expanded=True,
        ):
            for item in hardware_list:
                bcol1, bcol2, bcol3, bcol4 = st.columns([3, 1, 1.5, 1])
                bcol1.write(f"**{item['name']}**")
                bcol2.write(f"x{item['qty']}")
                bcol3.write(f"£{item['line_total']:.2f}")
                if bcol4.button("Remove", key=f"remove_btn_{item['id']}"):
                    remove_from_basket(item["id"])
                    st.rerun()

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # --- Checkout / Quote Finalisation Form ---
    st.markdown(
        '<p class="section-title">Step 3: Generate Formal Quote &amp; Delivery</p>',
        unsafe_allow_html=True,
    )

    form_col1, form_col2, form_col3 = st.columns([1, 2, 1])
    with form_col2:
        with st.form(key="quotation_lead_form", clear_on_submit=False):
            st.markdown(
                "##### Recipient Details",
                help="These details will populate your quotation document.",
            )
            company_name = st.text_input(
                "Company Name*", placeholder="e.g. Apex Logistics Ltd"
            )
            contact_name = st.text_input(
                "Contact Name*", placeholder="e.g. John Smith"
            )
            contact_email = st.text_input(
                "Email Address*", placeholder="john@apexlogistics.co.uk"
            )
            contact_phone = st.text_input(
                "Phone Number", placeholder="e.g. 020 7946 0991"
            )

            needs_delivery = len(hardware_list) > 0
            if needs_delivery:
                st.markdown("<hr style='margin: 1.2rem 0;'>", unsafe_allow_html=True)
                st.markdown(
                    "##### Hardware Delivery Address",
                    help="Required for hardware dispatch.",
                )
                addr_line1 = st.text_input("Address Line 1*")
                addr_line2 = st.text_input("Address Line 2 (Optional)")
                city = st.text_input("Town / City*")
                postcode = st.text_input("Postcode*")
            else:
                addr_line1 = addr_line2 = city = postcode = ""

            notes = st.text_area(
                "Special Notes / Existing Provider (Optional)",
                placeholder="Mention number ports, broadband, or current contract end date...",
            )

            submit_btn = st.form_submit_button(
                label="Save & Submit Quotation", use_container_width=True
            )

            if submit_btn:
                missing_core = (
                    not company_name or not contact_name or not contact_email
                )
                missing_addr = needs_delivery and (
                    not addr_line1 or not city or not postcode
                )

                if missing_core:
                    st.error("Please fill in Company Name, Contact Name, and Email.")
                elif missing_addr:
                    st.error(
                        "Hardware has been selected. Please complete the delivery address fields."
                    )
                else:
                    quote_ref = f"TQT-{datetime.now().strftime('%y%m%d%H%M')}"
                    hardware_summary = (
                        "; ".join(
                            f"{item['name']} x{item['qty']} (£{item['line_total']:.2f})"
                            for item in hardware_list
                        )
                        if hardware_list
                        else "No Hardware (App/Licences Only)"
                    )
                    full_address = (
                        ", ".join(
                            [
                                p
                                for p in [addr_line1, addr_line2, city, postcode]
                                if p.strip()
                            ]
                        )
                        if needs_delivery
                        else "N/A"
                    )

                    new_record = {
                        "Quote Ref": [quote_ref],
                        "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                        "Company": [company_name],
                        "Contact": [contact_name],
                        "Email": [contact_email],
                        "Phone": [contact_phone],
                        "Licence Count": [st.session_state.num_licences],
                        "Monthly Licences (£)": [
                            f"{total_monthly_licences():.2f}"
                        ],
                        "Hardware Summary": [hardware_summary],
                        "Hardware Upfront (£)": [
                            f"{total_hardware_capex():.2f}"
                        ],
                        "Delivery Address": [full_address],
                        "Notes": [notes],
                    }

                    df = pd.DataFrame(new_record)
                    csv_name = "quotes.csv"
                    if not os.path.isfile(csv_name):
                        df.to_csv(csv_name, index=False)
                    else:
                        df.to_csv(
                            csv_name, mode="a", header=False, index=False
                        )

                    st.success(f"Quotation #{quote_ref} saved successfully!")
                    st.info(
                        "Click the **💼 Customer Presentation View** tab above to view the formal client breakdown."
                    )


with tab_customer_view:
    # --- SECTION C: Dedicated Customer Presentation View ---
    st.markdown("<br>", unsafe_allow_html=True)
    summary_col1, summary_col2, summary_col3 = st.columns([1, 4, 1])

    with summary_col2:
        mrc_total = total_monthly_licences()
        hardware_items = basket_items()
        capex_total = total_hardware_capex()
        first_month_outlay = mrc_total + capex_total

        st.markdown(
            f"""
            <div class="quote-box">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #E2E8F0; padding-bottom: 1.5rem; margin-bottom: 1.5rem;">
                    <div>
                        <h2 style="color: #0F5A73; margin: 0; font-size: 1.8rem; font-weight: 800;">Telephony Solution Quotation</h2>
                        <p style="color: #64748B; margin: 0.25rem 0 0 0; font-size: 0.95rem;">Independent Enterprise Communications Proposal</p>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: #E2E8F0; color: #334155; font-size: 0.8rem; padding: 0.35rem 0.75rem; border-radius: 6px; font-weight: 700;">
                            DATE: {datetime.now().strftime('%d/%m/%Y')}
                        </span>
                    </div>
                </div>

                <!-- Headline Totals -->
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-bottom: 2rem;">
                    <div class="quote-stat-box">
                        <div class="quote-stat-num">£{mrc_total:.2f}</div>
                        <div class="quote-stat-label">Monthly Recurring (Ex VAT)</div>
                    </div>
                    <div class="quote-stat-box">
                        <div class="quote-stat-num">£{capex_total:.2f}</div>
                        <div class="quote-stat-label">One-off Hardware (Ex VAT)</div>
                    </div>
                    <div class="quote-stat-box" style="border-left-color: #38BDF8;">
                        <div class="quote-stat-num" style="color: #0F172A;">£{first_month_outlay:.2f}</div>
                        <div class="quote-stat-label">Total Month 1 Outlay</div>
                    </div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        # Tabular breakdown
        st.markdown("#### 1. Ongoing Monthly Services (Opex)")
        if st.session_state.num_licences > 0:
            st.markdown(
                f"""
                | Service Item | Unit Price | Users / Qty | Monthly Total |
                | :--- | :--- | :--- | :--- |
                | **Hosted VoIP Cloud User Licence** (Apps, Recording, Inclusive UK Mins) | £{LICENCE_MONTHLY_RATE:.2f} / mo | {st.session_state.num_licences} | **£{mrc_total:.2f} / mo** |
                """
            )
        else:
            st.caption("No monthly user licences currently selected.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 2. Physical Handsets & Hardware (Capex)")
        if hardware_items:
            table_rows = "\n".join(
                f"| **{i['name']}** - {i['desc']} | £{i['price']:.2f} | {i['qty']} | £{i['line_total']:.2f} |"
                for i in hardware_items
            )
            st.markdown(
                f"""
                | Handset Model | Unit Price | Qty | Line Total |
                | :--- | :--- | :--- | :--- |
                {table_rows}
                | **Hardware Subtotal** | | | **£{capex_total:.2f}** |
                """
            )
        else:
            st.info(
                "No hardware added. Users can make and take calls using the inclusive Windows, Mac, iOS, and Android softphone applications."
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="background-color: #F8FAFC; padding: 1rem 1.25rem; border-radius: 8px; border: 1px dashed #CBD5E1; font-size: 0.85rem; color: #64748B;">
                <strong>Terms & Notes:</strong> All quotations are subject to standard telecoms terms and valid for 30 days. Prices exclude VAT. Hosted licences operate on rolling 30-day or 12-month agreements. Handset hardware includes manufacturer warranty and plug-and-play pre-provisioning.
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
