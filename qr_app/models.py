# qr_app/models.py

from django.db import models

# Choices for background type
BACKGROUND_TYPE_CHOICES = [
    ('color', 'Color'),
    ('image', 'Image'),
]

class QRCodeData(models.Model):
    """
    Model to store data related to each generated QR code.
    """
    unique_key = models.CharField(max_length=20, unique=True, help_text="Unique identifier for the QR code (e.g., DK001)")
    link = models.URLField(max_length=500, help_text="The URL encoded in the QR code")
    message = models.TextField(blank=True, null=True, help_text="The message associated with the QR code, entered by the user")

    # New fields for message styling
    text_color = models.CharField(
        max_length=7,
        default='#4a2c2a',  # Dark chocolate color
        help_text="Hex code for the message text color (e.g., #RRGGBB)"
    )
    background_type = models.CharField(
        max_length=10,
        choices=BACKGROUND_TYPE_CHOICES,
        default='color',
        help_text="Choose 'color' for a solid background or 'image' for a background image."
    )
    background_value = models.CharField(
        max_length=255,
        default='#fff8e1',  # Creamy background color
        blank=True,
        help_text="For 'color', enter a hex code (e.g., #FFFFFF). For 'image', enter a URL or path to the image."
    )
    attached_image = models.ImageField(
        upload_to='message_images/',
        blank=True,
        null=True,
        help_text="Optional: An image to be displayed *inside* the message box with the text."
    )

    qr_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True, help_text="The generated QR code image file")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.unique_key

    class Meta:
        verbose_name = "QR Code Data"
        verbose_name_plural = "QR Code Data"
        ordering = ['unique_key']