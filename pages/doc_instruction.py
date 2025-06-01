import streamlit as st
import os
from PIL import Image

def main():
    display_doc_instructions()

def display_doc_instructions():
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none !important;}
    /* Hide default Streamlit sidebar navigation */
    div[data-testid="stSidebarNav"] {
        display: none;
    }
    /* Hide sidebar collapse/expand button and its parent container */
    button[data-testid="stBaseButton-headerNoPadding"] {display: none !important;}
    div.st-emotion-cache-1y9tyez.eczjsme4 {display: none !important;}
    </style>
    """, unsafe_allow_html=True)

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    images_path = os.path.join(project_root, "artifacts", "doc")
    abs_images_path = os.path.abspath(images_path)

    if not os.path.exists(images_path):
        st.warning(f"Doc instruction images directory not found at: {abs_images_path}")
        st.info("Please create the directory and add instruction images (png, jpg, jpeg, gif) to it.")
        return

    image_files = [f for f in os.listdir(images_path)
                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    if not image_files:
        st.info("No instruction images found in the doc directory.")
        return

    st.markdown("<h3 style='text-align: center;'>Gyaan Doc Instructions</h3>", unsafe_allow_html=True)

    # Show "Upload your docs" image and instructions
    if "upload yourdocs.png" in [f.lower() for f in image_files]:
        try:
            img_path = os.path.join(images_path, "upload yourdocs.PNG")
            image = Image.open(img_path)
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.image(image, use_column_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(
                "<h3 style='text-align: center;'>Now you can browse your files here(as the red arrow shows you) and add PDF, DOCX, DOC, TXT files.</h3>",
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Error loading image upload yourdocs.PNG: {e}")

    # Show "Answer to the questions" image and instructions
    if "answr to the questuons.png" in [f.lower() for f in image_files]:
        try:
            img_path = os.path.join(images_path, "answr to the questuons.PNG")
            image = Image.open(img_path)
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.image(image, use_column_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(
                "<h3 style='text-align: center;'>Now you can ask queries and questions related to your documents(in the search bar..following the red arrow).</h3>",
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Error loading image answr to the questuons.PNG: {e}")
    # ...existing code...

    # Show "Specifics" image and instructions
    if "specifics.png" in [f.lower() for f in image_files]:
        try:
            img_path = os.path.join(images_path, "specifics.PNG")
            image = Image.open(img_path)
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.image(image, use_column_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(
                "<h3 style='text-align: center;'>The green arrow shows your uploaded document and the red arrow shows the delete button to delete the selected document.</h3>",
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Error loading image specifics.PNG: {e}")

# ...existing code...
if __name__ == "__main__":
    main()