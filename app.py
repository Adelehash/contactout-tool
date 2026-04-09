import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="LinkedIn Contact Finder", page_icon="📞")

st.title("📞 LinkedIn → Phone & Email Finder")

API_KEY = st.secrets["CONTACTOUT_API_KEY"]

# -------- CREDIT TRACKING --------
if "phone_credits" not in st.session_state:
    st.session_state.phone_credits = 0

if "email_credits" not in st.session_state:
    st.session_state.email_credits = 0

# -------- SIDEBAR --------
st.sidebar.title("📊 Credit Usage")
st.sidebar.write(f"📱 Phone Credits Used: {st.session_state.phone_credits}")
st.sidebar.write(f"📧 Email Credits Used: {st.session_state.email_credits}")

# -------- FUNCTION --------
def fetch_contact(linkedin_url):
    url = "https://api.contactout.com/v1/people/linkedin"

    params = {
        "profile": linkedin_url,
        "include_phone": "true"
    }

    headers = {
        "token": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        res = requests.get(url, headers=headers, params=params)
        data = res.json()

        profile = data.get("profile", {})

        phones = profile.get("phone", [])
        emails = profile.get("email", [])

        # ✅ Keep ALL phones
        phone_list = phones

        # ✅ Limit emails to MAX 2
        email_list = emails[:2]

        # ✅ Track credits
        if phones:
            st.session_state.phone_credits += len(phones)

        if email_list:
            st.session_state.email_credits += len(email_list)

        return {
            "linkedin_url": linkedin_url,
            "phone": ", ".join(phone_list) if phone_list else "",
            "emails": ", ".join(email_list) if email_list else ""
        }

    except:
        return {
            "linkedin_url": linkedin_url,
            "phone": "",
            "emails": ""
        }

# -------- MODE SWITCH --------
mode = st.radio("Select Mode", ["Single Lookup", "Bulk Upload"])

# -------- SINGLE MODE --------
if mode == "Single Lookup":
    linkedin_url = st.text_input("Enter LinkedIn Profile URL")

    if st.button("Find Contact Info"):
        if not linkedin_url:
            st.warning("Please enter a LinkedIn URL")
        else:
            with st.spinner("Fetching..."):
                result = fetch_contact(linkedin_url)

                if result["phone"]:
                    st.success("Phone Found 🎉")
                    st.write(f"📱 {result['phone']}")
                else:
                    st.warning("No phone found")

                if result["emails"]:
                    st.success("Emails Found 📧")
                    st.write(f"✉️ {result['emails']}")

# -------- BULK MODE --------
if mode == "Bulk Upload":
    uploaded_file = st.file_uploader("Upload CSV with 'linkedin_url' column", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        if "linkedin_url" not in df.columns:
            st.error("CSV must contain 'linkedin_url' column")
        else:
            st.write(f"Total rows: {len(df)}")

            if st.button("Start Bulk Processing"):
                results = []

                with st.spinner("Processing..."):
                    for i, row in df.iterrows():
                        result = fetch_contact(row["linkedin_url"])
                        results.append(result)

                result_df = pd.DataFrame(results)

                st.success("Done 🎉")
                st.dataframe(result_df)

                csv = result_df.to_csv(index=False).encode("utf-8")

                st.download_button(
                    label="Download Results CSV",
                    data=csv,
                    file_name="contact_results.csv",
                    mime="text/csv"
                )
