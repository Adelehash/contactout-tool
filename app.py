import streamlit as st
import requests

st.set_page_config(page_title="LinkedIn → Phone Finder", page_icon="📞")

st.title("📞 LinkedIn URL → Phone Finder")

API_KEY = st.secrets["CONTACTOUT_API_KEY"]

linkedin_url = st.text_input("Enter LinkedIn Profile URL")

if st.button("Find Contact Info"):

    if not linkedin_url:
        st.warning("Please enter a LinkedIn URL")
    else:
        with st.spinner("Fetching contact details..."):

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
                response = requests.get(url, headers=headers, params=params)
                data = response.json()

                profile = data.get("profile", {})

                phones = profile.get("phone", [])
                emails = profile.get("email", [])

                if phones:
                    st.success("Phone Found 🎉")
                    for p in phones:
                        st.write(f"📱 {p}")
                else:
                    st.warning("No phone found")

                if emails:
                    st.success("Emails Found 📧")
                    for e in emails:
                        st.write(f"✉️ {e}")

                if not phones and not emails:
                    st.error("No contact info found")

                with st.expander("Full Response"):
                    st.json(data)

            except Exception as e:
                st.error(f"Error: {e}")