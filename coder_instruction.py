import streamlit as st
import os
from PIL import Image

def main():
    display_gyaan_coder()

def display_gyaan_coder():
    
    # Display images from the coder folder
    images_path = os.path.join("artifacts", "coder")
    
    # Check if directory exists
    if os.path.exists(images_path):
        image_files = [f for f in os.listdir(images_path)
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        
        if image_files:
            st.markdown("<h3 style='text-align: center;'>Gyaan Coder Instructions</h3>", unsafe_allow_html=True)
            
            # Display images individually instead of using a for loop
            if len(image_files) > 0:
                try:
                    img_path = os.path.join(images_path, image_files[1])
                    image = Image.open(img_path)
                    # Display image without columns, auto-fit to page width
                    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                    st.image(image, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    # Center align the subheader using HTML with normal sentence case
                    st.markdown("<h3 style='text-align: center;'>Navigate to the Gyaan Coder option on the home page interface</h3>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error loading image {image_files[1]}: {e}")
            
            if len(image_files) > 1:
                try:
                    img_path = os.path.join(images_path, image_files[0])
                    image = Image.open(img_path)
                    # Display image without columns, auto-fit to page width
                    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                    st.image(image, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    # Center align the subheader using HTML with normal sentence case
                    st.markdown("<h3 style='text-align: center;'>Input your technical query in the designated search field and submit to receive appropriate code solutions or troubleshooting assistance</h3>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error loading image {image_files[0]}: {e}")

if __name__ == "__main__":
    main()