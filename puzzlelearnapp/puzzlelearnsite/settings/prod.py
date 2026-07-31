from .base import *
from dotenv import load_dotenv
import os
from django.core.management.utils import get_random_secret_key

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', get_random_secret_key())

DEBUG = False

ALLOWED_HOSTS = ['puzzlelearn.fly.dev']

CSRF_TRUSTED_ORIGINS = ['https://puzzlelearn.fly.dev/']