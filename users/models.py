from django.db import models
from django.utils import timezone 

class SessionStorage(models.Model):

    session_key = models.CharField(max_length=255, unique=True)
    
    session_data = models.TextField()

    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"Session: {self.session_key}"

