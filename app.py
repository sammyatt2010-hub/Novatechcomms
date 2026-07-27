import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# 1. Page Configuration
st.set_page_config(
    page_title="NovaLinkComms | Smart Telephony",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Premium Overhaul CSS (With Bulletproof Text Box Visibility Fixes)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background-color: #F8FAFC;
    }

    /* Hero & Titles */
    .hero-title {
        font-size: 3.2rem;
        font-weight: 800;
        color: #0F5A73;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        font-size: 1.4rem;
        color: #475569;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    .section-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0F5A73;
        text-align: center;
        padding-top: 3.5rem;
        padding-bottom: 1.5rem;
    }

    /* Feature Cards */
    .feature-card {
        background-color: #FFFFFF;
        padding: 2.2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border-top: 5px solid #127996;
        height: 100%;
    }
    .feature-card h3 {
        color: #0F5A73 !important;
        font-weight: 700 !important;
        font-size: 1.4rem !important;
        margin-bottom: 0.75rem !important;
    }

    /* Product Cards */
    .product-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
        height: 100%;
    }
    .product-name {
        text-align: center;
        color: #0F5A73;
        font-weight: 700;
        font-size: 1.2rem;
        margin-top: 0.5rem;
        margin-bottom: 0.25rem;
    }
    .product-desc {
        text-align: center;
        color: #64748B;
        font-size: 0.9rem;
        margin: 0 0 0.5rem 0;
    }
    .product-price {
        text-align: center;
        color: #127996;
        font-weight: 800;
        font-size: 1.3rem;
        margin-bottom: 0.75rem;
    }

    /* Basket panel */
    .basket-total {
        font-size: 1.3rem;
        font-weight: 800;
        color: #0F5A73;
        text-align: right;
    }

    /* Phone Image Constraints */
    div[data-testid="stColumn"] img {
        max-height: 180px !important;
        object-fit: contain !important;
    }

    /* 🚨 DEEP BOX FIX: Force backgrounds white, text dark, borders clean across ALL states */
    div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        color: #0F172A !important;
    }
    div[data-baseweb="input"] input {
        color: #0F172A !important;
        background-color: #FFFFFF !important;
        -webkit-text-fill-color: #0F172A !important;
    }
    div[data-baseweb="input"] input[type="number"] {
        color: #0F172A !important;
        background-color: #FFFFFF !important;
    }
    label {
        color: #1E293B !important;
        font-weight: 600 !important;
    }
    .stForm {
        background-color: #FFFFFF !important;
        padding: 2.5rem !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid #E2E8F0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Product Catalogue
# Pulled from catalogue.json so this page and the main quoting app's admin
# panel can share a single source of truth for pricing. Falls back to
# built-in defaults if the file isn't present so the page never breaks.
CATALOGUE_FILE = "catalogue.json"

_FALLBACK_PRODUCTS = [
    {
        "id": "v67",
        "name": "Executive V67",
        "desc": "Flagship smart screen console",
        "image": "Fanvil V67.webp",
        "price": 189.00,
    },
    {
        "id": "v66pro",
        "name": "Premium V66 Pro",
        "desc": "Multi-line audio console",
        "image": "V66 Pro.webp",
        "price": 129.00,
    },
    {
        "id": "v62pro",
        "name": "Essential V62 Pro",
        "desc": "Flexible wireless deployment",
        "image": "Fanvil V62 Pro.png",
        "price": 89.00,
    },
    {
        "id": "w620w",
        "name": "Linkvil Rugged",
        "desc": "Built tough for heavy sites",
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

# 4. Basket State
if "basket" not in st.session_state:
    st.session_state.basket = {}  # product_id -> qty


def add_to_basket(product_id, qty):
    st.session_state.basket[product_id] = st.session_state.basket.get(product_id, 0) + qty


def remove_from_basket(product_id):
    st.session_state.basket.pop(product_id, None)


def basket_items():
    items = []
    for pid, qty in st.session_state.basket.items():
        product = next((p for p in PRODUCTS if p["id"] == pid), None)
        if product and qty > 0:
            items.append({**product, "qty": qty, "line_total": product["price"] * qty})
    return items


def basket_total():
    return sum(item["line_total"] for item in basket_items())


# 5. Logo Centering Fix
logo_col1, logo_col2, logo_col3 = st.columns([1.5, 1, 1.5])
with logo_col2:
    st.image("logo.png", use_container_width=True)

# 6. Hero Section
st.markdown('<p class="hero-title">Transform Your Business Communications</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Experience amazing efficiency and incredible cost savings with next-generation telephony systems.</p>', unsafe_allow_html=True)

# 7. Basket summary bar (visible everywhere once something's added)
items_in_basket = basket_items()
basket_col1, basket_col2, basket_col3 = st.columns([1.5, 1, 1.5])
with basket_col2:
    basket_label = f"🛒 Basket ({sum(i['qty'] for i in items_in_basket)})" if items_in_basket else "🛒 Basket (empty)"
    with st.expander(basket_label, expanded=False):
        if not items_in_basket:
            st.caption("Nothing in your basket yet — add some hardware below.")
        else:
            for item in items_in_basket:
                bcol1, bcol2, bcol3, bcol4 = st.columns([3, 1, 1.5, 1])
                bcol1.write(item["name"])
                bcol2.write(f"x{item['qty']}")
                bcol3.write(f"£{item['line_total']:.2f}")
                if bcol4.button("Remove", key=f"remove_{item['id']}"):
                    remove_from_basket(item["id"])
                    st.rerun()
            st.markdown(f"<p class='basket-total'>Total: £{basket_total():.2f}</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 8. Core Features (The "Why")
st.markdown('<p class="section-title">Why Businesses Switch to NovaLinkComms</p>', unsafe_allow_html=True)

feat_col1, feat_col2, feat_col3 = st.columns(3)
with feat_col1:
    st.markdown("""
    <div class="feature-card">
        <h3>📱 Integrated Mobile Apps</h3>
        <p style='color: #475569; font-size: 1.05rem; line-height: 1.5;'>Turn your smartphone into your desk phone. Take your business number anywhere, ensuring you never miss a vital client call, whether in the office or on the road.</p>
    </div>
    """, unsafe_allow_html=True)

with feat_col2:
    st.markdown("""
    <div class="feature-card">
        <h3>⏺️ Cloud Call Recording</h3>
        <p style='color: #475569; font-size: 1.05rem; line-height: 1.5;'>Enhance training, resolve disputes, and maintain absolute compliance with seamless, secure cloud-based call recording available at the click of a button.</p>
    </div>
    """, unsafe_allow_html=True)

with feat_col3:
    st.markdown("""
    <div class="feature-card">
        <h3>⚙️ Central Management</h3>
        <p style='color: #475569; font-size: 1.05rem; line-height: 1.5;'>Take total control with an intuitive portal. Easily manage users, configure complex call routing, and monitor system health without needing an IT background.</p>
    </div>
    """, unsafe_allow_html=True)

# 9. Hybrid Workforce Image Cluster
st.markdown('<p class="section-title">Built for the Modern, Flexible Workforce</p>', unsafe_allow_html=True)

img_col1, img_col2 = st.columns(2)
with img_col1:
    st.image("https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=800", use_container_width=True)
    st.markdown("<p style='color: #334155; margin-top: 0.75rem; font-size: 1.1rem; text-align: center;'><strong>In the Office:</strong> Give your teams dedicated, ultra-reliable desk hardware that speeds up collaborative tasks and client handovers.</p>", unsafe_allow_html=True)
with img_col2:
    st.image("https://images.unsplash.com/photo-1543269865-cbf427effbad?q=80&w=800", use_container_width=True)
    st.markdown("<p style='color: #334155; margin-top: 0.75rem; font-size: 1.1rem; text-align: center;'><strong>On the Go:</strong> Seamlessly switch calls over to high-performance rugged handsets or mobile applications for roaming, remote staff, and site visits.</p>", unsafe_allow_html=True)

# 10. Hardware Showcase - now shoppable
st.markdown('<p class="section-title">Premium Enterprise Hardware</p>', unsafe_allow_html=True)

hw_cols = st.columns(4)
for col, product in zip(hw_cols, PRODUCTS):
    with col:
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        st.image(product["image"], use_container_width=True)
        st.markdown(f'<p class="product-name">{product["name"]}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="product-desc">{product["desc"]}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="product-price">£{product["price"]:.2f}</p>', unsafe_allow_html=True)

        qty = st.number_input(
            "Qty",
            min_value=1,
            value=1,
            step=1,
            key=f"qty_{product['id']}",
            label_visibility="collapsed",
        )
        if st.button("Add to Basket", key=f"add_{product['id']}", use_container_width=True):
            add_to_basket(product["id"], qty)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# 11. Checkout / Call to Action (CTA) Form Section with Data Capture
st.markdown('<p class="section-title">Checkout &amp; Request Your Free Telephony Audit</p>', unsafe_allow_html=True)

cta_col1, cta_col2, cta_col3 = st.columns([1, 1.8, 1])
with cta_col2:
    checkout_items = basket_items()
    if checkout_items:
        st.markdown("**Your basket:**")
        for item in checkout_items:
            st.write(f"- {item['name']} x{item['qty']} — £{item['line_total']:.2f}")
        st.markdown(f"**Order total: £{basket_total():.2f}**")
        st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.caption("Your basket is empty — you can still request an audit, or add hardware above first.")

    with st.form(key="telephony_audit_form", clear_on_submit=True):
        st.markdown("<p style='color: #475569; text-align: center; margin-bottom: 1.5rem;'>Drop your details below. A telecoms expert will show you exactly how much time and money NovaLinkComms can save your business.</p>", unsafe_allow_html=True)

        company_name = st.text_input("Company Name")
        contact_email = st.text_input("Business Email")
        current_phones = st.number_input("Roughly how many phone users do you have?", min_value=1, value=5)

        if checkout_items:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<p style='color: #0F5A73; font-weight:700; text-align:center;'>Delivery Address</p>", unsafe_allow_html=True)
            address_line1 = st.text_input("Address Line 1")
            address_line2 = st.text_input("Address Line 2 (optional)")
            city = st.text_input("Town / City")
            postcode = st.text_input("Postcode")

        st.markdown("<br>", unsafe_allow_html=True)
        button_label = "Request a Free Telephony Audit" if not checkout_items else "Submit Order (Invoice to Follow)"
        submit_button = st.form_submit_button(label=button_label)

        if submit_button:
            missing_address = checkout_items and not (address_line1 and city and postcode)
            if not company_name or not contact_email:
                st.error("Please fill out your Company Name and Email.")
            elif missing_address:
                st.error("Please fill out your delivery address (Address Line 1, Town/City and Postcode).")
            else:
                order_summary = "; ".join(
                    f"{item['name']} x{item['qty']}" for item in checkout_items
                ) if checkout_items else "No hardware selected"

                delivery_address = ", ".join(
                    part for part in [
                        address_line1 if checkout_items else "",
                        address_line2 if checkout_items else "",
                        city if checkout_items else "",
                        postcode if checkout_items else "",
                    ] if part
                )

                new_lead = {
                    "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "Company Name": [company_name],
                    "Business Email": [contact_email],
                    "Phone Users": [current_phones],
                    "Basket Items": [order_summary],
                    "Basket Total": [f"{basket_total():.2f}"],
                    "Delivery Address": [delivery_address],
                    "Payment Status": ["Awaiting Invoice" if checkout_items else "N/A"],
                }
                new_df = pd.DataFrame(new_lead)

                # Sheet Capture Logic: Append data to a local leads.csv file
                csv_filename = "leads.csv"
                if not os.path.isfile(csv_filename):
                    new_df.to_csv(csv_filename, index=False)
                else:
                    new_df.to_csv(csv_filename, mode='a', header=False, index=False)

                if checkout_items:
                    st.success(
                        f"Thanks, {company_name}! Your order (£{basket_total():.2f}) is confirmed and will be "
                        f"delivered to your address on file. We'll send an invoice with payment instructions to {contact_email} shortly."
                    )
                else:
                    st.success(f"Awesome! Thanks, {company_name}. We'll reach out to {contact_email} shortly to discuss your custom savings plan.")
                st.session_state.basket = {}
