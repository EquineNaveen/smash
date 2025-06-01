import streamlit as st
import os
from PIL import Image

def main():
    display_doc_instructions()

def display_doc_instructions():
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none !important;}
    div[data-testid="stSidebarNav"] {display: none;}
    button[data-testid="stBaseButton-headerNoPadding"] {display: none !important;}
    div.st-emotion-cache-1y9tyez.eczjsme4 {display: none !important;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='text-align: center;'>Gyaan Doc Instructions</h2>", unsafe_allow_html=True)

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    images_path = os.path.join(project_root, "artifacts", "doc")

    def show_image(image_name, caption):
        img_path = os.path.join(images_path, image_name)
        if os.path.exists(img_path):
            image = Image.open(img_path)
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.image(image, use_column_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(f"<h4 style='text-align: center;'>{caption}</h4>", unsafe_allow_html=True)
        else:
            st.warning(f"Image not found: {img_path}")

    # Step 1: Open Gyaan Doc (show homescreen.png)
    show_image(
        "homescreen.png",
        "Click on the <b>'Open GYAAN DOC'</b> button on the Gyaan Apps home page."
    )

    # Step 2: Browse & Upload (show upload_doc.jpg)
    show_image(
        "upload_doc.jpg",
        "Click on <b>Browse files</b> and upload your pdf, docx, doc, or txt document."
    )

    

    # Step 4: View Summary (specifics.PNG)
    show_image(
        "specifics.PNG",
        "Wait for your document to be processed after the document is processed you will see your uploaded document on the left,click on it the summary and details of the document will be displayed in the main area."
    )
    

    # Step 5: Ask Questions (ask_questions.PNG)
    show_image(
        "ask_questions.PNG",
        "Use the input bar to ask questions on the uploaded document."
    )
  

if __name__ == "__main__":
    main()