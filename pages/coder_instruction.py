import streamlit as st
import os
from PIL import Image

def main():
    display_gyaan_coder()

def display_gyaan_coder():
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
    images_path = os.path.join(project_root, "artifacts", "coder")
    abs_images_path = os.path.abspath(images_path)

    if not os.path.exists(images_path):
        st.warning(f"Coder instruction images directory not found at: {abs_images_path}")
        st.info("Please create the directory and add instruction images (png, jpg, jpeg, gif) to it.")
        return

    image_files = [f for f in os.listdir(images_path)
                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    if not image_files:
        st.info("No instruction images found in the coder directory.")
        return

    st.markdown("<h3 style='text-align: center;'>Gyaan Coder Instructions</h3>", unsafe_allow_html=True)

    # Display images with checks for their existence
    if len(image_files) > 1:
        try:
            img_path = os.path.join(images_path, image_files[1])
            image = Image.open(img_path)
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.image(image, use_column_width=True)  
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center;'>Navigate to the Gyaan Coder button on the home page.</h3>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading image {image_files[1]}: {e}")

    if len(image_files) > 0:
        try:
            img_path = os.path.join(images_path, image_files[0])
            image = Image.open(img_path)
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.image(image, use_column_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center;'>Input your query in the designated search field and submit to receive appropriate code solutions or troubleshooting assistance</h3>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading image {image_files[0]}: {e}")

if __name__ == "__main__":
    main()