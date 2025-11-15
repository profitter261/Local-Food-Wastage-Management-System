import streamlit as st

# --- About / Contact Creator ---
st.markdown("---")  # horizontal line to separate sections
st.header("👤 About the Creator")

col1, col2 = st.columns([2, 2], gap="large")

with col2:
    st.image("https://avatars.githubusercontent.com/u/583231?v=4")  # example image, replace with yours

with col1:
    st.markdown("""
**Name:** Arvind S  
**Role:** Aspiring Data Scientist & Dashboard Developer  

**Connect with me:**  
- 📧 Email: [jellypie03@gmail.com](mailto:jellypie03@gmail.com)  
- 💼 LinkedIn: [linkedin.com/in/johndoe](www.linkedin.com/in/arvind-s-99914a24a)  
- 🐙 GitHub: [https://github.com/profitter261](https://github.com/profitter261)  

*Thank you for using this dashboard! For suggestions or bug reports, feel free to reach out.*
""")
