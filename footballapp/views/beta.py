from django.shortcuts import render
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings

from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.decorators import api_view

from ..models import AdminProfile, Team, Players, Mappings, Viewer, Bookings

import jwt
import datetime
from functools import wraps

# Put your code here