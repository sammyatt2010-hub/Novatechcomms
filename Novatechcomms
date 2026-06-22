import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Next-Gen B2B Telecoms",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Custom CSS for a Polished, Professional Look
st.markdown("""
    <style>
    /* Hide the default Streamlit menu and footer for a cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom styling for headers */
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        color: #1E3A8A; /* Deep Trust Blue */
        text-align: center;
        margin-bottom: 1rem;
    }
    .hero-subtitle {
        font-size: 1.5rem;
        color: #4B5563; /* Slate Gray */
        text-align: center;
        margin-bottom: 3rem;
    }
    .section-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1E3A8A;
        text-align: center;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Hero Section (The Hook)
st.markdown('<p class="hero-title">Reliable. Scalable. Smart Telecoms.</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Empowering your business with enterprise-grade connectivity and communication solutions.</p>', unsafe_allow_html=True)

# Place a stunning hero banner image (Replace with your actual image path or URL)
# Recommendation: A high-quality abstract tech background or a modern office setup
st.image("https://images.unsplash.com/photo-1557426305-2822e3045388?q=80&w=1470", use_container_width=True)

st.markdown("---")

# 4. What We Do Section (The Core Offerings)
st.markdown('<p class="section-title">Our Core B2B Solutions</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    # Feature 1: VoIP / Hosted Phone Systems
    st.image("https://images.unsplash.com/photo-1543269865-cbf427effbad?q=80&w=500", use_container_width=True)
    st.subheader("Unified Communications")
    st.write("Cloud-based VoIP solutions that keep your team connected anywhere, on any device. Features crystal-clear HD voice, video conferencing, and seamless CRM integration.")

with col2:
    # Feature 2: Business Broadband & Leased Lines
    st.image("https://images.unsplash.com/photo-1600132806370-bf17e65e942f?q=80&w=500", use_container_width=True)
    st.subheader("Ultra-Fast Connectivity")
    st.write("Dedicating leased lines and business broadband with 99.9% uptime SLAs. Keep your operations running at the speed of light without interruption.")

with col3:
    # Feature 3: Mobile Fleet Management
    st.image("https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=500", use_container_width=True)
    st.subheader("Business Mobile Plans")
    st.write("Tailored multi-network SIMs and mobile fleet management solutions to ensure your remote and field teams stay connected seamlessly.")

st.markdown("---")

# 5. Call to Action (CTA) & Interaction
st.markdown('<p class="section-title">Ready to Upgrade Your Connectivity?</p>', unsafe_allow_html=True)

# Center the contact button using columns
cta_col1, cta_col2, cta_col3 = st.columns([1, 2, 1])
with cta_col2:
    st.write("Drop your details below and a telecoms expert will build a bespoke quote for your business.")
    
    with st.form(key="lead_form", clear_on_submit=True):
        company_name = st.text_input("Company Name")
        contact_email = st.text_input("Business Email")
        requirements = st.multiselect(
            "What solutions are you looking for?",
            ["VoIP Phone Systems", "Leased Lines / Broadband", "Business Mobile", "Not sure / General Audit"]
        )
        submit_button = st.form_submit_button(label="Request a Free Telecoms Audit")
        
        if submit_button:
            if company_name and contact_email:
                st.success(f"Thank you, {company_name}! We'll reach out to {contact_email} shortly.")
                # Here you can add code to append data to a database, csv, or trigger a webhook
            else:
                st.error("Please fill out your Company Name and Email.")
