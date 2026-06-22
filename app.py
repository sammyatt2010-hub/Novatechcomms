import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="NovaLinkComms | Smart Telephony",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Premium Design System CSS
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
        padding-top: 3rem;
        padding-bottom: 1.5rem;
    }
    
    /* Feature Cards */
    .feature-card {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border-top: 4px solid #127996;
        height: 100%;
    }
    
    /* Hardware Card Styling & Image Resizing Fix */
    .hardware-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    /* Force phone images to occupy a clean, identical box size without stretching */
    .hardware-card img {
        height: 180px !important;
        object-fit: contain !important;
        margin-bottom: 1rem;
    }
    
    /* Phone Headers Fix */
    .phone-header {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        color: #0F5A73 !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.25rem !important;
    }
    
    /* Form input styling */
    div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
    }
    input {
        color: #0F172A !important; 
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

# 3. Controlled Header & Logo Size
# Adjusted grid weight [2, 1, 2] to tightly compress the logo in the middle
logo_col1, logo_col2, logo_col3 = st.columns([2, 1, 2])
with logo_col2:
    st.image("logo.png", width=220) # Hardcoded width to stop it dominating the page

# 4. Hero Section
st.markdown('<p class="hero-title">Transform Your Business Communications</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Experience amazing efficiency and incredible cost savings with next-generation telephony systems.</p>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. Core Features
st.markdown('<p class="section-title">Why Businesses Switch to NovaLinkComms</p>', unsafe_allow_html=True)

feat_col1, feat_col2, feat_col3 = st.columns(3)
with feat_col1:
    st.markdown("""
    <div class="feature-card">
        <h3>📱 Integrated Mobile Apps</h3>
        <p style='color: #475569;'>Turn your smartphone into your desk phone. Take your business number anywhere, ensuring you never miss a vital client call, whether in the office or on the road.</p>
    </div>
    """, unsafe_allow_html=True)

with feat_col2:
    st.markdown("""
    <div class="feature-card">
        <h3>⏺️ Cloud Call Recording</h3>
        <p style='color: #475569;'>Enhance training, resolve disputes, and maintain absolute compliance with seamless, secure cloud-based call recording available at the click of a button.</p>
    </div>
    """, unsafe_allow_html=True)

with feat_col3:
    st.markdown("""
    <div class="feature-card">
        <h3>⚙️ Central Management</h3>
        <p style='color: #475569;'>Take total control with an intuitive portal. Easily manage users, configure complex call routing, and monitor system health without needing an IT background.</p>
    </div>
    """, unsafe_allow_html=True)

# 6. NEW SECTION: The Human Element (Breaking up the tech with color)
st.markdown('<p class="section-title">Built for the Modern, Flexible Workforce</p>', unsafe_allow_html=True)

img_col1, img_col2 = st.columns(2)
with img_col1:
    # High-quality vibrant hybrid team image
    st.image("https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=800", use_container_width=True)
    st.markdown("<p style='color: #475569; margin-top: 0.5rem;'><strong>In the Office:</strong> Give your teams dedicated, ultra-reliable desk hardware that speeds up collaborative tasks and client handovers.</p>", unsafe_allow_html=True)
with img_col2:
    # High-quality remote/home office image
    st.image("https://images.unsplash.com/photo-1543269865-cbf427effbad?q=80&w=800", use_container_width=True)
    st.markdown("<p style='color: #475569; margin-top: 0.5rem;'><strong>On the Go:</strong> Seamlessly switch calls over to high-performance rugged handsets or mobile applications for roaming, remote staff, and site visits.</p>", unsafe_allow_html=True)

# 7. Hardware Showcase (Uniform boxes & fixed typography)
st.markdown('<p class="section-title">Premium Enterprise Hardware</p>', unsafe_allow_html=True)

hw_col1, hw_col2, hw_col3, hw_col4 = st.columns(4)

with hw_col1:
    st.markdown('<div class="hardware-card">', unsafe_allow_html=True)
    st.image("Fanvil V67.webp", use_container_width=True)
    st.markdown('<p class="phone-header">Executive V67</p>', unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 0.85rem; margin:0;'>Flagship smart screen console</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with hw_col2:
    st.markdown('<div class="hardware-card">', unsafe_allow_html=True)
    st.image("V66 Pro.webp", use_container_width=True)
    st.markdown('<p class="phone-header">Premium V66 Pro</p>', unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 0.85rem; margin:0;'>Multi-line audio console</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with hw_col3:
    st.markdown('<div class="hardware-card">', unsafe_allow_html=True)
    st.image("Fanvil V62 Pro.png", use_container_width=True)
    st.markdown('<p class="phone-header">Essential V62 Pro</p>', unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 0.85rem; margin:0;'>Flexible wireless deployment</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with hw_col4:
    st.markdown('<div class="hardware-card">', unsafe_allow_html=True)
    st.image("Linkvil W620W Rugged.png", use_container_width=True)
    st.markdown('<p class="phone-header">Linkvil Rugged</p>', unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 0.85rem; margin:0;'>Built tough for heavy sites</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# 8. Call to Action (CTA) Form Section
st.markdown('<p class="section-title">Start Saving on Your Telecoms Today</p>', unsafe_allow_html=True)

cta_col1, cta_col2, cta_col3 = st.columns([1, 1.8, 1])
with cta_col2:
    with st.form(key="telephony_audit_form", clear_on_submit=True):
        st.markdown("<p style='color: #475569; text-align: center; margin-bottom: 1.5rem;'>Drop your details below. A telecoms expert will show you exactly how much time and money NovaLinkComms can save your business.</p>", unsafe_allow_html=True)
        
        company_name = st.text_input("Company Name")
        contact_email = st.text_input("Business Email")
        current_phones = st.number_input("Roughly how many phone users do you have?", min_value=1, value=5)
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit_button = st.form_submit_button(label="Request a Free Telephony Audit")
        
        if submit_button:
            if company_name and contact_email:
                st.success(f"Awesome! Thanks, {company_name}. We'll reach out to {contact_email} shortly to discuss your custom savings plan.")
            else:
                st.error("Please fill out your Company Name and Email.")
