import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="NovaLinkComms | Smart Telephony",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Custom CSS for a Light, Clean, Logo-Matched Look
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background-color: #F8FAFC; 
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: #127996; 
        text-align: center;
        margin-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .hero-subtitle {
        font-size: 1.5rem;
        color: #475569; 
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 300;
    }
    .section-title {
        font-size: 2rem;
        font-weight: 700;
        color: #0F5A73; 
        text-align: center;
        padding-top: 3rem;
        padding-bottom: 1.5rem;
    }
    .feature-text {
        color: #334155;
        font-size: 1.1rem;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Header & Logo (Now pointing to the clean renamed file)
logo_col1, logo_col2, logo_col3 = st.columns([1, 2, 1])
with logo_col2:
    st.image("logo.png", use_container_width=True)

# 4. Hero Section
st.markdown('<p class="hero-title">Transform Your Business Communications</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Experience amazing efficiency and incredible cost savings with next-generation telephony systems.</p>', unsafe_allow_html=True)

st.markdown("---")

# 5. Core Features
st.markdown('<p class="section-title">More Than Just a Phone System</p>', unsafe_allow_html=True)

feat_col1, feat_col2, feat_col3 = st.columns(3)

with feat_col1:
    st.subheader("📱 Integrated Mobile Apps")
    st.markdown('<p class="feature-text">Turn your smartphone into your desk phone. Take your business number anywhere, ensuring you never miss a vital client call, whether in the office or on the road.</p>', unsafe_allow_html=True)

with feat_col2:
    st.subheader("⏺️ Call Recording")
    st.markdown('<p class="feature-text">Enhance training, resolve disputes, and maintain compliance with seamless, secure cloud-based call recording available at the click of a button.</p>', unsafe_allow_html=True)

with feat_col3:
    st.subheader("⚙️ System Management")
    st.markdown('<p class="feature-text">Take control with an intuitive online portal. Easily manage users, set up complex call routing, and monitor system health without needing an IT degree.</p>', unsafe_allow_html=True)

st.markdown("---")

# 6. Hardware Showcase
st.markdown('<p class="section-title">Premium Hardware for Every Role</p>', unsafe_allow_html=True)

hw_col1, hw_col2, hw_col3, hw_col4 = st.columns(4)

with hw_col1:
    st.image("Fanvil V67.webp", use_container_width=True)
    st.write("**Executive Video Phone**")
    st.caption("The flagship V67 for dynamic video conferencing and executive control.")

with hw_col2:
    st.image("V66 Pro.webp", use_container_width=True)
    st.write("**Premium Desk Phone**")
    st.caption("The V66 Pro offers crystal-clear audio and advanced features for power users.")

with hw_col3:
    st.image("Fanvil V62 Pro.png", use_container_width=True)
    st.write("**Essential WiFi Phone**")
    st.caption("The V62 Pro provides flexible, wireless desk deployment for modern workspaces.")

with hw_col4:
    st.image("Linkvil W620W Rugged.png", use_container_width=True)
    st.write("**Rugged Portable**")
    st.caption("The Linkvil W620W keeps warehouse and field teams connected in tough environments.")

st.markdown("---")

# 7. Call to Action (CTA)
st.markdown('<p class="section-title">Start Saving on Your Telecoms Today</p>', unsafe_allow_html=True)

cta_col1, cta_col2, cta_col3 = st.columns([1, 2, 1])
with cta_col2:
    st.write("Drop your details below. We'll show you exactly how much time and money NovaLinkComms can save your business.")
    
    with st.form(key="telephony_audit_form", clear_on_submit=True):
        company_name = st.text_input("Company Name")
        contact_email = st.text_input("Business Email")
        current_phones = st.number_input("Roughly how many phone users do you have?", min_value=1, value=5)
        
        submit_button = st.form_submit_button(label="Request a Free Telephony Audit")
        
        if submit_button:
            if company_name and contact_email:
                st.success(f"Awesome! Thanks, {company_name}. We'll reach out to {contact_email} shortly to discuss your custom savings plan.")
            else:
                st.error("Please fill out your Company Name and Email.")
