# qr_app/views.py

import qrcode
from qrcode.image.pil import PilImage
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.urls import reverse
from .models import QRCodeData,BACKGROUND_TYPE_CHOICES 
import io
import os
from django.core.files.base import ContentFile
from django.conf import settings
from PIL import ImageDraw, ImageFont # Import ImageDraw and ImageFont here

def generate_qr_page(request):
    """
    Renders the page where users can specify the number of QR codes to generate.
    """
    return render(request, 'qr_generator.html')

def generate_qr_codes(request):
    """
    Handles the form submission for QR code generation.
    Generates QR codes, saves them to the database, and provides download links.
    """
    if request.method == 'POST':
        try:
            limit_str = request.POST.get('limit', '10') # Default to 10 if not provided
            if limit_str.isdigit():
                limit = int(limit_str)
            else:
                # Handle custom input if it's not a number, or set a default
                # For simplicity, we'll assume it's a number for now.
                # You might want to add more robust validation here.
                limit = 10 # Fallback

            if not (1 <= limit <= 100): # Set a reasonable upper limit to prevent abuse
                return render(request, 'qr_generator.html', {'error': 'Limit must be between 1 and 100.'})

            generated_qrs = []
            base_key = "DK"
            # Find the highest existing unique_key to continue numbering
            last_qr = QRCodeData.objects.filter(unique_key__startswith=base_key).order_by('-unique_key').first()
            if last_qr:
                try:
                    last_num = int(last_qr.unique_key[len(base_key):])
                except ValueError:
                    last_num = 0
            else:
                last_num = 0

            for i in range(1, limit + 1):
                new_num = last_num + i
                unique_key = f"{base_key}{new_num:03d}" # e.g., DK001, DK002

                # Construct the full link that will be embedded in the QR code
                # This link will point to the 'enter_message' page for this specific QR code
                qr_link = request.build_absolute_uri(reverse('display_message', args=[unique_key]))


                # Generate QR code image
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_link)
                qr.make(fit=True)

                # Create an image with the unique key in the center
                img = qr.make_image(image_factory=PilImage).convert("RGB")
                
                # Add text to the center of the QR code (this requires PIL/Pillow)
                draw = ImageDraw.Draw(img)
                try:
                    # Try to load a default font, adjust path/name as needed
                    # You might need to provide a full path to a .ttf font file
                    font = ImageFont.truetype("arial.ttf", 40)
                except IOError:
                    # Fallback to a simpler font if arial.ttf is not found
                    font = ImageFont.load_default()
                    print("Could not load arial.ttf, using default font.")

                # Use textbbox instead of textsize for newer Pillow versions
                # textbbox returns (left, top, right, bottom)
                bbox = draw.textbbox((0, 0), unique_key, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                img_width, img_height = img.size
                text_x = (img_width - text_width) / 2
                text_y = (img_height - text_height) / 2
                draw.text((text_x, text_y), unique_key, font=font, fill=(0, 0, 0)) # Black text

                # Save QR code image to a buffer
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                image_file = ContentFile(buffer.getvalue())

                # Create or update QRCodeData object
                qr_data, created = QRCodeData.objects.get_or_create(unique_key=unique_key)
                qr_data.link = qr_link
                qr_data.qr_image.save(f'{unique_key}.png', image_file, save=False) # save=False to avoid double save
                qr_data.save()

                generated_qrs.append(qr_data)

            return render(request, 'qr_generator.html', {'generated_qrs': generated_qrs})

        except Exception as e:
            return render(request, 'qr_generator.html', {'error': f'An error occurred: {e}'})
    return redirect('generate_qr_page')

# qr_app/views.py

# ... (imports) ...

# qr_app/views.py

import base64
import re

# ... (other imports) ...

def save_message(request, unique_key):
    """
    Handles the form submission for saving a message and its styling to a QR code.
    """
    qr_data = get_object_or_404(QRCodeData, unique_key=unique_key)

    if request.method == 'POST':
        print("--- POST Request Received ---")
        print("POST Data Keys:", request.POST.keys()) # Check for 'cropped_image_data'
        print("FILES Data:", request.FILES)

        message = request.POST.get('message', '').strip()
        text_color = request.POST.get('text_color', '#4a2c2a')
        background_type = request.POST.get('background_type', 'color')
        background_value = request.POST.get('background_value', '#fff8e1')

        # --- NEW LOGIC FOR HANDLING BASE64 IMAGE ---
        attached_image_base64 = request.POST.get('cropped_image_data')

        if not message:
            print("Error: Message is empty.")
            context = {
                'qr_data': qr_data,
                'error': 'Message cannot be empty.',
                'background_type_choices': BACKGROUND_TYPE_CHOICES,
            }
            return render(request, 'enter_message.html', context)

        # Update the QR code data object
        qr_data.message = message
        qr_data.text_color = text_color
        qr_data.background_type = background_type
        qr_data.background_value = background_value

        if attached_image_base64:
            print("Received cropped image data. Processing...")
            # Clean up the Base64 string (e.g., remove 'data:image/png;base64,')
            data_uri_pattern = re.compile(r'^data:image/(png|jpeg|jpg);base64,')
            clean_base64_string = data_uri_pattern.sub('', attached_image_base64)
            image_data = base64.b64decode(clean_base64_string)

            # Create a Django ContentFile from the decoded data
            image_file = ContentFile(image_data, name=f'{qr_data.unique_key}_attached.png')
            
            # Save the new image to the model field
            qr_data.attached_image.save(f'{qr_data.unique_key}_attached.png', image_file)
            print(f"Attached image saved as: {qr_data.attached_image.name}")
        
        elif 'clear_attached_image' in request.POST:
            print("Clearing attached image.")
            qr_data.attached_image = None
            qr_data.save()
        else:
            print("No new image uploaded, and clear image not checked. Keeping existing image (if any).")
            # We still need to save other changes, so call save() here too if no image was involved
            qr_data.save()

        print("QR Data saved successfully!")
        return redirect('display_message', unique_key=unique_key)

    print("--- GET Request Received (or not a POST) ---")
    return redirect('enter_message_page', unique_key=unique_key)

# You'll also need an 'enter_message' view if you don't have one:
def enter_message_page(request, unique_key):
    """
    Renders the form page for entering or editing a message for a QR code.
    """
    qr_data = get_object_or_404(QRCodeData, unique_key=unique_key)
    context = {
        'qr_data': qr_data,
        'background_type_choices': BACKGROUND_TYPE_CHOICES, # Pass choices to the template
    }
    return render(request, 'enter_message.html', context)


def display_message_page(request, unique_key):
    """
    Renders the page to display the message associated with a QR code.
    """
    qr_data_obj = get_object_or_404(QRCodeData, unique_key=unique_key)

    if not qr_data_obj.message:
        # If no message exists yet, redirect to the enter message page
        return redirect('enter_message', unique_key=unique_key)

    # Pass all relevant data from qr_data_obj to the template context
    context = {
        'qr_data': {
            'unique_key': qr_data_obj.unique_key,
            'message': qr_data_obj.message,
            'text_color': qr_data_obj.text_color,
            'background_type': qr_data_obj.background_type,
            'background_value': qr_data_obj.background_value,
            'attached_image': qr_data_obj.attached_image.url if qr_data_obj.attached_image else '',
        }
    }
    return render(request, 'display_message.html', context)

def download_qr(request, unique_key):
    """
    Allows downloading a specific QR code image.
    """
    qr_data = get_object_or_404(QRCodeData, unique_key=unique_key)
    if qr_data.qr_image:
        # Construct the full path to the image file
        file_path = os.path.join(settings.MEDIA_ROOT, qr_data.qr_image.name)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="image/png")
                response['Content-Disposition'] = f'attachment; filename="{qr_data.unique_key}.png"'
                return response
        else:
            raise Http404("QR code image not found.")
    else:
        raise Http404("No QR code image associated with this key.")

