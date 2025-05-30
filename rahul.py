import streamlit as st
import os
from PIL import Image

def main():
    # Create sidebar
    st.sidebar.title("Navigation")
    
    # Create Gyaan Meeting button in sidebar
    if st.sidebar.button("Gyaan Meeting"):
        display_gyaan_meeting()

def display_gyaan_meeting():
    # Display heading
    st.title("Gyaan Meeting")
    
    # Display images from the meeting folder
    images_path = os.path.join("rahul", "rahul", "meeting")
    
    # Check if directory exists
    if os.path.exists(images_path):
        image_files = [f for f in os.listdir(images_path) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        
        if image_files:
            st.subheader("Meeting Images")
            
            # Display images individually instead of using a for loop
            if len(image_files) > 0:
                try:
                    img_path = os.path.join(images_path, image_files[0])
                    image = Image.open(img_path)
                    st.image(image, caption=image_files[0], use_container_width=True)
                    st.subheader("enter the name of the meeting")
                except Exception as e:
                    st.error(f"Error loading image {image_files[0]}: {e}")
            
            if len(image_files) > 1:
                try:
                    img_path = os.path.join(images_path, image_files[1])
                    image = Image.open(img_path)
                    st.image(image, caption=image_files[1], use_container_width=True)
                    st.subheader("enter you name in the meeting")
                except Exception as e:
                    st.error(f"Error loading image {image_files[1]}: {e}")
            
            if len(image_files) > 2:
                try:
                    img_path = os.path.join(images_path, image_files[2])
                    image = Image.open(img_path)
                    st.image(image, caption=image_files[2], use_container_width=True)
                    st.subheader("click on three dots in the bottom and start recording")
                except Exception as e:
                    st.error(f"Error loading image {image_files[2]}: {e}")
            
            if len(image_files) > 3:
                try:
                    img_path = os.path.join(images_path, image_files[3])
                    image = Image.open(img_path)
                    st.image(image, caption=image_files[3], use_container_width=True)
                    st.subheader("select chrome tab")
                except Exception as e:
                    st.error(f"Error loading image {image_files[3]}: {e}")
                    
            if len(image_files) > 4:
                try:
                    img_path = os.path.join(images_path, image_files[4])
                    image = Image.open(img_path)
                    st.image(image, caption=image_files[4], use_container_width=True)  
                    st.subheader("click on the share button")
                except Exception as e:
                    st.error(f"Error loading image {image_files[4]}: {e}")
                    
            if len(image_files) > 5:
                try:
                    img_path = os.path.join(images_path, image_files[5])
                    image = Image.open(img_path)
                    st.image(image, caption=image_files[5], use_container_width=True)
                    st.subheader("click on the start recording button")
                except Exception as e:
                    st.error(f"Error loading image {image_files[5]}: {e}")
                    
            if len(image_files) > 6:
                try:
                    img_path = os.path.join(images_path, image_files[6])
                    image = Image.open(img_path)
                    st.image(image, caption=image_files[6], use_container_width=True)
                    st.subheader("recording has started")
                except Exception as e:
                    st.error(f"Error loading image {image_files[6]}: {e}")
                    
            if len(image_files) > 7:
                try:
                    img_path = os.path.join(images_path, image_files[7])
                    image = Image.open(img_path)
                    st.image(image, caption=image_files[7], use_container_width=True)
                    st.subheader("click on the stop recording button")
                except Exception as e:
                    st.error(f"Error loading image {image_files[7]}: {e}")
                    
            if len(image_files) > 8:
                try:
                    img_path = os.path.join(images_path, image_files[8])
                    image = Image.open(img_path)
                    st.image(image, caption=image_files[8], use_container_width=True)
                    st.subheader("save the recording in the preferred location")
                except Exception as e:
                    st.error(f"Error loading image {image_files[8]}: {e}")
            
            # If there are more than 9 images, notify the user
            if len(image_files) > 9:
                st.info(f"{len(image_files) - 9} more images available but not displayed.")
        else:
            st.info("No images found in the meeting folder.")
    else:
        st.warning(f"Directory not found: {images_path}")

if __name__ == "__main__":
    main()