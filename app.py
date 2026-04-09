import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Bulk LinkedIn → Contact Finder", page_icon="📞")

st.title("📞 Bulk LinkedIn → Phone & Email Finder")

API_KEY = st.secrets["CONTACTOUT_API_KEY"]

uploaded_file = st.file_uploader("Upload CSV with LinkedIn URLs", type=["csv"])

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

        return {
            "linkedin_url": linkedin_url,
            "phone": ", ".join(phones) if phones else "",
            "emails": ", ".join(emails) if emails else ""
        }

    except:
        return {
            "linkedin_url": linkedin_url,
            "phone": "",
            "emails": ""
        }

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if "linkedin_url" not in df.columns:
        st.error("CSV must contain 'linkedin_url' column")
    else:
        results = []

        if st.button("Start Processing"):
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
