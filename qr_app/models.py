# qr_app/models.py
from django.db import models

# Choices for background type
BACKGROUND_TYPE_CHOICES = [
    ('color', 'Color'),
    ('image', 'Image'),
]

# Font choices
FONT_CHOICES = [
    ('Lora', 'Lora'),
    ('Montserrat', 'Montserrat'),
    ('Pacifico', 'Pacifico'),
    ('Caveat', 'Caveat'),
]

class QRCodeData(models.Model):
    """
    Model to store data related to each generated QR code.
    Now includes comprehensive text formatting and positioning.
    """
    unique_key = models.CharField(
        max_length=20, 
        unique=True, 
        null=True, 
        help_text="Unique identifier for the QR code (e.g., DK001)"
    )
    
    link = models.URLField(
        max_length=500, 
        help_text="The URL encoded in the QR code", 
        null=True
    )
    
    message = models.TextField(
        blank=True, 
        null=True, 
        help_text="The message associated with the QR code, entered by the user"
    )
    
    # Text styling fields
    text_color = models.CharField(
        max_length=7,
        default='#333333',
        help_text="Hex code for the message text color (e.g., #333333)"
    )
    
    font_family = models.CharField(
        max_length=50,
        choices=FONT_CHOICES,
        default='Lora',
        help_text="Font family for the message text"
    )
    
    font_size = models.IntegerField(
        default=24,
        help_text="Font size in pixels (12-48)"
    )
    
    # Text positioning fields (stored as percentages)
    text_position_x = models.FloatField(
        default=50.0,
        help_text="Horizontal position of text as percentage (0-100)"
    )
    
    text_position_y = models.FloatField(
        default=50.0,
        help_text="Vertical position of text as percentage (0-100)"
    )
    
    # Background fields (kept for compatibility)
    background_type = models.CharField(
        max_length=10,
        choices=BACKGROUND_TYPE_CHOICES,
        default='color',
        help_text="Choose 'color' for a solid background or 'image' for a background image."
    )
    
    background_value = models.CharField(
        max_length=255,
        default='#f0f0f0',
        blank=True,
        help_text="For 'color', enter a hex code. For 'image', enter a URL or path."
    )
    
    # The composite image containing both background and positioned text
    attached_image = models.ImageField(
        upload_to='message_images/',
        blank=True,
        null=True,
        help_text="Composite image containing background and positioned text overlay"
    )
    
    # QR code image
    qr_image = models.ImageField(
        upload_to='qr_codes/', 
        blank=True, 
        null=True, 
        help_text="The generated QR code image file"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.unique_key} - {self.message[:50] if self.message else 'No message'}"

    class Meta:
        verbose_name = "QR Code Data"
        verbose_name_plural = "QR Code Data"
        ordering = ['-updated_at', 'unique_key']

    def get_text_style_dict(self):
        """Return a dictionary of text styling properties for easy template use"""
        return {
            'color': self.text_color,
            'font_family': self.font_family,
            'font_size': f"{self.font_size}px",
            'position_x': f"{self.text_position_x}%",
            'position_y': f"{self.text_position_y}%",
        }