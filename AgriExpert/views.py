from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from .forms import FarmerSignupForm, ExpertSignupForm
from django.conf import settings
from supabase import create_client
import uuid
import mimetypes
from django.contrib.auth import authenticate, login, logout
from AgriExpert.models import Farmer, Expert , Admin , Message, PredictionHistory
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.views import View
import requests
from .forms import PasswordResetRequestForm, PasswordResetConfirmForm
from django.core.mail import send_mail
from django.shortcuts import render, HttpResponse
import os
import requests
import pdfkit
import pypandoc
from django.http import HttpResponse
from django.conf import settings
from docx import Document
from django.http import JsonResponse, HttpResponse, FileResponse
import subprocess
from urllib.parse import urlparse
import numpy as np
from PIL import Image
# import tensorflow as tf
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
import io
from datetime import datetime, timedelta
# import datetime
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import random
import base64

# THIS IS A SAMPLE COMMENT TO COMMIT CHANGES
# Supabase Setup
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_KEY = settings.SUPABASE_KEY
SUPABASE_BUCKET = settings.SUPABASE_BUCKET
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

PDFKIT_CONFIG = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)
def upload_to_supabase(file, folder):
    """Uploads a file to Supabase Storage and returns the public URL."""
    if not file:
        return None

    unique_filename = f"{uuid.uuid4().hex}_{file.name}"
    file_path = f"{folder}/{unique_filename}"

    # Read file data
    file_content = file.read()
    mime_type, _ = mimetypes.guess_type(file.name)

    # Upload file to Supabase Storage
    res = supabase.storage.from_(SUPABASE_BUCKET).upload(
        file_path, file_content, file_options={"content-type": mime_type}
    )

    # Check for errors in response
    if isinstance(res, dict) and "error" in res and res["error"]:
        print(f"Supabase upload failed: {res['error']}")
        return None

    # Construct and return public file URL
    return f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{file_path}"


# SENDING MESSAGE FROM FARMER TO EXPERT
# def send_message(request, expert_id):
#     """Handles sending messages and uploading images to Supabase."""
#     user_id = request.session.get("user_id")
#     user_role = request.session.get("role")

#     if not user_id or user_role != "Magsasaka":
#         messages.error(request, "Kailangan mong mag-login bilang Magsasaka upang magpadala ng mensahe.")
#         return redirect("login")

#     farmer = get_object_or_404(Farmer, id=user_id)
#     expert = get_object_or_404(Expert, id=expert_id)

#     if request.method == "POST":
#         message_text = request.POST.get("message")
#         image_file = request.FILES.get("image")

#         # CALL upload_to_supabase() DIRECTLY (No need to import)
#         image_url = upload_to_supabase(image_file, "messages") if image_file else None

#         try:
#             # Save message to database with image URL
#             message = Message.objects.create(
#                 sender_farmer=farmer,
#                 receiver_expert=expert,
#                 message_text=message_text,
#                 image=image_url  # Save the image URL
#             )
#             print(f"✅ Message saved successfully: {message}")
#         except Exception as e:
#             print("❌ Error saving message:", e)

#         return redirect("farmer_collab")

#     return render(request, "farmer/viewedit/message_expert.html", {"expert": expert})
# def send_message(request, expert_id):
#     """Handles sending messages and uploading images to Supabase for both message_expert and chat_detail."""
#     user_id = request.session.get("user_id")
#     user_role = request.session.get("role")

#     if not user_id or user_role != "Magsasaka":
#         messages.error(request, "Kailangan mong mag-login bilang Magsasaka upang magpadala ng mensahe.")
#         return redirect("login")

#     farmer = get_object_or_404(Farmer, id=user_id)
#     expert = get_object_or_404(Expert, id=expert_id)

#     if request.method == "POST":
#         message_text = request.POST.get("message_text")  # Ensure correct field name
#         image_file = request.FILES.get("image")

#         # Upload the image to Supabase (if provided)
#         image_url = upload_to_supabase(image_file, "messages") if image_file else None

#         try:
#             # Save message to the database
#             message = Message.objects.create(
#                 sender_farmer=farmer,
#                 receiver_expert=expert,
#                 message_text=message_text,
#                 image=image_url  # Save the image URL
#             )
#             print(f"✅ Message saved successfully: {message}")
#         except Exception as e:
#             print("❌ Error saving message:", e)

#         # Redirect back to the appropriate chat page
#         if "chat_details" in request.path:
#             return redirect("chat_detail", expert_id=expert.id)
#         return redirect("farmer_collab")

#     return render(request, "farmer/viewedit/message_expert.html", {"expert": expert})

# def send_message(request, expert_id):
#     """Handles sending messages and uploading images to Supabase for both message_expert and chat_detail."""
#     user_id = request.session.get("user_id")
#     user_role = request.session.get("role")

#     if not user_id or user_role != "Magsasaka":
#         messages.error(request, "Kailangan mong mag-login bilang Magsasaka upang magpadala ng mensahe.")
#         return redirect("login")

#     farmer = get_object_or_404(Farmer, id=user_id)
#     expert = get_object_or_404(Expert, id=expert_id)

#     # Check if there is an existing conversation
#     # existing_messages = Message.objects.filter(sender_farmer=farmer, receiver_expert=expert).exists()
#     # if existing_messages:
#     #     return redirect("chat_detail", expert_id=expert.id)  # Redirect to chat if conversation exists

#     if request.method == "POST":
#         message_text = request.POST.get("message_text")  # Ensure correct field name
#         image_file = request.FILES.get("image")

#         # Upload the image to Supabase (if provided)
#         image_url = upload_to_supabase(image_file, "messages") if image_file else None

#         try:
#             # Save message to the database
#             message = Message.objects.create(
#                 sender_farmer=farmer,
#                 receiver_expert=expert,
#                 message_text=message_text,
#                 image=image_url  # Save the image URL
#             )
#             print(f"✅ Message saved successfully: {message}")
#         except Exception as e:
#             print("❌ Error saving message:", e)

#         return redirect("chat_detail", expert_id=expert.id)  # Redirect to chat page after sending

#     return render(request, "farmer/viewedit/message_expert.html", {"expert": expert})
# def send_message(request, expert_id):
#     """Handles sending messages and redirects properly based on conversation history."""
#     user_id = request.session.get("user_id")
#     user_role = request.session.get("role")

#     if not user_id or user_role != "Magsasaka":
#         messages.error(request, "Kailangan mong mag-login bilang Magsasaka upang magpadala ng mensahe.")
#         return redirect("login")

#     # Check if the expert exists
#     expert_response = supabase.table("AgriExpert_expert").select("*").eq("id", expert_id).single().execute()
#     if not expert_response.data:
#         messages.error(request, "Hindi natagpuan ang eksperto.")
#         return redirect("farmer_experts")

#     expert = expert_response.data  # Extract expert data

#     # Check if a conversation already exists
#     existing_messages_response = (
#         supabase.table("AgriExpert_messages")
#         .select("*")
#         .eq("sender_farmer_id", user_id)
#         .eq("receiver_expert_id", expert_id)
#         .execute()
#     )

#     if existing_messages_response.data:  # If messages exist, redirect to chat_detail
#         return redirect("chat_detail", expert_id=expert_id)

#     if request.method == "POST":
#         message_text = request.POST.get("message_text")
#         image_file = request.FILES.get("image")

#         # Upload image to Supabase if provided
#         image_url = upload_to_supabase(image_file, "messages") if image_file else None

#         try:
#             # Save message in Supabase
#             new_message = {
#                 "sender_farmer": user_id,
#                 "receiver_expert": expert_id,
#                 "message_text": message_text,
#                 "image": image_url
#             }
#             supabase.table("AgriExpert_messages").insert(new_message).execute()

#             return redirect("chat_detail", expert_id=expert_id)  # Redirect after sending
#         except Exception as e:
#             messages.error(request, f"❌ Error saving message: {e}")

#     return render(request, "farmer/viewedit/message_expert.html", {"expert": expert})


# def send_message(request, expert_id):
#     """Handles sending messages and redirects properly based on conversation history."""
#     user_id = request.session.get("user_id")
#     user_role = request.session.get("role")

#     if not user_id or user_role != "Magsasaka":
#         messages.error(request, "Kailangan mong mag-login bilang Magsasaka upang magpadala ng mensahe.")
#         return redirect("login")

#     # Check if the expert exists
#     expert_response = supabase.table("AgriExpert_expert").select("*").eq("id", expert_id).single().execute()
#     if not expert_response.data:
#         messages.error(request, "Hindi natagpuan ang eksperto.")
#         return redirect("farmer_experts")

#     expert = expert_response.data  # Extract expert data

#     if request.method == "POST":
#         message_text = request.POST.get("message_text")
#         image_file = request.FILES.get("image")

#         # Check if message is empty
#         if not message_text and not image_file:
#             messages.error(request, "Hindi maaaring magpadala ng walang laman na mensahe.")
#             return redirect("message_expert", expert_id=expert_id)

#         # Upload image to Supabase if provided
#         image_url = upload_to_supabase(image_file, "messages") if image_file else None

#         try:
#             # Save message in Supabase
#             new_message = {
#                 "sender_farmer_id": user_id,  # Make sure these match your database fields
#                 "receiver_expert_id": expert_id,
#                 "message_text": message_text,
#                 "image": image_url,
#                 "timestamp": "now()"  # Add a timestamp if needed
#             }
#             response = supabase.table("AgriExpert_messages").insert(new_message).execute()

#             # Check if insertion was successful
#             if response.data:
#                 return redirect("chat_detail", expert_id=expert_id)
#             else:
#                 messages.error(request, "❌ Error: Message was not saved.")

#         except Exception as e:
#             messages.error(request, f"❌ Error saving message: {e}")

#     return render(request, "farmer/viewedit/message_expert.html", {"expert": expert})
# def send_message(request, expert_id):
#     """Handles sending messages and allows sending new messages even if a conversation exists."""
#     user_id = request.session.get("user_id")
#     user_role = request.session.get("role")

#     if not user_id or user_role != "Magsasaka":
#         messages.error(request, "Kailangan mong mag-login bilang Magsasaka upang magpadala ng mensahe.")
#         return redirect("login")

#     # Check if the expert exists using Supabase
#     expert_response = supabase.table("AgriExpert_expert").select("*").eq("id", expert_id).single().execute()
#     if not expert_response.data:
#         messages.error(request, "Hindi natagpuan ang eksperto.")
#         return redirect("farmer_experts")
#     expert = expert_response.data  # Extract expert data

#     if request.method == "POST":
#         # Process the POST request: send a new message regardless of existing conversation.
#         message_text = request.POST.get("message_text", "").strip()
#         image_file = request.FILES.get("image")

#         if not message_text and not image_file:
#             messages.error(request, "Hindi maaaring magpadala ng walang laman na mensahe.")
#             return redirect("chat_detail", expert_id=expert_id)

#         # Upload image to Supabase if provided
#         image_url = upload_to_supabase(image_file, "messages") if image_file else None

#         try:
#             new_message = {
#                 "sender_farmer_id": user_id,        # Ensure these field names match your Supabase schema
#                 "receiver_expert_id": expert_id,
#                 "message_text": message_text,
#                 "image": image_url
#                 # Let the database assign timestamp automatically if defined (auto_now_add=True)
#             }
#             response = supabase.table("AgriExpert_messages").insert(new_message).execute()
#             if response.data:
#                 return redirect("chat_detail", expert_id=expert_id)
#             else:
#                 messages.error(request, "❌ Error: Message was not saved.")
#         except Exception as e:
#             messages.error(request, f"❌ Error saving message: {e}")
#         return redirect("chat_detail", expert_id=expert_id)
#     else:
#         # For GET requests, check if a conversation exists:
#         existing_messages_response = (
#             supabase.table("AgriExpert_messages")
#             .select("*")
#             .eq("sender_farmer_id", user_id)
#             .eq("receiver_expert_id", expert_id)
#             .execute()
#         )
#         if existing_messages_response.data:
#             # If conversation exists, redirect to chat_detail.
#             return redirect("chat_detail", expert_id=expert_id)
#         else:
#             # Otherwise, render the form to start a new conversation.
#             return render(request, "farmer/viewedit/message_expert.html", {"expert": expert})
# from datetime import datetime

# def send_message(request, expert_id):
#     """Handles sending messages and redirects properly based on conversation history."""
#     user_id = request.session.get("user_id")
#     user_role = request.session.get("role")

#     if not user_id or user_role != "Magsasaka":
#         messages.error(request, "Kailangan mong mag-login bilang Magsasaka upang magpadala ng mensahe.")
#         return redirect("login")

#     # Check if the expert exists using Supabase
#     expert_response = supabase.table("AgriExpert_expert").select("*").eq("id", expert_id).single().execute()
#     if not expert_response.data:
#         messages.error(request, "Hindi natagpuan ang eksperto.")
#         return redirect("farmer_experts")
#     expert = expert_response.data  # Extract expert data

#     if request.method == "POST":
#         message_text = request.POST.get("message_text", "").strip()
#         image_file = request.FILES.get("image")

#         if not message_text and not image_file:
#             messages.error(request, "Hindi maaaring magpadala ng walang laman na mensahe.")
#             return redirect("chat_detail", expert_id=expert_id)

#         # Upload image to Supabase if provided
#         image_url = upload_to_supabase(image_file, "messages") if image_file else None

#         try:
#             new_message = {
#                 "sender_farmer_id": user_id,        # Must match your Supabase schema
#                 "receiver_expert_id": expert_id,      # Must match your Supabase schema
#                 "message_text": message_text,
#                 "image": image_url,
#                 "timestamp": datetime.utcnow().isoformat()  # Provide a valid timestamp
#             }
#             response = supabase.table("AgriExpert_messages").insert(new_message).execute()
#             if response.data:
#                 messages.success(request, "Mensahe naipadala.")
#                 return redirect("chat_detail", expert_id=expert_id)
#             else:
#                 messages.error(request, "❌ Error: Message was not saved.")
#         except Exception as e:
#             messages.error(request, f"❌ Error saving message: {e}")
#         return redirect("chat_detail", expert_id=expert_id)
#     else:
#         # For GET requests, check if a conversation exists:
#         existing_messages_response = (
#             supabase.table("AgriExpert_messages")
#             .select("*")
#             .eq("sender_farmer_id", user_id)
#             .eq("receiver_expert_id", expert_id)
#             .execute()
#         )
#         if existing_messages_response.data:
#             return redirect("chat_detail", expert_id=expert_id)
#         else:
#             return render(request, "farmer/viewedit/message_expert.html", {"expert": expert})

def send_message(request, expert_id):
    """Handles sending messages and redirects properly based on conversation history."""
    user_id = request.session.get("user_id")
    user_role = request.session.get("role")

    print(f"🔹 Debug: user_id={user_id}, role={user_role}, expert_id={expert_id}")

    if not user_id or user_role != "Magsasaka":
        messages.error(request, "Kailangan mong mag-login bilang Magsasaka upang magpadala ng mensahe.")
        return redirect("login")

    # ✅ Check if the expert exists
    expert_response = supabase.table("AgriExpert_expert").select("*").eq("id", expert_id).single().execute()
    if not expert_response.data:
        messages.error(request, "Hindi natagpuan ang eksperto.")
        return redirect("farmer_experts")
    expert = expert_response.data  # Extract expert data
    print(f"✅ Debug: Expert found - {expert}")

    if request.method == "POST":
        message_text = request.POST.get("message_text", "").strip()
        image_file = request.FILES.get("image")

        print(f"📩 Debug: Message Text = '{message_text}', Image File = {image_file}")

        if not message_text and not image_file:
            messages.error(request, "Hindi maaaring magpadala ng walang laman na mensahe.")
            return redirect("chat_detail", expert_id=expert_id)

        # ✅ Upload image to Supabase if provided
        image_url = upload_to_supabase(image_file, "messages") if image_file else None

        try:
            new_message = {
                "sender_farmer_id": user_id,        
                "receiver_expert_id": expert_id,      
                "message_text": message_text,
                "image": image_url,
                "timestamp": timezone.now().isoformat()
            }
            print(f"📝 Debug: New Message Data - {new_message}")

            response = supabase.table("AgriExpert_messages").insert(new_message).execute()
            if response.data:
                messages.success(request, "Mensahe naipadala.")
                print("✅ Debug: Message successfully saved!")
                return redirect("chat_detail", expert_id=expert_id)
            else:
                messages.error(request, "❌ Error: Message was not saved.")
                print("❌ Debug: Supabase did not return data!")
        except Exception as e:
            messages.error(request, f"❌ Error saving message: {e}")
            print(f"❌ Debug: Exception - {e}")

        return redirect("chat_detail", expert_id=expert_id)

    else:
        # ✅ Check if conversation exists
        existing_messages_response = (
            supabase.table("AgriExpert_messages")
            .select("*")
            .eq("sender_farmer_id", user_id)
            .eq("receiver_expert_id", expert_id)
            .execute()
        )

        print(f"🔍 Debug: Existing messages = {existing_messages_response.data}")

        if existing_messages_response.data:
            return redirect("chat_detail", expert_id=expert_id)
        else:
            return render(request, "farmer/viewedit/message_expert.html", {"expert": expert})


from django.http import JsonResponse
import json

def edit_message(request, message_id):
    """Handles editing a message in Supabase."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message_text = data.get("message_text")

            message = get_object_or_404(Message, id=message_id, sender_farmer__id=request.session.get("user_id"))
            message.message_text = message_text
            message.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

def delete_message(request, message_id):
    """Handles deleting a message in Supabase."""
    if request.method == "DELETE":
        try:
            message = get_object_or_404(Message, id=message_id, sender_farmer__id=request.session.get("user_id"))
            message.delete()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

@login_required
def inbox(request):
    messages = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    return render(request, "farmer/farmer_collab.html", {"messages": messages})

# NAGANA KANINA
# def signup(request):
#     if request.method == "POST":
#         role = request.POST.get("role")  # ✅ Get the selected role

#         # Debugging: Print role to confirm it's retrieved correctly
#         print(f"Selected role: {role}")  

#         # ✅ Ensure matching against the correct values from ROLE_CHOICES
#         if role == "Magsasaka":
#             form = FarmerSignupForm(request.POST, request.FILES)
#         elif role == "Eksperto":  # ✅ Use "Eksperto" instead of "Expert"
#             form = ExpertSignupForm(request.POST, request.FILES)
#         else:
#             print("Invalid role selected.")  # Debugging
#             return render(request, "signup.html", {"error": "Invalid role selected."})

#         if form.is_valid():
#             user = form.save(commit=False)
#             user.password = make_password(request.POST["password"])  # Encrypt password

#             user.role = role  # ✅ Explicitly set role before saving

#             # Upload profile picture
#             user.profile_picture = upload_to_supabase(request.FILES.get("profile_picture"), "profile_pictures") or None

#             # Upload proof of expertise if role is "Eksperto"
#             if role == "Eksperto":
#                 user.proof_of_expertise = upload_to_supabase(request.FILES.get("proof_of_expertise"), "proof_of_expertise") or None

#             print(f"Saving user: {user.username}, Role: {user.role}")  # ✅ Debugging

#             user.save()
#             print("User successfully saved!")  # ✅ Debugging confirmation

#             return redirect("login")

#         else:
#             print("Form errors:", form.errors)  # ✅ Debugging form errors

#     return render(request, "signup.html")

# def signup(request):
#     form = None  # Ensure form is defined before usage

#     if request.method == "POST":
#         role = request.POST.get("role")

#         print(f"Selected role: {role}")  # ✅ Debugging role selection

#         if role == "Magsasaka":
#             form = FarmerSignupForm(request.POST, request.FILES)
#         elif role == "Eksperto":
#             form = ExpertSignupForm(request.POST, request.FILES)
#         else:
#             print("Invalid role selected.")  # Debugging
#             return render(request, "signup.html", {
#                 "error": "Invalid role selected.",
#                 "form": None
#             })

#         if form.is_valid():
#             user = form.save(commit=False)

#             # ✅ Handle file uploads (Prevent NoneType Errors)
#             user.profile_picture = upload_to_supabase(request.FILES.get("profile_picture"), "profile_pictures") or None

#             if role == "Eksperto":
#                 user.proof_of_expertise = upload_to_supabase(request.FILES.get("proof_of_expertise"), "proof_of_expertise") or None

#             print(f"Saving user: {user.username}, Role: {role}")  # ✅ Debugging

#             user.save()
#             print("User successfully saved!")  # ✅ Debugging confirmation

#             return redirect("login")

#         else:
#             print("Form errors:", form.errors)  # ✅ Debugging form errors

#     return render(request, "signup.html", {"form": form})

# MAY KASAMANG EMAIL
# from django.core.mail import send_mail
# from django.contrib import messages
# from django.conf import settings

def signup(request):
    form = None  # Ensure form is defined before usage

    if request.method == "POST":
        role = request.POST.get("role")

        print(f"Selected role: {role}")  # ✅ Debugging role selection

        if role == "Magsasaka":
            form = FarmerSignupForm(request.POST, request.FILES)
        elif role == "Eksperto":
            form = ExpertSignupForm(request.POST, request.FILES)
        else:
            print("Invalid role selected.")  # Debugging
            return render(request, "signup.html", {
                "error": "Invalid role selected.",
                "form": None
            })

        if form.is_valid():
            user = form.save(commit=False)

            # ✅ Handle file uploads (Prevent NoneType Errors)
            user.profile_picture = upload_to_supabase(request.FILES.get("profile_picture"), "profile_pictures") or None

            if role == "Eksperto":
                user.proof_of_expertise = upload_to_supabase(request.FILES.get("proof_of_expertise"), "proof_of_expertise") or None
                user.position = form.cleaned_data["position"]  # ✅ Save the position
                user.status = "Pending"

            print(f"Saving user: {user.username}, Role: {role}")  # ✅ Debugging

            user.save()
            print("User successfully saved!")  # ✅ Debugging confirmation

            # ✅ Send an email to Experts
            if role == "Eksperto":
                subject = "AgriExpert: Kumpirmasyon ng iyong Pagpaparehistro"
                message = (
                    f"Magandang araw {user.first_name},\n\n"
                    "Matagumpay ang iyong pagpaparehistro bilang isang Eksperto sa AgriExpert!\n"
                    "Gayunpaman, kailangan mong maghintay habang sinusuri ng aming admin ang iyong ipinasa na datos.\n"
                    "Makakatanggap ka ng isa pang email kapag naaprubahan na ang iyong account.\n\n"
                    "Salamat at patuloy kang mag-abang ng update mula sa amin!\n\n"
                    "AgriExpert Team"
                )
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            return redirect("login")

        else:
            print("Form errors:", form.errors)  # ✅ Debugging form errors

    return render(request, "signup.html", {"form": form})


def landing(request):
    return render(request, "landing.html")  

# Custom login required decorator for session-based auth
def role_required(role):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if "user_id" not in request.session or request.session.get("role") != role:
                return redirect("login")  # Redirect to login if not authenticated
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
def farmer_announcements(request):
    # Check if user is logged in as Farmer
    if request.session.get('role') != 'Magsasaka':
        messages.error(request, "Please log in as Farmer to access this page.")
        return redirect('login')
    
    # Get the current farmer from session
    farmer_id = request.session.get('user_id')
    if not farmer_id:
        messages.error(request, "Please log in to access announcements.")
        return redirect('login')
    
    try:
        from .models import Farmer
        farmer_user = Farmer.objects.get(id=farmer_id)
    except Farmer.DoesNotExist:
        messages.error(request, "Farmer not found. Please log in again.")
        return redirect('login')
    
    # Get ALL active announcements from ALL admins that are relevant to farmers
    announcements = Announcement.objects.filter(
        status='active'
    ).filter(
        Q(target_audience='all') | 
        Q(target_audience='farmers') | 
        Q(target_audience='both')
    ).order_by('-created_at')
    
    # INCREMENT VIEW COUNT UNIQUELY FOR THIS FARMER
    for announcement in announcements:
        announcement.increment_views(user_id=farmer_id, user_type='farmer')
    
    # Get filter parameters
    priority_filter = request.GET.get('priority', '')
    search_query = request.GET.get('search', '')
    
    # Apply filters
    if priority_filter:
        announcements = announcements.filter(priority=priority_filter)
    
    if search_query:
        announcements = announcements.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    # Get statistics
    total_announcements = announcements.count()
    urgent_count = announcements.filter(priority='urgent').count()
    high_priority_count = announcements.filter(priority='high').count()
    
    context = {
        'farmer': farmer_user,
        'announcements': announcements,
        'total_announcements': total_announcements,
        'urgent_count': urgent_count,
        'high_priority_count': high_priority_count,
        'priority_filter': priority_filter,
        'search_query': search_query,
    }
    
    return render(request, 'farmer/farmer_announcements.html', context)

from django.db.models import Q
from datetime import timedelta
import json
from django.utils import timezone
from collections import defaultdict
# Apply role-based access control
@role_required("Magsasaka")
# def farmer_home(request):
#     return render(request, "farmer/home.html")



def farmer_home(request):
    user_id = request.session.get('user_id')
    
    try:
        farmer = Farmer.objects.get(id=user_id)
    except Farmer.DoesNotExist:
        return redirect('login')

    # Get farmer's prediction history
    predictions = PredictionHistory.objects.filter(farmer_id=user_id).order_by('-uploaded_at')
    
    pest_classes = [
        'Beetle', 'Brown Plant Hopper', 'Grass Hopper', 'Paddy Stem Maggot',
        'Rice Gall Midge', 'Rice Leaf Caterpillar', 'Rice Leaf Hopper',
        'Rice Leaf Roller', 'Rice Skipper', 'Rice Stem Borer Adult',
        'Rice Stem Borer Larva', 'Rice Water Weevil', 'Thrips'
    ]
    
    disease_classes = [
        'Bacterial Leaf Blight', 'Bacterial Leaf Streak', 'Brown Spot',
        'Dead Heart Pest Attack Symptom','Grain Rot','Healthy Grain',
        'Healthy Leaf','Leaf Scald','Rice Blast','Rice False Smut',
        'Rice Stripe Virus','Sheath Blight','Stem Rot','Tungro Virus',
        'Unknown'
    ]

    # Basic counts
    pest_count = predictions.filter(predicted_class__in=pest_classes).count()
    disease_count = predictions.filter(predicted_class__in=disease_classes).count()
    total_predictions = predictions.count()

    # Monthly trends (last 6 months)
    monthly_labels = []
    monthly_pests = []
    monthly_diseases = []
    
    for i in range(5, -1, -1):
        month_start = timezone.now() - timedelta(days=30*i)
        month_label = month_start.strftime('%b %Y')
        
        month_predictions = predictions.filter(
            uploaded_at__year=month_start.year,
            uploaded_at__month=month_start.month
        )
        
        monthly_labels.append(month_label)
        monthly_pests.append(month_predictions.filter(predicted_class__in=pest_classes).count())
        monthly_diseases.append(month_predictions.filter(predicted_class__in=disease_classes).count())

    # Enhanced calendar events with admin-style grouping
    daily_predictions = defaultdict(lambda: {'pest': [], 'disease': []})
    now = timezone.now()

    for p in predictions:
        date_key = p.uploaded_at.date().isoformat()
        
        time_diff = (now - p.uploaded_at).total_seconds()
        is_new = time_diff < 86400  # 24 hours
        
        prediction_data = {
            'id': p.id,
            'class': p.predicted_class,
            'confidence': float(p.confidence),
            'time': p.uploaded_at.strftime('%I:%M %p'),
            'datetime': p.uploaded_at.isoformat(),
            'is_new': is_new,
            'image_url': p.image_url if p.image_url else '',
            'type': 'pest' if p.predicted_class in pest_classes else 'disease'
        }
        
        if p.predicted_class in pest_classes:
            daily_predictions[date_key]['pest'].append(prediction_data)
        elif p.predicted_class in disease_classes:
            daily_predictions[date_key]['disease'].append(prediction_data)

    # Create aggregated calendar events like admin dashboard
    calendar_events = []
    for date_str, types in daily_predictions.items():
        pest_count_day = len(types['pest'])
        disease_count_day = len(types['disease'])
        
        # Check if there are any new predictions on this day
        has_new = any(p['is_new'] for p in types['pest'] + types['disease'])
        
        if pest_count_day > 0 and disease_count_day > 0:
            # Both types on same day - yellow
            calendar_events.append({
                'title': f"🐛 {pest_count_day} Peste | 🦠 {disease_count_day} Sakit",
                'start': date_str,
                'backgroundColor': '#ffc107',
                'borderColor': '#ff9800',
                'extendedProps': {
                    'pest_count': pest_count_day,
                    'disease_count': disease_count_day,
                    'pest_predictions': types['pest'],
                    'disease_predictions': types['disease'],
                    'has_new': has_new
                }
            })
        elif pest_count_day > 0:
            # Only pest - green
            calendar_events.append({
                'title': f"🐛 {pest_count_day} Peste",
                'start': date_str,
                'backgroundColor': '#28a745',
                'borderColor': '#1e7e34',
                'extendedProps': {
                    'pest_count': pest_count_day,
                    'disease_count': 0,
                    'pest_predictions': types['pest'],
                    'disease_predictions': [],
                    'has_new': has_new
                }
            })
        elif disease_count_day > 0:
            # Only disease - red
            calendar_events.append({
                'title': f"🦠 {disease_count_day} Sakit",
                'start': date_str,
                'backgroundColor': '#dc3545',
                'borderColor': '#c82333',
                'extendedProps': {
                    'pest_count': 0,
                    'disease_count': disease_count_day,
                    'pest_predictions': [],
                    'disease_predictions': types['disease'],
                    'has_new': has_new
                }
            })

    # Consultation data
    messages = Message.objects.filter(
        Q(sender_farmer_id=user_id) | Q(receiver_farmer_id=user_id)
    )
    
    unique_expert_ids = set()
    solved_consultations = messages.filter(is_solved=True).count()
    
    for msg in messages:
        if msg.sender_expert:
            unique_expert_ids.add(msg.sender_expert_id)
        if msg.receiver_expert:
            unique_expert_ids.add(msg.receiver_expert_id)
    
    consultation_count = len(unique_expert_ids)

    # Recent predictions
    recent_predictions = predictions[:10]

    context = {
        'farmer': farmer,
        'total_predictions': total_predictions,
        'pest_count': pest_count,
        'disease_count': disease_count,
        'consultation_count': consultation_count,
        'solved_consultations': solved_consultations,
        'recent_predictions': recent_predictions,
        'pest_classes': pest_classes,
        'disease_classes': disease_classes,
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_pests': json.dumps(monthly_pests),
        'monthly_diseases': json.dumps(monthly_diseases),
        'calendar_events': json.dumps(calendar_events),
    }

    return render(request, 'farmer/home.html', context)


from google import genai
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Initialize client (Option A = auto env key, Option B = explicit key)
client = genai.Client(api_key="AIzaSyAynoIbQ8T3HH-iqzmrkAKBDfmL0rhGtnU") 

@csrf_exempt
def agribot_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()

        if not user_message:
            return JsonResponse({"error": "Empty message"}, status=400)

        # AgriBot personality (Adjust freely)
        system_instruction = (
            "You are AgriBot, an expert assistant specializing ONLY in rice farming, "
            "field management, pests, diseases, and cultivation techniques."
        )

        full_prompt = f"{system_instruction}\nUser: {user_message}"

        # NEW API REQUEST (Gemini 2.5 Flash)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )

        return JsonResponse({"response": response.text}, status=200)

    except Exception as e:
        print("AGRIBOT ERROR:", e)
        return JsonResponse({"error": str(e)}, status=500)


# CHANGED THIS NOVEMBER 7, 2025
# def farmer_home(request):
#     user_id = request.session.get('user_id')

#     # Get only this farmer's history
#     predictions = PredictionHistory.objects.filter(farmer_id=user_id)

#     pest_classes = [
#         'Beetle', 'Brown Plant Hopper', 'Grass Hopper', 'Paddy Stem Maggot',
#         'Rice Gall Midge', 'Rice Leaf Caterpillar', 'Rice Leaf Hopper',
#         'Rice Leaf Roller', 'Rice Skipper', 'Rice Stem Borer Adult',
#         'Rice Stem Borer Larva', 'Rice Water Weevil', 'Thrips'
#     ]

#     disease_classes = [
#         'Bacterial Leaf Blight', 'Bacterial Leaf Streak', 'Bakanae', 'Brown Spot',
#         'Dead Heart', 'Downy', 'Grassy Stunt Virus', 'Healthy Leaf', 'Healthyn Grain',
#         'Hispa Disease', 'Leaf Scald', 'Narrow Brown Spot', 'Neck Blast',
#         'Ragged Stunt Virus', 'Rice Blast', 'Rice False Smut', 'Rice Leaffolder',
#         'Rice Stripes', 'Sheath Blight', 'Sheath Rot', 'Stem Rot', 'Tungro Virus', 'grain rot'
#     ]

#     # Counters
#     pest_count = 0
#     disease_count = 0

#     calendar_events = []
#     for p in predictions:
#         color = None
#         if p.predicted_class in pest_classes:
#             color = 'green'
#             pest_count += 1
#         elif p.predicted_class in disease_classes:
#             color = 'red'
#             disease_count += 1

#         if color:
#             calendar_events.append({
#                 'title': f"{p.predicted_class} ({p.confidence:.1f}%)",
#                 'start': p.uploaded_at.isoformat(),
#                 'color': color,
#             })
        
#         # Fetch all messages where the user is involved as sender or receiver
#         messages = Message.objects.filter(
#             Q(sender_farmer_id=user_id) | Q(receiver_farmer_id=user_id)
#         )

#         # Use a set to collect unique expert IDs in the conversation
#         unique_expert_ids = set()
#         for msg in messages:
#             if msg.sender_expert:
#                 unique_expert_ids.add(msg.sender_expert_id)
#             if msg.receiver_expert:
#                 unique_expert_ids.add(msg.receiver_expert_id)

#         consultation_count = len(unique_expert_ids)
#     context = {
#         'calendar_events': calendar_events,
#         'pest_count': pest_count,
#         'disease_count': disease_count,
#         'consultation_count': consultation_count,
#     }

#     return render(request, 'farmer/home.html', context)
# END OF CHANGE THIS NOV 7, 2025

# @role_required("Eksperto")
# def expert_home(request):
#     return render(request, "expert/home.html")

from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.db.models import Q
from collections import Counter
from .models import (
    Expert, Farmer, Message, ExpertPost, FarmerPost, 
    Upvote, FarmerUpvote, Comment, FarmerPostComment, 
    PredictionHistory, Library
)

def get_disease_pest_classification():
    """
    Get Disease vs Pest classification data from PredictionHistory table.
    This function processes ALL predictions globally and should return the same data for all experts.
    """
    # Define exact class lists for matching
    disease_classes = [
        'Bacterial Leaf Blight', 'Bacterial Leaf Streak', 'Bakanae', 'Brown Spot',
        'Dead Heart', 'Downy', 'Grassy Stunt Virus', 'Healthy Leaf', 'Healthyn Grain',
        'Hispa Disease', 'Leaf Scald', 'Narrow Brown Spot', 'Neck Blast',
        'Ragged Stunt Virus', 'Rice Blast', 'Rice False Smut', 'Rice Leaffolder',
        'Rice Stripes', 'Sheath Blight', 'Sheath Rot', 'Stem Rot', 'Tungro Virus', 'grain rot'
    ]
    
    pest_classes = [
        'Beetle', 'Brown Plant Hopper', 'Grass Hopper', 'Paddy Stem Maggot',
        'Rice Gall Midge', 'Rice Leaf Caterpillar', 'Rice Leaf Hopper',
        'Rice Leaf Roller', 'Rice Skipper', 'Rice Stem Borer Adult',
        'Rice Stem Borer Larva', 'Rice Water Weevil', 'Thrips'
    ]
    
    try:
        # Get ALL predictions from PredictionHistory table (global data)
        all_predictions = PredictionHistory.objects.all()
        
        print(f"[DEBUG] Total predictions found: {all_predictions.count()}")
        
        disease_count = 0
        pest_count = 0
        unknown_count = 0
        
        for prediction in all_predictions:
            predicted_class = prediction.predicted_class
            print(f"[DEBUG] Processing: {predicted_class}")
            
            # Use exact matching with predefined class lists
            if predicted_class in disease_classes:
                disease_count += 1
                print(f"[DEBUG] Classified as DISEASE: {predicted_class}")
            elif predicted_class in pest_classes:
                pest_count += 1
                print(f"[DEBUG] Classified as PEST: {predicted_class}")
            else:
                unknown_count += 1
                print(f"[DEBUG] Classified as UNKNOWN: {predicted_class}")
        
        print(f"[DEBUG] Final counts - Disease: {disease_count}, Pest: {pest_count}, Unknown: {unknown_count}")
        
        classification_data = [disease_count, pest_count, unknown_count]
        classification_labels = ['Sakit (Disease)', 'Peste (Pest)', 'Hindi Nakilala']
        
        return classification_data, classification_labels
        
    except Exception as e:
        print(f"❌ ERROR in get_disease_pest_classification: {e}")
        import traceback
        traceback.print_exc()
        return [0, 0, 0], ['Sakit (Disease)', 'Peste (Pest)', 'Hindi Nakilala']

def expert_home(request):
    """Enhanced expert dashboard with comprehensive analytics and weather integration."""
    expert_id = request.session.get("user_id")
    
    if not expert_id:
        return redirect("login")

    classification_data, classification_labels = get_disease_pest_classification()

    try:
        # Get expert information
        try:
            expert = Expert.objects.get(id=expert_id)
        except Expert.DoesNotExist:
            return redirect("login")

        # Get messages where farmers communicate with this specific expert
        farmer_to_expert_messages = Message.objects.filter(
            sender_farmer__isnull=False,
            receiver_expert_id=expert_id
        )
        
        expert_to_farmer_messages = Message.objects.filter(
            sender_expert_id=expert_id,
            receiver_farmer__isnull=False
        )
        
        # Combine both message types for complete farmer-expert conversations
        expert_messages = farmer_to_expert_messages.union(expert_to_farmer_messages)
        
        unique_farmers = set()
        for msg in expert_messages:
            # Add farmer from farmer-to-expert messages
            if msg.sender_farmer:
                unique_farmers.add(msg.sender_farmer.id)
            # Add farmer from expert-to-farmer messages  
            if msg.receiver_farmer:
                unique_farmers.add(msg.receiver_farmer.id)
        
        unique_farmers_count = len(unique_farmers)
        print(f"[DEBUG] Unique farmers count: {unique_farmers_count}")
        print(f"[DEBUG] Farmer IDs: {list(unique_farmers)}")

        conversations = {}
        for msg in expert_messages:
            # Get farmer ID from either sender or receiver
            farmer_id = None
            if msg.sender_farmer:
                farmer_id = msg.sender_farmer.id
            elif msg.receiver_farmer:
                farmer_id = msg.receiver_farmer.id
                
            if farmer_id:
                key = (farmer_id, expert_id)
                if key not in conversations:
                    conversations[key] = {'total': 0, 'solved': False}
                conversations[key]['total'] += 1
                if msg.is_solved:
                    conversations[key]['solved'] = True

        solved_consultations = sum(1 for conv in conversations.values() if conv['solved'])
        unsolved_consultations = len(conversations) - solved_consultations
        total_consultations = len(conversations)

        print(f"[DEBUG] Total consultations: {total_consultations}")
        print(f"[DEBUG] Solved: {solved_consultations}, Unsolved: {unsolved_consultations}")



        barangay_labels = []
        barangay_counts = []
        
        if unique_farmers:
            farmers_with_barangay = Farmer.objects.filter(
                id__in=list(unique_farmers)
            ).values('barangay')
            
            barangay_list = [f['barangay'] for f in farmers_with_barangay if f['barangay']]
            barangay_counter = Counter(barangay_list)
            barangay_labels = list(barangay_counter.keys())
            barangay_counts = list(barangay_counter.values())


        monthly_data = Message.objects.filter(
            Q(sender_expert_id=expert_id) | Q(receiver_expert_id=expert_id)
        ).annotate(
            month=TruncMonth('timestamp')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        monthly_data_list = list(monthly_data)
        
        month_labels = []
        month_counts = []
        
        # Get last 12 months of data
        recent_data = monthly_data_list[-12:] if len(monthly_data_list) >= 12 else monthly_data_list
        
        for data in recent_data:
            if data['month']:
                month_labels.append(data['month'].strftime("%B %Y"))
                month_counts.append(data['count'])


        consulted_farmers = Message.objects.filter(
            receiver_expert_id=expert_id,
            sender_farmer__isnull=False
        ).values_list('sender_farmer_id', flat=True).distinct()
        
        predictions = PredictionHistory.objects.filter(
            farmer_id__in=consulted_farmers
        )
        
        confidence_ranges = {
            '90-100%': predictions.filter(confidence__gte=90).count(),
            '80-89%': predictions.filter(confidence__gte=80, confidence__lt=90).count(),
            '70-79%': predictions.filter(confidence__gte=70, confidence__lt=80).count(),
            '60-69%': predictions.filter(confidence__gte=60, confidence__lt=70).count(),
            'Below 60%': predictions.filter(confidence__lt=60).count(),
        }
        
        confidence_labels = list(confidence_ranges.keys())
        confidence_data = list(confidence_ranges.values())


        current_date = timezone.now()

        engagement_months = []
        posts_data = []

        for i in range(5, -1, -1):  # Last 6 months
            month_start = current_date.replace(day=1) - timedelta(days=30*i)
            month_end = month_start.replace(day=28) + timedelta(days=4)  # End of month
            month_end = month_end - timedelta(days=month_end.day)
            
            engagement_months.append(month_start.strftime('%b'))
            
            # Count actual ExpertPost objects created by this expert in this month
            posts_count = ExpertPost.objects.filter(
                expert_id=expert_id,
                created_at__gte=month_start,
                created_at__lte=month_end
            ).count()
            
            posts_data.append(posts_count)


        solved_messages = Message.objects.filter(
            receiver_expert_id=expert_id,
            is_solved=True
        )
        
        resolution_timeline = {
            'Same Day': 0,
            '1-2 Days': solved_messages.count(),  # Simplified
            '3-7 Days': 0,
            '1-2 Weeks': 0,
            'Over 2 Weeks': 0
        }

        resolution_labels = list(resolution_timeline.keys())
        resolution_data = list(resolution_timeline.values())


        common_issues = PredictionHistory.objects.filter(
            farmer_id__in=consulted_farmers
        ).values('predicted_class').annotate(
            count=Count('predicted_class')
        ).order_by('-count')[:7]
        
        issue_labels = [issue['predicted_class'] for issue in common_issues if issue['predicted_class']]
        issue_counts = [issue['count'] for issue in common_issues if issue['predicted_class']]


        seasonal_data = [
            Message.objects.filter(receiver_expert_id=expert_id, timestamp__month__in=[1,2,3]).count(),
            Message.objects.filter(receiver_expert_id=expert_id, timestamp__month__in=[4,5,6]).count(),
            Message.objects.filter(receiver_expert_id=expert_id, timestamp__month__in=[7,8,9]).count(),
            Message.objects.filter(receiver_expert_id=expert_id, timestamp__month__in=[10,11,12]).count(),
        ]
        seasonal_labels = ['Q1 (Jan-Mar)', 'Q2 (Apr-Jun)', 'Q3 (Jul-Sep)', 'Q4 (Oct-Dec)']


        library_monthly_data = Library.objects.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        library_monthly_list = list(library_monthly_data)
        
        knowledge_months = []
        knowledge_data = []
        
        if library_monthly_list:
            # Get last 12 months of library additions
            recent_library_data = library_monthly_list[-12:] if len(library_monthly_list) >= 12 else library_monthly_list
            
            for data in recent_library_data:
                if data['month']:
                    knowledge_months.append(data['month'].strftime("%b %Y"))
                    knowledge_data.append(data['count'])
        
        # If no monthly data exists, create placeholder showing total count
        if not knowledge_months:
            total_library_items = Library.objects.count()
            current_month = datetime.now().strftime("%b %Y")
            knowledge_months = [current_month]
            knowledge_data = [total_library_items]


        expert_posts = ExpertPost.objects.filter(expert_id=expert_id)
        total_expert_posts = expert_posts.count()
        total_upvotes_received = Upvote.objects.filter(post__expert_id=expert_id).count()
        total_comments_made = Comment.objects.filter(expert_id=expert_id).count()
        total_farmer_comments_made = FarmerPostComment.objects.filter(expert_id=expert_id).count()
        
        performance_metrics = {
            'total_posts': total_expert_posts,
            'upvotes_received': total_upvotes_received,
            'comments_made': total_comments_made + total_farmer_comments_made,
            'consultations_handled': total_consultations,
            'solutions_provided': solved_consultations
        }

        recent_activity = {
            'new_consultations_today': Message.objects.filter(
                receiver_expert_id=expert_id,
                sender_farmer__isnull=False,
                timestamp__date=timezone.now().date()
            ).count(),
            'pending_responses': Message.objects.filter(
                receiver_expert_id=expert_id,
                is_read=False
            ).count(),
            'library_items_total': Library.objects.count(),
            'active_conversations': len([conv for conv in conversations.values() if not conv['solved']]),
            'messages_sent_today': Message.objects.filter(
                sender_expert_id=expert_id,
                timestamp__date=timezone.now().date()
            ).count(),
            'solutions_this_week': Message.objects.filter(
                sender_expert_id=expert_id,
                is_solved=True,
                timestamp__gte=timezone.now() - timezone.timedelta(days=7)
            ).count()
        }

    except Exception as e:
        print(f"❌ ERROR in expert_home: {e}")
        import traceback
        traceback.print_exc()
        
        # Set default values on error (but keep the global classification_data)
        unique_farmers_count = 0
        solved_consultations = 0
        unsolved_consultations = 0
        total_consultations = 0
        barangay_labels = []
        barangay_counts = []
        month_labels = []
        month_counts = []
        confidence_labels = []
        confidence_data = []
        engagement_months = []
        posts_data = []
        # upvotes_data = []
        resolution_labels = []
        resolution_data = []
        issue_labels = []
        issue_counts = []
        seasonal_data = []
        seasonal_labels = []
        knowledge_months = []
        knowledge_data = []
        performance_metrics = {}
        recent_activity = {}
        expert = None

    context = {
        'expert': expert,
        'unique_farmers': unique_farmers_count,  # Changed from 'unique_farmers_count' to 'unique_farmers'
        'solved_consultations': solved_consultations,
        'unsolved_consultations': unsolved_consultations,
        'total_consultations': total_consultations,
        'barangay_labels': barangay_labels,
        'barangay_counts': barangay_counts,
        'month_labels': month_labels,
        'month_counts': month_counts,
        'classification_data': classification_data,  # Global data processed outside try-catch
        'classification_labels': classification_labels,  # Global labels
        'confidence_labels': confidence_labels,
        'confidence_data': confidence_data,
        'engagement_months': engagement_months,
        'posts_data': posts_data,
        # 'upvotes_data': upvotes_data,
        'resolution_labels': resolution_labels,
        'resolution_data': resolution_data,
        'issue_labels': issue_labels,
        'issue_counts': issue_counts,
        'seasonal_data': seasonal_data,
        'seasonal_labels': seasonal_labels,
        'knowledge_months': knowledge_months,
        'knowledge_data': knowledge_data,
        'performance_metrics': performance_metrics,
        'recent_activity': recent_activity,
    }
    
    return render(request, 'expert/home.html', context)




# def expert_home(request):
#     expert_id = request.session.get("user_id")

#     # Fetch consultations involving this expert
#     messages_response = supabase.table("AgriExpert_messages") \
#         .select("sender_farmer_id, receiver_farmer_id, is_solved, barangay, timestamp") \
#         .or_(f"sender_expert_id.eq.{expert_id},receiver_expert_id.eq.{expert_id}") \
#         .execute()

#     data = messages_response.data or []

#     # Unique farmers contacted
#     unique_farmers = {msg.get("sender_farmer_id") or msg.get("receiver_farmer_id") for msg in data if msg.get("sender_farmer_id") or msg.get("receiver_farmer_id")}
#     unique_farmers_count = len(unique_farmers)

#     # Solved vs Unsolved
#     solved_consultations = sum(1 for msg in data if msg.get("is_solved"))
#     unsolved_consultations = len(data) - solved_consultations

#     # Barangay distribution
#     barangay_counts = {}
#     for msg in data:
#         if msg.get("barangay"):
#             barangay_counts[msg["barangay"]] = barangay_counts.get(msg["barangay"], 0) + 1
#     barangay_labels = list(barangay_counts.keys())
#     barangay_values = list(barangay_counts.values())

#     # Monthly trends
#     month_labels, month_counts = [], []
#     for i in range(5, -1, -1):  # last 6 months
#         month = (datetime.datetime.now() - datetime.timedelta(days=30*i)).strftime("%B %Y")
#         count = sum(1 for msg in data if msg.get("timestamp", "").startswith(month[:3]))
#         month_labels.append(month)
#         month_counts.append(count)

#     context = {
#         "unique_farmers": unique_farmers_count,
#         "solved_consultations": solved_consultations,
#         "unsolved_consultations": unsolved_consultations,
#         "barangay_labels": barangay_labels,
#         "barangay_counts": barangay_values,
#         "month_labels": month_labels,
#         "month_counts": month_counts,
#     }
#     return render(request, "expert/home.html", context)


@role_required("Admin")
def adminako_dashboard(request):
    return render(request, "adminako/dashboard.html")

def user_logout(request):
    logout(request)  # Ends Django session
    request.session.flush()  # Completely remove session data
    messages.success(request, "Matagumpay kang naka-log out.")
    return redirect("login")

# Dating Logout
# def user_logout(request):
#     logout(request)  # Ends session
#     messages.success(request, "Matagumpay kang naka-log out.")
#     return redirect("login")

# Dating Login
# def user_login(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         role = request.POST.get("role")  # Get the selected role

#         user = None

#         if role == "Magsasaka":
#             try:
#                 user = Farmer.objects.get(username=username)
#                 if not check_password(password, user.password):  
#                     messages.error(request, "Maling password.")
#                     return redirect("login")
#                 request.session["user_id"] = user.id
#                 request.session["role"] = role
#                 messages.success(request, f"Maligayang pagdating, {user.username}!")
#                 return redirect("farmer_home")  
#             except Farmer.DoesNotExist:
#                 messages.error(request, "Walang rehistradong Magsasaka na may ganitong username.")
#                 return redirect("login")

#         elif role == "Eksperto":
#             try:
#                 user = Expert.objects.get(username=username)
#                 if not check_password(password, user.password):
#                     messages.error(request, "Maling password.")
#                     return redirect("login")
#                 request.session["user_id"] = user.id
#                 request.session["role"] = role
#                 messages.success(request, f"Maligayang pagdating, {user.username}!")
#                 return redirect("expert_home")  
#             except Expert.DoesNotExist:
#                 messages.error(request, "Walang rehistradong Eksperto na may ganitong username.")
#                 return redirect("login")

#         elif role == "Admin":  
#             try:
#                 user = Admin.objects.get(username=username)
#                 if not check_password(password, user.password):  
#                     messages.error(request, "Maling password.")
#                     return redirect("login")
#                 request.session["user_id"] = user.id
#                 request.session["role"] = role
#                 messages.success(request, f"Maligayang pagdating, {user.username}!")
#                 return redirect("/adminako/dashboard/")  
#             except Admin.DoesNotExist:
#                 messages.error(request, "Walang rehistradong Admin na may ganitong username.")
#                 return redirect("login")

#         else:
#             messages.error(request, "Pumili ng wastong gampanin.")
#             return redirect("login")

#     return render(request, "login.html")


# def user_login(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         role = request.POST.get("role")  

#         user = None

#         if role == "Magsasaka":
#             try:
#                 user = Farmer.objects.get(username=username)
#                 if not check_password(password, user.password):
#                     messages.error(request, "Maling password.")
#                     return redirect("login")
#                 request.session["user_id"] = user.id
#                 request.session["role"] = role
#                 messages.success(request, f"Maligayang pagdating, {user.username}!")
#                 return redirect("farmer_home")  # ✅ Redirect to farmer dashboard
#             except Farmer.DoesNotExist:
#                 messages.error(request, "Walang rehistradong Magsasaka na may ganitong username.")
#                 return redirect("login")

#         elif role == "Eksperto":
#             try:
#                 user = Expert.objects.get(username=username)
#                 if not check_password(password, user.password):
#                     messages.error(request, "Maling password.")
#                     return redirect("login")
#                 request.session["user_id"] = user.id
#                 request.session["role"] = role
#                 messages.success(request, f"Maligayang pagdating, {user.username}!")
#                 return redirect("expert_home")  # ✅ Redirect to expert dashboard
#             except Expert.DoesNotExist:
#                 messages.error(request, "Walang rehistradong Eksperto na may ganitong username.")
#                 return redirect("login")

#         elif role == "Admin":
#             try:
#                 user = Admin.objects.get(username=username)
#                 if not check_password(password, user.password):
#                     messages.error(request, "Maling password.")
#                     return redirect("login")
#                 request.session["user_id"] = user.id
#                 request.session["role"] = role
#                 messages.success(request, f"Maligayang pagdating, {user.username}!")
#                 return redirect("admin_dashboard")  # ✅ Redirect to admin dashboard
#             except Admin.DoesNotExist:
#                 messages.error(request, "Walang rehistradong Admin na may ganitong username.")
#                 return redirect("login")

#         else:
#             messages.error(request, "Pumili ng wastong gampanin.")
#             return redirect("login")

#     return render(request, "login.html")

# BAGONG LOGIN WITH PREVENTION SA PENDING NA EXPERT
def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")

        user = None

        if role == "Magsasaka":
            try:
                user = Farmer.objects.get(username=username)
                if not check_password(password, user.password):
                    messages.error(request, "Maling password.", extra_tags="password_error")
                    return redirect("login")
                request.session["user_id"] = user.id
                request.session["role"] = role
                messages.success(request, f"Maligayang pagdating, {user.username}!")
                return redirect("farmer_home")
            except Farmer.DoesNotExist:
                messages.error(request, "Walang rehistradong Magsasaka na may ganitong username.", extra_tags="username_error")
                return redirect("login")

        elif role == "Eksperto":
            try:
                user = Expert.objects.get(username=username)
                
                if user.status == "Pending":
                    messages.error(request, "Ang iyong account ay nasa 'Pending' status. Hintayin ang kumpirmasyon ng admin.", extra_tags="pending_error")
                    return redirect("login")

                if not check_password(password, user.password):
                    messages.error(request, "Maling password.", extra_tags="password_error")
                    return redirect("login")

                request.session["user_id"] = user.id
                request.session["role"] = role
                messages.success(request, f"Maligayang pagdating, {user.username}!")
                return redirect("expert_home")

            except Expert.DoesNotExist:
                messages.error(request, "Walang rehistradong Eksperto na may ganitong username.", extra_tags="username_error")
                return redirect("login")

        elif role == "Admin":
            try:
                user = Admin.objects.get(username=username)
                if not check_password(password, user.password):
                    messages.error(request, "Maling password.", extra_tags="password_error")
                    return redirect("login")
                request.session["user_id"] = user.id
                request.session["role"] = role
                messages.success(request, f"Maligayang pagdating, {user.username}!")
                return redirect("admin_dashboard")
            except Admin.DoesNotExist:
                messages.error(request, "Walang rehistradong Admin na may ganitong username.", extra_tags="username_error")
                return redirect("login")

        else:
            messages.error(request, "Pumili ng wastong gampanin.", extra_tags="role_error")
            return redirect("login")

    return render(request, "login.html")

# def for admin
# def admin_dashboard(request):
#     try:
#         # Fetch Farmer Count
#         farmer_count_response = supabase.table("AgriExpert_farmer").select("id", count="exact").execute()
#         farmer_count = farmer_count_response.count if farmer_count_response.count is not None else 0

#         # Fetch Expert Count (only Approved ones)
#         expert_count_response = supabase.table("AgriExpert_expert").select("id", count="exact").eq("status", "Approved").execute()
#         expert_count = expert_count_response.count if expert_count_response.count is not None else 0

#     except Exception as e:
#         farmer_count = 0
#         expert_count = 0

#     context = {
#         "farmer_count": farmer_count,
#         "expert_count": expert_count,
#     }

#     return render(request, "adminako/dashboard.html", context)

# def admin_dashboard(request):
#     try:
#         # Fetch Farmer Count
#         farmer_count_response = supabase.table("AgriExpert_farmer").select("id", count="exact").execute()
#         farmer_count = farmer_count_response.count if farmer_count_response.count is not None else 0
#         # Fetch total expert count (all statuses)
#         expert_count_response = supabase.table("AgriExpert_expert").select("id", count="exact").execute()
#         expert_count = expert_count_response.count if expert_count_response.count is not None else 0


#         # Fetch Expert Counts by Status
#         expert_approved_response = supabase.table("AgriExpert_expert").select("id", count="exact").eq("status", "Approved").execute()
#         expert_pending_response = supabase.table("AgriExpert_expert").select("id", count="exact").eq("status", "Pending").execute()
#         expert_rejected_response = supabase.table("AgriExpert_expert").select("id", count="exact").eq("status", "Rejected").execute()

#         expert_approved = expert_approved_response.count if expert_approved_response.count is not None else 0
#         expert_pending = expert_pending_response.count if expert_pending_response.count is not None else 0
#         expert_rejected = expert_rejected_response.count if expert_rejected_response.count is not None else 0

#     except Exception as e:
#         farmer_count = 0
#         expert_count = 0
#         expert_approved = 0
#         expert_pending = 0
#         expert_rejected = 0

#     context = {
#         "farmer_count": farmer_count,
#         "expert_count": expert_count,
#         "expert_approved": expert_approved,
#         "expert_pending": expert_pending,
#         "expert_rejected": expert_rejected,
#     }

#     return render(request, "adminako/dashboard.html", context)

from collections import Counter
# def admin_dashboard(request):
#     try:
#         # Farmer & Expert Counts
#         farmer_count = supabase.table("AgriExpert_farmer").select("id", count="exact").execute().count or 0
#         expert_count = supabase.table("AgriExpert_expert").select("id", count="exact").execute().count or 0

#         expert_approved = supabase.table("AgriExpert_expert").select("id", count="exact").eq("status", "Approved").execute().count or 0
#         expert_pending = supabase.table("AgriExpert_expert").select("id", count="exact").eq("status", "Pending").execute().count or 0
#         expert_rejected = supabase.table("AgriExpert_expert").select("id", count="exact").eq("status", "Rejected").execute().count or 0

#         # Consultations Count
#         consultation_count = supabase.table("AgriExpert_messages").select("id", count="exact").execute().count or 0
#         consultation_solved = supabase.table("AgriExpert_messages").select("id", count="exact").eq("is_solved", True).execute().count or 0
#         consultation_unsolved = supabase.table("AgriExpert_messages").select("id", count="exact").eq("is_solved", False).execute().count or 0
        
#         # Barangay Distribution
#         barangay_response = supabase.table("AgriExpert_farmer").select("barangay").execute()
#         barangay_list = [item["barangay"] for item in barangay_response.data if "barangay" in item]
#         barangay_data = dict(Counter(barangay_list))

#         # Monthly Trends
#         now = datetime.datetime.now()
#         consultation_trends_data = {}

#         for i in range(11, -1, -1):  # last 12 months, oldest to newest
#             month_date = now - datetime.timedelta(days=30*i)
#             year = month_date.year
#             month = month_date.month

#             start_date = datetime.datetime(year, month, 1)
#             if month == 12:
#                 end_date = datetime.datetime(year + 1, 1, 1)
#             else:
#                 end_date = datetime.datetime(year, month + 1, 1)

#             response = supabase.table("AgriExpert_messages") \
#                 .select("id", count="exact") \
#                 .gte("timestamp", start_date.isoformat()) \
#                 .lt("timestamp", end_date.isoformat()) \
#                 .execute()

#             consultation_trends_data[start_date.strftime("%B %Y")] = response.count or 0

#     except Exception as e:
#         farmer_count = expert_count = expert_approved = expert_pending = expert_rejected = 0
#         consultation_count = consultation_solved = consultation_unsolved = 0
#         barangay_data = {}
#         consultation_trends_data = {}

#     context = {
#         "farmer_count": farmer_count,
#         "expert_count": expert_count,
#         "expert_approved": expert_approved,
#         "expert_pending": expert_pending,
#         "expert_rejected": expert_rejected,
#         "consultation_count": consultation_count,
#         "consultation_solved": consultation_solved,
#         "consultation_unsolved": consultation_unsolved,
#         "barangay_data": barangay_data,
#         "consultation_trends_data": consultation_trends_data,
#     }

#     return render(request, "adminako/dashboard.html", context)
# Fixed admin_dashboard function with correct datetime usage:


# CHANGED WORKING ADMIN DASHBOARD
# def admin_dashboard(request):
#     try:
#         # Farmer & Expert Counts
#         farmer_count = supabase.table("AgriExpert_farmer").select("id", count="exact").execute().count or 0
#         expert_count = supabase.table("AgriExpert_expert").select("id", count="exact").execute().count or 0

#         expert_approved = supabase.table("AgriExpert_expert").select("id", count="exact").eq("status", "Approved").execute().count or 0
#         expert_pending = supabase.table("AgriExpert_expert").select("id", count="exact").eq("status", "Pending").execute().count or 0
#         expert_rejected = supabase.table("AgriExpert_expert").select("id", count="exact").eq("status", "Rejected").execute().count or 0

#         # Consultations Count - Unique Conversations
#         messages_response = supabase.table("AgriExpert_messages") \
#             .select("sender_farmer_id,sender_expert_id,receiver_farmer_id,receiver_expert_id") \
#             .execute()

#         unique_conversations = set()

#         for msg in messages_response.data:
#             expert_id = msg.get("sender_expert_id") or msg.get("receiver_expert_id")
#             farmer_id = msg.get("sender_farmer_id") or msg.get("receiver_farmer_id")
#             if expert_id and farmer_id:
#                 unique_conversations.add((farmer_id, expert_id))

#         consultation_count = len(unique_conversations)

#         # Solved/Unsolved Count
#         consultation_solved = supabase.table("AgriExpert_messages").select("id", count="exact").eq("is_solved", True).execute().count or 0
#         # Fetch all messages with solved status and participants
#         all_messages_response = supabase.table("AgriExpert_messages") \
#             .select("is_solved,sender_farmer_id,sender_expert_id,receiver_farmer_id,receiver_expert_id") \
#             .execute()

#         solved_conversations = set()
#         unsolved_conversations = set()

#         for msg in all_messages_response.data:
#             expert_id = msg.get("sender_expert_id") or msg.get("receiver_expert_id")
#             farmer_id = msg.get("sender_farmer_id") or msg.get("receiver_farmer_id")

#             if not expert_id or not farmer_id:
#                 continue

#             convo_key = (farmer_id, expert_id)

#             if msg.get("is_solved"):
#                 solved_conversations.add(convo_key)
#             else:
#                 if convo_key not in solved_conversations:
#                     unsolved_conversations.add(convo_key)

#         # Final clean-up: remove any from unsolved that were later marked solved
#         unsolved_conversations = unsolved_conversations - solved_conversations

#         consultation_solved = len(solved_conversations)
#         consultation_unsolved = len(unsolved_conversations)
        
#          # Sakit vs Peste (Only Solved)
#         solved_messages_response = supabase.table("AgriExpert_messages") \
#             .select("classification") \
#             .eq("is_solved", True) \
#             .execute()

#         sakit_count = 0
#         peste_count = 0

#         for msg in solved_messages_response.data:
#             classification = msg.get("classification")
#             if classification == "Sakit":
#                 sakit_count += 1
#             elif classification == "Peste":
#                 peste_count += 1

#         consultation_type_chart_data = {
#             "solved_sakit": sakit_count,
#             "solved_peste": peste_count
#         }

#         # Extract unique farmer IDs from the consultations
#         consulting_farmer_ids = {msg.get("sender_farmer_id") or msg.get("receiver_farmer_id") 
#                                 for msg in messages_response.data 
#                                 if msg.get("sender_farmer_id") or msg.get("receiver_farmer_id")}

#         # Get barangays only for those farmers
#         barangay_response = supabase.table("AgriExpert_farmer") \
#             .select("id", "barangay") \
#             .in_("id", list(consulting_farmer_ids)) \
#             .execute()

#         # Count barangay occurrences from consulting farmers only
#         barangay_list = [item["barangay"] for item in barangay_response.data if "barangay" in item]
#         barangay_data = dict(Counter(barangay_list))

#         # Monthly Trends - Unique Conversations per Month - FIXED datetime usage
#         now = datetime.now()  # Changed from datetime.datetime.now()
#         consultation_trends_data = {}

#         for i in range(11, -1, -1):
#             month_date = now - timedelta(days=30*i)  # Changed from datetime.timedelta
#             year = month_date.year
#             month = month_date.month

#             start_date = datetime(year, month, 1)  # Changed from datetime.datetime
#             end_date = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)  # Changed from datetime.datetime

#             response = supabase.table("AgriExpert_messages") \
#                 .select("sender_farmer_id,sender_expert_id,receiver_farmer_id,receiver_expert_id,timestamp") \
#                 .gte("timestamp", start_date.isoformat()) \
#                 .lt("timestamp", end_date.isoformat()) \
#                 .execute()

#             unique_conversations = set()

#             for msg in response.data:
#                 expert_id = msg.get("sender_expert_id") or msg.get("receiver_expert_id")
#                 farmer_id = msg.get("sender_farmer_id") or msg.get("receiver_farmer_id")
#                 if expert_id and farmer_id:
#                     unique_conversations.add((farmer_id, expert_id))

#             consultation_trends_data[start_date.strftime("%B %Y")] = len(unique_conversations)
            
#         # Calendar prediction events
#         predictions = PredictionHistory.objects.all()

#         pest_classes = [
#             'Beetle', 'Brown Plant Hopper', 'Grass Hopper', 'Paddy Stem Maggot',
#             'Rice Gall Midge', 'Rice Leaf Caterpillar', 'Rice Leaf Hopper',
#             'Rice Leaf Roller', 'Rice Skipper', 'Rice Stem Borer Adult',
#             'Rice Stem Borer Larva', 'Rice Water Weevil', 'Thrips'
#         ]

#         disease_classes = [
#             'Bacterial Leaf Blight', 'Bacterial Leaf Streak', 'Bakanae', 'Brown Spot',
#             'Dead Heart', 'Downy', 'Grassy Stunt Virus', 'Healthy Leaf', 'Healthyn Grain',
#             'Hispa Disease', 'Leaf Scald', 'Narrow Brown Spot', 'Neck Blast',
#             'Ragged Stunt Virus', 'Rice Blast', 'Rice False Smut', 'Rice Leaffolder',
#             'Rice Stripes', 'Sheath Blight', 'Sheath Rot', 'Stem Rot', 'Tungro Virus', 'Grain rot'
#         ]

#         calendar_events = []

#         for p in predictions:
#             color = None
#             if p.predicted_class in pest_classes:
#                 color = 'green'
#             elif p.predicted_class in disease_classes:
#                 color = 'red'

#             if color:
#                 calendar_events.append({
#                     'title': f"{p.predicted_class} ({p.confidence:.1f}%)",
#                     'start': p.uploaded_at.isoformat(),
#                     'color': color,
#                 })
                
#         calendar_events_json = json.dumps(calendar_events)

#     except Exception as e:
#         print("Error in admin_dashboard:", e)  # Debug print to see the actual error
#         import traceback
#         traceback.print_exc()  # Print full stack trace for debugging
#         farmer_count = expert_count = expert_approved = expert_pending = expert_rejected = 0
#         consultation_count = consultation_solved = consultation_unsolved = 0
#         barangay_data = {}
#         consultation_trends_data = {}
#         calendar_events = []
#         calendar_events_json = "[]"

#     context = {
#         "farmer_count": farmer_count,
#         "expert_count": expert_count,
#         "expert_approved": expert_approved,
#         "expert_pending": expert_pending,
#         "expert_rejected": expert_rejected,
#         "consultation_count": consultation_count,
#         "consultation_solved": consultation_solved,
#         "consultation_unsolved": consultation_unsolved,
#         "barangay_data": barangay_data,
#         "consultation_trends_data": consultation_trends_data,
#         "consultation_type_chart_data": consultation_type_chart_data,
#         "calendar_events": calendar_events,
#         "calendar_events_json": calendar_events_json,
#     }

#     return render(request, "adminako/dashboard.html", context)

from collections import defaultdict, Counter
from datetime import timedelta
import json
from django.utils import timezone
# NEW ADMIN DASHBOARD BY V0
def admin_dashboard(request):
    # Initialize all variables at the start to prevent UnboundLocalError
    farmer_count = expert_count = expert_approved = expert_pending = expert_rejected = 0
    consultation_count = consultation_solved = consultation_unsolved = 0
    barangay_data = {}
    consultation_trends_data = {}
    calendar_events = []
    calendar_events_json = "[]"
    pest_count = disease_count = 0
    top_predictions = {}
    confidence_distribution = {"high": 0, "medium": 0, "low": 0}
    user_growth_data = {"farmers": {}, "experts": {}}
    post_engagement_data = {"expert_posts": 0, "farmer_posts": 0, "total_upvotes": 0, "total_comments": 0}
    farm_sizes = {"small": 0, "medium": 0, "large": 0}
    farmer_barangay_data = {}
    expert_barangay_data = {}
    consultation_type_chart_data = {"solved_sakit": 0, "solved_peste": 0}
    
    try:
        print("[v0] Starting admin_dashboard data collection...")
        
        # Farmer & Expert Counts
        farmer_count = supabase.table("AgriExpert_farmer").select("id", count="exact").execute().count or 0
        expert_count = supabase.table("AgriExpert_expert").select("id", count="exact").execute().count or 0
        print(f"[v0] Farmer count: {farmer_count}, Expert count: {expert_count}")

        expert_approved = supabase.table("AgriExpert_expert").select("id", count="exact").eq("status", "Approved").execute().count or 0
        expert_pending = supabase.table("AgriExpert_expert").select("id", count="exact").eq("status", "Pending").execute().count or 0
        expert_rejected = supabase.table("AgriExpert_expert").select("id", count="exact").eq("status", "Rejected").execute().count or 0

        # Consultations Count - Unique Conversations
        messages_response = supabase.table("AgriExpert_messages") \
            .select("sender_farmer_id,sender_expert_id,receiver_farmer_id,receiver_expert_id") \
            .execute()

        unique_conversations = set()

        for msg in messages_response.data:
            expert_id = msg.get("sender_expert_id") or msg.get("receiver_expert_id")
            farmer_id = msg.get("sender_farmer_id") or msg.get("receiver_farmer_id")
            if expert_id and farmer_id:
                unique_conversations.add((farmer_id, expert_id))

        consultation_count = len(unique_conversations)

        # Solved/Unsolved Count
        consultation_solved = supabase.table("AgriExpert_messages").select("id", count="exact").eq("is_solved", True).execute().count or 0
        all_messages_response = supabase.table("AgriExpert_messages") \
            .select("is_solved,sender_farmer_id,sender_expert_id,receiver_farmer_id,receiver_expert_id") \
            .execute()

        solved_conversations = set()
        unsolved_conversations = set()

        for msg in all_messages_response.data:
            expert_id = msg.get("sender_expert_id") or msg.get("receiver_expert_id")
            farmer_id = msg.get("sender_farmer_id") or msg.get("receiver_farmer_id")

            if not expert_id or not farmer_id:
                continue

            convo_key = (farmer_id, expert_id)

            if msg.get("is_solved"):
                solved_conversations.add(convo_key)
            else:
                if convo_key not in solved_conversations:
                    unsolved_conversations.add(convo_key)

        unsolved_conversations = unsolved_conversations - solved_conversations

        consultation_solved = len(solved_conversations)
        consultation_unsolved = len(unsolved_conversations)
        
        # Sakit vs Peste (Only Solved)
        solved_messages_response = supabase.table("AgriExpert_messages") \
            .select("classification") \
            .eq("is_solved", True) \
            .execute()

        sakit_count = 0
        peste_count = 0

        for msg in solved_messages_response.data:
            classification = msg.get("classification")
            if classification == "Sakit":
                sakit_count += 1
            elif classification == "Peste":
                peste_count += 1

        consultation_type_chart_data = {
            "solved_sakit": sakit_count,
            "solved_peste": peste_count
        }

        consulting_farmer_ids = {msg.get("sender_farmer_id") or msg.get("receiver_farmer_id") 
                                for msg in messages_response.data 
                                if msg.get("sender_farmer_id") or msg.get("receiver_farmer_id")}

        barangay_response = supabase.table("AgriExpert_farmer") \
            .select("id", "barangay") \
            .in_("id", list(consulting_farmer_ids)) \
            .execute()

        barangay_list = [item["barangay"] for item in barangay_response.data if "barangay" in item]
        barangay_data = dict(Counter(barangay_list))

        now = timezone.now()
        consultation_trends_data = {}

        for i in range(11, -1, -1):
            month_date = now - timedelta(days=30*i)
            year = month_date.year
            month = month_date.month

            start_date = timezone.datetime(year, month, 1, tzinfo=now.tzinfo)
            if month == 12:
                end_date = timezone.datetime(year + 1, 1, 1, tzinfo=now.tzinfo)
            else:
                end_date = timezone.datetime(year, month + 1, 1, tzinfo=now.tzinfo)

            response = supabase.table("AgriExpert_messages") \
                .select("sender_farmer_id,sender_expert_id,receiver_farmer_id,receiver_expert_id,timestamp") \
                .gte("timestamp", start_date.isoformat()) \
                .lt("timestamp", end_date.isoformat()) \
                .execute()

            unique_conversations = set()

            for msg in response.data:
                expert_id = msg.get("sender_expert_id") or msg.get("receiver_expert_id")
                farmer_id = msg.get("sender_farmer_id") or msg.get("receiver_farmer_id")
                if expert_id and farmer_id:
                    unique_conversations.add((farmer_id, expert_id))

            consultation_trends_data[start_date.strftime("%B %Y")] = len(unique_conversations)
            
        # Prediction History with Farmer Details
        predictions = PredictionHistory.objects.select_related('farmer').all()
        print(f"[v0] Total predictions found: {predictions.count()}")
        
        pest_classes = [
            'Beetle', 'Brown Plant Hopper', 'Grass Hopper', 'Paddy Stem Maggot',
            'Rice Gall Midge', 'Rice Leaf Caterpillar', 'Rice Leaf Hopper',
            'Rice Leaf Roller', 'Rice Skipper', 'Rice Stem Borer Adult',
            'Rice Stem Borer Larva', 'Rice Water Weevil', 'Thrips'
        ]

        disease_classes = [
            'Bacterial Leaf Blight', 'Bacterial Leaf Streak', 'Bakanae', 'Brown Spot',
            'Dead Heart', 'Downy', 'Grassy Stunt Virus', 'Healthy Leaf', 'Healthyn Grain',
            'Hispa Disease', 'Leaf Scald', 'Narrow Brown Spot', 'Neck Blast',
            'Ragged Stunt Virus', 'Rice Blast', 'Rice False Smut', 'Rice Leaffolder',
            'Rice Stripes', 'Sheath Blight', 'Sheath Rot', 'Stem Rot', 'Tungro Virus', 'Grain rot', 'Unknown'
        ]

        pest_count = sum(1 for p in predictions if p.predicted_class in pest_classes)
        disease_count = sum(1 for p in predictions if p.predicted_class in disease_classes)
        print(f"[v0] Pest count: {pest_count}, Disease count: {disease_count}")
        
        # Top 5 most common predictions
        prediction_counter = Counter([p.predicted_class for p in predictions])
        top_predictions = dict(prediction_counter.most_common(5))
        
        # Confidence distribution
        high_confidence = sum(1 for p in predictions if p.confidence >= 80)
        medium_confidence = sum(1 for p in predictions if 50 <= p.confidence < 80)
        low_confidence = sum(1 for p in predictions if p.confidence < 50)
        
        confidence_distribution = {
            "high": high_confidence,
            "medium": medium_confidence,
            "low": low_confidence
        }

        daily_predictions = defaultdict(lambda: {'pest': [], 'disease': []})

        for p in predictions:
            date_key = p.uploaded_at.date().isoformat()
            
            time_diff = (now - p.uploaded_at).total_seconds()
            is_new = time_diff < 86400
            
            prediction_data = {
                'id': p.id,
                'class': p.predicted_class,
                'confidence': float(p.confidence),
                'time': p.uploaded_at.strftime('%I:%M %p'),
                'datetime': p.uploaded_at.isoformat(),
                'is_new': is_new,
                'image_url': p.image_url if p.image_url else '',
                # Flatten farmer data for easier JavaScript access
                'farmer_name': f"{p.farmer.first_name} {p.farmer.last_name}" if p.farmer else "Unknown",
                'farmer_contact': p.farmer.phone_number if p.farmer else "N/A",
                'farmer_barangay': p.farmer.barangay if p.farmer else "N/A",
                'farmer_farm_size': f"{p.farmer.farm_size} ha" if p.farmer and p.farmer.farm_size else "N/A",
                'type': 'pest' if p.predicted_class in pest_classes else 'disease'
            }
            
            if p.predicted_class in pest_classes:
                daily_predictions[date_key]['pest'].append(prediction_data)
            elif p.predicted_class in disease_classes:
                daily_predictions[date_key]['disease'].append(prediction_data)

        print(f"[v0] Daily predictions aggregated: {len(daily_predictions)} days")

        # Create aggregated calendar events
        calendar_events = []
        for date_str, types in daily_predictions.items():
            pest_count_day = len(types['pest'])
            disease_count_day = len(types['disease'])
            
            # Check if there are any new predictions on this day
            has_new = any(p['is_new'] for p in types['pest'] + types['disease'])
            
            if pest_count_day > 0 and disease_count_day > 0:
                # Both types on same day - yellow
                calendar_events.append({
                    'title': f"🐛 {pest_count_day} Peste | 🦠 {disease_count_day} Sakit",
                    'start': date_str,
                    'backgroundColor': '#ffc107',
                    'borderColor': '#ff9800',
                    'extendedProps': {
                        'pest_count': pest_count_day,
                        'disease_count': disease_count_day,
                        'pest_predictions': types['pest'],
                        'disease_predictions': types['disease'],
                        'has_new': has_new
                    }
                })
            elif pest_count_day > 0:
                # Only pest - green
                calendar_events.append({
                    'title': f"🐛 {pest_count_day} Peste",
                    'start': date_str,
                    'backgroundColor': '#28a745',
                    'borderColor': '#1e7e34',
                    'extendedProps': {
                        'pest_count': pest_count_day,
                        'disease_count': 0,
                        'pest_predictions': types['pest'],
                        'disease_predictions': [],
                        'has_new': has_new
                    }
                })
            elif disease_count_day > 0:
                # Only disease - red
                calendar_events.append({
                    'title': f"🦠 {disease_count_day} Sakit",
                    'start': date_str,
                    'backgroundColor': '#dc3545',
                    'borderColor': '#c82333',
                    'extendedProps': {
                        'pest_count': 0,
                        'disease_count': disease_count_day,
                        'pest_predictions': [],
                        'disease_predictions': types['disease'],
                        'has_new': has_new
                    }
                })
                
        calendar_events_json = json.dumps(calendar_events)
        print(f"[v0] Calendar events created: {len(calendar_events)}")
        
        user_growth_data = {"farmers": {}, "experts": {}}
        
        for i in range(11, -1, -1):
            month_date = now - timedelta(days=30*i)
            year = month_date.year
            month = month_date.month
            
            start_date = timezone.datetime(year, month, 1, tzinfo=now.tzinfo)
            if month == 12:
                end_date = timezone.datetime(year + 1, 1, 1, tzinfo=now.tzinfo)
            else:
                end_date = timezone.datetime(year, month + 1, 1, tzinfo=now.tzinfo)
            month_label = start_date.strftime("%B %Y")
            
            # Count new farmers
            farmers_response = supabase.table("AgriExpert_farmer") \
                .select("id", count="exact") \
                .execute()
            user_growth_data["farmers"][month_label] = len([f for f in farmers_response.data])
            
            # Count new experts
            experts_response = supabase.table("AgriExpert_expert") \
                .select("id", count="exact") \
                .execute()
            user_growth_data["experts"][month_label] = len([e for e in experts_response.data])
        
        print(f"[v0] User growth data collected for {len(user_growth_data['farmers'])} months")
        
        expert_posts_count = ExpertPost.objects.count()
        farmer_posts_count = FarmerPost.objects.count()
        total_posts = expert_posts_count + farmer_posts_count
        
        expert_upvotes_count = Upvote.objects.count()
        farmer_upvotes_count = FarmerUpvote.objects.count()
        total_upvotes = expert_upvotes_count + farmer_upvotes_count
        
        expert_comments_count = Comment.objects.count()
        farmer_comments_count = FarmerPostComment.objects.count()
        total_comments = expert_comments_count + farmer_comments_count
        
        post_engagement_data = {
            "expert_posts": expert_posts_count,
            "farmer_posts": farmer_posts_count,
            "total_upvotes": total_upvotes,
            "total_comments": total_comments
        }
        print(f"[v0] Post engagement - Expert posts: {expert_posts_count}, Farmer posts: {farmer_posts_count}")
        
        farmers_with_size = Farmer.objects.all()
        farm_sizes = {
            "small": 0,
            "medium": 0,
            "large": 0
        }
        
        for farmer in farmers_with_size:
            if farmer.farm_size < 1:
                farm_sizes["small"] += 1
            elif farmer.farm_size <= 5:
                farm_sizes["medium"] += 1
            else:
                farm_sizes["large"] += 1
        
        print(f"[v0] Farm sizes - Small: {farm_sizes['small']}, Medium: {farm_sizes['medium']}, Large: {farm_sizes['large']}")
        
        all_farmers_barangay = supabase.table("AgriExpert_farmer") \
            .select("barangay") \
            .execute()
        all_experts_barangay = supabase.table("AgriExpert_expert") \
            .select("barangay") \
            .execute()
        
        farmer_barangay_list = [item["barangay"] for item in all_farmers_barangay.data if "barangay" in item]
        expert_barangay_list = [item["barangay"] for item in all_experts_barangay.data if "barangay" in item]
        
        farmer_barangay_data = dict(Counter(farmer_barangay_list))
        expert_barangay_data = dict(Counter(expert_barangay_list))
        
        print(f"[v0] Barangay data - Farmers: {len(farmer_barangay_data)}, Experts: {len(expert_barangay_data)}")

    except Exception as e:
        print("[v0] Error in admin_dashboard:", e)
        import traceback
        traceback.print_exc()

    print(f"[v0] Final calendar events count: {len(calendar_events)}")
    print(f"[v0] Final post engagement data: {post_engagement_data}")
    print(f"[v0] Final farm sizes: {farm_sizes}")

    context = {
        "farmer_count": farmer_count,
        "expert_count": expert_count,
        "expert_approved": expert_approved,
        "expert_pending": expert_pending,
        "expert_rejected": expert_rejected,
        "consultation_count": consultation_count,
        "consultation_solved": consultation_solved,
        "consultation_unsolved": consultation_unsolved,
        "barangay_data": barangay_data,
        "consultation_trends_data": consultation_trends_data,
        "consultation_type_chart_data": consultation_type_chart_data,
        "calendar_events": calendar_events,
        "calendar_events_json": calendar_events_json,
        "pest_count": pest_count,
        "disease_count": disease_count,
        "top_predictions": top_predictions,
        "confidence_distribution": confidence_distribution,
        "user_growth_data": user_growth_data,
        "post_engagement_data": post_engagement_data,
        "farm_sizes": farm_sizes,
        "farmer_barangay_data": farmer_barangay_data,
        "expert_barangay_data": expert_barangay_data,
    }

    return render(request, "adminako/dashboard.html", context)



# CHANGED THIS SEPTEMBER 24
# def admin_dashboard(request):
#     try:
#         # Farmer & Expert Counts
#         farmer_count = supabase.table("AgriExpert_farmer").select("id", count="exact").execute().count or 0
#         expert_count = supabase.table("AgriExpert_expert").select("id", count="exact").execute().count or 0

#         expert_approved = supabase.table("AgriExpert_expert").select("id", count="exact").eq("status", "Approved").execute().count or 0
#         expert_pending = supabase.table("AgriExpert_expert").select("id", count="exact").eq("status", "Pending").execute().count or 0
#         expert_rejected = supabase.table("AgriExpert_expert").select("id", count="exact").eq("status", "Rejected").execute().count or 0

#         # Consultations Count - Unique Conversations
#         messages_response = supabase.table("AgriExpert_messages") \
#             .select("sender_farmer_id,sender_expert_id,receiver_farmer_id,receiver_expert_id") \
#             .execute()

#         unique_conversations = set()

#         for msg in messages_response.data:
#             expert_id = msg.get("sender_expert_id") or msg.get("receiver_expert_id")
#             farmer_id = msg.get("sender_farmer_id") or msg.get("receiver_farmer_id")
#             if expert_id and farmer_id:
#                 unique_conversations.add((farmer_id, expert_id))

#         consultation_count = len(unique_conversations)

#         # Solved/Unsolved Count
#         consultation_solved = supabase.table("AgriExpert_messages").select("id", count="exact").eq("is_solved", True).execute().count or 0
#         # Fetch all messages with solved status and participants
#         all_messages_response = supabase.table("AgriExpert_messages") \
#             .select("is_solved,sender_farmer_id,sender_expert_id,receiver_farmer_id,receiver_expert_id") \
#             .execute()

#         solved_conversations = set()
#         unsolved_conversations = set()

#         for msg in all_messages_response.data:
#             expert_id = msg.get("sender_expert_id") or msg.get("receiver_expert_id")
#             farmer_id = msg.get("sender_farmer_id") or msg.get("receiver_farmer_id")

#             if not expert_id or not farmer_id:
#                 continue

#             convo_key = (farmer_id, expert_id)

#             if msg.get("is_solved"):
#                 solved_conversations.add(convo_key)
#             else:
#                 if convo_key not in solved_conversations:
#                     unsolved_conversations.add(convo_key)

#         # Final clean-up: remove any from unsolved that were later marked solved
#         unsolved_conversations = unsolved_conversations - solved_conversations

#         consultation_solved = len(solved_conversations)
#         consultation_unsolved = len(unsolved_conversations)
        
#          # Sakit vs Peste (Only Solved)
#         solved_messages_response = supabase.table("AgriExpert_messages") \
#             .select("classification") \
#             .eq("is_solved", True) \
#             .execute()

#         sakit_count = 0
#         peste_count = 0

#         for msg in solved_messages_response.data:
#             classification = msg.get("classification")
#             if classification == "Sakit":
#                 sakit_count += 1
#             elif classification == "Peste":
#                 peste_count += 1

#         consultation_type_chart_data = {
#             "solved_sakit": sakit_count,
#             "solved_peste": peste_count
#         }
#         # Barangay Distribution
#         # barangay_response = supabase.table("AgriExpert_farmer").select("barangay").execute()
#         # barangay_list = [item["barangay"] for item in barangay_response.data if "barangay" in item]
#         # barangay_data = dict(Counter(barangay_list))
#         # Extract unique farmer IDs from the consultations
#         consulting_farmer_ids = {msg.get("sender_farmer_id") or msg.get("receiver_farmer_id") 
#                                 for msg in messages_response.data 
#                                 if msg.get("sender_farmer_id") or msg.get("receiver_farmer_id")}

#         # Get barangays only for those farmers
#         barangay_response = supabase.table("AgriExpert_farmer") \
#             .select("id", "barangay") \
#             .in_("id", list(consulting_farmer_ids)) \
#             .execute()

#         # Count barangay occurrences from consulting farmers only
#         barangay_list = [item["barangay"] for item in barangay_response.data if "barangay" in item]
#         barangay_data = dict(Counter(barangay_list))
#         # Monthly Trends - Unique Conversations per Month
#         now = datetime.datetime.now()
#         consultation_trends_data = {}

#         for i in range(11, -1, -1):
#             month_date = now - datetime.timedelta(days=30*i)
#             year = month_date.year
#             month = month_date.month

#             start_date = datetime.datetime(year, month, 1)
#             end_date = datetime.datetime(year + 1, 1, 1) if month == 12 else datetime.datetime(year, month + 1, 1)

#             response = supabase.table("AgriExpert_messages") \
#                 .select("sender_farmer_id,sender_expert_id,receiver_farmer_id,receiver_expert_id,timestamp") \
#                 .gte("timestamp", start_date.isoformat()) \
#                 .lt("timestamp", end_date.isoformat()) \
#                 .execute()

#             unique_conversations = set()

#             for msg in response.data:
#                 expert_id = msg.get("sender_expert_id") or msg.get("receiver_expert_id")
#                 farmer_id = msg.get("sender_farmer_id") or msg.get("receiver_farmer_id")
#                 if expert_id and farmer_id:
#                     unique_conversations.add((farmer_id, expert_id))

#             consultation_trends_data[start_date.strftime("%B %Y")] = len(unique_conversations)
            
#                     # 🔍 Add this for calendar prediction events
#         predictions = PredictionHistory.objects.all()

#         pest_classes = [
#             'Beetle', 'Brown Plant Hopper', 'Grass Hopper', 'Paddy Stem Maggot',
#             'Rice Gall Midge', 'Rice Leaf Caterpillar', 'Rice Leaf Hopper',
#             'Rice Leaf Roller', 'Rice Skipper', 'Rice Stem Borer Adult',
#             'Rice Stem Borer Larva', 'Rice Water Weevil', 'Thrips'
#         ]

#         disease_classes = [
#             'Bacterial Leaf Blight', 'Bacterial Leaf Streak', 'Bakanae', 'Brown Spot',
#             'Dead Heart', 'Downy', 'Grassy Stunt Virus', 'Healthy Leaf', 'Healthyn Grain',
#             'Hispa Disease', 'Leaf Scald', 'Narrow Brown Spot', 'Neck Blast',
#             'Ragged Stunt Virus', 'Rice Blast', 'Rice False Smut', 'Rice Leaffolder',
#             'Rice Stripes', 'Sheath Blight', 'Sheath Rot', 'Stem Rot', 'Tungro Virus', 'grain rot'
#         ]

#         calendar_events = []

#         for p in predictions:
#             color = None
#             if p.predicted_class in pest_classes:
#                 color = 'green'
#             elif p.predicted_class in disease_classes:
#                 color = 'red'

#             if color:
#                 calendar_events.append({
#                     'title': f"{p.predicted_class} ({p.confidence:.1f}%)",
#                     'start': p.uploaded_at.isoformat(),
#                     'color': color,
#                 })
                
#             calendar_events_json = json.dumps(calendar_events)

#     except Exception as e:
#         print("Error in admin_dashboard:", e)  # Debug print
#         farmer_count = expert_count = expert_approved = expert_pending = expert_rejected = 0
#         consultation_count = consultation_solved = consultation_unsolved = 0
#         barangay_data = {}
#         consultation_trends_data = {}
#         calendar_events = []
#         calendar_events_json = "[]"

#     context = {
#         "farmer_count": farmer_count,
#         "expert_count": expert_count,
#         "expert_approved": expert_approved,
#         "expert_pending": expert_pending,
#         "expert_rejected": expert_rejected,
#         "consultation_count": consultation_count,
#         "consultation_solved": consultation_solved,
#         "consultation_unsolved": consultation_unsolved,
#         "barangay_data": barangay_data,
#         "consultation_trends_data": consultation_trends_data,
#         "consultation_type_chart_data": consultation_type_chart_data,
#         "calendar_events": calendar_events,
#         "calendar_events_json": calendar_events_json,
#     }

#     return render(request, "adminako/dashboard.html", context)


from django.db.models import Max,Q, F, Value, Case, When
from django.db.models.functions import Least, Greatest

# def admin_reports(request):
#     # Fetch all farmers from the AgriExpert_farmer table
#     farmers_response = supabase.table("AgriExpert_farmer").select("*").execute()
#     farmers = farmers_response.data if farmers_response.data else []

#     # Fetch all experts from the AgriExpert_expert table
#     experts_response = supabase.table("AgriExpert_expert").select("*").execute()
#     experts = experts_response.data if experts_response.data else []

#     # Filter experts based on status
#     pending_experts = [expert for expert in experts if expert["status"] == "Pending"]
#     approved_experts = [expert for expert in experts if expert["status"] == "Approved"]
#     rejected_experts = [expert for expert in experts if expert["status"] == "Rejected"]

#      # 🧠 Smart Filtering of Unique Farmer–Expert Consultations (ignoring who sent it)
#     messages = Message.objects.filter(
#         Q(sender_farmer__isnull=False, receiver_expert__isnull=False) |
#         Q(sender_expert__isnull=False, receiver_farmer__isnull=False)
#     ).annotate(
#         farmer_id=Case(
#             When(sender_farmer__isnull=False, then=F('sender_farmer')),
#             default=F('receiver_farmer'),
#         ),
#         expert_id=Case(
#             When(sender_expert__isnull=False, then=F('sender_expert')),
#             default=F('receiver_expert'),
#         )
#     )

#     # Get latest message per Farmer–Expert pair
#     latest_msg_ids = (
#         messages.values('farmer_id', 'expert_id')
#         .annotate(latest_id=Max('id'))
#         .values_list('latest_id', flat=True)
#     )

#     consultations = Message.objects.filter(id__in=latest_msg_ids).select_related(
#         "sender_farmer", "receiver_farmer", "sender_expert", "receiver_expert"
#     )

#     context = {
#         "farmers": farmers,
#         "experts": experts,
#         "pending_experts": pending_experts,
#         "approved_experts": approved_experts,
#         "rejected_experts": rejected_experts,
#         "consultations": consultations,
#     }
#     return render(request, "adminako/admin_reports.html", context)


# CHANGED NOVEMBER 30
# def admin_reports(request):
#     """
#     Enhanced admin reports view with comprehensive data for multiple report types
#     """
    
#     # === DEMOGRAPHICS DATA ===
#     # Fetch all farmers and experts
#     farmers = Farmer.objects.all().order_by('-id')
#     experts = Expert.objects.all().order_by('-id')
    
#     # Filter experts by status
#     pending_experts = experts.filter(status='Pending')
#     approved_experts = experts.filter(status='Approved')
#     rejected_experts = experts.filter(status='Rejected')
    
#     # === CONSULTATION DATA ===
#     # Group messages uniquely per farmer–expert pair
#     messages = Message.objects.filter(
#         Q(sender_farmer__isnull=False, receiver_expert__isnull=False) |
#         Q(sender_expert__isnull=False, receiver_farmer__isnull=False)
#     ).annotate(
#         farmer_id=Case(
#             When(sender_farmer__isnull=False, then=F('sender_farmer')),
#             default=F('receiver_farmer'),
#         ),
#         expert_id=Case(
#             When(sender_expert__isnull=False, then=F('sender_expert')),
#             default=F('receiver_expert'),
#         )
#     ).select_related("sender_farmer", "receiver_farmer", "sender_expert", "receiver_expert")
    
#     # Organize messages by farmer–expert pair
#     grouped_consultations = {}
#     for msg in messages:
#         key = (msg.farmer_id, msg.expert_id)
#         grouped_consultations.setdefault(key, []).append(msg)
    
#     consultations = []
#     for pair, msgs in grouped_consultations.items():
#         solved_msgs = [m for m in msgs if m.is_solved]
#         solved_msgs.sort(key=lambda x: x.timestamp)
        
#         for i, solved in enumerate(solved_msgs, start=1):
#             solved.solved_count = i
#             consultations.append(solved)
        
#         if not solved_msgs:
#             latest_msg = sorted(msgs, key=lambda x: x.timestamp)[-1]
#             latest_msg.solved_count = None
#             consultations.append(latest_msg)
    
#     consultations.sort(key=lambda x: x.timestamp, reverse=True)
    
#     # === PREDICTION HISTORY DATA ===
#     predictions = PredictionHistory.objects.select_related('farmer', 'library').all().order_by('-uploaded_at')
    
#     # Categorize predictions
#     pest_classes = [
#         'Beetle', 'Brown Plant Hopper', 'Grass Hopper', 'Paddy Stem Maggot',
#         'Rice Gall Midge', 'Rice Leaf Caterpillar', 'Rice Leaf Hopper',
#         'Rice Leaf Roller', 'Rice Skipper', 'Rice Stem Borer Adult',
#         'Rice Stem Borer Larva', 'Rice Water Weevil', 'Thrips'
#     ]
    
#     disease_classes = [
#         'Bacterial Leaf Blight', 'Bacterial Leaf Streak', 'Bakanae', 'Brown Spot',
#         'Dead Heart', 'Downy', 'Grassy Stunt Virus', 'Healthy Leaf', 'Healthyn Grain',
#         'Hispa Disease', 'Leaf Scald', 'Narrow Brown Spot', 'Neck Blast',
#         'Ragged Stunt Virus', 'Rice Blast', 'Rice False Smut', 'Rice Leaffolder',
#         'Rice Stripes', 'Sheath Blight', 'Sheath Rot', 'Stem Rot', 'Tungro Virus', 'Grain rot'
#     ]
    
#     # Add category to each prediction
#     for pred in predictions:
#         if pred.predicted_class in pest_classes:
#             pred.category = 'Peste'
#         elif pred.predicted_class in disease_classes:
#             pred.category = 'Sakit'
#         else:
#             pred.category = 'Unknown'
    
#     # === EXPERT POSTS DATA ===
#     expert_posts = ExpertPost.objects.annotate(
#         upvotes_count=Count('upvote'),
#         comments_count=Count('comment')
#     ).select_related('expert').order_by('-created_at')
    
#     # === FARMER POSTS DATA ===
#     farmer_posts = FarmerPost.objects.annotate(
#         upvotes_count=Count('farmerupvote'),
#         comments_count=Count('farmerpostcomment')
#     ).select_related('farmer').order_by('-created_at')
    
#     # === LIBRARY DATA ===
#     library_entries = Library.objects.all().order_by('-created_at')
    
#     # === STATISTICS ===
#     total_farmers = farmers.count()
#     total_experts = experts.count()
#     total_consultations = len(consultations)
#     solved_consultations = sum(1 for c in consultations if c.is_solved)
#     total_predictions = predictions.count()
#     total_expert_posts = expert_posts.count()
#     total_farmer_posts = farmer_posts.count()
    
#     context = {
#         # Demographics
#         "farmers": farmers,
#         "experts": experts,
#         "pending_experts": pending_experts,
#         "approved_experts": approved_experts,
#         "rejected_experts": rejected_experts,
        
#         # Consultations
#         "consultations": consultations,
        
#         # Predictions
#         "predictions": predictions,
        
#         # Posts
#         "expert_posts": expert_posts,
#         "farmer_posts": farmer_posts,
        
#         # Library
#         "library_entries": library_entries,
        
#         # Statistics
#         "total_farmers": total_farmers,
#         "total_experts": total_experts,
#         "total_consultations": total_consultations,
#         "solved_consultations": solved_consultations,
#         "total_predictions": total_predictions,
#         "total_expert_posts": total_expert_posts,
#         "total_farmer_posts": total_farmer_posts,
        
#         # Current date for reports
#         "report_date": timezone.now(),
#     }
    
#     return render(request, "adminako/admin_reports.html", context)
# END OF CHANGE NOVEMBER 30
# NEW ADMIN REPORTS WITH EXPERT MANAGEMENT
def admin_reports(request):
    """
    Enhanced admin reports view with comprehensive data for multiple report types
    """
    
    # === DEMOGRAPHICS DATA ===
    # Fetch all farmers and experts
    farmers = Farmer.objects.all().order_by('-id')
    experts = Expert.objects.all().order_by('-id')
    
    # Filter experts by status
    pending_experts = experts.filter(status='Pending')
    approved_experts = experts.filter(status='Approved')
    rejected_experts = experts.filter(status='Rejected')
    
    # === CONSULTATION DATA ===
    # Group messages uniquely per farmer–expert pair
    messages = Message.objects.filter(
        Q(sender_farmer__isnull=False, receiver_expert__isnull=False) |
        Q(sender_expert__isnull=False, receiver_farmer__isnull=False)
    ).annotate(
        farmer_id=Case(
            When(sender_farmer__isnull=False, then=F('sender_farmer')),
            default=F('receiver_farmer'),
        ),
        expert_id=Case(
            When(sender_expert__isnull=False, then=F('sender_expert')),
            default=F('receiver_expert'),
        )
    ).select_related("sender_farmer", "receiver_farmer", "sender_expert", "receiver_expert")
    
    # Organize messages by farmer–expert pair
    grouped_consultations = {}
    for msg in messages:
        key = (msg.farmer_id, msg.expert_id)
        grouped_consultations.setdefault(key, []).append(msg)
    
    consultations = []
    for pair, msgs in grouped_consultations.items():
        solved_msgs = [m for m in msgs if m.is_solved]
        solved_msgs.sort(key=lambda x: x.timestamp)
        
        for i, solved in enumerate(solved_msgs, start=1):
            solved.solved_count = i
            consultations.append(solved)
        
        if not solved_msgs:
            latest_msg = sorted(msgs, key=lambda x: x.timestamp)[-1]
            latest_msg.solved_count = None
            consultations.append(latest_msg)
    
    consultations.sort(key=lambda x: x.timestamp, reverse=True)
    
    # === PREDICTION HISTORY DATA ===
    predictions = PredictionHistory.objects.select_related('farmer', 'library').all().order_by('-uploaded_at')
    
    # Categorize predictions
    pest_classes = [
        'Beetle', 'Brown Plant Hopper', 'Grass Hopper', 'Paddy Stem Maggot',
        'Rice Gall Midge', 'Rice Leaf Caterpillar', 'Rice Leaf Hopper',
        'Rice Leaf Roller', 'Rice Skipper', 'Rice Stem Borer Adult',
        'Rice Stem Borer Larva', 'Rice Water Weevil', 'Thrips'
    ]
    
    disease_classes = [
        'Bacterial Leaf Blight', 'Bacterial Leaf Streak', 'Bakanae', 'Brown Spot',
        'Dead Heart', 'Downy', 'Grassy Stunt Virus', 'Healthy Leaf', 'Healthyn Grain',
        'Hispa Disease', 'Leaf Scald', 'Narrow Brown Spot', 'Neck Blast',
        'Ragged Stunt Virus', 'Rice Blast', 'Rice False Smut', 'Rice Leaffolder',
        'Rice Stripes', 'Sheath Blight', 'Sheath Rot', 'Stem Rot', 'Tungro Virus', 'Grain rot'
    ]
    
    # Add category to each prediction
    for pred in predictions:
        if pred.predicted_class in pest_classes:
            pred.category = 'Peste'
        elif pred.predicted_class in disease_classes:
            pred.category = 'Sakit'
        else:
            pred.category = 'Unknown'
    
    # === EXPERT POSTS DATA ===
    expert_posts = ExpertPost.objects.annotate(
        upvotes_count=Count('upvote'),
        comments_count=Count('comment')
    ).select_related('expert').order_by('-created_at')
    
    # === FARMER POSTS DATA ===
    farmer_posts = FarmerPost.objects.annotate(
        upvotes_count=Count('farmerupvote'),
        comments_count=Count('farmerpostcomment')
    ).select_related('farmer').order_by('-created_at')
    
    # === LIBRARY DATA ===
    library_entries = Library.objects.all().order_by('-created_at')
    
    # === STATISTICS ===
    total_farmers = farmers.count()
    total_experts = experts.count()
    total_consultations = len(consultations)
    solved_consultations = sum(1 for c in consultations if c.is_solved)
    total_predictions = predictions.count()
    total_expert_posts = expert_posts.count()
    total_farmer_posts = farmer_posts.count()
    
    context = {
        # Demographics
        "farmers": farmers,
        "experts": experts,
        "pending_experts": pending_experts,
        "approved_experts": approved_experts,
        "rejected_experts": rejected_experts,
        
        # Consultations
        "consultations": consultations,
        
        # Predictions
        "predictions": predictions,
        
        # Posts
        "expert_posts": expert_posts,
        "farmer_posts": farmer_posts,
        
        # Library
        "library_entries": library_entries,
        
        # Statistics
        "total_farmers": total_farmers,
        "total_experts": total_experts,
        "total_consultations": total_consultations,
        "solved_consultations": solved_consultations,
        "total_predictions": total_predictions,
        "total_expert_posts": total_expert_posts,
        "total_farmer_posts": total_farmer_posts,
        
        # Current date for reports
        "report_date": timezone.now(),
    }
    
    return render(request, "adminako/admin_reports.html", context)
# END OF NEW ADMIN REPORTS

# CHANGED OCT 1 BY VO ON TOP
# def admin_reports(request):
#     # Fetch all farmers from the AgriExpert_farmer table
#     farmers_response = supabase.table("AgriExpert_farmer").select("*").execute()
#     farmers = farmers_response.data if farmers_response.data else []

#     # Fetch all experts from the AgriExpert_expert table
#     experts_response = supabase.table("AgriExpert_expert").select("*").execute()
#     experts = experts_response.data if experts_response.data else []

#     # Filter experts based on status
#     pending_experts = [expert for expert in experts if expert["status"] == "Pending"]
#     approved_experts = [expert for expert in experts if expert["status"] == "Approved"]
#     rejected_experts = [expert for expert in experts if expert["status"] == "Rejected"]

#     # Group messages uniquely per farmer–expert pair
#     messages = Message.objects.filter(
#         Q(sender_farmer__isnull=False, receiver_expert__isnull=False) |
#         Q(sender_expert__isnull=False, receiver_farmer__isnull=False)
#     ).annotate(
#         farmer_id=Case(
#             When(sender_farmer__isnull=False, then=F('sender_farmer')),
#             default=F('receiver_farmer'),
#         ),
#         expert_id=Case(
#             When(sender_expert__isnull=False, then=F('sender_expert')),
#             default=F('receiver_expert'),
#         )
#     ).select_related("sender_farmer", "receiver_farmer", "sender_expert", "receiver_expert")

#     # Organize messages by farmer–expert pair
#     grouped_consultations = {}
#     for msg in messages:
#         key = (msg.farmer_id, msg.expert_id)
#         grouped_consultations.setdefault(key, []).append(msg)

#     consultations = []
#     for pair, msgs in grouped_consultations.items():
#         solved_msgs = [m for m in msgs if m.is_solved]
#         solved_msgs.sort(key=lambda x: x.timestamp)

#         # Assign solved count
#         for i, solved in enumerate(solved_msgs, start=1):
#             solved.solved_count = i
#             consultations.append(solved)

#         if not solved_msgs:
#             # No solved messages — add latest one as ongoing
#             latest_msg = sorted(msgs, key=lambda x: x.timestamp)[-1]
#             latest_msg.solved_count = None  # Indicates ongoing
#             consultations.append(latest_msg)

#     # Sort final consultations for table display
#     consultations.sort(key=lambda x: x.timestamp, reverse=True)

#     context = {
#         "farmers": farmers,
#         "experts": experts,
#         "pending_experts": pending_experts,
#         "approved_experts": approved_experts,
#         "rejected_experts": rejected_experts,
#         "consultations": consultations,
#     }
#     return render(request, "adminako/admin_reports.html", context)

# Explicitly set Pandoc path (Replace this with your actual Pandoc path)
PANDOC_PATH = r"C:\Users\LENOVO_\AppData\Local\Pandoc\pandoc.exe"
pypandoc.pandoc_path = PANDOC_PATH  # Set Pandoc path in pypandoc

# def convert_docx_to_pdf(request):
#     file_url = request.GET.get('file_url')
    
#     if not file_url:
#         return JsonResponse({'error': 'No file URL provided'}, status=400)

#     # Extract filename from URL
#     parsed_url = urlparse(file_url)
#     filename = os.path.basename(parsed_url.path)  # Example: "example.docx"
#     pdf_filename = filename.replace(".docx", ".pdf")

#     # Download DOCX file from Supabase
#     local_docx_path = f"C:/laragon/www/CapstoneAgriExpertvenv/temp/{filename}"
#     local_pdf_path = local_docx_path.replace(".docx", ".pdf")

#     response = requests.get(file_url)
#     if response.status_code == 200:
#         with open(local_docx_path, 'wb') as f:
#             f.write(response.content)
#     else:
#         return JsonResponse({'error': 'Failed to download DOCX file'}, status=500)

#     # Convert DOCX to PDF using LibreOffice
#     try:
#         subprocess.run([
#             r"C:\Program Files\LibreOffice\program\soffice.exe",
#             "--headless", "--convert-to", "pdf", local_docx_path, "--outdir", os.path.dirname(local_pdf_path)
#         ], check=True)
#     except subprocess.CalledProcessError as e:
#         return JsonResponse({'error': f'Failed to convert DOCX: {e}'}, status=500)

#     # Upload converted PDF back to Supabase (Bucket: "media/proof_of_expertise_pdfs")
#     with open(local_pdf_path, "rb") as pdf_file:
#         supabase.storage.from_("media").upload(f"proof_of_expertise_pdfs/{pdf_filename}", pdf_file, {"content-type": "application/pdf"})

#     # Generate the Supabase public URL for the new PDF file
#     pdf_url = f"{SUPABASE_URL}/storage/v1/object/public/media/proof_of_expertise_pdfs/{pdf_filename}"

#     # Clean up local files (optional)
#     os.remove(local_docx_path)
#     os.remove(local_pdf_path)

#     return JsonResponse({'pdf_url': pdf_url})


# LibreOffice Path (Windows)
LIBREOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"

# Temp Folder for Local Conversion
TEMP_FOLDER = os.path.join(settings.BASE_DIR, "temp")
os.makedirs(TEMP_FOLDER, exist_ok=True)

def convert_docx_to_pdf(request):
    file_url = request.GET.get("file_url")
    if not file_url:
        return JsonResponse({"error": "Missing file_url parameter"}, status=400)

    try:
        # Extract file name
        file_name = os.path.basename(file_url)
        pdf_filename = file_name.replace(".docx", ".pdf")
        pdf_path = f"converted_pdfs/{pdf_filename}"

        # 🔍 Step 1: Check if the PDF already exists in Supabase
        existing_pdf_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(pdf_path)
        pdf_response = requests.head(existing_pdf_url)  # Check if file exists

        if pdf_response.status_code == 200:
            print("✅ PDF already exists. Returning URL:", existing_pdf_url)
            return JsonResponse({"pdf_url": existing_pdf_url})  # ✅ Return existing PDF URL

        # 📥 Step 2: Download DOCX from Supabase
        docx_path = os.path.join(TEMP_FOLDER, file_name)
        response = requests.get(file_url)
        if response.status_code != 200:
            return JsonResponse({"error": "Failed to download DOCX file"}, status=500)

        with open(docx_path, "wb") as file:
            file.write(response.content)

        # 🔄 Step 3: Convert DOCX → PDF
        local_pdf_path = os.path.join(TEMP_FOLDER, pdf_filename)

        command = [
            LIBREOFFICE_PATH, "--headless", "--convert-to", "pdf", "--outdir", TEMP_FOLDER, docx_path
        ]
        subprocess.run(command, check=True)

        # 📤 Step 4: Upload PDF to Supabase Storage
        with open(local_pdf_path, "rb") as pdf_file:
         pdf_data = pdf_file.read()  # Read file content first
        supabase.storage.from_(SUPABASE_BUCKET).upload(
        pdf_path, 
        pdf_data, 
        {
            "content-type": "application/pdf",
            "cacheControl": "3600",
            "contentDisposition": "inline"  # Forces browser preview
        }
    )
        # ✅ Step 5: Get Public URL of the newly uploaded PDF
        new_pdf_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(pdf_path)
        print("✅ PDF uploaded successfully:", new_pdf_url)

        # 🧹 Step 6: Cleanup Temp Files
        os.remove(docx_path)
        os.remove(local_pdf_path)

        return JsonResponse({"pdf_url": new_pdf_url})

    except subprocess.CalledProcessError as e:
        return JsonResponse({"error": f"Conversion failed: {e}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


from django.shortcuts import render, get_object_or_404

def view_expert(request, expert_id):
    expert = get_object_or_404(Expert, id=expert_id)
    return render(request, "adminako/viewedit/view_expert.html", {"expert": expert})

def generate_expert_pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Eksperto_Report.pdf"'

    pdf = SimpleDocTemplate(response, pagesize=landscape(letter))
    elements = []

    # Title (Centered)
    title = [["Eksperto Demographic Report"]]
    title_table = Table(title, colWidths=[550])
    title_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 16),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(title_table)

    # **Date & Time (Centered)**
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_info = [[f"Generated on: {now}"]]
    date_table = Table(date_info, colWidths=[550])  # Full width for centering
    date_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(date_table)

    # Fetch experts from Supabase based on status
    statuses = ["Pending", "Approved", "Rejected"]
    
    for status in statuses:
        # Section Title
        section_title = [[f"{status} Eksperto:"]]
        section_table = Table(section_title, colWidths=[550])
        section_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(section_table)

        # Get data
        experts = supabase.table("AgriExpert_expert").select("*").eq("status", status).execute()

        # If no records
        if not experts.data:
            no_data_table = Table([["No records found."]], colWidths=[550])
            no_data_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            elements.append(no_data_table)
            continue

        # Table Data
        table_data = [["ID", "Full Name", "Email", "Phone", "Barangay", "License Number"]]  # Headers
        for expert in experts.data:
            table_data.append([
                str(expert["id"]),
                f"{expert['first_name']} {expert['last_name']}",
                expert["email"],
                expert["phone_number"],
                expert["barangay"],
                expert["license_number"],
            ])

        # Table Styling
        table = Table(table_data, colWidths=[50, 150, 200, 100, 100, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)

    # Footer (Centered)
    footer = [["AgriExpert 2025 - Victoria Farmers Association"]]
    footer_table = Table(footer, colWidths=[550])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Oblique'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
    ]))
    elements.append(footer_table)

    # Build PDF
    pdf.build(elements)
    return response

def generate_farmer_pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Magsasaka_Report.pdf"'

    pdf = canvas.Canvas(response, pagesize=landscape(letter))

    # Title (Centered)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(400, 550, "Magsasaka Demographic Report")

    # Date & Time (Centered)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(400, 530, f"Generated on: {now}")

    # Fetch all farmers from Supabase
    farmers = supabase.table("AgriExpert_farmer").select("*").execute()

    # If no data, show message
    if not farmers.data:
        pdf.drawString(50, 500, "No farmer records found.")
        pdf.save()
        return response

    # Table Data
    table_data = [["ID", "Full Name", "Email", "Phone", "Barangay", "Farm Size (Hectares)"]]
    for farmer in farmers.data:
        table_data.append([
            str(farmer["id"]),
            f"{farmer['first_name']} {farmer['last_name']}",
            farmer["email"],
            farmer["phone_number"],
            farmer["barangay"],
            str(farmer["farm_size"]) + " ha" if "farm_size" in farmer else "N/A"
        ])

    # Create Table
    table = Table(table_data, colWidths=[50, 150, 200, 100, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Draw Table
    table.wrapOn(pdf, 50, 300)
    table.drawOn(pdf, 50, 300)

    # Footer (Centered)
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawCentredString(400, 50, "AgriExpert 2025 - Victoria Farmers Association")

    pdf.save()
    return response



from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@csrf_exempt
def update_expert_status(request):
    if request.method == "POST":
        expert_id = request.POST.get("expert_id")
        new_status = request.POST.get("status")
        
        expert = get_object_or_404(Expert, id=expert_id)
        expert.status = new_status
        expert.save()

        # Define email message
        if new_status == "Approved":
            subject = "AgriExpert: Account Approved"
            message = f"""Magandang Araw {expert.first_name}, 
            Ang iyong detalye ay nabusisi na ng aming admin at malugod na ibinabalita na na approve na ang iyong account sa AgriExpert.
            Mangyaring mag login upang tignan ang iyong account. 
            Salamat!"""
        elif new_status == "Rejected":
            subject = "AgriExpert: Account Rejected"
            message = f"""Paumanhin {expert.first_name},
            Matapos ang aming pagsusuri, hindi namin ma-approve ang iyong account sa AgriExpert.
            Mangyaring makipag-ugnayan sa admin para sa karagdagang impormasyon. 
            Salamat!"""
        else:
            subject = "AgriExpert: Account Under Review"
            message = f"""Kumusta {expert.first_name}, 
            Ang iyong account ay kasalukuyang sinusuri ng aming admin. Makakatanggap ka ng update sa lalong madaling panahon.
            Salamat!"""

        # Send email
        send_mail(
            subject,
            message,
            "admin@agriexpert.com",
            [expert.email],
            fail_silently=False,
        )

        return JsonResponse({"message": "Status updated and email sent successfully!"})

    return JsonResponse({"error": "Invalid request"}, status=400)
# farmer

# def predict(request):
#     if request.method == 'POST' and request.FILES.get('image'):
#         if not request.user.is_authenticated:
#             return render(request, 'farmer/farmer_scan.html', {'error': "Please log in first."})

#         image = request.FILES['image']
#         farmer = Farmer.objects.get(username=request.user.username)  # Get logged-in farmer
        
#         # Generate a unique filename
#         unique_filename = f"{uuid.uuid4()}_{image.name}"

#         # Upload image to Supabase "media" bucket
#         try:
#             response = supabase.storage.from_("media").upload(unique_filename, image.file)
#             image_url = f"{SUPABASE_URL}/storage/v1/object/public/media/{unique_filename}"
#         except Exception as e:
#             return render(request, 'farmer/farmer_scan.html', {'error': f"Image upload failed: {str(e)}"})

#         # Make the prediction based on the uploaded image
#         predicted_class, confidence = predict_plant_disease(image_url)  # Call your ML model function

#         if confidence < 70:
#             predicted_class = "Unknown"

#         # Save prediction history in the database
#         prediction_history = PredictionHistory(
#             farmer=farmer,
#             image=image_url,  # Store the Supabase URL
#             predicted_class=predicted_class,
#             confidence=confidence
#         )
#         prediction_history.save()

#         # Render results
#         return render(request, 'farmer/farmer_scan.html', {
#             'uploaded_file_url': image_url,
#             'predicted_class': predicted_class,
#             'confidence': confidence
#         })

#     return render(request, 'farmer/farmer_scan.html')

def farmer_scan(request):
    return render(request, 'farmer/farmer_scan.html')

def farmer_library(request):
    return render(request, 'farmer/farmer_library.html')

from .models import Library
def get_library_details(request, paksa):
    try:
        item = Library.objects.get(paksa__iexact=paksa)
        data = {
            "paksa": item.paksa,
            "deskripsyon": item.deskripsyon,
            "ano_ang_nagagawa_nito": item.ano_ang_nagagawa_nito,
            "bakit_at_saan_ito_nangyayari": item.bakit_at_saan_ito_nangyayari,
            "paano_ito_matutukoy": item.paano_ito_matutukoy,
            "bakit_ito_mahalaga": item.bakit_ito_mahalaga,
            "paano_ito_pangangasiwaan": item.paano_ito_pangangasiwaan
        }
        return JsonResponse(data)
    except Library.DoesNotExist:
        return JsonResponse({"error": "Item not found"}, status=404)
    

from django.utils.dateparse import parse_date
# For History of Scan of Farmers
@csrf_exempt
def get_prediction_history(request):
    if request.method == "GET":
        user_id = request.session.get("user_id")
        role = request.session.get("role")

        if not user_id or role != "Magsasaka":
            return JsonResponse({"error": "Unauthorized"}, status=401)

        # Class name lists
        pest_classes = [
            'Beetle', 'Brown Plant Hopper', 'Grass Hopper', 'Paddy Stem Maggot',
            'Rice Gall Midge', 'Rice Leaf Caterpillar', 'Rice Leaf Hopper',
            'Rice Leaf Roller', 'Rice Skipper', 'Rice Stem Borer Adult',
            'Rice Stem Borer Larva', 'Rice Water Weevil', 'Thrips'
        ]
        disease_classes = [
            'Bacterial Leaf Blight', 'Bacterial Leaf Streak', 'Brown Spot',
            'Dead Heart Pest Attack Symptom','Grain Rot','Healthy Grain',
            'Healthy Leaf','Leaf Scald','Rice Blast','Rice False Smut',
            'Rice Stripe Virus','Sheath Blight','Stem Rot','Tungro Virus',
            'Unknown'
        ]

        history = PredictionHistory.objects.filter(farmer_id=user_id).order_by("-uploaded_at")

        # Optional filtering
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        classification = request.GET.get("classification")  # peste / sakit

        if start_date:
            history = history.filter(uploaded_at__date__gte=parse_date(start_date))
        if end_date:
            history = history.filter(uploaded_at__date__lte=parse_date(end_date))
        if classification:
            classification = classification.lower()
            if classification == "peste":
                history = history.filter(predicted_class__in=pest_classes)
            elif classification == "sakit":
                history = history.filter(predicted_class__in=disease_classes)

        data = [
            {
                "id": h.id,
                "predicted_class": h.predicted_class,
                "confidence": h.confidence,
                "uploaded_at": h.uploaded_at.strftime("%Y-%m-%d %H:%M"),
                "image_url": h.image_url,
            }
            for h in history
        ]
        return JsonResponse({"history": data}, safe=False)

    return JsonResponse({"error": "Invalid request method"}, status=405)

# def farmer_experts(request):
#     return render(request, 'farmer/farmer_experts.html')
# def farmer_experts(request):
#     try:
#         # Fetch only approved experts
#         approved_experts_response = supabase.table("AgriExpert_expert").select("*").eq("status", "Approved").execute()
#         approved_experts = approved_experts_response.data if approved_experts_response.data else []

#     except Exception as e:
#         approved_experts = []

#     context = {
#         "approved_experts": approved_experts,
#     }
#     return render(request, "farmer/farmer_experts.html", context)
# def farmer_experts(request):
#     try:
#         user_id = request.session.get("user_id")
#         user_role = request.session.get("role")

#         if not user_id or user_role != "Magsasaka":
#             messages.error(request, "Kailangan mong mag-login bilang Magsasaka upang makita ang mga eksperto.")
#             return redirect("login")

#         # Fetch only approved experts
#         approved_experts_response = supabase.table("AgriExpert_expert").select("*").eq("status", "Approved").execute()
#         approved_experts = approved_experts_response.data if approved_experts_response.data else []

#         # Get list of expert IDs with whom the farmer has existing messages
#         existing_chat_response = supabase.table("AgriExpert_messages").select("receiver_expert").eq("sender_farmer", user_id).execute()
#         existing_chat_experts = [message["receiver_expert"] for message in existing_chat_response.data] if existing_chat_response.data else []

#     except Exception as e:
#         approved_experts = []
#         existing_chat_experts = []

#     context = {
#         "approved_experts": approved_experts,
#         "existing_chat_experts": existing_chat_experts,  # Pass to template
#     }
#     return render(request, "farmer/farmer_experts.html", context)

# def farmer_experts(request):
#     try:
#         user_id = request.session.get("user_id")
#         user_role = request.session.get("role")

#         if not user_id or user_role != "Magsasaka":
#             messages.error(request, "Kailangan mong mag-login bilang Magsasaka upang makita ang mga eksperto.")
#             return redirect("login")

#         # Fetch only approved experts
#         approved_experts_response = supabase.table("AgriExpert_expert").select("*").eq("status", "Approved").execute()
#         approved_experts = approved_experts_response.data if approved_experts_response.data else []

#         # Get list of expert IDs with whom the farmer has existing messages
#         existing_chat_response = supabase.table("AgriExpert_messages").select("receiver_expert_id").eq("sender_farmer_id", user_id).execute()
#         existing_chat_experts = [message["receiver_expert_id"] for message in existing_chat_response.data] if existing_chat_response.data else []

#         # Add a flag to indicate if the farmer has a chat with the expert
#         for expert in approved_experts:
#             expert["has_existing_chat"] = expert["id"] in existing_chat_experts
            
#     except Exception as e:
#         print(f"❌ Error fetching experts: {e}")
#         approved_experts = []

#     context = {
#         "approved_experts": approved_experts,
#     }
#     return render(request, "farmer/farmer_experts.html", context)

from .models import ExpertPost

# def farmer_experts(request):
#     try:
#         user_id = request.session.get("user_id")
#         user_role = request.session.get("role")

#         if not user_id or user_role != "Magsasaka":
#             messages.error(request, "Kailangan mong mag-login bilang Magsasaka upang makita ang mga eksperto.")
#             return redirect("login")

#         # Fetch approved experts
#         approved_experts_response = supabase.table("AgriExpert_expert").select("*").eq("status", "Approved").execute()
#         approved_experts = approved_experts_response.data if approved_experts_response.data else []

#         # Check chats
#         existing_chat_response = supabase.table("AgriExpert_messages").select("receiver_expert_id").eq("sender_farmer_id", user_id).execute()
#         existing_chat_experts = [message["receiver_expert_id"] for message in existing_chat_response.data] if existing_chat_response.data else []

#         for expert in approved_experts:
#             expert["has_existing_chat"] = expert["id"] in existing_chat_experts

#         # ✅ Get expert posts using Django ORM
#         expert_posts = list(ExpertPost.objects.select_related('expert').all())

#         # Attach expert info manually using Supabase data
#         for post in expert_posts:
#             matching_expert = next((expert for expert in approved_experts if expert["id"] == post.expert.id), None)
#             post.expert.supabase_data = matching_expert

#         expert_posts.sort(key=lambda x: x.created_at, reverse=True)

#     except Exception as e:
#         print(f"❌ Error fetching experts: {e}")
#         approved_experts = []
#         expert_posts = []

#     context = {
#         "approved_experts": approved_experts,
#         "expert_posts": expert_posts,
#     }
#     return render(request, "farmer/farmer_experts.html", context)

def farmer_experts(request):
    try:
        user_id = request.session.get("user_id")
        user_role = request.session.get("role")

        if not user_id or user_role != "Magsasaka":
            messages.error(request, "Kailangan mong mag-login bilang Magsasaka upang makita ang mga eksperto.")
            return redirect("login")

        # Get filter parameters from request
        post_sort = request.GET.get('post_sort', 'newest')
        has_solution = request.GET.get('has_solution', '')
        search_query = request.GET.get('search', '')

        # Fetch approved experts using Django ORM
        approved_experts = Expert.objects.filter(status="Approved")

        # Check chats
        existing_chat_response = supabase.table("AgriExpert_messages").select("receiver_expert_id").eq("sender_farmer_id", user_id).execute()
        existing_chat_experts = [message["receiver_expert_id"] for message in existing_chat_response.data] if existing_chat_response.data else []

        # Get expert posts using Django ORM with filters
        expert_posts = ExpertPost.objects.select_related('expert').filter(expert__in=approved_experts)

        # Apply search filter
        if search_query:
            expert_posts = expert_posts.filter(
                models.Q(title__icontains=search_query) |
                models.Q(caption__icontains=search_query) |
                models.Q(expert__first_name__icontains=search_query) |
                models.Q(expert__last_name__icontains=search_query)
            )

        # Apply solution filter
        if has_solution == 'yes':
            # Get posts that have at least one solution comment
            posts_with_solutions = ExpertPost.objects.filter(
                comment__is_solution=True
            ).distinct()
            expert_posts = expert_posts.filter(id__in=posts_with_solutions)
        elif has_solution == 'no':
            # Get posts that don't have solution comments
            posts_without_solutions = ExpertPost.objects.exclude(
                comment__is_solution=True
            ).distinct()
            expert_posts = expert_posts.filter(id__in=posts_without_solutions)

        # Apply sorting (REMOVED most_upvotes option)
        if post_sort == 'oldest':
            expert_posts = expert_posts.order_by('created_at')
        elif post_sort == 'most_comments':
            expert_posts = expert_posts.annotate(
                comment_count=models.Count('comment')
            ).order_by('-comment_count')
        else:  # newest (default)
            expert_posts = expert_posts.order_by('-created_at')

        # Get stats for the dashboard
        total_experts = Expert.objects.filter(status="Approved").count()
        approved_experts_count = total_experts  # Since we're only showing approved
        total_posts = expert_posts.count()

        # Add additional methods for posts (SIMPLIFIED - no upvote checks)
        for post in expert_posts:
            # Get the marked solution comment
            solution_comment = post.get_comments().filter(is_solution=True).first()
            post.solution_comment = solution_comment
            
            # Get latest comments (limit to 3 for preview)
            post.latest_comments = post.get_comments().order_by('-created_at')[:3]
            # Add engagement metrics for display (only comments)
            post.comment_count = post.get_comments().count()

    except Exception as e:
        print(f"❌ Error fetching experts: {e}")
        approved_experts = []
        expert_posts = []
        total_experts = 0
        approved_experts_count = 0
        total_posts = 0

    context = {
        "approved_experts": approved_experts,
        "expert_posts": expert_posts,
        "existing_chat_experts": existing_chat_experts,
        "total_experts": total_experts,
        "approved_experts_count": approved_experts_count,
        "total_posts": total_posts,
        "current_filters": {
            'post_sort': post_sort,
            'has_solution': has_solution,
            'search_query': search_query,
        }
    }
    return render(request, "farmer/farmer_experts.html", context)

def view_expertfromfarmer(request, expert_id):
    try:
        # Fetch expert details by ID
        expert_response = supabase.table("AgriExpert_expert").select("*").eq("id", expert_id).single().execute()
        expert = expert_response.data if expert_response.data else None

    except Exception as e:
        expert = None

    return render(request, "farmer/viewedit/view_expertfromfarmer.html", {"expert": expert})

# def farmer_farmers(request):
#     return render(request, 'farmer/farmer_farmers.html')
# def farmer_farmers(request):
#     """
#     Display all farmer posts to farmers (similar to how admin sees expert posts)
#     """
#     # Check if user is logged in and is a farmer
#     if request.session.get("user_id") and request.session.get("role") == "Magsasaka":
#         # Get all farmers (excluding rejected ones if you have status field)
#         farmers = Farmer.objects.all().order_by('first_name')
        
#         # Get all farmer posts ordered by creation date
#         farmer_posts = FarmerPost.objects.all().order_by('-created_at')
        
#         # Add additional methods for posts if needed
#         for post in farmer_posts:
#             # Get latest comments (limit to 3 for preview, similar to expert posts)
#             post.latest_comments = post.get_comments()[:3]
            
#         context = {
#             'farmers': farmers,
#             'farmer_posts': farmer_posts,
#         }
        
#         return render(request, 'farmer/farmer_farmers.html', context)
#     else:
#         # Redirect unauthorized users
#         return redirect("login")
from django.views.decorators.http import require_POST

def farmer_farmers(request):
    """
    Display all farmer posts to farmers with filters and search functionality
    """
    # Check if user is logged in and is a farmer
    if request.session.get("user_id") and request.session.get("role") == "Magsasaka":
        current_user_id = request.session["user_id"]
        
        # Get filter parameters from request
        barangay_filter = request.GET.get('barangay', '')
        post_sort = request.GET.get('post_sort', 'newest')
        has_solution = request.GET.get('has_solution', '')
        search_query = request.GET.get('search', '')
        farm_size_min = request.GET.get('farm_size_min', '')
        farm_size_max = request.GET.get('farm_size_max', '')

        # Get all farmers (excluding rejected ones if you have status field)
        farmers = Farmer.objects.all().order_by('first_name')

        if barangay_filter:
            farmers = farmers.filter(barangay__icontains=barangay_filter)

        unique_barangays = Farmer.objects.values_list('barangay', flat=True).distinct().order_by('barangay')

        # Get all farmer posts with filters
        farmer_posts = FarmerPost.objects.select_related('farmer').prefetch_related(
            'images',
            'farmerpostcomment_set'
        ).all()
        
        # Search filter
        if search_query:
            farmer_posts = farmer_posts.filter(
                Q(title__icontains=search_query) |
                Q(caption__icontains=search_query) |
                Q(farmer__first_name__icontains=search_query) |
                Q(farmer__last_name__icontains=search_query) |
                Q(farmer__barangay__icontains=search_query)
            )
        
        # Barangay filter
        if barangay_filter:
            farmer_posts = farmer_posts.filter(farmer__barangay__icontains=barangay_filter)
        
        # Farm size filter
        if farm_size_min:
            farmer_posts = farmer_posts.filter(farmer__farm_size__gte=float(farm_size_min))
        if farm_size_max:
            farmer_posts = farmer_posts.filter(farmer__farm_size__lte=float(farm_size_max))
        
        # Solution filter
        if has_solution == 'yes':
            farmer_posts = farmer_posts.filter(farmerpostcomment__is_solution=True).distinct()
        elif has_solution == 'no':
            farmer_posts = farmer_posts.exclude(farmerpostcomment__is_solution=True).distinct()
        
        # Sorting
        if post_sort == 'oldest':
            farmer_posts = farmer_posts.order_by('created_at')
        elif post_sort == 'most_comments':
            farmer_posts = farmer_posts.annotate(
                comment_count=Count('farmerpostcomment')
            ).order_by('-comment_count')
        elif post_sort == 'most_upvotes':
            farmer_posts = farmer_posts.annotate(
                upvote_count=Count('farmerupvote')
            ).order_by('-upvote_count')
        elif post_sort == 'most_engagement':
            farmer_posts = farmer_posts.annotate(
                engagement=Count('farmerpostcomment') + Count('farmerupvote')
            ).order_by('-engagement')
        else:  # newest (default)
            farmer_posts = farmer_posts.order_by('-created_at')

        # Statistics
        total_farmers = Farmer.objects.count()
        total_posts = farmer_posts.count()
        total_comments = FarmerPostComment.objects.count()
        total_upvotes = FarmerUpvote.objects.count()
        
        # Barangay stats
        barangay_stats = Farmer.objects.values('barangay').annotate(
            farmer_count=Count('id'),
            post_count=Count('farmerpost')
        ).order_by('-farmer_count')

        # Add additional methods for posts
        current_farmer = Farmer.objects.get(id=current_user_id)
        for post in farmer_posts:
            # Get latest comments (limit to 3 for preview, similar to expert posts)
            post.latest_comments = post.get_comments()[:3]
            # Check if current user has upvoted this post
            post.user_has_upvoted = FarmerUpvote.objects.filter(
                post=post, farmer=current_farmer
            ).exists()
            # Add engagement metrics
            post.comment_count = post.get_comments().count()
            post.upvote_count = post.get_upvotes_count()
            post.engagement_score = post.comment_count + post.upvote_count
            post.has_solution = post.get_comments().filter(is_solution=True).exists()
            
        context = {
            'farmers': farmers,
            'farmer_posts': farmer_posts,
            'unique_barangays': unique_barangays,
            'total_farmers': total_farmers,
            'total_posts': total_posts,
            'total_comments': total_comments,
            'total_upvotes': total_upvotes,
            'barangay_stats': barangay_stats[:6],
            'current_filters': {
                'barangay': barangay_filter,
                'post_sort': post_sort,
                'has_solution': has_solution,
                'search_query': search_query,
                'farm_size_min': farm_size_min,
                'farm_size_max': farm_size_max,
            }
        }
        
        return render(request, 'farmer/farmer_farmers.html', context)
    else:
        # Redirect unauthorized users
        return redirect("login")
    
# def farmer_farmers(request):
#     """
#     Display all farmer posts to farmers (similar to how admin sees expert posts)
#     """
#     # Check if user is logged in and is a farmer
#     if request.session.get("user_id") and request.session.get("role") == "Magsasaka":
#         current_user_id = request.session["user_id"]
        
#         # Get all farmers (excluding rejected ones if you have status field)
#         farmers = Farmer.objects.all().order_by('first_name')
        
#         # Get all farmer posts ordered by creation date
#         farmer_posts = FarmerPost.objects.all().order_by('-created_at')
        
#         # Add additional methods for posts if needed
#         for post in farmer_posts:
#             # Get latest comments (limit to 3 for preview, similar to expert posts)
#             post.latest_comments = post.get_comments()[:3]
#             # Check if current user has upvoted this post
#             current_farmer = Farmer.objects.get(id=current_user_id)
#             post.user_has_upvoted = FarmerUpvote.objects.filter(
#                 post=post, farmer=current_farmer
#             ).exists()
            
#         context = {
#             'farmers': farmers,
#             'farmer_posts': farmer_posts,
#         }
        
#         return render(request, 'farmer/farmer_farmers.html', context)
#     else:
#         # Redirect unauthorized users
#         return redirect("login")


def view_farmer_post(request, post_id):
    """
    View individual farmer post with all comments
    """
    if not (request.session.get("user_id") and request.session.get("role") == "Magsasaka"):
        return redirect("login")
    
    post = get_object_or_404(FarmerPost, id=post_id)
    current_user_id = request.session["user_id"]
    current_farmer = Farmer.objects.get(id=current_user_id)
    
    # Check if user has upvoted
    user_has_upvoted = FarmerUpvote.objects.filter(
        post=post, farmer=current_farmer
    ).exists()
    
    # Get all comments
    comments = post.get_comments()
    
    # Get solution comment if exists
    solution_comment = comments.filter(is_solution=True).first()
    
    context = {
        'post': post,
        'comments': comments,
        'solution_comment': solution_comment,
        'user_has_upvoted': user_has_upvoted,
    }
    
    return render(request, 'farmer/viewedit/view_farmer_post.html', context)


@require_POST
def toggle_farmer_post_upvote(request, post_id):
    """
    Toggle upvote for a farmer post
    """
    if not (request.session.get("user_id") and request.session.get("role") == "Magsasaka"):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    post = get_object_or_404(FarmerPost, id=post_id)
    current_user_id = request.session["user_id"]
    current_farmer = Farmer.objects.get(id=current_user_id)
    
    # Check if user already upvoted
    upvote, created = FarmerUpvote.objects.get_or_create(
        post=post,
        farmer=current_farmer
    )
    
    if not created:
        # User already upvoted, so remove the upvote
        upvote.delete()
        upvoted = False
    else:
        # New upvote created
        upvoted = True
    
    # Get updated count
    upvote_count = post.get_upvotes_count()
    
    return JsonResponse({
        'upvoted': upvoted,
        'upvote_count': upvote_count
    })


@require_POST
def add_farmer_post_comment(request, post_id):
    """
    Add comment to a farmer post
    """
    if not (request.session.get("user_id") and request.session.get("role") == "Magsasaka"):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    post = get_object_or_404(FarmerPost, id=post_id)
    current_user_id = request.session["user_id"]
    current_farmer = Farmer.objects.get(id=current_user_id)
    
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({'error': 'Comment cannot be empty'}, status=400)
        
        # Create the comment
        comment = FarmerPostComment.objects.create(
            post=post,
            farmer=current_farmer,
            content=content
        )
        
        # Return comment data
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%b %d, %Y %H:%M'),
                'commenter_name': f"{current_farmer.first_name} {current_farmer.last_name}",
                'commenter_type': 'farmer',
                'profile_picture': current_farmer.profile_picture or '/static/default-profile.jpg'
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# For experts to interact with farmer posts (if you want to allow this)
def expert_view_farmer_posts(request):
    """
    Allow experts to view and interact with farmer posts
    """
    if not (request.session.get("user_id") and request.session.get("role") == "Eksperto"):
        return redirect("login")
    
    current_user_id = request.session["user_id"]
    current_expert = Expert.objects.get(id=current_user_id)
    
    # Get all farmer posts
    farmer_posts = FarmerPost.objects.all().order_by('-created_at')
    
    for post in farmer_posts:
        post.latest_comments = post.get_comments()[:3]
        # Check if expert has upvoted
        post.user_has_upvoted = FarmerUpvote.objects.filter(
            post=post, expert=current_expert
        ).exists()
    
    context = {
        'farmer_posts': farmer_posts,
        'user_type': 'expert'
    }
    
    return render(request, 'expert/view_farmer_posts.html', context)


@require_POST
def expert_toggle_farmer_post_upvote(request, post_id):
    """
    Allow expert to upvote farmer post
    """
    if not (request.session.get("user_id") and request.session.get("role") == "Eksperto"):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    post = get_object_or_404(FarmerPost, id=post_id)
    current_user_id = request.session["user_id"]
    current_expert = Expert.objects.get(id=current_user_id)
    
    upvote, created = FarmerUpvote.objects.get_or_create(
        post=post,
        expert=current_expert
    )
    
    if not created:
        upvote.delete()
        upvoted = False
    else:
        upvoted = True
    
    return JsonResponse({
        'upvoted': upvoted,
        'upvote_count': post.get_upvotes_count()
    })


@require_POST
def expert_add_farmer_post_comment(request, post_id):
    """
    Allow expert to comment on farmer post
    """
    if not (request.session.get("user_id") and request.session.get("role") == "Eksperto"):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    post = get_object_or_404(FarmerPost, id=post_id)
    current_user_id = request.session["user_id"]
    current_expert = Expert.objects.get(id=current_user_id)
    
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({'error': 'Comment cannot be empty'}, status=400)
        
        comment = FarmerPostComment.objects.create(
            post=post,
            expert=current_expert,
            content=content
        )
        
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%b %d, %Y %H:%M'), 
                'commenter_name': f"{current_expert.first_name} {current_expert.last_name}",
                'commenter_type': 'expert',
                'profile_picture': current_expert.profile_picture or '/static/default-profile.jpg'
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


    
# def message_expert(request, expert_id):
#     try:
#         # Fetch expert details by ID
#         expert_response = supabase.table("AgriExpert_expert").select("*").eq("id", expert_id).single().execute()
#         expert = expert_response.data if expert_response.data else None

#     except Exception as e:
#         expert = None

#     return render(request, "farmer/viewedit/message_expert.html", {"expert": expert})

def message_expert(request, expert_id):
    try:
        # Fetch expert details by ID
        expert_response = supabase.table("AgriExpert_expert").select("*").eq("id", expert_id).single().execute()
        expert = expert_response.data if expert_response.data else None

        # Get the current farmer ID
        user_id = request.session.get("user_id")
        if user_id:
            existing_messages = Message.objects.filter(sender_farmer_id=user_id, receiver_expert_id=expert_id).exists()
        else:
            existing_messages = False

    except Exception as e:
        expert = None
        existing_messages = False

    return render(request, "farmer/viewedit/message_expert.html", {
        "expert": expert,
        "existing_messages": existing_messages
    })


# def farmer_collab(request):
#     return render(request, 'farmer/farmer_collab.html')
from django.db.models import Q
from django.db import models
# def farmer_collab(request):
#     user_id = request.session.get("user_id")
#     farmer = get_object_or_404(Farmer, id=user_id)

#     # Get all experts who have sent or received messages with this farmer
#     experts = Expert.objects.filter(
#         models.Q(received_messages_expert__sender_farmer=farmer) |
#         models.Q(sent_messages_expert__receiver_farmer=farmer)
#     ).distinct()

#     # Fetch latest messages for each expert
#     expert_messages = []
#     for expert in experts:
#         latest_message = Message.objects.filter(
#             models.Q(sender_farmer=farmer, receiver_expert=expert) |
#             models.Q(sender_expert=expert, receiver_farmer=farmer)
#         ).order_by("-timestamp").first()

#         expert_messages.append({"expert": expert, "latest_message": latest_message})

#     return render(request, "farmer/farmer_collab.html", {"expert_messages": expert_messages})

# def farmer_collab(request):
#     user_id = request.session.get("user_id")
#     farmer = get_object_or_404(Farmer, id=user_id)

#     # ✅ Get all experts who have exchanged messages with this farmer
#     experts = Expert.objects.filter(
#         Q(received_messages_expert__sender_farmer=farmer) |
#         Q(sent_messages_expert__receiver_farmer=farmer)
#     ).distinct()

#     # ✅ Fetch latest messages for each expert
#     expert_messages = []
#     for expert in experts:
#         latest_message = Message.objects.filter(
#             Q(sender_farmer=farmer, receiver_expert=expert) |
#             Q(sender_expert=expert, receiver_farmer=farmer)
#         ).order_by("-timestamp").first()  # Get latest message

#         # ✅ Append each expert & their latest message
#         expert_messages.append({
#             "expert": expert, 
#             "latest_message": latest_message
#         })

#     print("Experts Found:", len(expert_messages))  # Debugging print

#     return render(request, "farmer/farmer_collab.html", {"expert_messages": expert_messages})
def farmer_collab(request):
    user_id = request.session.get("user_id")
    farmer = get_object_or_404(Farmer, id=user_id)

    # ✅ Get all experts who have exchanged messages with this farmer
    experts = Expert.objects.filter(
        Q(received_messages_expert__sender_farmer=farmer) |
        Q(sent_messages_expert__receiver_farmer=farmer)
    ).distinct()

    # ✅ Fetch latest messages for each expert
    expert_messages = []
    for expert in experts:
        latest_message = Message.objects.filter(
            Q(sender_farmer=farmer, receiver_expert=expert) |
            Q(sender_expert=expert, receiver_farmer=farmer)
        ).order_by("-timestamp").first()  # Get latest message

        # ✅ Append each expert & their latest message
        expert_messages.append({
            "expert": expert, 
            "latest_message": latest_message if latest_message else None
        })

    # ✅ Sort the conversations by latest message timestamp (newest first)
    expert_messages.sort(key=lambda x: x["latest_message"].timestamp if x["latest_message"] else None, reverse=True)

    return render(request, "farmer/farmer_collab.html", {"expert_messages": expert_messages})

# def chat_detail(request, expert_id):
#     user_id = request.session.get("user_id")
#     farmer = get_object_or_404(Farmer, id=user_id)
#     expert = get_object_or_404(Expert, id=expert_id)

#     messages = Message.objects.filter(
#         models.Q(sender_farmer=farmer, receiver_expert=expert) |
#         models.Q(sender_expert=expert, receiver_farmer=farmer)
#     ).order_by("timestamp")

#     return render(request, "farmer/viewedit/chat_detail.html", {"expert": expert, "messages": messages, "farmer": farmer})
def chat_detail(request, expert_id):
    user_id = request.session.get("user_id")
    farmer = get_object_or_404(Farmer, id=user_id)
    expert = get_object_or_404(Expert, id=expert_id)

    # ✅ Get all messages exchanged between this farmer and expert
    messages = Message.objects.filter(
        Q(sender_farmer=farmer, receiver_expert=expert) |
        Q(sender_expert=expert, receiver_farmer=farmer)
    ).order_by("timestamp")

    # ✅ Mark all unread messages as read
    messages.filter(receiver_farmer=farmer, is_read=False).update(is_read=True)

    return render(request, "farmer/viewedit/chat_detail.html", {"messages": messages, "expert": expert})

def farmer_profile(request):
    return render(request, 'farmer/farmer_profile.html')
# password reseta
# class PasswordResetRequestView(View):
#     def get(self, request):
#         form = PasswordResetRequestForm()
#         return render(request, 'email/password_reset.html', {'form': form})

#     def post(self, request):
#         form = PasswordResetRequestForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             role = form.cleaned_data['role']

#             # Query Supabase to check if the user exists
#             response = supabase.table(role).select("id", "username").eq("email", email).execute()

#             if response.data:
#                 # Generate Reset Link
#                 reset_link = f"http://127.0.0.1:8000/reset_password/confirm/{role}/{email}/"

#                 # Send Email
#                 subject = "I-reset ang iyong AgriExpert Password"
#                 message = f"""
#                 Kumusta {response.data[0]['username']},

#                 Humiling ka ng pag-reset ng password. I-click ang link sa ibaba upang baguhin ang iyong password:

#                 {reset_link}
    
#                 Kung hindi ikaw ang humiling nito, huwag pansinin ang email na ito.

#                 Salamat,
#                 AgriExpert Team
#                 """
#                 send_mail(subject, message, 'agriexpertvfa@gmail.com'0p, [email], fail_silently=False)

#                 messages.success(request, "Ipinadala na ang email sa pag-reset ng password.")
#                 return redirect('password_reset_done')
#             else:
#                 messages.error(request, "Walang nahanap na user sa role na ito.")

#         return render(request, 'email/password_reset.html', {'form': form})

class PasswordResetRequestView(View):
    def get(self, request):
        """ Show the password reset form when accessed via GET """
        form = PasswordResetRequestForm()
        return render(request, 'email/password_reset.html', {'form': form})

    def post(self, request):
        """ Handle form submission when accessed via POST """
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']

            # Query Supabase for the user
            response = supabase.table(role).select("id", "username").eq("email", email).execute()

            if response.data:
                # Generate the reset link dynamically
                host = request.get_host()
                reset_link = f"http://{host}/reset_password/confirm/{role}/{email}/"

                # Send Email
                subject = "I-reset ang iyong AgriExpert Password"
                message = f"""
                Kumusta {response.data[0]['username']},

                Humiling ka ng pag-reset ng password. I-click ang link sa ibaba upang baguhin ang iyong password:

                {reset_link}

                Kung hindi ikaw ang humiling nito, huwag pansinin ang email na ito.

                Salamat,
                AgriExpert Team
                """
                send_mail(subject, message, 'agriexpertvfa@gmail.com', [email], fail_silently=False)

                messages.success(request, "Ipinadala na ang email sa pag-reset ng password.")
                return redirect('password_reset_done')
            else:
                messages.error(request, "Walang nahanap na user sa role na ito.")

        return render(request, 'email/password_reset.html', {'form': form})

class PasswordResetConfirmView(View):
    def get(self, request, role, email):
        form = PasswordResetConfirmForm()
        return render(request, 'email/password_confirm.html', {'form': form, 'role': role, 'email': email})

    def post(self, request, role, email):
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']

            if new_password != confirm_password:
                messages.error(request, "Ang password ay hindi magkatugma.")
                return render(request, 'email/password_confirm.html', {'form': form, 'role': role, 'email': email})

            # ✅ Hash the password before saving
            hashed_password = make_password(new_password)  

            # ✅ Update password in Supabase
            response = supabase.table(role).update({"password": hashed_password}).eq("email", email).execute()

            if response.data:
                messages.success(request, "Matagumpay na na-reset ang iyong password!")
                return redirect('password_reset_complete')
            else:
                messages.error(request, "May naganap na error. Pakisubukang muli.")

        return render(request, 'email/password_confirm.html', {'form': form, 'role': role, 'email': email})
    
    
# def admin_reports(request):
#     return render(request, 'adminako/admin_reports.html')
# def view_expert(request, expert_id):
#     return render(request, "adminako/viewedit/view_expert.html", {"expert_id": expert_id})

# def edit_expert(request, expert_id):
#     return render(request, "adminako/viewedit/edit_expert.html", {"expert_id": expert_id})

# def view_farmer(request, farmer_id):
#     return render(request, "adminako/viewedit/view_farmer.html", {"farmer_id": farmer_id})  # ✅ Fixed Template Name
# def view_farmer(request, farmer_id):
#     print(f"Received farmer_id: {farmer_id}")  # Debugging output

#     # Fetch the farmer from Supabase
#     response = supabase.table("AgriExpert_farmer").select("*").eq("id", farmer_id).execute()

#     if response.data:
#         farmer = response.data[0]  # First record
#         print(f"Farmer Data: {farmer}")  # Debugging output
#         return render(request, 'adminako/viewedit/view_farmer.html', {'farmer': farmer})
#     else:
#         print("No farmer found!")  # Debugging output
#         return render(request, 'adminako/viewedit/view_farmer.html', {'error': 'Farmer not found'})

# def view_farmer(request, farmer_id):
#     farmer = get_object_or_404(Farmer, id=farmer_id)
#     return render(request, "adminako/viewedit/view_farmer.html", {"farmer": farmer})
def view_farmer(request, farmer_id):
    farmer = get_object_or_404(Farmer, id=farmer_id)
    
    # Get farmer's posts with related images
    farmer_posts = FarmerPost.objects.filter(farmer=farmer).prefetch_related('images').order_by('-created_at')
    
    # Get farmer's comments
    farmer_comments = FarmerPostComment.objects.filter(farmer=farmer).select_related('post').order_by('-created_at')[:10]
    
    # Get farmer's consultations
    consultations = Message.objects.filter(
        Q(sender_farmer=farmer) | Q(receiver_farmer=farmer)
    ).select_related('receiver_expert', 'sender_expert').order_by('-timestamp')[:20]
    
    # Calculate statistics
    total_posts = farmer_posts.count()
    total_comments = FarmerPostComment.objects.filter(farmer=farmer).count()
    total_consultations = consultations.count()
    total_predictions = PredictionHistory.objects.filter(farmer=farmer).count()
    
    context = {
        'farmer': farmer,
        'farmer_posts': farmer_posts,
        'farmer_comments': farmer_comments,
        'consultations': consultations,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_consultations': total_consultations,
        'total_predictions': total_predictions,
    }
    
    return render(request, "adminako/viewedit/view_farmer.html", context)
def admin_library(request):
    return render(request, 'adminako/admin_library.html')

# def admin_farmers(request):
#     return render(request, 'adminako/admin_farmers.html')

# def admin_experts(request):
#     return render(request, 'adminako/admin_experts.html')
# def admin_experts(request):
#     # Fetch all experts except rejected ones
#     experts = Expert.objects.exclude(status="Rejected").order_by('-id')  # Show latest first
#     return render(request, 'adminako/admin_experts.html', {'experts': experts})

# def admin_experts(request):
#     # Fetch all experts except rejected ones
#     experts = Expert.objects.exclude(status="Rejected").order_by('-id')  # Show latest first
    
#     # Fetch posts for all experts
#     expert_posts = ExpertPost.objects.filter(expert__in=experts).order_by('-created_at')
    
#     # Get the solution comments and regular comments for each post
#     for post in expert_posts:
#         # Get solution comment if available
#         solution_comment = post.get_comments().filter(is_solution=True).first()
#         if solution_comment:
#             post.solution_comment = solution_comment
#         else:
#             post.solution_comment = None
            
#         # Get regular comments (limited to latest few for display)
#         post.latest_comments = post.get_comments().order_by('-created_at')[:3]
    
#     return render(request, 'adminako/admin_experts.html', {
#         'experts': experts,
#         'expert_posts': expert_posts
#     })
def admin_experts(request):
    # Get filter parameters from request
    expert_status = request.GET.get('expert_status', '')
    post_sort = request.GET.get('post_sort', 'newest')
    has_solution = request.GET.get('has_solution', '')
    search_query = request.GET.get('search', '')
    
    # Fetch all experts except rejected ones
    experts = Expert.objects.exclude(status="Rejected").order_by('-id')
    
    # Apply expert status filter
    if expert_status:
        experts = experts.filter(status=expert_status)
    
    # Fetch posts for filtered experts
    expert_posts = ExpertPost.objects.filter(expert__in=experts)
    
    # Apply search filter
    if search_query:
        expert_posts = expert_posts.filter(
            models.Q(title__icontains=search_query) |
            models.Q(caption__icontains=search_query) |
            models.Q(expert__first_name__icontains=search_query) |
            models.Q(expert__last_name__icontains=search_query)
        )
    
    # Apply solution filter
    if has_solution == 'yes':
        # Get posts that have at least one solution comment
        posts_with_solutions = ExpertPost.objects.filter(
            comment__is_solution=True
        ).distinct()
        expert_posts = expert_posts.filter(id__in=posts_with_solutions)
    elif has_solution == 'no':
        # Get posts that don't have solution comments
        posts_without_solutions = ExpertPost.objects.exclude(
            comment__is_solution=True
        ).distinct()
        expert_posts = expert_posts.filter(id__in=posts_without_solutions)
    
    # Apply sorting
    if post_sort == 'oldest':
        expert_posts = expert_posts.order_by('created_at')
    elif post_sort == 'most_comments':
        expert_posts = expert_posts.annotate(
            comment_count=models.Count('comment')
        ).order_by('-comment_count')
    elif post_sort == 'most_upvotes':
        expert_posts = expert_posts.annotate(
            upvote_count=models.Count('upvote')
        ).order_by('-upvote_count')
    else:  # newest (default)
        expert_posts = expert_posts.order_by('-created_at')
    
    # Get stats for the dashboard
    total_experts = Expert.objects.exclude(status="Rejected").count()
    approved_experts = Expert.objects.filter(status="Approved").count()
    pending_experts = Expert.objects.filter(status="Pending").count()
    total_posts = expert_posts.count()
    
    # Get the solution comments and regular comments for each post
    for post in expert_posts:
        solution_comment = post.get_comments().filter(is_solution=True).first()
        if solution_comment:
            post.solution_comment = solution_comment
        else:
            post.solution_comment = None
            
        post.latest_comments = post.get_comments().order_by('-created_at')[:3]
        # Add engagement metrics for display
        post.comment_count = post.get_comments().count()
        post.upvote_count = post.get_upvotes_count()
    
    context = {
        'experts': experts,
        'expert_posts': expert_posts,
        'total_experts': total_experts,
        'approved_experts': approved_experts,
        'pending_experts': pending_experts,
        'total_posts': total_posts,
        'current_filters': {
            'expert_status': expert_status,
            'post_sort': post_sort,
            'has_solution': has_solution,
            'search_query': search_query,
        }
    }
    
    return render(request, 'adminako/admin_experts.html', context)

def view_post_asadmin(request, post_id):
    try:
        print(f"Attempting to fetch post with ID: {post_id}")
        post = get_object_or_404(ExpertPost, id=post_id)
        print(f"Post found: {post.title}")

        # Check if the post has images and comments
        images = post.get_images()
        print(f"Images found: {images.count()}")
        
        comments = post.get_comments()
        print(f"Comments found: {comments.count()}")
        
        solution_comment = comments.filter(is_solution=True).first()
        print(f"Solution comment found: {solution_comment is not None}")

        # Calculate engagement metrics
        upvotes_count = post.get_upvotes_count()
        comments_count = comments.count()
        total_engagement = upvotes_count + comments_count

        context = {
            'post': post,
            'images': images,
            'solution_comment': solution_comment,
            'other_comments': comments.filter(is_solution=False).order_by('-created_at'),
            'upvotes_count': upvotes_count,
            'comments_count': comments_count,
            'total_engagement': total_engagement,
        }

        # Check if the template exists
        template_path = 'adminako/viewedit/view_post_asadmin.html'
        try:
            from django.template.loader import get_template
            template = get_template(template_path)
            print(f"Template found: {template_path}")
        except Exception as e:
            print(f"Template error: {str(e)}")
            return HttpResponse(f"Template not found: {template_path}")

        return render(request, template_path, context)

    except Exception as e:
        print(f"Error in view_post_asadmin: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full stack trace
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect("admin_experts")
# def view_post_asadmin(request, post_id):
#     try:
#         print(f"Attempting to fetch post with ID: {post_id}")
#         post = get_object_or_404(ExpertPost, id=post_id)
#         print(f"Post found: {post.title}")

#         # Check if the post has images and comments
#         images = post.get_images()
#         print(f"Images found: {images.count()}")
        
#         comments = post.get_comments()
#         print(f"Comments found: {comments.count()}")
        
#         solution_comment = comments.filter(is_solution=True).first()
#         print(f"Solution comment found: {solution_comment is not None}")

#         context = {
#             'post': post,
#             'images': images,
#             'solution_comment': solution_comment,
#             'other_comments': comments.filter(is_solution=False).order_by('-created_at'),
#         }

#         # Check if the template exists
#         template_path = 'adminako/viewedit/view_post_asadmin.html'
#         try:
#             from django.template.loader import get_template
#             template = get_template(template_path)
#             print(f"Template found: {template_path}")
#         except Exception as e:
#             print(f"Template error: {str(e)}")
#             return HttpResponse(f"Template not found: {template_path}")

#         return render(request, template_path, context)

#     except Exception as e:
#         print(f"Error in view_post_asadmin: {str(e)}")
#         import traceback
#         traceback.print_exc()  # Print full stack trace
#         messages.error(request, f"An error occurred: {str(e)}")
#         return redirect("admin_experts")

    
# def admin_farmers(request):
#     farmers = Farmer.objects.all()

#     # Generate random colors for each farmer
#     for farmer in farmers:
#         farmer.random_color = f"#{random.randint(0, 0xFFFFFF):06x}"  # Generates a random HEX color

#     return render(request, 'adminako/admin_farmers.html', {'farmers': farmers})
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
# from django.contrib.auth.decorators import login_required
# from .models import Farmer, FarmerPost, FarmerPostImage, FarmerPostComment, FarmerUpvote

# def admin_farmers(request):
#     """
#     Display all registered farmers and their posts for admin management
#     """
#     # Get all registered farmers ordered by ID (most recent first)
#     registered_farmers = Farmer.objects.all().order_by('-id')
    
#     # Get all farmer posts with related data - using correct related names
#     farmer_posts = FarmerPost.objects.select_related('farmer').prefetch_related(
#         'images',  # This is the correct related_name from FarmerPostImage
#         'farmerpostcomment_set'  # Default related_name for FarmerPostComment
#     ).order_by('-created_at')
    
#     # Add latest comments to each post (limit to 3)
#     for post in farmer_posts:
#         post.latest_comments = post.get_comments()[:3]
    
#     # Pagination for posts
#     paginator = Paginator(farmer_posts, 10)  # Show 10 posts per page
#     page_number = request.GET.get('page')
#     farmer_posts_paginated = paginator.get_page(page_number)
    
#     context = {
#         'registered_farmers': registered_farmers,
#         'farmer_posts': farmer_posts_paginated,
#     }
    
#     return render(request, 'adminako/admin_farmers.html', context)
from django.db.models import Q, Count
from django.core.paginator import Paginator

def admin_farmers(request):
    """
    Display all registered farmers and their posts for admin management with filters
    """

    # Filters
    barangay_filter = request.GET.get('barangay', '')
    post_sort = request.GET.get('post_sort', 'newest')
    has_solution = request.GET.get('has_solution', '')
    search_query = request.GET.get('search', '')
    farm_size_min = request.GET.get('farm_size_min', '')
    farm_size_max = request.GET.get('farm_size_max', '')
    
    # Registered farmers
    registered_farmers = Farmer.objects.all().order_by('-id')

    if barangay_filter:
        registered_farmers = registered_farmers.filter(barangay__icontains=barangay_filter)

    unique_barangays = Farmer.objects.values_list('barangay', flat=True).distinct().order_by('barangay')

    # Farmer posts
    farmer_posts = FarmerPost.objects.select_related('farmer').prefetch_related(
        'images',
        'farmerpostcomment_set'
    ).order_by('-created_at')
    
    # Search filter
    if search_query:
        farmer_posts = farmer_posts.filter(
            Q(title__icontains=search_query) |
            Q(caption__icontains=search_query) |
            Q(farmer__first_name__icontains=search_query) |
            Q(farmer__last_name__icontains=search_query) |
            Q(farmer__barangay__icontains=search_query)
        )
    
    # Barangay filter
    if barangay_filter:
        farmer_posts = farmer_posts.filter(farmer__barangay__icontains=barangay_filter)
    
    # Farm size filter
    if farm_size_min:
        farmer_posts = farmer_posts.filter(farmer__farm_size__gte=float(farm_size_min))
    if farm_size_max:
        farmer_posts = farmer_posts.filter(farmer__farm_size__lte=float(farm_size_max))
    
    # Solution filter
    if has_solution == 'yes':
        farmer_posts = farmer_posts.filter(farmerpostcomment__is_solution=True).distinct()
    elif has_solution == 'no':
        farmer_posts = farmer_posts.exclude(farmerpostcomment__is_solution=True).distinct()
    
    # Sorting
    if post_sort == 'oldest':
        farmer_posts = farmer_posts.order_by('created_at')
    elif post_sort == 'most_comments':
        farmer_posts = farmer_posts.annotate(
            comment_count=Count('farmerpostcomment')
        ).order_by('-comment_count')
    elif post_sort == 'most_upvotes':
        farmer_posts = farmer_posts.annotate(
            upvote_count=Count('farmerupvote')
        ).order_by('-upvote_count')
    elif post_sort == 'most_engagement':
        farmer_posts = farmer_posts.annotate(
            engagement=Count('farmerpostcomment') + Count('farmerupvote')
        ).order_by('-engagement')
    
    # Statistics
    total_farmers = Farmer.objects.count()
    total_posts = FarmerPost.objects.count()
    total_comments = FarmerPostComment.objects.count()
    total_upvotes = FarmerUpvote.objects.count()
    
    # Barangay stats
    barangay_stats = Farmer.objects.values('barangay').annotate(
        farmer_count=Count('id'),
        post_count=Count('farmerpost')
    ).order_by('-farmer_count')
    
    # Compute metrics for each post
    for post in farmer_posts:
        post.latest_comments = post.get_comments()[:3]
        post.comment_count = post.get_comments().count()
        post.upvote_count = post.get_upvotes_count()
        post.engagement_score = post.comment_count + post.upvote_count
        post.has_solution = post.get_comments().filter(is_solution=True).exists()

    # Pagination
    paginator = Paginator(farmer_posts, 10)
    page_number = request.GET.get('page')
    farmer_posts_paginated = paginator.get_page(page_number)

    context = {
        'registered_farmers': registered_farmers,
        'farmer_posts': farmer_posts_paginated,
        'unique_barangays': unique_barangays,
        'total_farmers': total_farmers,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_upvotes': total_upvotes,
        'barangay_stats': barangay_stats[:5],
        'current_filters': {
            'barangay': barangay_filter,
            'post_sort': post_sort,
            'has_solution': has_solution,
            'search_query': search_query,
            'farm_size_min': farm_size_min,
            'farm_size_max': farm_size_max,
        }
    }

    return render(request, 'adminako/admin_farmers.html', context)


def admin_view_farmer(request, farmer_id):
    """
    View detailed information about a specific farmer
    """
    farmer = get_object_or_404(Farmer, id=farmer_id)
    
    # Get farmer's posts with related images
    farmer_posts = FarmerPost.objects.filter(farmer=farmer).prefetch_related('images').order_by('-created_at')
    
    # Get farmer's comments
    farmer_comments = FarmerPostComment.objects.filter(farmer=farmer).select_related('post').order_by('-created_at')[:10]
    
    # Calculate statistics
    total_posts = farmer_posts.count()
    total_comments = FarmerPostComment.objects.filter(farmer=farmer).count()
    
    context = {
        'farmer': farmer,
        'farmer_posts': farmer_posts,
        'farmer_comments': farmer_comments,
        'total_posts': total_posts,
        'total_comments': total_comments,
    }
    
    return render(request, 'adminako/admin_view_farmer.html', context)

# def admin_view_farmer_post(request, post_id):
#     """
#     View detailed information about a specific farmer post
#     """
#     post = get_object_or_404(FarmerPost, id=post_id)
    
#     # Get all comments for this post
#     comments = FarmerPostComment.objects.filter(post=post).select_related(
#         'farmer', 'expert'
#     ).order_by('created_at')
    
#     # Get post images using the correct related name
#     post_images = post.images.all()
    
#     # Get upvotes count
#     upvotes_count = post.get_upvotes_count()
    
#     context = {
#         'post': post,
#         'comments': comments,
#         'post_images': post_images,
#         'upvotes_count': upvotes_count,
#     }
    
#     return render(request, 'adminako/admin_view_farmer_post.html', context)

def admin_view_farmer_post(request, post_id):
    """
    View detailed information about a specific farmer post
    """
    post = get_object_or_404(FarmerPost, id=post_id)
    
    # Get all comments for this post
    comments = FarmerPostComment.objects.filter(post=post).select_related(
        'farmer', 'expert'
    ).order_by('created_at')
    
    # Get post images using the correct related name
    post_images = post.images.all()
    
    upvotes = FarmerUpvote.objects.filter(post=post).select_related('farmer', 'expert').order_by('-created_at')
    upvotes_count = upvotes.count()
    farmer_upvotes = upvotes.filter(farmer__isnull=False)
    expert_upvotes = upvotes.filter(expert__isnull=False)
    
    solution_comments = comments.filter(is_solution=True)
    has_solution = solution_comments.exists()
    
    total_engagement = upvotes_count + comments.count()
    
    context = {
        'post': post,
        'comments': comments,
        'post_images': post_images,
        'upvotes_count': upvotes_count,
        'upvotes': upvotes,
        'farmer_upvotes': farmer_upvotes,
        'expert_upvotes': expert_upvotes,
        'solution_comments': solution_comments,
        'has_solution': has_solution,
        'total_engagement': total_engagement,
    }
    
    return render(request, 'adminako/admin_view_farmer_post.html', context)

def admin_remove_farmer_post(request, post_id):
    """
    Remove a farmer post (admin action)
    """
    if request.method == 'POST':
        post = get_object_or_404(FarmerPost, id=post_id)
        farmer_name = f"{post.farmer.first_name} {post.farmer.last_name}"
        post_title = post.title
        
        try:
            # Delete associated images first (using correct related name)
            post.images.all().delete()
            
            # Delete associated comments
            FarmerPostComment.objects.filter(post=post).delete()
            
            # Delete associated upvotes
            FarmerUpvote.objects.filter(post=post).delete()
            
            # Delete the post
            post.delete()
            
            messages.success(
                request, 
                f'Post "{post_title}" by {farmer_name} has been successfully removed.'
            )
        except Exception as e:
            messages.error(
                request, 
                f'Error removing post: {str(e)}'
            )
    
    return redirect('admin_farmers')

def admin_library(request):
    """
    Display the admin library page
    """
    return render(request, 'adminako/admin_library.html')

# Additional helper views

def admin_search_farmers(request):
    """
    Search farmers by name or barangay
    """
    query = request.GET.get('q', '')
    
    if query:
        farmers = Farmer.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(middle_name__icontains=query) |
            Q(barangay__icontains=query) |
            Q(username__icontains=query)
        )
    else:
        farmers = Farmer.objects.all()
    
    farmers_data = []
    for farmer in farmers:
        farmers_data.append({
            'id': farmer.id,
            'name': f"{farmer.first_name} {farmer.middle_name or ''} {farmer.last_name}".strip(),
            'barangay': farmer.barangay,
            'farm_size': str(farmer.farm_size),
            'profile_picture': farmer.profile_picture,
            'username': farmer.username,
        })
    
    return JsonResponse({'farmers': farmers_data})

def admin_farmer_statistics(request):
    """
    Get farmer statistics for admin dashboard
    """
    total_farmers = Farmer.objects.count()
    total_posts = FarmerPost.objects.count()
    total_comments = FarmerPostComment.objects.count()
    
    # Recent activity (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    recent_posts = FarmerPost.objects.filter(
        created_at__gte=thirty_days_ago
    ).count()
    
    recent_comments = FarmerPostComment.objects.filter(
        created_at__gte=thirty_days_ago
    ).count()
    
    # Get posts with most upvotes
    popular_posts = FarmerPost.objects.all()[:5]  # You can add ordering by upvotes if needed
    
    stats = {
        'total_farmers': total_farmers,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'recent_posts': recent_posts,
        'recent_comments': recent_comments,
    }
    
    return JsonResponse(stats)

def admin_toggle_post_visibility(request, post_id):
    """
    Toggle post visibility (if you want to implement this feature)
    """
    if request.method == 'POST':
        post = get_object_or_404(FarmerPost, id=post_id)
        # You can add a visibility field to your model if needed
        messages.info(
            request,
            f'Post visibility management not implemented yet for "{post.title}".'
        )
    
    return redirect('admin_view_farmer_post', post_id=post_id)

from .forms import AdminProfileForm
def admin_profile(request):
    # Check if user is logged in as Admin
    if request.session.get('role') != 'Admin':
        messages.error(request, "Please log in as Admin to access this page.")
        return redirect('login')
    
    # Get the current admin from session
    admin_id = request.session.get('user_id')
    if not admin_id:
        messages.error(request, "Please log in to access your profile.")
        return redirect('login')
    
    try:
        admin_user = Admin.objects.get(id=admin_id)
    except Admin.DoesNotExist:
        messages.error(request, "Admin not found. Please log in again.")
        return redirect('login')
    
    profile_verified = False
    form = None
    
    if request.method == 'POST':
        if 'verify_password' in request.POST:
            # Password verification step
            current_password = request.POST.get('current_password')
            if check_password(current_password, admin_user.password):
                request.session['profile_verified'] = True
                profile_verified = True
                messages.success(request, "Password verified successfully. You can now view and update your profile.")
            else:
                messages.error(request, "Incorrect password. Please try again.")
        
        elif 'update_profile' in request.POST:
            # Check if profile is verified
            if not request.session.get('profile_verified'):
                messages.error(request, "Please verify your password first.")
                return redirect('admin_profile')
            
            # Check if this is just a profile picture update (from camera button)
            profile_picture = request.FILES.get('profile_picture')
            if profile_picture and not any(key in request.POST for key in ['first_name', 'last_name', 'email', 'organization', 'position']):
                # This is just a profile picture update from the camera button
                try:
                    profile_picture_url = upload_to_supabase(profile_picture, "admin_profile_pictures")
                    if profile_picture_url:
                        admin_user.profile_picture = profile_picture_url
                        admin_user.save()
                        messages.success(request, "Profile picture updated successfully!")
                    else:
                        messages.error(request, "Profile picture upload failed. Please try again.")
                except Exception as e:
                    messages.error(request, f"Error uploading profile picture: {str(e)}")
                return redirect('admin_profile')
            
            else:
                # This is a full form submission with other fields
                form = AdminProfileForm(request.POST, request.FILES, instance=admin_user)
                if form.is_valid():
                    # Handle password update if provided
                    new_password = form.cleaned_data.get('new_password')
                    if new_password:
                        admin_user.password = make_password(new_password)
                        messages.info(request, "Password updated successfully.")
                    
                    # Handle profile picture upload from form field
                    profile_picture = request.FILES.get('profile_picture')
                    if profile_picture:
                        profile_picture_url = upload_to_supabase(profile_picture, "admin_profile_pictures")
                        if profile_picture_url:
                            admin_user.profile_picture = profile_picture_url
                            messages.info(request, "Profile picture updated successfully.")
                        else:
                            messages.warning(request, "Profile picture upload failed, but other changes were saved.")
                    
                    # Save the admin user
                    admin_user.save()
                    # Also save the form to update other fields
                    form.save()
                    
                    messages.success(request, "Profile updated successfully!")
                    return redirect('admin_profile')
                else:
                    messages.error(request, "Please correct the errors below.")
    
    # If profile is verified, create form with current data
    if request.session.get('profile_verified'):
        profile_verified = True
        form = AdminProfileForm(instance=admin_user)
    
    context = {
        'admin': admin_user,
        'profile_verified': profile_verified,
        'form': form,
    }
    
    return render(request, 'adminako/admin_profile.html', context)

def admin_logout_profile(request):
    """Clear profile verification session"""
    if 'profile_verified' in request.session:
        del request.session['profile_verified']
    messages.info(request, "Profile session ended. Please verify password again to view profile.")
    return redirect('admin_profile')

from .models import Announcement, Admin
from .forms import AnnouncementForm

from django.utils import timezone
from datetime import datetime

def admin_announcements(request):
    # Check if user is logged in as Admin
    if request.session.get('role') != 'Admin':
        messages.error(request, "Please log in as Admin to access this page.")
        return redirect('login')
    
    # Get the current admin from session
    admin_id = request.session.get('user_id')
    if not admin_id:
        messages.error(request, "Please log in to access announcements.")
        return redirect('login')
    
    try:
        admin_user = Admin.objects.get(id=admin_id)
    except Admin.DoesNotExist:
        messages.error(request, "Admin not found. Please log in again.")
        return redirect('login')
    
    # Handle form submission
    if request.method == 'POST':
        if 'create_announcement' in request.POST:
            # Get form data
            title = request.POST.get('title')
            content = request.POST.get('content')
            status = request.POST.get('status', 'draft')
            priority = request.POST.get('priority', 'normal')
            target_audience = request.POST.get('target_audience', 'all')
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')
            
            # Validate required fields
            if not title or not content:
                messages.error(request, "Title and content are required.")
            else:
                try:
                    # Create announcement
                    announcement = Announcement(
                        title=title,
                        content=content,
                        author=admin_user,
                        status=status,
                        priority=priority,
                        target_audience=target_audience,
                    )
                    
                    # Handle dates - convert string to datetime
                    if start_date_str:
                        try:
                            # Parse the datetime string from form
                            start_date = datetime.fromisoformat(start_date_str)
                            announcement.start_date = timezone.make_aware(start_date)
                        except ValueError as e:
                            messages.warning(request, f"Invalid start date format: {str(e)}")
                    
                    if end_date_str:
                        try:
                            # Parse the datetime string from form
                            end_date = datetime.fromisoformat(end_date_str)
                            announcement.end_date = timezone.make_aware(end_date)
                        except ValueError as e:
                            messages.warning(request, f"Invalid end date format: {str(e)}")
                    
                    # Save announcement first to get an ID
                    announcement.save()
                    print(f"Announcement saved with ID: {announcement.id}")  # Debug
                    
                    # Handle image upload
                    image = request.FILES.get('image')
                    if image:
                        try:
                            image_url = upload_to_supabase(image, "announcement_images")
                            if image_url:
                                announcement.image = image_url
                                announcement.save()  # Save again with image URL
                                messages.info(request, "Announcement image uploaded successfully!")
                            else:
                                messages.warning(request, "Image upload failed, but announcement was created.")
                        except Exception as e:
                            messages.warning(request, f"Image upload error: {str(e)}")
                    
                    messages.success(request, "Announcement created successfully!")
                    return redirect('admin_announcements')
                    
                except Exception as e:
                    messages.error(request, f"Error creating announcement: {str(e)}")
                    # Debug information
                    print(f"Error details: {str(e)}")
        
        elif 'edit_announcement' in request.POST:
            # Handle edit announcement
            announcement_id = request.POST.get('announcement_id')
            title = request.POST.get('title')
            content = request.POST.get('content')
            status = request.POST.get('status')
            priority = request.POST.get('priority')
            target_audience = request.POST.get('target_audience')
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')
            
            try:
                announcement = Announcement.objects.get(id=announcement_id, author=admin_user)
                
                # Validate required fields
                if not title or not content:
                    messages.error(request, "Title and content are required.")
                else:
                    # Update announcement
                    announcement.title = title
                    announcement.content = content
                    announcement.status = status
                    announcement.priority = priority
                    announcement.target_audience = target_audience
                    
                    # Handle dates
                    if start_date_str:
                        try:
                            start_date = datetime.fromisoformat(start_date_str)
                            announcement.start_date = timezone.make_aware(start_date)
                        except ValueError:
                            announcement.start_date = None
                    else:
                        announcement.start_date = None
                    
                    if end_date_str:
                        try:
                            end_date = datetime.fromisoformat(end_date_str)
                            announcement.end_date = timezone.make_aware(end_date)
                        except ValueError:
                            announcement.end_date = None
                    else:
                        announcement.end_date = None
                    
                    # Handle image upload
                    image = request.FILES.get('image')
                    if image:
                        try:
                            image_url = upload_to_supabase(image, "announcement_images")
                            if image_url:
                                announcement.image = image_url
                                messages.info(request, "Announcement image updated successfully!")
                            else:
                                messages.warning(request, "Image upload failed, but announcement was updated.")
                        except Exception as e:
                            messages.warning(request, f"Image upload error: {str(e)}")
                    
                    announcement.save()
                    messages.success(request, "Announcement updated successfully!")
                    
            except Announcement.DoesNotExist:
                messages.error(request, "Announcement not found.")
            except Exception as e:
                messages.error(request, f"Error updating announcement: {str(e)}")
            
            return redirect('admin_announcements')
            
        elif 'delete_announcement' in request.POST:
            announcement_id = request.POST.get('announcement_id')
            try:
                announcement = Announcement.objects.get(id=announcement_id, author=admin_user)
                announcement.delete()
                messages.success(request, "Announcement deleted successfully!")
            except Announcement.DoesNotExist:
                messages.error(request, "Announcement not found.")
            return redirect('admin_announcements')
        
        elif 'update_status' in request.POST:
            announcement_id = request.POST.get('announcement_id')
            new_status = request.POST.get('new_status')
            try:
                announcement = Announcement.objects.get(id=announcement_id, author=admin_user)
                announcement.status = new_status
                announcement.save()
                messages.success(request, f"Announcement status updated to {new_status}!")
            except Announcement.DoesNotExist:
                messages.error(request, "Announcement not found.")
            return redirect('admin_announcements')
    
    # Get announcements for this admin
    announcements = Announcement.objects.filter(author=admin_user).order_by('-created_at')
    
    # Debug: Check if announcements are being retrieved
    print(f"Found {announcements.count()} announcements for admin {admin_user.username}")
    
    # Calculate statistics
    total_announcements = announcements.count()
    active_count = announcements.filter(status='active').count()
    draft_count = announcements.filter(status='draft').count()
    archived_count = announcements.filter(status='archived').count()
    
    # Separate announcements by status
    active_announcements_list = announcements.filter(status='active')
    draft_announcements_list = announcements.filter(status='draft')
    archived_announcements_list = announcements.filter(status='archived')
    
    form = AnnouncementForm()
    
    context = {
        'admin': admin_user,
        'form': form,
        'active_announcements': active_announcements_list,
        'draft_announcements': draft_announcements_list,
        'archived_announcements': archived_announcements_list,
        'total_announcements': total_announcements,
        'active_count': active_count,
        'draft_count': draft_count,
        'archived_count': archived_count,
    }
    
    return render(request, 'adminako/admin_announcements.html', context)

# You can remove the old edit_announcement view since we're handling edits in the main view now

from django.db.models import Q

def announcement_feed(request):
    """Public announcement feed for all users with filtering options"""
    
    # Get ALL active announcements from ALL admins
    announcements = Announcement.objects.filter(status='active').order_by('-created_at')
    
    # Get user info from session for unique view counting
    user_id = request.session.get('user_id')
    user_role = request.session.get('role', '').lower()
    
    # Map role to user_type
    user_type_map = {
        'admin': 'admin',
        'eksperto': 'expert',  # Map your role name to user_type
        'farmer': 'farmer'
    }
    user_type = user_type_map.get(user_role)
    
    # INCREMENT VIEW COUNT UNIQUELY FOR THIS USER
    for announcement in announcements:
        if user_id and user_type:
            announcement.increment_views(user_id=user_id, user_type=user_type)
        else:
            # For anonymous users, use simple counting
            announcement.increment_views()
    
    # Get filter parameters
    priority_filter = request.GET.get('priority', '')
    audience_filter = request.GET.get('audience', '')
    search_query = request.GET.get('search', '')
    
    # Apply filters
    if priority_filter:
        announcements = announcements.filter(priority=priority_filter)
    
    if audience_filter:
        announcements = announcements.filter(target_audience=audience_filter)
    
    if search_query:
        announcements = announcements.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    # Get filter counts for the sidebar
    total_count = announcements.count()
    priority_counts = {
        'urgent': announcements.filter(priority='urgent').count(),
        'high': announcements.filter(priority='high').count(),
        'normal': announcements.filter(priority='normal').count(),
        'low': announcements.filter(priority='low').count(),
    }
    
    audience_counts = {
        'all': announcements.filter(target_audience='all').count(),
        'farmers': announcements.filter(target_audience='farmers').count(),
        'experts': announcements.filter(target_audience='experts').count(),
        'both': announcements.filter(target_audience='both').count(),
    }
    
    context = {
        'announcements': announcements,
        'total_count': total_count,
        'priority_filter': priority_filter,
        'audience_filter': audience_filter,
        'search_query': search_query,
        'priority_counts': priority_counts,
        'audience_counts': audience_counts,
    }
    
    return render(request, 'adminako/viewedit/announcement_feed.html', context)
def admin_mapping(request):
    # Check if user is logged in as Admin using YOUR custom session
    if request.session.get('role') != 'Admin':
        messages.error(request, "Please log in as Admin to access this page.")
        return redirect('login')  # This should be YOUR custom login page, not Django admin
    
    # Get the current admin from session
    admin_id = request.session.get('user_id')
    if not admin_id:
        messages.error(request, "Please log in to access mapping.")
        return redirect('login')  # This should be YOUR custom login page
    
    try:
        admin_user = Admin.objects.get(id=admin_id)
    except Admin.DoesNotExist:
        messages.error(request, "Admin not found. Please log in again.")
        return redirect('login')  # This should be YOUR custom login page
    
    context = {
        'admin': admin_user,
    }
    
    return render(request, 'adminako/admin_mapping.html', context)
@csrf_exempt
@require_POST
def mark_farmer_comment_as_solution(request, comment_id):
    """
    Allow farmers to mark comments as solutions on their own posts
    """
    user_id = request.session.get("user_id")
    role = request.session.get("role")
    
    if not user_id or role != "Magsasaka":
        return JsonResponse({"success": False, "error": "Unauthorized. Only farmers can mark solutions."}, status=403)
    
    try:
        # Convert user_id to integer for comparison
        user_id = int(user_id)
        
        # Get the comment
        comment = get_object_or_404(FarmerPostComment, id=comment_id)
        
        # Check if the current user is the owner of the post
        if comment.post.farmer.id != user_id:
            return JsonResponse({"success": False, "error": "You can only mark solutions on your own posts."}, status=403)
        
        # Check if comment is already a solution
        if comment.is_solution:
            # Unmark as solution
            comment.is_solution = False
            comment.solution_highlighted = False
            comment.save()
            
            return JsonResponse({
                "success": True,
                "message": "Solution unmarked.",
                "is_solution": False,
                "comment_id": comment_id
            })
        else:
            # First, unmark any existing solutions for this post
            FarmerPostComment.objects.filter(post=comment.post, is_solution=True).update(is_solution=False, solution_highlighted=False)
            
            # Mark as solution
            comment.is_solution = True
            comment.solution_highlighted = True
            comment.save()
            
            # Get commenter name
            if comment.farmer:
                commenter_name = f"{comment.farmer.first_name} {comment.farmer.last_name}"
                commenter_type = "farmer"
            else:
                commenter_name = f"{comment.expert.first_name} {comment.expert.last_name}"
                commenter_type = "expert"
            
            return JsonResponse({
                "success": True,
                "message": "Comment marked as solution!",
                "is_solution": True,
                "comment_id": comment_id,
                "commenter_name": commenter_name,
                "commenter_type": commenter_type
            })
            
    except ValueError:
        return JsonResponse({"success": False, "error": "Invalid user ID."}, status=400)
    except FarmerPostComment.DoesNotExist:
        return JsonResponse({"success": False, "error": "Comment not found."}, status=404)
    except Exception as e:
        print(f"Error marking comment as solution: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    
@csrf_exempt
def api_detections_map(request):
    """API endpoint to get detection data for mapping"""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    # Check if user is admin
    if request.session.get('role') != 'Admin':
        return JsonResponse({"error": "Unauthorized"}, status=403)
    
    try:
        # Get filter parameters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        detection_type = request.GET.get('type', 'all')
        confidence_filter = request.GET.get('confidence', 'all')
        farmer_id = request.GET.get('farmer_id', 'all')
        
        # Disease and Pest class definitions
        DISEASE_CLASSES = [
            'Bacterial Leaf Blight', 'Bacterial Leaf Streak', 'Brown Spot',
            'Dead Heart Pest Attack Symptom', 'Grain Rot', 'Healthy Grain',
            'Healthy Leaf', 'Leaf scald', 'Rice Blast', 'Rice False Smut',
            'Rice Stripe Virus', 'Sheath Blight', 'Stem Rot', 'Tungro Virus', 'Unknown'
        ]
        
        PEST_CLASSES = [
            'Beetle', 'Brown Plant Hopper', 'Grass Hopper', 'Paddy Stem Maggot Fly',
            'Rice Gall Midge', 'Rice Leaf Caterpillar', 'Rice Leaf Hopper',
            'Rice Leaf Roller', 'Rice Skipper', 'Rice Stem Borer Adult',
            'Rice Stem Borer Larva', 'Rice Water Weevil', 'Thrips', 'Unknown'
        ]
        
        # Base queryset - only include detections with location data
        detections = PredictionHistory.objects.filter(
            Q(latitude__isnull=False) & Q(longitude__isnull=False)
        ).select_related('farmer', 'library').order_by('-uploaded_at')
        
        # Apply date filters
        if start_date:
            detections = detections.filter(uploaded_at__date__gte=start_date)
        if end_date:
            detections = detections.filter(uploaded_at__date__lte=end_date)
        
        # Apply detection type filter
        if detection_type != 'all':
            if detection_type == 'disease':
                detections = detections.filter(predicted_class__in=DISEASE_CLASSES)
            elif detection_type == 'pest':
                detections = detections.filter(predicted_class__in=PEST_CLASSES)
            elif detection_type == 'unknown':
                detections = detections.filter(predicted_class='Unknown')
        
        # Apply confidence filter
        if confidence_filter != 'all':
            if confidence_filter == 'high':
                detections = detections.filter(confidence__gte=80)
            elif confidence_filter == 'medium':
                detections = detections.filter(confidence__gte=60, confidence__lt=80)
            elif confidence_filter == 'low':
                detections = detections.filter(confidence__lt=60)
        
        # Apply farmer filter
        if farmer_id != 'all':
            detections = detections.filter(farmer_id=farmer_id)
        
        # Prepare detection data
        detection_data = []
        for detection in detections:
            detection_data.append({
                'id': detection.id,
                'predicted_class': detection.predicted_class,
                'confidence': float(detection.confidence),
                'image_url': detection.image_url,
                'latitude': float(detection.latitude) if detection.latitude else None,
                'longitude': float(detection.longitude) if detection.longitude else None,
                'location_accuracy': detection.location_accuracy,
                'uploaded_at': detection.uploaded_at.isoformat(),
                'farmer_name': f"{detection.farmer.first_name} {detection.farmer.last_name}",
                'farmer_barangay': detection.farmer.barangay,
                'library': {
                    'paksa': detection.library.paksa if detection.library else None,
                    'deskripsyon': detection.library.deskripsyon if detection.library else None,
                } if detection.library else None
            })
        
        # Calculate statistics
        total_detections = PredictionHistory.objects.count()
        
        # Disease count (excluding 'Unknown' from disease classes)
        disease_count = PredictionHistory.objects.filter(
            predicted_class__in=[c for c in DISEASE_CLASSES if c != 'Unknown']
        ).count()
        
        # Pest count (excluding 'Unknown' from pest classes)
        pest_count = PredictionHistory.objects.filter(
            predicted_class__in=[c for c in PEST_CLASSES if c != 'Unknown']
        ).count()
        
        # Unknown count (only the 'Unknown' class)
        unknown_count = PredictionHistory.objects.filter(
            predicted_class='Unknown'
        ).count()
        
        with_location_count = PredictionHistory.objects.filter(
            latitude__isnull=False, longitude__isnull=False
        ).count()
        
        # Get unique farmers for filter
        farmers = Farmer.objects.all().values('id', 'first_name', 'last_name', 'barangay')
        
        return JsonResponse({
            'detections': detection_data,
            'stats': {
                'total_detections': total_detections,
                'disease_count': disease_count,
                'pest_count': pest_count,
                'unknown_count': unknown_count,
                'with_location_count': with_location_count,
            },
            'farmers': list(farmers)
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    # Rest of your code...
# EXPERT
# def expert_home(request):
#     expert_id = request.session.get("user_id")  # Get logged-in expert ID

#     if not expert_id:
#         return redirect("login")

#     # Get unique farmer IDs the expert has interacted with
#     unique_farmers = set(
#         Message.objects.filter(
#             Q(receiver_expert_id=expert_id) | Q(sender_expert_id=expert_id)
#         ).values_list("sender_farmer", "receiver_farmer", flat=False)
#     )

#     # Flatten the set and remove None values (in case an expert-to-expert message exists)
#     unique_farmers = {farmer for pair in unique_farmers for farmer in pair if farmer is not None}

#     # Count solved consultations of this expert
#     solved_consultations = Message.objects.filter(
#         receiver_expert_id=expert_id, is_solved=True
#     ).count()

#     context = {
#         "unique_farmers": len(unique_farmers),  # Count of unique farmers
#         "solved_consultations": solved_consultations,
#     }
#     return render(request, "expert/home.html", context)


# def expert_home(request):
#     expert_id = request.session.get("user_id")

#     if not expert_id:
#         return redirect("login")

#     try:
#         # Unique Farmer Interactions
#         unique_farmers_set = set(
#             Message.objects.filter(
#                 Q(receiver_expert_id=expert_id) | Q(sender_expert_id=expert_id)
#             ).values_list("sender_farmer", "receiver_farmer", flat=False)
#         )
#         unique_farmers = {farmer for pair in unique_farmers_set for farmer in pair if farmer is not None}

#         # Consultation Stats
#         solved_consultations = Message.objects.filter(receiver_expert_id=expert_id, is_solved=True).count()
#         unsolved_consultations = Message.objects.filter(receiver_expert_id=expert_id, is_solved=False).count()
#         total_consultations = solved_consultations + unsolved_consultations

#         # Barangay Data
#         interacted_farmer_ids = list(unique_farmers)
#         barangays = Farmer.objects.filter(id__in=interacted_farmer_ids).values_list("barangay", flat=True)
#         barangay_counter = Counter(barangays)

#         barangay_labels = list(barangay_counter.keys())
#         barangay_counts = list(barangay_counter.values())

#         now = datetime.datetime.now()
#         month_labels = []
#         month_counts = []

#         for i in range(11, -1, -1):
#             month_date = now - datetime.timedelta(days=30 * i)
#             year = month_date.year
#             month = month_date.month

#             start_date = datetime.datetime(year, month, 1)
#             end_month = (month % 12) + 1
#             end_year = year + (1 if month == 12 else 0)
#             end_date = datetime.datetime(end_year, end_month, 1)

#             # Get messages where expert is sender or receiver during this month
#             messages = Message.objects.filter(
#                 Q(sender_expert_id=expert_id) | Q(receiver_expert_id=expert_id),
#                 timestamp__gte=start_date,
#                 timestamp__lt=end_date
#             )

#             # Extract all related farmer IDs from those messages
#             farmer_ids = set()
#             for msg in messages:
#                 if msg.sender_farmer_id:
#                     farmer_ids.add(msg.sender_farmer_id)
#                 if msg.receiver_farmer_id:
#                     farmer_ids.add(msg.receiver_farmer_id)

#             month_labels.append(start_date.strftime("%B %Y"))
#             month_counts.append(len(farmer_ids))

#     except Exception as e:
#         unique_farmers = set()
#         solved_consultations = unsolved_consultations = total_consultations = 0
#         barangay_labels = barangay_counts = month_labels = month_counts = []

#     context = {
#         "unique_farmers": len(unique_farmers),
#         "solved_consultations": solved_consultations,
#         "unsolved_consultations": unsolved_consultations,
#         "total_consultations": total_consultations,
#         "barangay_labels": barangay_labels,
#         "barangay_counts": barangay_counts,
#         "month_labels": month_labels,
#         "month_counts": month_counts,
#     }

#     return render(request, "expert/home.html", context)
from django.db.models import Q, Count, F
# @role_required("Eksperto")
# def expert_home(request):
#     expert_id = request.session.get("user_id")
#     print(f"🔹 DEBUG: Expert ID = {expert_id}")

#     if not expert_id:
#         print("❌ No expert ID found in session")
#         return redirect("login")

#     try:
#         # First, let's check if this expert exists
#         try:
#             expert = Expert.objects.get(id=expert_id)
#             print(f"✅ Expert found: {expert.first_name} {expert.last_name}")
#         except Expert.DoesNotExist:
#             print(f"❌ Expert with ID {expert_id} does not exist")
#             return redirect("login")

#         # Check total messages in database
#         total_messages = Message.objects.count()
#         print(f"🔹 Total messages in database: {total_messages}")
        
#         # Check messages involving this expert
#         expert_messages = Message.objects.filter(
#             Q(receiver_expert_id=expert_id) | Q(sender_expert_id=expert_id)
#         )
#         print(f"🔹 Messages involving this expert: {expert_messages.count()}")
        
#         # Debug: Print some sample messages
#         for msg in expert_messages[:3]:
#             print(f"  - Message: sender_farmer={msg.sender_farmer_id}, sender_expert={msg.sender_expert_id}, receiver_farmer={msg.receiver_farmer_id}, receiver_expert={msg.receiver_expert_id}")

#         # Get unique farmers this expert has interacted with
#         unique_farmers = set()
#         for msg in expert_messages:
#             if msg.sender_farmer_id:
#                 unique_farmers.add(msg.sender_farmer_id)
#             if msg.receiver_farmer_id:
#                 unique_farmers.add(msg.receiver_farmer_id)
        
#         unique_farmers.discard(None)
#         unique_farmers_count = len(unique_farmers)
#         print(f"🔹 Unique farmers: {unique_farmers}")
#         print(f"🔹 Unique farmers count: {unique_farmers_count}")

#         # Count consultations by conversation (farmer-expert pairs)
#         conversations = {}
#         for msg in expert_messages:
#             farmer_id = msg.sender_farmer_id or msg.receiver_farmer_id
#             if farmer_id:
#                 key = (farmer_id, expert_id)
#                 if key not in conversations:
#                     conversations[key] = {'total': 0, 'solved': False}
#                 conversations[key]['total'] += 1
#                 if msg.is_solved:
#                     conversations[key]['solved'] = True

#         print(f"🔹 Conversations: {conversations}")

#         solved_consultations = sum(1 for conv in conversations.values() if conv['solved'])
#         unsolved_consultations = len(conversations) - solved_consultations
#         total_consultations = len(conversations)

#         print(f"🔹 Solved = {solved_consultations}, Unsolved = {unsolved_consultations}, Total = {total_consultations}")

#         # Get barangay data for interacted farmers
#         barangay_labels = []
#         barangay_counts = []
        
#         if unique_farmers:
#             farmers_with_barangay = Farmer.objects.filter(
#                 id__in=list(unique_farmers)
#             ).values('barangay')
            
#             print(f"🔹 Farmers with barangay data: {list(farmers_with_barangay)}")
            
#             barangay_list = [f['barangay'] for f in farmers_with_barangay if f['barangay']]
#             barangay_counter = Counter(barangay_list)
#             barangay_labels = list(barangay_counter.keys())
#             barangay_counts = list(barangay_counter.values())

#         print(f"🔹 Barangay labels: {barangay_labels}")
#         print(f"🔹 Barangay counts: {barangay_counts}")

#         # Monthly interaction data - Fixed datetime usage
#         now = datetime.now()
#         month_labels = []
#         month_counts = []

#         print(f"🔹 Current date: {now}")

#         for i in range(11, -1, -1):  # Last 12 months
#             # Calculate the start of the month
#             month_date = now - timedelta(days=30 * i)
#             year = month_date.year
#             month = month_date.month
            
#             # Create proper datetime objects for the range
#             start_date = datetime(year, month, 1)
#             if month == 12:
#                 end_date = datetime(year + 1, 1, 1)
#             else:
#                 end_date = datetime(year, month + 1, 1)

#             print(f"🔹 Checking month: {start_date.strftime('%B %Y')} ({start_date} to {end_date})")

#             # Get messages in this time period
#             monthly_messages = Message.objects.filter(
#                 Q(sender_expert_id=expert_id) | Q(receiver_expert_id=expert_id),
#                 timestamp__gte=start_date,
#                 timestamp__lt=end_date
#             )

#             print(f"  - Messages in this month: {monthly_messages.count()}")

#             # Count unique farmers in this month
#             monthly_farmers = set()
#             for msg in monthly_messages:
#                 if msg.sender_farmer_id:
#                     monthly_farmers.add(msg.sender_farmer_id)
#                 if msg.receiver_farmer_id:
#                     monthly_farmers.add(msg.receiver_farmer_id)

#             month_labels.append(start_date.strftime("%B %Y"))
#             month_counts.append(len(monthly_farmers))
            
#             print(f"  - Unique farmers this month: {len(monthly_farmers)}")

#         print(f"🔹 Final month labels: {month_labels}")
#         print(f"🔹 Final month counts: {month_counts}")

#     except Exception as e:
#         print(f"❌ ERROR in expert_home: {e}")
#         import traceback
#         traceback.print_exc()
        
#         # Set default values on error
#         unique_farmers_count = 0
#         solved_consultations = 0
#         unsolved_consultations = 0
#         total_consultations = 0
#         barangay_labels = []
#         barangay_counts = []
#         month_labels = []
#         month_counts = []

#     context = {
#         "unique_farmers": unique_farmers_count,
#         "solved_consultations": solved_consultations,
#         "unsolved_consultations": unsolved_consultations,
#         "total_consultations": total_consultations,
#         "barangay_labels": barangay_labels,
#         "barangay_counts": barangay_counts,
#         "month_labels": month_labels,
#         "month_counts": month_counts,
#     }

#     print(f"🔹 Final context being sent to template: {context}")
#     return render(request, "expert/home.html", context)
# itong asa taas ang dati


# ITO YUNG NAG OOVERIDE
# def role_required(role):
#     def decorator(view_func):
#         def _wrapped_view(request, *args, **kwargs):
#             user_role = request.session.get("role")
#             if user_role != role:
#                 return redirect("login")
#             return view_func(request, *args, **kwargs)
#         return _wrapped_view
#     return decorator

# @role_required("Eksperto")
# def expert_home(request):
#     """Enhanced expert dashboard with comprehensive analytics and weather integration."""
#     expert_id = request.session.get("user_id")
    
#     if not expert_id:
#         return redirect("login")

#     try:
#         # Get expert information
#         try:
#             expert = Expert.objects.get(id=expert_id)
#         except Expert.DoesNotExist:
#             return redirect("login")

#         # Basic consultation metrics
#         expert_messages = Message.objects.filter(
#             Q(receiver_expert_id=expert_id) | Q(sender_expert_id=expert_id)
#         )
        
#         # Get unique farmers this expert has interacted with
#         unique_farmers = set()
#         for msg in expert_messages:
#             if msg.sender_farmer_id:
#                 unique_farmers.add(msg.sender_farmer_id)
#             if msg.receiver_farmer_id:
#                 unique_farmers.add(msg.receiver_farmer_id)
        
#         unique_farmers.discard(None)
#         unique_farmers_count = len(unique_farmers)

#         # Count consultations by conversation (farmer-expert pairs)
#         conversations = {}
#         for msg in expert_messages:
#             farmer_id = msg.sender_farmer_id or msg.receiver_farmer_id
#             if farmer_id:
#                 key = (farmer_id, expert_id)
#                 if key not in conversations:
#                     conversations[key] = {'total': 0, 'solved': False}
#                 conversations[key]['total'] += 1
#                 if msg.is_solved:
#                     conversations[key]['solved'] = True

#         solved_consultations = sum(1 for conv in conversations.values() if conv['solved'])
#         unsolved_consultations = len(conversations) - solved_consultations
#         total_consultations = len(conversations)

#         # Get barangay data for interacted farmers
#         barangay_labels = []
#         barangay_counts = []
        
#         if unique_farmers:
#             farmers_with_barangay = Farmer.objects.filter(
#                 id__in=list(unique_farmers)
#             ).values('barangay')
            
#             barangay_list = [f['barangay'] for f in farmers_with_barangay if f['barangay']]
#             barangay_counter = Counter(barangay_list)
#             barangay_labels = list(barangay_counter.keys())
#             barangay_counts = list(barangay_counter.values())

#         # Simplified monthly interaction data - using database aggregation
#         monthly_data = Message.objects.filter(
#             Q(sender_expert_id=expert_id) | Q(receiver_expert_id=expert_id)
#         ).annotate(
#             month=TruncMonth('timestamp')
#         ).values('month').annotate(
#             count=Count('id')
#         ).order_by('month')
        
#         monthly_data_list = list(monthly_data)
        
#         month_labels = []
#         month_counts = []
        
#         # Get last 12 months of data
#         recent_data = monthly_data_list[-12:] if len(monthly_data_list) >= 12 else monthly_data_list
        
#         for data in recent_data:
#             if data['month']:
#                 month_labels.append(data['month'].strftime("%B %Y"))
#                 month_counts.append(data['count'])
        
#         # Disease vs Pest Classification Data
#         disease_count = Message.objects.filter(
#             receiver_expert_id=expert_id,
#             classification='Sakit'
#         ).count()
        
#         pest_count = Message.objects.filter(
#             receiver_expert_id=expert_id,
#             classification='Peste'
#         ).count()
        
#         unclassified_count = Message.objects.filter(
#             receiver_expert_id=expert_id,
#             classification__isnull=True
#         ).count()
        
#         classification_data = [disease_count, pest_count, unclassified_count]
#         classification_labels = ['Sakit (Disease)', 'Peste (Pest)', 'Hindi Nakilala']
        
#         # AI Prediction Confidence Levels
#         consulted_farmers = Message.objects.filter(
#             receiver_expert_id=expert_id,
#             sender_farmer__isnull=False
#         ).values_list('sender_farmer_id', flat=True).distinct()
        
#         predictions = PredictionHistory.objects.filter(
#             farmer_id__in=consulted_farmers
#         )
        
#         confidence_ranges = {
#             '90-100%': predictions.filter(confidence__gte=90).count(),
#             '80-89%': predictions.filter(confidence__gte=80, confidence__lt=90).count(),
#             '70-79%': predictions.filter(confidence__gte=70, confidence__lt=80).count(),
#             '60-69%': predictions.filter(confidence__gte=60, confidence__lt=70).count(),
#             'Below 60%': predictions.filter(confidence__lt=60).count(),
#         }
        
#         confidence_labels = list(confidence_ranges.keys())
#         confidence_data = list(confidence_ranges.values())

#         # Expert Post Engagement Data (simplified)
#         expert_posts = ExpertPost.objects.filter(expert_id=expert_id)
#         engagement_months = []
#         posts_data = []
#         upvotes_data = []
        
#         from django.utils import timezone
        
#         current_date = timezone.now()
        
#         for i in range(5, -1, -1):  # Last 6 months
#             month_start = current_date.replace(day=1) - timedelta(days=30*i)
#             month_end = month_start + timedelta(days=31)
            
#             # Count posts for this month
#             monthly_posts = expert_posts.filter(
#                 created_at__gte=month_start,
#                 created_at__lt=month_end
#             ).count()
            
#             # Count upvotes for posts created in this month
#             monthly_upvotes = Upvote.objects.filter(
#                 post__expert_id=expert_id,
#                 post__created_at__gte=month_start,
#                 post__created_at__lt=month_end
#             ).count()
            
#             engagement_months.append(month_start.strftime('%b'))
#             posts_data.append(monthly_posts)
#             upvotes_data.append(monthly_upvotes)

#         # Problem Resolution Timeline Data (simplified to avoid timezone issues)
#         solved_messages = Message.objects.filter(
#             receiver_expert_id=expert_id,
#             is_solved=True
#         )
        
#         resolution_timeline = {
#             'Same Day': 0,
#             '1-2 Days': 0,
#             '3-7 Days': 0,
#             '1-2 Weeks': 0,
#             'Over 2 Weeks': 0
#         }
        
#         # Calculate actual resolution times (simplified approach)
#         for msg in solved_messages:
#             # Since we don't have resolution timestamp, use message timestamp as approximation
#             # In a real system, you'd track when the solution was marked
#             resolution_timeline['1-2 Days'] += 1  # Default to 1-2 days for existing solved messages

#         resolution_labels = list(resolution_timeline.keys())
#         resolution_data = list(resolution_timeline.values())

#         # Most Common Agricultural Issues (from AI predictions)
#         common_issues = PredictionHistory.objects.filter(
#             farmer_id__in=consulted_farmers
#         ).values('predicted_class').annotate(
#             count=Count('predicted_class')
#         ).order_by('-count')[:7]
        
#         issue_labels = [issue['predicted_class'] for issue in common_issues if issue['predicted_class']]
#         issue_counts = [issue['count'] for issue in common_issues if issue['predicted_class']]

#         # Seasonal Activity Pattern (simplified)
#         seasonal_data = [
#             Message.objects.filter(receiver_expert_id=expert_id, timestamp__month__in=[1,2,3]).count(),
#             Message.objects.filter(receiver_expert_id=expert_id, timestamp__month__in=[4,5,6]).count(),
#             Message.objects.filter(receiver_expert_id=expert_id, timestamp__month__in=[7,8,9]).count(),
#             Message.objects.filter(receiver_expert_id=expert_id, timestamp__month__in=[10,11,12]).count(),
#         ]
#         seasonal_labels = ['Q1 (Jan-Mar)', 'Q2 (Apr-Jun)', 'Q3 (Jul-Sep)', 'Q4 (Oct-Dec)']

#         # Knowledge Base Usage (sample data)
#         library_monthly_data = Library.objects.annotate(
#             month=TruncMonth('created_at')
#         ).values('month').annotate(
#             count=Count('id')
#         ).order_by('month')
        
#         library_monthly_list = list(library_monthly_data)
        
#         knowledge_months = []
#         knowledge_data = []
        
#         if library_monthly_list:
#             # Get last 12 months of library additions
#             recent_library_data = library_monthly_list[-12:] if len(library_monthly_list) >= 12 else library_monthly_list
            
#             for data in recent_library_data:
#                 if data['month']:
#                     knowledge_months.append(data['month'].strftime("%b %Y"))
#                     knowledge_data.append(data['count'])
        
#         # If no monthly data exists, create placeholder showing total count
#         if not knowledge_months:
#             total_library_items = Library.objects.count()
#             current_month = datetime.now().strftime("%b %Y")
#             knowledge_months = [current_month]
#             knowledge_data = [total_library_items]

#         # Expert Performance Metrics
#         total_expert_posts = expert_posts.count()
#         total_upvotes_received = Upvote.objects.filter(post__expert_id=expert_id).count()
#         total_comments_made = Comment.objects.filter(expert_id=expert_id).count()
#         total_farmer_comments_made = FarmerPostComment.objects.filter(expert_id=expert_id).count()
        
#         performance_metrics = {
#             'total_posts': total_expert_posts,
#             'upvotes_received': total_upvotes_received,
#             'comments_made': total_comments_made + total_farmer_comments_made,
#             'consultations_handled': total_consultations,
#             'solutions_provided': solved_consultations
#         }

#         recent_activity = {
#             'new_consultations_today': Message.objects.filter(
#                 receiver_expert_id=expert_id,
#                 timestamp__date=datetime.now().date()
#             ).count(),
#             'pending_responses': Message.objects.filter(
#                 receiver_expert_id=expert_id,
#                 is_read=False
#             ).count(),
#             'library_items_total': Library.objects.count(),
#             'active_conversations': len([conv for conv in conversations.values() if not conv['solved']])
#         }

#     except Exception as e:
#         print(f"❌ ERROR in expert_home: {e}")
#         import traceback
#         traceback.print_exc()
        
#         # Set default values on error
#         unique_farmers_count = 0
#         solved_consultations = 0
#         unsolved_consultations = 0
#         total_consultations = 0
#         barangay_labels = []
#         barangay_counts = []
#         month_labels = []
#         month_counts = []
        
#         # Default values for new charts
#         classification_data = [0, 0, 0]
#         classification_labels = ['Sakit (Disease)', 'Peste (Pest)', 'Hindi Nakilala']
#         confidence_labels = ['90-100%', '80-89%', '70-79%', '60-69%', 'Below 60%']
#         confidence_data = [0, 0, 0, 0, 0]
#         engagement_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
#         posts_data = [0, 0, 0, 0, 0, 0]
#         upvotes_data = [0, 0, 0, 0, 0, 0]  # Real zero values instead of fake data
#         resolution_labels = ['Solved', 'Unsolved']
#         resolution_data = [0, 0]
#         issue_labels = []
#         issue_counts = []
#         seasonal_data = [0, 0, 0, 0]
#         seasonal_labels = ['Q1 (Jan-Mar)', 'Q2 (Apr-Jun)', 'Q3 (Jul-Sep)', 'Q4 (Oct-Dec)']
#         knowledge_months = ['Total Items']
#         knowledge_data = [0]
#         performance_metrics = {
#             'total_posts': 0,
#             'upvotes_received': 0,
#             'comments_made': 0,
#             'consultations_handled': 0,
#             'solutions_provided': 0
#         }

#         # Default values for recent activity
#         recent_activity = {
#             'new_consultations_today': 0,
#             'pending_responses': 0,
#             'library_items_total': 0,
#             'active_conversations': 0
#         }

#     context = {
#         # Basic dashboard data
#         "unique_farmers": unique_farmers_count,
#         "solved_consultations": solved_consultations,
#         "unsolved_consultations": unsolved_consultations,
#         "total_consultations": total_consultations,
#         "barangay_labels": barangay_labels,
#         "barangay_counts": barangay_counts,
#         "month_labels": month_labels,
#         "month_counts": month_counts,
        
#         # Disease/Pest Classification
#         "classification_data": classification_data,
#         "classification_labels": classification_labels,
        
#         # AI Prediction Confidence
#         "confidence_labels": confidence_labels,
#         "confidence_data": confidence_data,
        
#         # Expert Engagement
#         "engagement_months": engagement_months,
#         "posts_data": posts_data,
#         "upvotes_data": upvotes_data,
        
#         # Problem Resolution Timeline
#         "resolution_labels": resolution_labels,
#         "resolution_data": resolution_data,
        
#         # Common Issues
#         "issue_labels": issue_labels,
#         "issue_counts": issue_counts,
        
#         # Seasonal Patterns
#         "seasonal_data": seasonal_data,
#         "seasonal_labels": seasonal_labels,
        
#         # Knowledge Base Usage
#         "knowledge_months": knowledge_months,
#         "knowledge_data": knowledge_data,
        
#         # Performance Metrics
#         "performance_metrics": performance_metrics,
        
#         # Recent Activity Data
#         "recent_activity": recent_activity,
#     }

#     return render(request, "expert/home.html", context)


def expert_scan(request):
    # Add logic for scanning functionality
    return render(request, "expert/expert_scan.html")

def expert_library(request):
    # Add logic for displaying library resources
    return render(request, "expert/expert_library.html")

# def expert_experts(request):
#     # Perhaps this view lists other experts for collaboration or consultation
#     # You can query your database for experts as needed.
#     experts = []  # Replace with actual query results
#     context = {"experts": experts}
#     return render(request, "expert/expert_experts.html", context)
# def expert_experts(request):
#     try:
#         user_id = request.session.get("user_id")
#         user_role = request.session.get("role")

#         # Ensure only experts can access this page
#         if not user_id or user_role != "Eksperto":
#             messages.error(request, "Kailangan mong mag-login bilang Eksperto upang makita ang ibang eksperto at mga magsasaka.")
#             return redirect("login")

#         # Fetch all approved experts except the logged-in expert
#         approved_experts_response = (
#             supabase.table("AgriExpert_expert")
#             .select("*")
#             .eq("status", "Approved")
#             .neq("id", user_id)  # Exclude the logged-in expert
#             .execute()
#         )
#         approved_experts = approved_experts_response.data if approved_experts_response.data else []

#         # Fetch all registered farmers
#         registered_farmers_response = supabase.table("AgriExpert_farmer").select("*").execute()
#         registered_farmers = registered_farmers_response.data if registered_farmers_response.data else []

#         # Get list of farmers the expert already has an existing chat with
#         existing_chat_response = (
#             supabase.table("AgriExpert_messages")
#             .select("receiver_farmer_id")
#             .eq("sender_expert_id", user_id)
#             .execute()
#         )
#         existing_chat_farmers = (
#             [message["receiver_farmer_id"] for message in existing_chat_response.data]
#             if existing_chat_response.data
#             else []
#         )

#         # Add a flag to indicate if the expert has a chat with the farmer
#         for farmer in registered_farmers:
#             farmer["has_existing_chat"] = farmer["id"] in existing_chat_farmers

#     except Exception as e:
#         print(f"❌ Error fetching experts and farmers: {e}")
#         approved_experts = []
#         registered_farmers = []

#     context = {
#         "approved_experts": approved_experts,
#         "registered_farmers": registered_farmers,
#     }
#     return render(request, "expert/expert_experts.html", context)

# def expert_experts(request):
#     try:
#         user_id = request.session.get("user_id")
#         user_role = request.session.get("role")

#         # Ensure only experts can access this page
#         if not user_id or user_role != "Eksperto":
#             messages.error(request, "Kailangan mong mag-login bilang Eksperto upang makita ang ibang eksperto.")
#             return redirect("login")

#         # Fetch all approved experts except the logged-in expert
#         approved_experts_response = (
#             supabase.table("AgriExpert_expert")
#             .select("*")
#             .eq("status", "Approved")
#             .neq("id", user_id)  # Exclude the logged-in expert
#             .execute()
#         )
#         approved_experts = approved_experts_response.data if approved_experts_response.data else []

#     except Exception as e:
#         print(f"❌ Error fetching experts: {e}")
#         approved_experts = []

#     context = {
#         "approved_experts": approved_experts,
#     }
#     return render(request, "expert/expert_experts.html", context)

# def expert_collab(request):
#     user_id = request.session.get("user_id")
#     expert = get_object_or_404(Expert, id=user_id)

#     # ✅ Get all farmers who have exchanged messages with this expert
#     farmers = Farmer.objects.filter(
#         Q(received_messages_farmer__sender_expert=expert) |
#         Q(sent_messages_farmer__receiver_expert=expert)
#     ).distinct()

#     # ✅ Fetch latest messages for each farmer
#     farmer_messages = []
#     for farmer in farmers:
#         latest_message = Message.objects.filter(
#             Q(sender_expert=expert, receiver_farmer=farmer) |
#             Q(sender_farmer=farmer, receiver_expert=expert)
#         ).order_by("-timestamp").first()  # Get latest message

#         # ✅ Append each farmer & their latest message
#         farmer_messages.append({
#             "farmer": farmer, 
#             "latest_message": latest_message
#         })

#     print("Farmers Found:", len(farmer_messages))  # Debugging print

#     return render(request, "expert/expert_collab.html", {"farmer_messages": farmer_messages})

# def expert_experts(request):
#     try:
#         user_id = request.session.get("user_id")
#         user_role = request.session.get("role")

#         # Ensure only experts can access this page
#         if not user_id or user_role != "Eksperto":
#             messages.error(request, "Kailangan mong mag-login bilang Eksperto upang makita ang ibang eksperto.")
#             return redirect("login")

#         # Fetch all experts (including logged-in expert)
#         approved_experts = Expert.objects.all()

#         # Fetch posts for all experts, including the logged-in expert's posts
#         expert_posts = ExpertPost.objects.filter(expert__in=approved_experts).order_by('-created_at')

#     except Exception as e:
#         print(f"❌ Error fetching experts: {e}")
#         approved_experts = []
#         expert_posts = []

#     context = {
#         "approved_experts": approved_experts,
#         "expert_posts": expert_posts,  # Add posts to context
#     }
#     return render(request, "expert/expert_experts.html", context)

# def expert_experts(request):
#     try:
#         user_id = request.session.get("user_id")
#         user_role = request.session.get("role")

#         if not user_id or user_role != "Eksperto":
#             messages.error(request, "Kailangan mong mag-login bilang Eksperto upang makita ang ibang eksperto.")
#             return redirect("login")

#         expert_user = Expert.objects.get(id=user_id)

#         # Fetch all experts (including logged-in expert)
#         approved_experts = Expert.objects.all()

#         # Fetch posts for all experts
#         expert_posts = ExpertPost.objects.filter(expert__in=approved_experts).order_by('-created_at')

#         # ✅ Annotate each post with whether this expert has upvoted it
#         for post in expert_posts:
#             post.already_upvoted = post.has_upvoted(expert_user)

#     except Exception as e:
#         print(f"❌ Error fetching experts: {e}")
#         approved_experts = []
#         expert_posts = []

#     context = {
#         "approved_experts": approved_experts,
#         "expert_posts": expert_posts,
#     }
#     return render(request, "expert/expert_experts.html", context)
def expert_announcements(request):
    # Check if user is logged in as Expert
    if request.session.get('role') != 'Eksperto':
        messages.error(request, "Please log in as Expert to access this page.")
        return redirect('login')
    
    # Get the current expert from session
    expert_id = request.session.get('user_id')
    if not expert_id:
        messages.error(request, "Please log in to access announcements.")
        return redirect('login')
    
    try:
        from .models import Expert
        expert_user = Expert.objects.get(id=expert_id)
    except Expert.DoesNotExist:
        messages.error(request, "Expert not found. Please log in again.")
        return redirect('login')
    
    # Get ALL active announcements from ALL admins that are relevant to experts
    announcements = Announcement.objects.filter(
        status='active'
    ).filter(
        Q(target_audience='all') | 
        Q(target_audience='experts') | 
        Q(target_audience='both')
    ).order_by('-created_at')
    
    # INCREMENT VIEW COUNT UNIQUELY FOR THIS EXPERT
    for announcement in announcements:
        announcement.increment_views(user_id=expert_id, user_type='expert')
    
    # Get filter parameters
    priority_filter = request.GET.get('priority', '')
    search_query = request.GET.get('search', '')
    
    # Apply filters
    if priority_filter:
        announcements = announcements.filter(priority=priority_filter)
    
    if search_query:
        announcements = announcements.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    # Get statistics
    total_announcements = announcements.count()
    urgent_count = announcements.filter(priority='urgent').count()
    high_priority_count = announcements.filter(priority='high').count()
    
    context = {
        'expert': expert_user,
        'announcements': announcements,
        'total_announcements': total_announcements,
        'urgent_count': urgent_count,
        'high_priority_count': high_priority_count,
        'priority_filter': priority_filter,
        'search_query': search_query,
    }
    
    return render(request, 'expert/expert_announcements.html', context)
def expert_experts(request):
    try:
        user_id = request.session.get("user_id")
        user_role = request.session.get("role")

        if not user_id or user_role != "Eksperto":
            messages.error(request, "Kailangan mong mag-login bilang Eksperto upang makita ang ibang eksperto.")
            return redirect("login")

        expert_user = Expert.objects.get(id=user_id)

        # Get filter parameters from request
        post_sort = request.GET.get('post_sort', 'newest')
        has_solution = request.GET.get('has_solution', '')
        search_query = request.GET.get('search', '')

        # Fetch only approved experts (excluding pending and rejected)
        approved_experts = Expert.objects.filter(status="Approved")

        # Fetch posts only from approved experts
        expert_posts = ExpertPost.objects.filter(expert__in=approved_experts)

        # Apply search filter
        if search_query:
            expert_posts = expert_posts.filter(
                models.Q(title__icontains=search_query) |
                models.Q(caption__icontains=search_query) |
                models.Q(expert__first_name__icontains=search_query) |
                models.Q(expert__last_name__icontains=search_query)
            )

        # Apply solution filter
        if has_solution == 'yes':
            # Get posts that have at least one solution comment
            posts_with_solutions = ExpertPost.objects.filter(
                comment__is_solution=True
            ).distinct()
            expert_posts = expert_posts.filter(id__in=posts_with_solutions)
        elif has_solution == 'no':
            # Get posts that don't have solution comments
            posts_without_solutions = ExpertPost.objects.exclude(
                comment__is_solution=True
            ).distinct()
            expert_posts = expert_posts.filter(id__in=posts_without_solutions)

        # Apply sorting
        if post_sort == 'oldest':
            expert_posts = expert_posts.order_by('created_at')
        elif post_sort == 'most_comments':
            expert_posts = expert_posts.annotate(
                comment_count=models.Count('comment')
            ).order_by('-comment_count')
        elif post_sort == 'most_upvotes':
            expert_posts = expert_posts.annotate(
                upvote_count=models.Count('upvote')
            ).order_by('-upvote_count')
        else:  # newest (default)
            expert_posts = expert_posts.order_by('-created_at')

        # Get stats for the dashboard
        total_experts = Expert.objects.filter(status="Approved").count()
        approved_experts_count = total_experts  # Since we're only showing approved
        pending_experts_count = 0  # Not showing pending to experts
        total_posts = expert_posts.count()

        # ✅ Annotate each post with whether this expert has upvoted it
        for post in expert_posts:
            post.already_upvoted = post.has_upvoted(expert_user)

            # Get the marked solution comment or the newest one
            solution_comment = post.get_comments().filter(is_solution=True).first()
            if solution_comment:
                post.solution_comment = solution_comment
            else:
                post.solution_comment = post.get_comments().order_by('-created_at').first()

            # Add engagement metrics for display
            post.comment_count = post.get_comments().count()
            post.upvote_count = post.get_upvotes_count()

    except Exception as e:
        print(f"❌ Error fetching experts: {e}")
        approved_experts = []
        expert_posts = []
        total_experts = 0
        approved_experts_count = 0
        pending_experts_count = 0
        total_posts = 0

    context = {
        "approved_experts": approved_experts,
        "expert_posts": expert_posts,
        "total_experts": total_experts,
        "approved_experts_count": approved_experts_count,
        "pending_experts_count": pending_experts_count,
        "total_posts": total_posts,
        "current_filters": {
            'post_sort': post_sort,
            'has_solution': has_solution,
            'search_query': search_query,
        }
    }
    return render(request, "expert/expert_experts.html", context)
# def expert_experts(request):
#     try:
#         user_id = request.session.get("user_id")
#         user_role = request.session.get("role")

#         if not user_id or user_role != "Eksperto":
#             messages.error(request, "Kailangan mong mag-login bilang Eksperto upang makita ang ibang eksperto.")
#             return redirect("login")

#         expert_user = Expert.objects.get(id=user_id)

#         # Fetch all experts (including logged-in expert)
#         approved_experts = Expert.objects.all()

#         # Fetch posts for all experts
#         expert_posts = ExpertPost.objects.filter(expert__in=approved_experts).order_by('-created_at')

#         # ✅ Annotate each post with whether this expert has upvoted it
#         for post in expert_posts:
#             post.already_upvoted = post.has_upvoted(expert_user)

#             # Get the marked solution comment or the newest one
#             solution_comment = post.get_comments().filter(is_solution=True).first()
#             if solution_comment:
#                 post.solution_comment = solution_comment
#             else:
#                 post.solution_comment = post.get_comments().order_by('-created_at').first()

#     except Exception as e:
#         print(f"❌ Error fetching experts: {e}")
#         approved_experts = []
#         expert_posts = []

#     context = {
#         "approved_experts": approved_experts,
#         "expert_posts": expert_posts,
#     }
#     return render(request, "expert/expert_experts.html", context)


# def view_post(request, post_id):
#     try:
#         user_id = request.session.get("user_id")
#         user_role = request.session.get("role")

#         post = ExpertPost.objects.get(id=post_id)
#         expert_user = Expert.objects.get(id=user_id) if user_id else None
        
#         is_owner = (expert_user == post.expert)

#         images = post.get_images()
#         comments = post.get_comments()

#         already_upvoted = False
#         if expert_user:
#             already_upvoted = post.has_upvoted(expert_user)

#     except ExpertPost.DoesNotExist:
#         messages.error(request, "Post not found.")
#         return redirect("expert_experts")

#     context = {
#         "post": post,
#         "images": images,
#         "comments": comments,
#         "already_upvoted": already_upvoted,
#         "allow_commenting": request.session.get("role") == "Eksperto" and request.session.get("user_id"),
#         "is_owner": is_owner,
#     }

#     return render(request, "expert/viewedit/view_post.html", context)

# def view_post(request, post_id):
#     try:
#         user_id = request.session.get("user_id")
#         user_role = request.session.get("role")

#         post = ExpertPost.objects.get(id=post_id)
#         expert_user = Expert.objects.get(id=user_id) if user_id else None
        
#         is_owner = (expert_user == post.expert)

#         images = post.get_images()
#         comments = post.get_comments()

#         # Separate the solution comment
#         solution_comment = comments.filter(is_solution=True).first()
#         other_comments = comments.exclude(id=solution_comment.id) if solution_comment else comments

#         already_upvoted = False
#         if expert_user:
#             already_upvoted = post.has_upvoted(expert_user)

#     except ExpertPost.DoesNotExist:
#         messages.error(request, "Post not found.")
#         return redirect("expert_experts")

#     context = {
#         "post": post,
#         "images": images,
#         "solution_comment": solution_comment,
#         "other_comments": other_comments,
#         "already_upvoted": already_upvoted,
#         "allow_commenting": request.session.get("role") == "Eksperto" and request.session.get("user_id"),
#         "is_owner": is_owner,
#     }

#     # 👇 Use different template depending on user role
#     if user_role == "Magsasaka":
#         return render(request, "farmer/viewedit/view_post.html", context)
#     else:
#         return render(request, "expert/viewedit/view_post.html", context)

def view_post(request, post_id):
    try:
        user_id = request.session.get("user_id")
        user_role = request.session.get("role")

        post = ExpertPost.objects.get(id=post_id)
        
        # Get expert if logged in
        expert_user = Expert.objects.get(id=user_id) if user_id and user_role == "Eksperto" else None
        
        # Check if user is owner (only for experts)
        is_owner = (expert_user == post.expert) if expert_user else False

        images = post.get_images()
        comments = post.get_comments()

        # Calculate post analytics
        post_analytics = {
            'total_comments': comments.count(),
            'solution_comments': comments.filter(is_solution=True).count(),
            'expert_comments': comments.filter(expert__isnull=False).count(),
            'days_since_post': (timezone.now() - post.created_at).days,
            'engagement_rate': min(100, comments.count() * 10),  # Simplified calculation
        }

        # Separate the solution comment
        solution_comment = comments.filter(is_solution=True).first()
        other_comments = comments.exclude(id=solution_comment.id) if solution_comment else comments

    except ExpertPost.DoesNotExist:
        messages.error(request, "Post not found.")
        return redirect("farmer_experts" if user_role == "Magsasaka" else "expert_experts")

    context = {
        "post": post,
        "images": images,
        "solution_comment": solution_comment,
        "other_comments": other_comments,
        "post_analytics": post_analytics,
        "is_owner": is_owner,
        "user_role": user_role,
    }

    # Use different template depending on user role
    if user_role == "Magsasaka":
        return render(request, "farmer/viewedit/view_post.html", context)
    else:
        return render(request, "expert/viewedit/view_post.html", context)
    
from django.urls import reverse
@csrf_exempt
def mark_comment_as_solution(request, comment_id):
    user_id = request.session.get("user_id")
    role = request.session.get("role")

    # Check if the user is authorized (Eksperto role)
    if not user_id or role != "Eksperto":
        messages.error(request, "Hindi ka awtorisadong gawin ito.")
        return redirect('some_error_page')  # Redirect to an error page or back to the post

    comment = get_object_or_404(Comment, id=comment_id)

    # Ensure the comment is on a post authored by the logged-in expert
    if comment.post.expert.id != user_id:
        messages.error(request, "Hindi ka ang may-akda ng post na ito.")
        return redirect('some_error_page')  # Redirect to an error page or back to the post

    # Unmark any existing solutions for the post
    Comment.objects.filter(post=comment.post, is_solution=True).update(is_solution=False, solution_highlighted=False)

    # Mark the selected comment as the solution
    comment.mark_as_solution()

    # Add a success message
    messages.success(request, "Minarkahan bilang solusyon.")

    # Redirect back to the post view page (assuming `view_post` is the view name for post detail)
    return redirect(reverse('view_post', kwargs={'post_id': comment.post.id}))



@csrf_exempt
def upvote_post(request, post_id):
    user_id = request.session.get("user_id")
    role = request.session.get("role")

    if not user_id or role != "Eksperto":
        return JsonResponse({"success": False, "message": "Kailangan munang mag-login bilang Eksperto."}, status=401)

    try:
        expert = Expert.objects.get(id=user_id)
    except Expert.DoesNotExist:
        return JsonResponse({"success": False, "message": "Eksperto hindi nahanap."}, status=404)

    post = get_object_or_404(ExpertPost, id=post_id)

    # Check if the expert already upvoted
    upvote = Upvote.objects.filter(post=post, expert=expert).first()

    if upvote:
        upvote.delete()
        return JsonResponse({
            "success": True,
            "message": "Inalis ang upvote.",
            "upvotes": post.get_upvotes_count(),
            "already_upvoted": False
        })
    else:
        Upvote.objects.create(post=post, expert=expert)
        return JsonResponse({
            "success": True,
            "message": "Na-upvote mo ang post!",
            "upvotes": post.get_upvotes_count(),
            "already_upvoted": True
        })

def comment_post(request, post_id):
    user_id = request.session.get("user_id")
    role = request.session.get("role")

    if not user_id or role != "Eksperto":
        messages.error(request, "You must be logged in as an expert to comment.")
        return redirect('expert_experts')  # replace with your actual feed URL name

    expert = get_object_or_404(Expert, id=user_id)
    post = get_object_or_404(ExpertPost, id=post_id)

    if request.method == "POST":
        content = request.POST.get('content')

        if not content:
            messages.error(request, "Comment content cannot be empty.")
        else:
            Comment.objects.create(post=post, expert=expert, content=content)
            messages.success(request, "Comment added successfully.")

    return redirect('expert_experts')  # or redirect to same post detail if you have one
    
# def expert_experts(request):
#     try:
#         user_id = request.session.get("user_id")
#         user_role = request.session.get("role")

#         # Ensure only experts can access this page
#         if not user_id or user_role != "Eksperto":
#             messages.error(request, "Kailangan mong mag-login bilang Eksperto upang makita ang ibang eksperto.")
#             return redirect("login")

#         # Fetch all approved experts except the logged-in expert
#         approved_experts_response = (
#             supabase.table("AgriExpert_expert")
#             .select("*")
#             .eq("status", "Approved")
#             .neq("id", user_id)  # Exclude the logged-in expert
#             .execute()
#         )
#         approved_experts = approved_experts_response.data if approved_experts_response.data else []

#         # Fetch posts for each expert
#         expert_posts = ExpertPost.objects.filter(expert__in=[expert['id'] for expert in approved_experts]).order_by('-created_at')

#     except Exception as e:
#         print(f"❌ Error fetching experts: {e}")
#         approved_experts = []
#         expert_posts = []

#     context = {
#         "approved_experts": approved_experts,
#         "expert_posts": expert_posts,  # Add posts to context
#     }
#     return render(request, "expert/expert_experts.html", context)


def expert_collab(request):
    user_id = request.session.get("user_id")
    expert = get_object_or_404(Expert, id=user_id)

    # ✅ Get all farmers who have exchanged messages with this expert
    farmers = Farmer.objects.filter(
        Q(received_messages_farmer__sender_expert=expert) |
        Q(sent_messages_farmer__receiver_expert=expert)
    ).distinct()

    # ✅ Fetch latest messages for each farmer & check unread status
    farmer_messages = []
    for farmer in farmers:
        latest_message = Message.objects.filter(
            Q(sender_expert=expert, receiver_farmer=farmer) |
            Q(sender_farmer=farmer, receiver_expert=expert)
        ).order_by("-timestamp").first()  # Get latest message

        # ✅ Check if the latest message is unread
        is_unread = latest_message and not latest_message.is_read and latest_message.sender_farmer == farmer

        # ✅ Append each farmer & their latest message + unread status
        farmer_messages.append({
            "farmer": farmer, 
            "latest_message": latest_message,
            "is_unread": is_unread
        })

    return render(request, "expert/expert_collab.html", {"farmer_messages": farmer_messages})


# def expert_farmers(request):
#     try:
#         user_id = request.session.get("user_id")
#         user_role = request.session.get("role")

#         # Ensure only experts can access this page
#         if not user_id or user_role != "Eksperto":
#             messages.error(request, "Kailangan mong mag-login bilang Eksperto upang makita ang mga magsasaka.")
#             return redirect("login")

#         # Fetch all registered farmers
#         registered_farmers_response = supabase.table("AgriExpert_farmer").select("*").execute()
#         registered_farmers = registered_farmers_response.data if registered_farmers_response.data else []

#         # Get list of farmers the expert already has an existing chat with
#         existing_chat_response = (
#             supabase.table("AgriExpert_messages")
#             .select("receiver_farmer_id")
#             .eq("sender_expert_id", user_id)
#             .execute()
#         )
#         existing_chat_farmers = (
#             [message["receiver_farmer_id"] for message in existing_chat_response.data]
#             if existing_chat_response.data
#             else []
#         )

#         # Add a flag to indicate if the expert has a chat with the farmer
#         for farmer in registered_farmers:
#             farmer["has_existing_chat"] = farmer["id"] in existing_chat_farmers

#     except Exception as e:
#         print(f"❌ Error fetching farmers: {e}")
#         registered_farmers = []

#     context = {
#         "registered_farmers": registered_farmers,
#     }
#     return render(request, "expert/expert_farmers.html", context)

# August 20, 2025
# def expert_farmers(request):
#     try:
#         user_id = request.session.get("user_id")
#         user_role = request.session.get("role")

#         # Ensure only experts can access this page
#         if not user_id or user_role != "Eksperto":
#             messages.error(request, "Kailangan mong mag-login bilang Eksperto upang makita ang mga magsasaka.")
#             return redirect("login")

#         # Fetch all registered farmers
#         registered_farmers_response = supabase.table("AgriExpert_farmer").select("*").execute()
#         registered_farmers = registered_farmers_response.data if registered_farmers_response.data else []

#         # Get list of farmers the expert already has an existing chat with
#         existing_chat_response = (
#             supabase.table("AgriExpert_messages")
#             .select("receiver_farmer_id")
#             .eq("sender_expert_id", user_id)
#             .execute()
#         )
#         existing_chat_farmers = (
#             [message["receiver_farmer_id"] for message in existing_chat_response.data]
#             if existing_chat_response.data
#             else []
#         )

#         # ✅ Pass `existing_chat_farmers` to the template
#         context = {
#             "registered_farmers": registered_farmers,
#             "existing_chat_farmers": existing_chat_farmers,  # ✅ Add this line
#         }

#     except Exception as e:
#         print(f"❌ Error fetching farmers: {e}")
#         context = {
#             "registered_farmers": [],
#             "existing_chat_farmers": [],  # Ensure it's always defined
#         }

#     return render(request, "expert/expert_farmers.html", context)

def expert_farmers(request):
    try:
        user_id = request.session.get("user_id")
        user_role = request.session.get("role")

        # Ensure only experts can access this page
        if not user_id or user_role != "Eksperto":
            messages.error(request, "Kailangan mong mag-login bilang Eksperto upang makita ang mga magsasaka.")
            return redirect("login")

        # Get current expert for upvote checking
        current_expert = Expert.objects.get(id=user_id)

        # Get filter parameters from request
        barangay_filter = request.GET.get('barangay', '')
        post_sort = request.GET.get('post_sort', 'newest')
        has_solution = request.GET.get('has_solution', '')
        search_query = request.GET.get('search', '')
        farm_size_min = request.GET.get('farm_size_min', '')
        farm_size_max = request.GET.get('farm_size_max', '')

        # Fetch all registered farmers with filters
        registered_farmers = Farmer.objects.all().order_by('first_name')

        if barangay_filter:
            registered_farmers = registered_farmers.filter(barangay__icontains=barangay_filter)

        unique_barangays = Farmer.objects.values_list('barangay', flat=True).distinct().order_by('barangay')

        # Get list of farmers the expert already has an existing chat with
        existing_chat_response = (
            supabase.table("AgriExpert_messages")
            .select("receiver_farmer_id")
            .eq("sender_expert_id", user_id)
            .execute()
        )
        existing_chat_farmers = (
            [message["receiver_farmer_id"] for message in existing_chat_response.data]
            if existing_chat_response.data
            else []
        )

        # Get all farmer posts with filters
        farmer_posts = FarmerPost.objects.select_related('farmer').prefetch_related(
            'images',
            'farmerpostcomment_set'
        ).all()
        
        # Search filter
        if search_query:
            farmer_posts = farmer_posts.filter(
                Q(title__icontains=search_query) |
                Q(caption__icontains=search_query) |
                Q(farmer__first_name__icontains=search_query) |
                Q(farmer__last_name__icontains=search_query) |
                Q(farmer__barangay__icontains=search_query)
            )
        
        # Barangay filter
        if barangay_filter:
            farmer_posts = farmer_posts.filter(farmer__barangay__icontains=barangay_filter)
        
        # Farm size filter
        if farm_size_min:
            farmer_posts = farmer_posts.filter(farmer__farm_size__gte=float(farm_size_min))
        if farm_size_max:
            farmer_posts = farmer_posts.filter(farmer__farm_size__lte=float(farm_size_max))
        
        # Solution filter
        if has_solution == 'yes':
            farmer_posts = farmer_posts.filter(farmerpostcomment__is_solution=True).distinct()
        elif has_solution == 'no':
            farmer_posts = farmer_posts.exclude(farmerpostcomment__is_solution=True).distinct()
        
        # Sorting
        if post_sort == 'oldest':
            farmer_posts = farmer_posts.order_by('created_at')
        elif post_sort == 'most_comments':
            farmer_posts = farmer_posts.annotate(
                comment_count=Count('farmerpostcomment')
            ).order_by('-comment_count')
        elif post_sort == 'most_upvotes':
            farmer_posts = farmer_posts.annotate(
                upvote_count=Count('farmerupvote')
            ).order_by('-upvote_count')
        elif post_sort == 'most_engagement':
            farmer_posts = farmer_posts.annotate(
                engagement=Count('farmerpostcomment') + Count('farmerupvote')
            ).order_by('-engagement')
        else:  # newest (default)
            farmer_posts = farmer_posts.order_by('-created_at')

        # Statistics
        total_farmers = Farmer.objects.count()
        total_posts = farmer_posts.count()
        total_comments = FarmerPostComment.objects.count()
        total_upvotes = FarmerUpvote.objects.count()
        
        # Barangay stats
        barangay_stats = Farmer.objects.values('barangay').annotate(
            farmer_count=Count('id'),
            post_count=Count('farmerpost')
        ).order_by('-farmer_count')

        # Add additional methods for posts
        for post in farmer_posts:
            # Get latest comments (limit to 3 for preview)
            post.latest_comments = post.get_comments()[:3]
            # Check if current expert has upvoted this post
            post.user_has_upvoted = FarmerUpvote.objects.filter(
                post=post, expert=current_expert
            ).exists()
            # Add engagement metrics
            post.comment_count = post.get_comments().count()
            post.upvote_count = post.get_upvotes_count()
            post.engagement_score = post.comment_count + post.upvote_count
            post.has_solution = post.get_comments().filter(is_solution=True).exists()

        context = {
            "registered_farmers": registered_farmers,
            "existing_chat_farmers": existing_chat_farmers,
            "farmer_posts": farmer_posts,
            "unique_barangays": unique_barangays,
            "total_farmers": total_farmers,
            "total_posts": total_posts,
            "total_comments": total_comments,
            "total_upvotes": total_upvotes,
            "barangay_stats": barangay_stats[:6],
            "current_filters": {
                'barangay': barangay_filter,
                'post_sort': post_sort,
                'has_solution': has_solution,
                'search_query': search_query,
                'farm_size_min': farm_size_min,
                'farm_size_max': farm_size_max,
            }
        }

    except Exception as e:
        print(f"❌ Error fetching farmers: {e}")
        context = {
            "registered_farmers": [],
            "existing_chat_farmers": [],
            "farmer_posts": [],
            "unique_barangays": [],
            "total_farmers": 0,
            "total_posts": 0,
            "total_comments": 0,
            "total_upvotes": 0,
            "barangay_stats": [],
            "current_filters": {}
        }

    return render(request, "expert/expert_farmers.html", context)

# New From Cladudeai
# def expert_farmers(request):
#     try:
#         user_id = request.session.get("user_id")
#         user_role = request.session.get("role")

#         # Ensure only experts can access this page
#         if not user_id or user_role != "Eksperto":
#             messages.error(request, "Kailangan mong mag-login bilang Eksperto upang makita ang mga magsasaka.")
#             return redirect("login")

#         # Get current expert for upvote checking
#         current_expert = Expert.objects.get(id=user_id)

#         # Fetch all registered farmers
#         registered_farmers = Farmer.objects.all().order_by('first_name')

#         # Get list of farmers the expert already has an existing chat with
#         existing_chat_response = (
#             supabase.table("AgriExpert_messages")
#             .select("receiver_farmer_id")
#             .eq("sender_expert_id", user_id)
#             .execute()
#         )
#         existing_chat_farmers = (
#             [message["receiver_farmer_id"] for message in existing_chat_response.data]
#             if existing_chat_response.data
#             else []
#         )

#         # Get all farmer posts ordered by creation date
#         farmer_posts = FarmerPost.objects.all().order_by('-created_at')
        
#         # Add additional methods for posts
#         for post in farmer_posts:
#             # Get latest comments (limit to 3 for preview)
#             post.latest_comments = post.get_comments()[:3]
#             # Check if current expert has upvoted this post
#             post.user_has_upvoted = FarmerUpvote.objects.filter(
#                 post=post, expert=current_expert
#             ).exists()

#         context = {
#             "registered_farmers": registered_farmers,
#             "existing_chat_farmers": existing_chat_farmers,
#             "farmer_posts": farmer_posts,  # Add farmer posts
#         }

#     except Exception as e:
#         print(f"❌ Error fetching farmers: {e}")
#         context = {
#             "registered_farmers": [],
#             "existing_chat_farmers": [],
#             "farmer_posts": [],  # Ensure it's always defined
#         }

#     return render(request, "expert/expert_farmers.html", context)

def expert_view_farmer_post(request, post_id):
    """
    Allow expert to view individual farmer post with all comments
    """
    if not (request.session.get("user_id") and request.session.get("role") == "Eksperto"):
        return redirect("login")
    
    post = get_object_or_404(FarmerPost, id=post_id)
    current_user_id = request.session["user_id"]
    current_expert = Expert.objects.get(id=current_user_id)
    
    # Check if expert has upvoted
    user_has_upvoted = FarmerUpvote.objects.filter(
        post=post, expert=current_expert
    ).exists()
    
    # Get all comments
    comments = post.get_comments()
    
    # Get solution comment if exists
    solution_comment = comments.filter(is_solution=True).first()
    
    context = {
        'post': post,
        'comments': comments,
        'solution_comment': solution_comment,
        'user_has_upvoted': user_has_upvoted,
        'user_type': 'expert'
    }
    
    return render(request, 'expert/viewedit/view_farmer_post.html', context)

# def expert_collaboration(request):
#     # Render the expert's profile page
#     return render(request, "expert/expert_collaboration.html")

# def expert_report(request):
#     expert_id = request.session.get("user_id")  # Get logged-in expert ID

#     if not expert_id:
#         return redirect("login")

#     # Get unique farmer IDs the expert has interacted with
#     unique_farmers = set(
#         Message.objects.filter(
#             Q(receiver_expert_id=expert_id) | Q(sender_expert_id=expert_id)
#         ).values_list("sender_farmer", "receiver_farmer", flat=False)
#     )

#     # Flatten the set and remove None values (in case an expert-to-expert message exists)
#     unique_farmers = {farmer for pair in unique_farmers for farmer in pair if farmer is not None}

#     # Count solved consultations of this expert
#     solved_consultations = Message.objects.filter(
#         receiver_expert_id=expert_id, is_solved=True
#     ).count()

#     context = {
#         "unique_farmers": len(unique_farmers),  # Count of unique farmers
#         "solved_consultations": solved_consultations,
#     }
#     return render(request, "expert/expert_report.html", context)

def expert_report(request):
    """Comprehensive expert report with multiple data categories."""
    expert_id = request.session.get("user_id")
    
    if not expert_id:
        return redirect("login")
    
    try:
        expert = Expert.objects.get(id=expert_id)
    except Expert.DoesNotExist:
        return redirect("login")
    
    # 1. CONSULTATIONS REPORT - Solved messages from farmers to this expert
    expert_reports = Message.objects.filter(
        receiver_expert_id=expert_id,
        is_solved=True
    ).select_related("sender_farmer").order_by("-timestamp")
    
    # 2. POSTS REPORT - Expert's own posts with engagement metrics
    expert_posts = ExpertPost.objects.filter(
        expert_id=expert_id
    ).prefetch_related('images').order_by("-created_at")
    
    # 3. INTERACTIONS REPORT - All messages (solved and unsolved) from farmers
    all_messages = Message.objects.filter(
        receiver_expert_id=expert_id,
        sender_farmer__isnull=False
    ).select_related("sender_farmer").order_by("-timestamp")
    
    # 4. PREDICTIONS REPORT - AI predictions from farmers who consulted this expert
    # Get farmers who have consulted this expert
    consulted_farmers = Message.objects.filter(
        receiver_expert_id=expert_id,
        sender_farmer__isnull=False
    ).values_list('sender_farmer_id', flat=True).distinct()
    
    farmer_predictions = PredictionHistory.objects.filter(
        farmer_id__in=consulted_farmers
    ).select_related("farmer").order_by("-uploaded_at")
    
    # 5. SOLUTIONS REPORT - Comments/solutions provided by this expert
    # Comments on ExpertPosts
    expert_comments = Comment.objects.filter(
        expert_id=expert_id
    ).select_related("post").order_by("-created_at")
    
    # Comments on FarmerPosts
    farmer_comments = FarmerPostComment.objects.filter(
        expert_id=expert_id
    ).select_related("post").order_by("-created_at")
    
    context = {
        # Current user info
        "expert": expert,
        
        # Report data for each tab
        "expert_reports": expert_reports,
        "expert_posts": expert_posts,
        "all_messages": all_messages,
        "farmer_predictions": farmer_predictions,
        "expert_comments": expert_comments,
        "farmer_comments": farmer_comments,
        
        # Summary statistics (optional, for future dashboard use)
        "total_solved_consultations": expert_reports.count(),
        "total_posts": expert_posts.count(),
        "total_interactions": all_messages.count(),
        "total_predictions_tracked": farmer_predictions.count(),
        "total_solutions_provided": expert_comments.filter(is_solution=True).count() + 
                                   farmer_comments.filter(is_solution=True).count(),
    }
    
    return render(request, "expert/expert_report.html", context)

def expert_reports_view(request):
    """Alternative expert reports view."""
    expert_id = request.session.get("user_id")
    
    if not expert_id:
        return redirect("login")
    
    try:
        expert = Expert.objects.get(id=expert_id)
        expert_name = f"{expert.first_name} {expert.last_name}"
    except Expert.DoesNotExist:
        expert_name = "Unknown Expert"
    
    return render(request, "expert_reports.html", {
        "expert_name": expert_name
    })

from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.conf import settings
from .models import Expert
from .forms import ExpertProfileUpdateForm
import json

def expert_profile(request):
    # Check if user is logged in and is an expert
    if 'user_id' not in request.session or request.session.get('role') != 'Eksperto':
        messages.error(request, "Kailangan mong mag-login bilang Eksperto para ma-access ang profile.")
        return redirect('login')
    
    try:
        expert = Expert.objects.get(id=request.session['user_id'])
    except Expert.DoesNotExist:
        messages.error(request, "Hindi nahanap ang expert account.")
        return redirect('login')
    
    expert_stats = {
        'messages_sent': expert.sent_messages_expert.count() if hasattr(expert, 'sent_messages_expert') else 0,
        'problems_solved': expert.sent_messages_expert.filter(is_solved=True).count() if hasattr(expert, 'sent_messages_expert') else 0,
        'posts_created': expert.expertpost_set.count() if hasattr(expert, 'expertpost_set') else 0,
        'upvotes_given': expert.upvote_set.count() if hasattr(expert, 'upvote_set') else 0,
    }
    
    # Password verification step
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'verify_password':
            # Step 1: Verify current password before showing profile settings
            current_password = request.POST.get('current_password')
            
            if not check_password(current_password, expert.password):
                messages.error(request, "Maling password. Hindi ka makakapag-access sa profile settings.")
                return render(request, 'expert/expert_profile.html', {
                    'expert': expert,
                    'expert_stats': expert_stats,
                    'show_password_form': True,
                    'password_verified': False
                })
            else:
                messages.success(request, "Password na-verify! Pwede mo nang i-edit ang inyong profile.")
                return render(request, 'expert/expert_profile.html', {
                    'expert': expert,
                    'expert_stats': expert_stats,
                    'show_password_form': False,
                    'password_verified': True
                })
        
        elif action == 'update_profile':
            # Step 2: Update profile information
            password_verified = request.POST.get('password_verified') == 'true'
            
            if not password_verified:
                messages.error(request, "Kailangan mo munang i-verify ang password.")
                return redirect('expert_profile')
            
            # Get form data
            first_name = request.POST.get('first_name')
            middle_name = request.POST.get('middle_name', '')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            barangay = request.POST.get('barangay')
            license_number = request.POST.get('license_number')
            position = request.POST.get('position', '')
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')
            
            # Validation
            errors = []
            
            if not all([first_name, last_name, email, phone_number, barangay, license_number]):
                errors.append("Lahat ng required fields ay dapat na-fill up.")
            
            # Check if email is unique (excluding current user)
            if Expert.objects.filter(email=email).exclude(id=expert.id).exists():
                errors.append("Ang email na ito ay ginagamit na ng ibang expert.")
            
            # Password validation if changing password
            if new_password:
                if new_password != confirm_password:
                    errors.append("Ang mga password ay hindi magkatugma.")
                elif len(new_password) < 8:
                    errors.append("Ang password ay dapat na hindi bababa sa 8 characters.")
            
            if errors:
                for error in errors:
                    messages.error(request, error)
                return render(request, 'expert/expert_profile.html', {
                    'expert': expert,
                    'expert_stats': expert_stats,
                    'show_password_form': False,
                    'password_verified': True,
                    'form_data': request.POST
                })
            
            # Update expert information
            expert.first_name = first_name
            expert.middle_name = middle_name
            expert.last_name = last_name
            expert.email = email
            expert.phone_number = phone_number
            expert.barangay = barangay
            expert.license_number = license_number
            expert.position = position
            
            # Update password if provided
            if new_password:
                expert.password = make_password(new_password)
            
            if 'profile_picture' in request.FILES:
                try:
                    # Upload to the same "profile_pictures" folder as in signup
                    profile_picture_url = upload_to_supabase(request.FILES['profile_picture'], "profile_pictures")
                    if profile_picture_url:
                        expert.profile_picture = profile_picture_url
                        messages.success(request, "Matagumpay na na-upload ang bagong profile picture!")
                    else:
                        messages.warning(request, "Hindi na-upload ang profile picture, pero na-save ang iba pang changes.")
                except Exception as e:
                    messages.warning(request, f"May problema sa pag-upload ng profile picture: {str(e)}")
            
            expert.save()
            
            messages.success(request, "Matagumpay na na-update ang inyong profile!")
            return redirect('expert_profile')
    
    # Default GET request - show password verification form
    return render(request, 'expert/expert_profile.html', {
        'expert': expert,
        'expert_stats': expert_stats,
        'show_password_form': True,
        'password_verified': False
    })


def view_expertfromexpert(request, expert_id):
    """Display expert's profile for logged-in experts."""
    expert = get_object_or_404(Expert, id=expert_id)
    
    upvotes_on_expert_posts = Upvote.objects.filter(post__expert=expert).count()
    
    solutions_count = Comment.objects.filter(expert=expert, is_solution=True).count()
    solutions_count += FarmerPostComment.objects.filter(expert=expert, is_solution=True).count()
    
    context = {
        "expert": expert,
        "total_upvotes": upvotes_on_expert_posts,
        "solutions_count": solutions_count,
    }
    
    return render(request, "expert/viewedit/view_expertfromexpert.html", context)


def view_farmerfromexpert(request, farmer_id):
    """Display farmer's profile for logged-in experts."""
    farmer = get_object_or_404(Farmer, id=farmer_id)
    return render(request, "expert/viewedit/view_farmerfromexpert.html", {"farmer": farmer})

def message_farmer(request, farmer_id):
    try:
        # Fetch farmer details by ID
        farmer_response = supabase.table("AgriExpert_farmer").select("*").eq("id", farmer_id).single().execute()
        farmer = farmer_response.data if farmer_response.data else None

        # Get the current expert ID from the session
        user_id = request.session.get("user_id")
        if user_id:
            existing_messages = Message.objects.filter(sender_expert_id=user_id, receiver_farmer_id=farmer_id).exists()
        else:
            existing_messages = False

    except Exception as e:
        farmer = None
        existing_messages = False

    return render(request, "expert/viewedit/message_farmer.html", {
        "farmer": farmer,
        "existing_messages": existing_messages
    })

# def chat_detailexpert(request, farmer_id):
#     user_id = request.session.get("user_id")
#     expert = get_object_or_404(Expert, id=user_id)
#     farmer = get_object_or_404(Farmer, id=farmer_id)

#     # ✅ Fetch chat messages between the logged-in expert and selected farmer
#     messages = Message.objects.filter(
#         Q(sender_expert=expert, receiver_farmer=farmer) |
#         Q(sender_farmer=farmer, receiver_expert=expert)
#     ).order_by("timestamp")

#     return render(request, "expert/viewedit/chat_detailexpert.html", {
#         "farmer": farmer,
#         "messages": messages
#     })
# def chat_detailexpert(request, farmer_id):
#     user_id = request.session.get("user_id")
#     expert = get_object_or_404(Expert, id=user_id)
#     farmer = get_object_or_404(Farmer, id=farmer_id)

#     # ✅ Fetch chat messages between the logged-in expert and selected farmer
#     messages = Message.objects.filter(
#         Q(sender_expert=expert, receiver_farmer=farmer) |
#         Q(sender_farmer=farmer, receiver_expert=expert)
#     ).order_by("timestamp")

#     # ✅ Mark unread messages as read
#     messages.filter(receiver_expert=expert, is_read=False).update(is_read=True)

#     return render(request, "expert/viewedit/chat_detailexpert.html", {
#         "farmer": farmer,
#         "messages": messages
#     })
    
def chat_detailexpert(request, farmer_id):
    user_id = request.session.get("user_id")
    expert = get_object_or_404(Expert, id=user_id)
    farmer = get_object_or_404(Farmer, id=farmer_id)

    messages_list = Message.objects.filter(
        Q(sender_expert=expert, receiver_farmer=farmer) |
        Q(sender_farmer=farmer, receiver_expert=expert)
    ).order_by("timestamp")

    # ✅ Corrected this line
    messages_list.filter(receiver_expert=expert, is_read=False).update(is_read=True)

    conversation_solved = messages_list.filter(is_solved=True).exists()

    return render(request, "expert/viewedit/chat_detailexpert.html", {
        "farmer": farmer,
        "messages": messages_list,
        "conversation_solved": conversation_solved
    })

# def send_message_expert(request, farmer_id):
#     """Handles sending messages from an expert to a farmer."""
#     user_id = request.session.get("user_id")
#     user_role = request.session.get("role")

#     if not user_id or user_role != "Eksperto":
#         messages.error(request, "You must be logged in as an Expert to send messages.")
#         return redirect("login")

#     # Check if the farmer exists
#     farmer_response = supabase.table("AgriExpert_farmer").select("*").eq("id", farmer_id).single().execute()
#     if not farmer_response.data:
#         messages.error(request, "Farmer not found.")
#         return redirect("expert_dashboard")  # Adjust as needed
#     farmer = farmer_response.data  

#     if request.method == "POST":
#         message_text = request.POST.get("message_text", "").strip()
#         image_file = request.FILES.get("image")

#         if not message_text and not image_file:
#             messages.error(request, "You cannot send an empty message.")
#             return redirect("chat_detailexpert", farmer_id=farmer_id)

#         # Upload image to Supabase if provided
#         image_url = upload_to_supabase(image_file, "messages") if image_file else None

#         try:
#             new_message = {
#                 "sender_expert_id": user_id,      # Ensure this matches your Supabase schema
#                 "receiver_farmer_id": farmer_id,  # Ensure this matches your Supabase schema
#                 "message_text": message_text,
#                 "image": image_url,
#                 "timestamp": datetime.utcnow().isoformat()
#             }
#             response = supabase.table("AgriExpert_messages").insert(new_message).execute()
#             if response.data:
#                 messages.success(request, "Message sent successfully.")
#                 return redirect("chat_detailexpert", farmer_id=farmer_id)
#             else:
#                 messages.error(request, "Error: Message was not saved.")
#         except Exception as e:
#             messages.error(request, f"Error saving message: {e}")
#         return redirect("chat_detailexpert", farmer_id=farmer_id)
#     else:
#         existing_messages_response = (
#             supabase.table("AgriExpert_messages")
#             .select("*")
#             .eq("sender_expert_id", user_id)
#             .eq("receiver_farmer_id", farmer_id)
#             .execute()
#         )
#         if existing_messages_response.data:
#             return redirect("chat_detailexpert", farmer_id=farmer_id)
#         else:
#             return render(request, "expert/viewedit/message_farmer.html", {"farmer": farmer})
def send_message_expert(request, farmer_id):
    user_id = request.session.get("user_id")
    user_role = request.session.get("role")

    if not user_id or user_role != "Eksperto":
        messages.error(request, "You must be logged in as an Expert to send messages.")
        return redirect("login")

    # Debugging: Check user session data
    print(f"User ID: {user_id}, Role: {user_role}")

    # Check if the farmer exists
    farmer_response = supabase.table("AgriExpert_farmer").select("*").eq("id", farmer_id).single().execute()
    if not farmer_response.data:
        messages.error(request, "Farmer not found.")
        return redirect("expert_dashboard")
    
    farmer = farmer_response.data  

    if request.method == "POST":
        message_text = request.POST.get("message_text", "").strip()
        image_file = request.FILES.get("image")

        # Debugging: Check if message is empty
        print(f"Message Text: {message_text}, Image File: {image_file}")

        if not message_text and not image_file:
            messages.error(request, "You cannot send an empty message.")
            return redirect("chat_detailexpert", farmer_id=farmer_id)

        # Upload image to Supabase if provided
        image_url = upload_to_supabase(image_file, "messages") if image_file else None

        try:
            new_message = {
                "sender_expert_id": user_id,
                "receiver_farmer_id": farmer_id,
                "message_text": message_text,
                "image": image_url,
                "timestamp": timezone.now().isoformat(),
                # "timestamp": datetime.datetime.utcnow().isoformat(),
                "is_solved": False  # Ensure this is explicitly set to avoid issues
            }
            response = supabase.table("AgriExpert_messages").insert(new_message).execute()

            # Debugging: Check if message was inserted
            print(f"Insert Response: {response}")

            if response.data:
                messages.success(request, "Message sent successfully.")
                return redirect("chat_detailexpert", farmer_id=farmer_id)
            else:
                messages.error(request, "Error: Message was not saved.")

        except Exception as e:
            messages.error(request, f"Error saving message: {e}")
            print(f"Error: {e}")  # Debugging error
        return redirect("chat_detailexpert", farmer_id=farmer_id)

def edit_message_expert(request, message_id):
    """Handles editing a message for experts."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message_text = data.get("message_text")

            # Ensure the expert is editing only their own messages
            message = get_object_or_404(Message, id=message_id, sender_expert__id=request.session.get("user_id"))
            message.message_text = message_text
            message.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

def delete_message_expert(request, message_id):
    """Handles deleting a message for experts."""
    if request.method == "DELETE":
        try:
            # Ensure the expert is deleting only their own messages
            message = get_object_or_404(Message, id=message_id, sender_expert__id=request.session.get("user_id"))
            message.delete()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

# def mark_solved(request, message_id):
#     if request.method == "POST":
#         message = get_object_or_404(Message, id=message_id)
#         message.is_solved = not message.is_solved  # ✅ Toggle the solved status
#         message.save()
#         return JsonResponse({"success": True, "is_solved": message.is_solved})
#     return JsonResponse({"success": False})

def mark_solved(request, message_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("Received Data:", data)  # Debugging

            solution_description = data.get("solution_description", "").strip()
            classification = data.get("classification", "").strip()

            if not solution_description:
                return JsonResponse({"success": False, "error": "Solution description is required."})

            if classification not in ["Sakit", "Peste"]:
                return JsonResponse({"success": False, "error": "Invalid classification type."})

            message = get_object_or_404(Message, id=message_id)
            message.is_solved = True
            message.solution_description = solution_description
            message.classification = classification
            message.save()

            print("Message saved:", message.solution_description, message.classification)  # Debugging

            return JsonResponse({
                "success": True,
                "is_solved": message.is_solved,
                "solution_description": message.solution_description,
                "classification": message.classification
            })

        except Exception as e:
            print("Error:", str(e))  # Debugging
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method."})

def expert_reports_view(request):
    return render(request, "expert_reports.html", {
        "expert_name": request.user.get_full_name()  # Pass the full name manually
    })

# EXPERT COLLABORATION
from .models import ExpertPost, ExpertPostImage, Upvote, Comment
from .forms import ExpertPostForm
# def expert_collaboration(request):
#     posts = ExpertPost.objects.all().order_by('-created_at')
#     return render(request, 'expert/expert_collaboration.html', {'posts': posts})

def expert_collaboration(request):
    # Check if user is logged in and is an expert
    if request.session.get("user_id") and request.session.get("role") == "Eksperto":
        expert_id = request.session["user_id"]
        expert = Expert.objects.get(id=expert_id)
        posts = ExpertPost.objects.filter(expert=expert).order_by('-created_at')
        return render(request, 'expert/expert_collaboration.html', {'posts': posts})
    else:
        # Redirect unauthorized users
        return redirect("login")

from .models import FarmerPost, FarmerPostComment, FarmerPostImage, FarmerUpvote
from .forms import FarmerPostForm

def farmer_collaboration(request):
    # Check if user is logged in and is an expert
    if request.session.get("user_id") and request.session.get("role") == "Magsasaka":
        farmer_id = request.session["user_id"]
        farmer = Farmer.objects.get(id=farmer_id)
        posts = FarmerPost.objects.filter(farmer=farmer).order_by('-created_at')
        return render(request, 'farmer/farmer_collaboration.html', {'posts': posts})
    else:
        # Redirect unauthorized users
        return redirect("login")

def create_farmer_post(request):
    # Ensure user is an expert
    if request.session.get("role") != "Magsasaka":
        return HttpResponse("⛔ Only approved experts can post.", status=403)

    try:
        farmer_id = request.session.get("user_id")
        farmer_profile = Farmer.objects.get(id=farmer_id)
    except Farmer.DoesNotExist:
        return HttpResponse("❌ Expert not found.", status=404)

    if request.method == 'POST':
        form = FarmerPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.farmer = farmer_profile
            post.save()

            images = request.FILES.getlist('images')
            for img in images:
                # ✅ Upload each image to Supabase
                image_url = upload_to_supabase(img, "farmer_posts")
                if image_url:
                    FarmerPostImage.objects.create(
                        post=post,
                        image_url=image_url
                    )

            # Redirect to the collaboration list page
            return redirect('farmer_collaboration')

    else:
        form = FarmerPostForm()

    return render(request, 'farmer/viewedit/create_farmer_post.html', {'form': form})
# views.py
def create_expert_post(request):
    # Ensure user is an expert
    if request.session.get("role") != "Eksperto":
        return HttpResponse("⛔ Only approved experts can post.", status=403)

    try:
        expert_id = request.session.get("user_id")
        expert_profile = Expert.objects.get(id=expert_id)
    except Expert.DoesNotExist:
        return HttpResponse("❌ Expert not found.", status=404)

    if request.method == 'POST':
        form = ExpertPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.expert = expert_profile
            post.save()

            images = request.FILES.getlist('images')
            for img in images:
                # ✅ Upload each image to Supabase
                image_url = upload_to_supabase(img, "expert_posts")
                if image_url:
                    ExpertPostImage.objects.create(
                        post=post,
                        image_url=image_url
                    )

            # Redirect to the collaboration list page
            return redirect('expert_collaboration')

    else:
        form = ExpertPostForm()

    return render(request, 'expert/viewedit/create_post.html', {'form': form})

# # Function to truncate the file name
# def truncate_filename(filename, max_length=200):
#     base_name, ext = os.path.splitext(filename)
#     if len(base_name) > max_length:
#         base_name = base_name[:max_length]  # Truncate the file name
#     return base_name + ext  # Return the truncated file name with extension

# def create_expert_post(request):
#     # Ensure user is an expert
#     if request.session.get("role") != "Eksperto":
#         return HttpResponse("⛔ Only approved experts can post.", status=403)

#     try:
#         expert_id = request.session.get("user_id")
#         expert_profile = Expert.objects.get(id=expert_id)
#     except Expert.DoesNotExist:
#         return HttpResponse("❌ Expert not found.", status=404)

#     if request.method == 'POST':
#         form = ExpertPostForm(request.POST, request.FILES)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.expert = expert_profile
#             post.save()

#             # Get list of images uploaded
#             images = request.FILES.getlist('images')

#             # Loop through the uploaded images
#             for img in images:
#                 # Truncate file name if it's too long
#                 truncated_filename = truncate_filename(img.name)

#                 # Upload each image to Supabase or your image storage solution
#                 image_url = upload_to_supabase(img, "expert_posts", truncated_filename)  # Pass truncated name if needed

#                 if image_url:
#                     ExpertPostImage.objects.create(
#                         post=post,
#                         image_url=image_url
#                     )

#             # Redirect to the collaboration list page after success
#             return redirect('expert_collaboration')

#     else:
#         form = ExpertPostForm()

#     return render(request, 'expert/viewedit/create_post.html', {'form': form})

def edit_farmer_post(request, post_id):
    if request.session.get("role") != "Magsasaka":
        return HttpResponse("⛔ Only approved experts can edit posts.", status=403)

    post = get_object_or_404(FarmerPost, id=post_id)

    if post.farmer.id != request.session.get("user_id"):
        return HttpResponse("⛔ You are not authorized to edit this post.", status=403)

    if request.method == 'POST':
        form = FarmerPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()

            # ✅ Handle deleted images
            deleted_ids = request.POST.getlist('deleted_images')
            for img_id in deleted_ids:
                image = FarmerPostImage.objects.filter(id=img_id, post=post).first()
                if image:
                    image.delete()

            # ✅ Upload newly added images (if any)
            images = request.FILES.getlist('images')
            for img in images:
                image_url = upload_to_supabase(img, "farmer_posts")
                if image_url:
                   FarmerPostImage.objects.create(
                        post=post,
                        image_url=image_url
                    )

            return redirect('farmer_collaboration')
    else:
        form = ExpertPostForm(instance=post)

    return render(request, 'farmer/viewedit/edit_farmer_post.html', {'form': form, 'post': post})

def edit_expert_post(request, post_id):
    if request.session.get("role") != "Eksperto":
        return HttpResponse("⛔ Only approved experts can edit posts.", status=403)

    post = get_object_or_404(ExpertPost, id=post_id)

    if post.expert.id != request.session.get("user_id"):
        return HttpResponse("⛔ You are not authorized to edit this post.", status=403)

    if request.method == 'POST':
        form = ExpertPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()

            # ✅ Handle deleted images
            deleted_ids = request.POST.getlist('deleted_images')
            for img_id in deleted_ids:
                image = ExpertPostImage.objects.filter(id=img_id, post=post).first()
                if image:
                    image.delete()

            # ✅ Upload newly added images (if any)
            images = request.FILES.getlist('images')
            for img in images:
                image_url = upload_to_supabase(img, "expert_posts")
                if image_url:
                    ExpertPostImage.objects.create(
                        post=post,
                        image_url=image_url
                    )

            return redirect('expert_collaboration')
    else:
        form = ExpertPostForm(instance=post)

    return render(request, 'expert/viewedit/edit_post.html', {'form': form, 'post': post})

from django.http import JsonResponse, HttpResponseNotAllowed
from .models import ExpertPostImage

def delete_expert_post_image(request, image_id):
    if request.method == 'DELETE':
        # Get the image object
        image = get_object_or_404(ExpertPostImage, id=image_id)
        
        # Delete the image from the database
        image.delete()
        
        return JsonResponse({'message': 'Image deleted successfully.'}, status=200)
    else:
        return HttpResponseNotAllowed(['DELETE'])

# DISEASE USING VGG16 NI JUNREY
# from django.conf import settings
# from .models import PredictionHistory, Farmer, Library
# import tensorflow as tf
# import numpy as np
# import cv2
# import os
# import tempfile
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from PIL import Image
# import traceback

# # Class names - EXACT match from your training data
# CLASS_NAMES = [
#     'Bacterial Leaf Blight',      # 0
#     'Bacterial Leaf Streak',     # 1  
#     'Brown Spot',                # 2
#     'Dead Heart Pest Attack Symptom',  # 3
#     'Grain Rot',                 # 4
#     'Healthy Grain',             # 5
#     'Healthy Leaf',              # 6
#     'Leaf scald',                # 7 - NOTE: lowercase 's'
#     'Rice Blast',                # 8
#     'Rice False Smut',           # 9
#     'Rice Stripe Virus',         # 10
#     'Sheath Blight',             # 11
#     'Stem Rot',                  # 12
#     'Tungro Virus',              # 13
#     'Unknown'                    # 14
# ]

# # Load VGG16 model with proper error handling
# try:
#     model_path = os.path.join(settings.BASE_DIR, 'models', 'EPOCH24to28diseaseVGG16_finetuned_model.keras')
#     print(f"Django BASE_DIR: {settings.BASE_DIR}")
#     print(f"Looking for model at: {model_path}")
#     print(f"Model file exists: {os.path.exists(model_path)}")
    
#     if os.path.exists(model_path):
#         model = tf.keras.models.load_model(model_path)
#         print("✓ VGG16 model loaded successfully!")
#         print(f"Model input shape: {model.input_shape}")
#         print(f"Model output shape: {model.output_shape}")
#     else:
#         model = None
#         print("✗ ERROR: Model file not found!")
# except Exception as e:
#     model = None
#     print(f"✗ ERROR loading model: {e}")
#     traceback.print_exc()

# def preprocess_disease_image_vgg16(image_path):
#     """
#     Preprocess image for VGG16 model - matches your training preprocessing
#     """
#     try:
#         # Load image using OpenCV
#         img = cv2.imread(image_path)
#         if img is None:
#             raise Exception(f"Could not load image from {image_path}")
        
#         # Convert BGR to RGB (OpenCV loads as BGR, but model expects RGB)
#         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
#         # Resize to model input size (224, 224)
#         img = cv2.resize(img, (224, 224))
        
#         # Convert to float32 and normalize (same as training: rescale=1./255)
#         img_array = img.astype("float32") / 255.0
        
#         # Add batch dimension
#         img_array = np.expand_dims(img_array, axis=0)
        
#         return img_array
        
#     except Exception as e:
#         print(f"Error in preprocessing: {e}")
#         traceback.print_exc()
#         raise

# @csrf_exempt
# def predict_disease(request):
#     if request.method == "POST":
#         try:
#             # Check user session
#             user_id = request.session.get("user_id")
#             role = request.session.get("role")
            
#             if role != "Magsasaka" or not user_id:
#                 return JsonResponse({"error": "Unauthorized or invalid user session"}, status=403)
            
#             # Check if model is loaded
#             if model is None:
#                 return JsonResponse({"error": "Model not available. Please check server logs."}, status=500)
            
#             # Get image file
#             image_file = request.FILES.get("disease_image") or request.FILES.get("image")
#             if not image_file:
#                 return JsonResponse({"error": "No image uploaded"}, status=400)
            
#             # Save uploaded file temporarily
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
#                 for chunk in image_file.chunks():
#                     temp_file.write(chunk)
#                 temp_file_path = temp_file.name
            
#             # Preprocess image for VGG16
#             image_array = preprocess_disease_image_vgg16(temp_file_path)
            
#             # Predict with VGG16 model
#             predictions = model.predict(image_array, verbose=0)
#             confidence = float(np.max(predictions) * 100)  # Convert to Python float
#             class_index = int(np.argmax(predictions))       # Convert to Python int
#             predicted_class = CLASS_NAMES[class_index]
            
#             # Clean up temporary file
#             try:
#                 os.unlink(temp_file_path)
#             except:
#                 pass
            
#             # Fetch related Library data
#             library_data = None
#             try:
#                 # Try exact match first
#                 library_entry = Library.objects.get(paksa__iexact=predicted_class)
#                 library_data = {
#                     "paksa": library_entry.paksa,
#                     "deskripsyon": library_entry.deskripsyon,
#                     "ano_ang_nagagawa_nito": library_entry.ano_ang_nagagawa_nito,
#                     "bakit_at_saan_ito_nangyayari": library_entry.bakit_at_saan_ito_nangyayari,
#                     "paano_ito_matutukoy": library_entry.paano_ito_matutukoy,
#                     "bakit_ito_mahalaga": library_entry.bakit_ito_mahalaga,
#                     "paano_ito_pangangasiwaan": library_entry.paano_ito_pangangasiwaan,
#                     "id": library_entry.id
#                 }
#             except Library.DoesNotExist:
#                 # Try with different case variations for "Leaf scald"
#                 if predicted_class == "Leaf scald":
#                     try:
#                         library_entry = Library.objects.get(paksa__iexact="Leaf Scald")
#                         library_data = {
#                             "paksa": library_entry.paksa,
#                             "deskripsyon": library_entry.deskripsyon,
#                             "ano_ang_nagagawa_nito": library_entry.ano_ang_nagagawa_nito,
#                             "bakit_at_saan_ito_nangyayari": library_entry.bakit_at_saan_ito_nangyayari,
#                             "paano_ito_matutukoy": library_entry.paano_ito_matutukoy,
#                             "bakit_ito_mahalaga": library_entry.bakit_ito_mahalaga,
#                             "paano_ito_pangangasiwaan": library_entry.paano_ito_pangangasiwaan,
#                             "id": library_entry.id
#                         }
#                     except Library.DoesNotExist:
#                         print(f"No library entry found for: {predicted_class} (tried both cases)")
#                 else:
#                     print(f"No library entry found for: {predicted_class}")
#             except Exception as e:
#                 print(f"Error fetching library data: {e}")
            
#             response_data = {
#                 "predicted_class": predicted_class,
#                 "confidence": round(confidence, 2),
#                 "library_data": library_data
#             }
            
#             return JsonResponse(response_data)
            
#         except Exception as e:
#             print(f"ERROR in predict_disease: {e}")
#             traceback.print_exc()
            
#             # Clean up temp file if it exists
#             try:
#                 if 'temp_file_path' in locals():
#                     os.unlink(temp_file_path)
#             except:
#                 pass
            
#             return JsonResponse({
#                 "error": f"Error processing image: {str(e)}"
#             }, status=500)
    
#     return JsonResponse({"error": "Invalid request method"}, status=400)
# # END NG VGG 16 NI JUNREY


# Disease Using Resnet to the End SEPTEMBER 4
# from django.conf import settings
# from .models import PredictionHistory, Farmer
# import tensorflow as tf
# import numpy as np
# import cv2
# import os
# import tempfile
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import torch
# import torchvision.transforms as transforms
# import torch
# import torchvision.models as models
# from PIL import Image
# CLASS_NAMES = [
#     'Bacterial Leaf Blight', 'Bacterial Leaf Streak', 'Brown Spot',
#     'Dead Heart Pest Attack Symptom','Grain Rot','Healthy Grain',
#     'Healthy Leaf','Leaf Scald','Rice Blast','Rice False Smut',
#     'Rice Stripe Virus','Sheath Blight','Stem Rot','Tungro Virus',
#     'Unknown'
# ]
# # ✅ Recreate your architecture (must match training time)
# # Model must match training
# model = models.resnet18(pretrained=False)  # keep False if your .pth contains all weights
# num_ftrs = model.fc.in_features
# model.fc = torch.nn.Linear(num_ftrs, len(CLASS_NAMES))

# model_path = os.path.join(settings.BASE_DIR, 'models', 'diseaseresnet.pth')
# state_dict = torch.load(model_path, map_location=torch.device('cpu'))
# model.load_state_dict(state_dict)
# model.eval()

# # EXACT preprocessing from training
# transform = transforms.Compose([
#     transforms.Resize((224, 224)),
#     transforms.ToTensor(),
#     transforms.Normalize(mean=[0.485, 0.456, 0.406],
#     std=[0.229, 0.224, 0.225])
# ])
# def preprocess_disease_image(image_path):
#     image = Image.open(image_path).convert("RGB")
#     image = transform(image)  # ✅ call your pipeline, not transforms module
#     image = image.unsqueeze(0)  # add batch dimension
#     return image
# START



# HINDI ITO KASALI
# For disease detection
# def preprocess_disease_image(image_path):
#     image = cv2.imread(image_path)
#     image = cv2.resize(image, (150, 150))
#     image = image / 255.0
#     return np.expand_dims(image, axis=0)

# @csrf_exempt
# def predict_disease(request):
#     if request.method == "POST":
#         user_id = request.session.get("user_id")
#         role = request.session.get("role")

#         if role != "Magsasaka" or not user_id:
#             return JsonResponse({"error": "Unauthorized or invalid user session"}, status=403)

#         image_file = request.FILES.get("image")
#         if not image_file:
#             return JsonResponse({"error": "No image uploaded"}, status=400)

#         # Save to temporary file for prediction only
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
#             for chunk in image_file.chunks():
#                 temp_file.write(chunk)
#             temp_file_path = temp_file.name

#         # Preprocess and predict
#         processed_image = preprocess_disease_image(temp_file_path)
#         prediction = model.predict(processed_image)[0]
#         class_index = np.argmax(prediction)
#         predicted_class = CLASS_NAMES[class_index]
#         confidence = float(prediction[class_index]) * 100

#         # ✅ Don't upload or save yet!
#         return JsonResponse({
#             "predicted_class": predicted_class,
#             "confidence": round(confidence, 2)
#         })

#     return JsonResponse({"error": "Invalid request"}, status=400)

# Disease for Keras
# @csrf_exempt
# def predict_disease(request):
#     if request.method == "POST":
#         user_id = request.session.get("user_id")
#         role = request.session.get("role")

#         if role != "Magsasaka" or not user_id:
#             return JsonResponse({"error": "Unauthorized or invalid user session"}, status=403)
        
#         image_file = request.FILES.get("disease_image") or request.FILES.get("image")
#         if not image_file:
#             return JsonResponse({"error": "No image uploaded"}, status=400)

#         with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
#             for chunk in image_file.chunks():
#                 temp_file.write(chunk)
#             temp_file_path = temp_file.name

#         processed_image = preprocess_disease_image(temp_file_path)
#         prediction = model.predict(processed_image)[0]
#         class_index = np.argmax(prediction)
#         predicted_class = CLASS_NAMES[class_index]
#         confidence = float(prediction[class_index]) * 100

#         # 🔍 Try to find a matching Library entry
#         try:
#             library_entry = Library.objects.get(paksa__iexact=predicted_class)
#             library_data = {
#                 "paksa": library_entry.paksa,
#                 "deskripsyon": library_entry.deskripsyon,
#                 "ano_ang_nagagawa_nito": library_entry.ano_ang_nagagawa_nito,
#                 "bakit_at_saan_ito_nangyayari": library_entry.bakit_at_saan_ito_nangyayari,
#                 "paano_ito_matutukoy": library_entry.paano_ito_matutukoy,
#                 "bakit_ito_mahalaga": library_entry.bakit_ito_mahalaga,
#                 "paano_ito_pangangasiwaan": library_entry.paano_ito_pangangasiwaan,
#                 "id": library_entry.id
#             }
#         except Library.DoesNotExist:
#             library_data = None

#         return JsonResponse({
#             "predicted_class": predicted_class,
#             "confidence": round(confidence, 2),
#             "library_data": library_data
#         })

#     return JsonResponse({"error": "Invalid request"}, status=400)


# START OF SEPT 4 USING RESNET
# Disease using PyTorch
# @csrf_exempt
# def predict_disease(request):
#     if request.method == "POST":
#         user_id = request.session.get("user_id")
#         role = request.session.get("role")

#         if role != "Magsasaka" or not user_id:
#             return JsonResponse({"error": "Unauthorized or invalid user session"}, status=403)
        
#         image_file = request.FILES.get("disease_image") or request.FILES.get("image")
#         if not image_file:
#             return JsonResponse({"error": "No image uploaded"}, status=400)

#         # Save uploaded file temporarily
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
#             for chunk in image_file.chunks():
#                 temp_file.write(chunk)
#             temp_file_path = temp_file.name

#         # Preprocess image for PyTorch
#         image_tensor = preprocess_disease_image(temp_file_path)

#         # Predict with PyTorch model
#         with torch.no_grad():
#             outputs = model(image_tensor)
#             probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
#             class_index = torch.argmax(probabilities).item()
#             confidence = probabilities[class_index].item() * 100
#             predicted_class = CLASS_NAMES[class_index]

#         # Fetch related Library data
#         try:
#             library_entry = Library.objects.get(paksa__iexact=predicted_class)
#             library_data = {
#                 "paksa": library_entry.paksa,
#                 "deskripsyon": library_entry.deskripsyon,
#                 "ano_ang_nagagawa_nito": library_entry.ano_ang_nagagawa_nito,
#                 "bakit_at_saan_ito_nangyayari": library_entry.bakit_at_saan_ito_nangyayari,
#                 "paano_ito_matutukoy": library_entry.paano_ito_matutukoy,
#                 "bakit_ito_mahalaga": library_entry.bakit_ito_mahalaga,
#                 "paano_ito_pangangasiwaan": library_entry.paano_ito_pangangasiwaan,
#                 "id": library_entry.id
#             }
#         except Library.DoesNotExist:
#             library_data = None

#         return JsonResponse({
#             "predicted_class": predicted_class,
#             "confidence": round(confidence, 2),
#             "library_data": library_data
#         })

#     return JsonResponse({"error": "Invalid request"}, status=400)
# END ITO NG SEPTEMBER 4 USING RESNET


# @csrf_exempt
# def upload_to_supabase_and_save(request):
#     if request.method == "POST":
#         user_id = request.session.get("user_id")
#         role = request.session.get("role")

#         if role != "Magsasaka" or not user_id:
#             return JsonResponse({"error": "Unauthorized or invalid user session"}, status=403)

#         try:
#             farmer = Farmer.objects.get(id=user_id)
#         except Farmer.DoesNotExist:
#             return JsonResponse({"error": "Farmer not found"}, status=404)

#         image_file = request.FILES.get("image")
#         predicted_class = request.POST.get("predicted_class")
#         confidence = request.POST.get("confidence")

#         if not all([image_file, predicted_class, confidence]):
#             return JsonResponse({"error": "Missing data"}, status=400)

#         # ✅ Upload to Supabase
#         image_url = upload_to_supabase(image_file, "History_images")
#         if not image_url:
#             return JsonResponse({"error": "Failed to upload image to Supabase"}, status=500)

#         # ✅ Save to database
#         PredictionHistory.objects.create(
#             farmer=farmer,
#             image_url=image_url,
#             predicted_class=predicted_class,
#             confidence=confidence
#         )

#         return JsonResponse({"success": True, "message": "Image and prediction saved"})

#     return JsonResponse({"error": "Invalid request"}, status=400)

# CHANGED NOV 30, 2025
# @csrf_exempt
# def upload_to_supabase_and_save(request):
#     if request.method == "POST":
#         user_id = request.session.get("user_id")
#         role = request.session.get("role")

#         if role != "Magsasaka" or not user_id:
#             return JsonResponse({"error": "Unauthorized or invalid user session"}, status=403)

#         try:
#             farmer = Farmer.objects.get(id=user_id)
#         except Farmer.DoesNotExist:
#             return JsonResponse({"error": "Farmer not found"}, status=404)

#         image_file = request.FILES.get("image")
#         predicted_class = request.POST.get("predicted_class")
#         confidence = request.POST.get("confidence")
#         library_id = request.POST.get("library_id")

#         if not all([image_file, predicted_class, confidence]):
#             return JsonResponse({"error": "Missing data"}, status=400)

#         image_url = upload_to_supabase(image_file, "History_images")
#         if not image_url:
#             return JsonResponse({"error": "Failed to upload image to Supabase"}, status=500)

#         library_entry = Library.objects.filter(id=library_id).first() if library_id else None

#         PredictionHistory.objects.create(
#             farmer=farmer,
#             image_url=image_url,
#             predicted_class=predicted_class,
#             confidence=confidence,
#             library=library_entry
#         )

#         return JsonResponse({"success": True, "message": "Image and prediction saved"})

#     return JsonResponse({"error": "Invalid request"}, status=400)



# # PESTimport os
# import torch
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.core.files.storage import FileSystemStorage
# from torchvision import transforms
# from PIL import Image
# from .models import PredictionHistory
# from django.conf import settings
# import torchvision

# def load_model():
#     device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    
#     # Add safe globals
#     torch.serialization.add_safe_globals([torchvision.models.resnet.ResNet])
    
#     model = torch.load('models/rice_pest_resnet.pth', map_location=device, weights_only=False)
#     model.eval()
#     return model

# class_names = ['Beetle', 'Brown Plant Hopper', 'Grass Hopper', 'Paddy Stem Maggot',
#     'Rice Gall Midge', 'Rice Leaf Caterpillar', 'Rice Leaf Hopper',
#     'Rice Leaf Roller', 'Rice Skipper', 'Rice Stem Borer Adult',
#     'Rice Stem Borer Larva', 'Rice Water Weevil', 'Thrips']  # Replace with your actual class names

# # Function to preprocess image
# from django.core.files.storage import default_storage

# # Function to preprocess image
# # For pest detection
# def preprocess_pest_image(image_path):
#     transform = transforms.Compose([
#         transforms.Resize(256),
#         transforms.CenterCrop(224),
#         transforms.ToTensor(),
#         transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
#     ])
#     img = Image.open(image_path).convert("RGB")  # Ensure RGB
#     img = transform(img).unsqueeze(0)
#     return img
# CHANGED NOV 30, 2025


# NOT INCLUDED BELOW
# Predict Pest Image and Return Results
# def predict_pest_image(request):
#     if request.method == 'POST' and request.FILES.get('pest_image'):
#         pest_image = request.FILES['pest_image']
        
#         # Save the uploaded file to a temporary location
#         fs = FileSystemStorage()
#         file_path = fs.save(pest_image.name, pest_image)  # Store file
#         full_file_path = fs.path(file_path)  # Get full path for file

#         # Preprocess the image after saving it
#         img = preprocess_pest_image(full_file_path)  # Pass the full file path

#         # Load the model (consider keeping it loaded in memory)
#         model = load_model()

#         # Run the prediction
#         img = img.to(torch.device("cuda:0" if torch.cuda.is_available() else "cpu"))
#         with torch.no_grad():
#             outputs = model(img)
#             _, preds = torch.max(outputs, 1)
#             predicted_class = class_names[preds.item()]
#             confidence = torch.nn.functional.softmax(outputs, dim=1)[0][preds.item()] * 100

#         return JsonResponse({
#             'predicted_class': predicted_class,
#             'confidence': confidence.item(),
#             'file_url': fs.url(file_path)  # Pass the URL of the uploaded image to the front-end
#         })
#     else:
#         return JsonResponse({'error': 'No image provided'}, status=400)


# # CHANGED NOV 30, 2025
# def predict_pest_image(request):
#     if request.method == 'POST' and request.FILES.get('pest_image'):
#         pest_image = request.FILES['pest_image']

#         fs = FileSystemStorage()
#         file_path = fs.save(pest_image.name, pest_image)
#         full_file_path = fs.path(file_path)

#         img = preprocess_pest_image(full_file_path)

#         model = load_model()
#         device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
#         model.to(device)
#         img = img.to(device)

#         with torch.no_grad():
#             outputs = model(img)
#             _, preds = torch.max(outputs, 1)
#             predicted_class = class_names[preds.item()]
#             confidence = torch.nn.functional.softmax(outputs, dim=1)[0][preds.item()] * 100

#         try:
#             library_item = Library.objects.get(paksa__icontains=predicted_class)
#             library_data = {
#                 'id': library_item.id,
#                 'deskripsyon': library_item.deskripsyon,
#                 'ano_ang_nagagawa_nito': library_item.ano_ang_nagagawa_nito,
#                 'paano_ito_pangangasiwaan': library_item.paano_ito_pangangasiwaan,
#                 'paksa': library_item.paksa,
#             }
#         except Library.DoesNotExist:
#             library_data = None

#         return JsonResponse({
#             'predicted_class': predicted_class,
#             'confidence': round(confidence.item(), 2),
#             'file_url': fs.url(file_path),
#             'library_data': library_data
#         })

#     return JsonResponse({'error': 'No image provided'}, status=400)
# @csrf_exempt
# def save_pest_prediction(request):
#     if request.method == 'POST':
#         user_id = request.session.get("user_id")
#         role = request.session.get("role")

#         if not user_id or role != "Magsasaka":
#             return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)

#         try:
#             farmer = Farmer.objects.get(id=user_id)
#         except Farmer.DoesNotExist:
#             return JsonResponse({'success': False, 'error': 'Farmer not found'}, status=404)

#         pest_image = request.FILES.get('pest_image')
#         predicted_class = request.POST.get('predicted_class')
#         confidence = request.POST.get('confidence')

#         if not all([pest_image, predicted_class, confidence]):
#             return JsonResponse({'success': False, 'error': 'Missing fields'}, status=400)

#         try:
#             confidence = float(confidence)
#         except ValueError:
#             return JsonResponse({'success': False, 'error': 'Invalid confidence value'}, status=400)

#         image_url = upload_to_supabase(pest_image, folder="uploads")
#         if not image_url:
#             return JsonResponse({'success': False, 'error': 'Image upload failed'}, status=500)

#         library = Library.objects.filter(paksa__icontains=predicted_class).first()

#         prediction = PredictionHistory.objects.create(
#             farmer=farmer,
#             image_url=image_url,
#             predicted_class=predicted_class,
#             confidence=confidence,
#             library=library
#         )

#         return JsonResponse({'success': True, 'prediction_id': prediction.id})

#     return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
# CHANGED 30, 2025

from django.conf import settings
from .models import PredictionHistory, Farmer, Library
import torch
import torch.nn as nn
from torchvision import models, transforms
import numpy as np
import cv2
import os
import tempfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import traceback
import torchvision
from django.core.files.storage import default_storage
import json
from datetime import datetime

# ========================
# DISEASE DETECTION SETUP
# ========================

# Disease class names
DISEASE_CLASS_NAMES = [
    'Bacterial Leaf Blight',      # 0
    'Bacterial Leaf Streak',     # 1  
    'Brown Spot',                # 2
    'Dead Heart Pest Attack Symptom',  # 3
    'Grain Rot',                 # 4
    'Healthy Grain',             # 5
    'Healthy Leaf',              # 6
    'Leaf scald',                # 7
    'Rice Blast',                # 8
    'Rice False Smut',           # 9
    'Rice Stripe Virus',         # 10
    'Sheath Blight',             # 11
    'Stem Rot',                  # 12
    'Tungro Virus',              # 13
    'Unknown'                    # 14
]

# Pest class names
PEST_CLASS_NAMES = [
    'Beetle',
    'Brown Plant Hopper',
    'Grass Hopper',
    'Paddy Stem Maggot Fly',
    'Rice Gall Midge',
    'Rice Leaf Caterpillar',
    'Rice Leaf Hopper',
    'Rice Leaf Roller',
    'Rice Skipper',
    'Rice Stem Borer Adult',
    'Rice Stem Borer Larva',
    'Rice Water Weevil',
    'Thrips',
    'Unknown'
]

# Image transforms for both models
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Load models with error handling
disease_model = None
pest_model = None

try:
    # Load Disease Model
    disease_model_path = os.path.join(settings.BASE_DIR, 'models', 'DISEASE_resnet_state_dict.pth')
    print(f"Loading disease model from: {disease_model_path}")
    
    if os.path.exists(disease_model_path):
        disease_model = models.resnet18(pretrained=False)
        num_ftrs = disease_model.fc.in_features
        disease_model.fc = nn.Linear(num_ftrs, len(DISEASE_CLASS_NAMES))
        disease_model.load_state_dict(torch.load(disease_model_path, map_location="cpu"))
        disease_model.eval()
        print("✓ Disease ResNet model loaded successfully!")
    else:
        print("✗ ERROR: Disease model file not found!")
except Exception as e:
    disease_model = None
    print(f"✗ ERROR loading disease model: {e}")
    traceback.print_exc()

try:
    # Load Pest Model
    pest_model_path = os.path.join(settings.BASE_DIR, 'models', 'PEST_resnet_state_dict24.pth')
    print(f"Loading pest model from: {pest_model_path}")
    
    if os.path.exists(pest_model_path):
        pest_model = models.resnet18(pretrained=False)
        num_ftrs = pest_model.fc.in_features
        pest_model.fc = nn.Linear(num_ftrs, len(PEST_CLASS_NAMES))
        pest_model.load_state_dict(torch.load(pest_model_path, map_location="cpu"))
        pest_model.eval()
        print("✓ Pest ResNet model loaded successfully!")
    else:
        print("✗ ERROR: Pest model file not found!")
except Exception as e:
    pest_model = None
    print(f"✗ ERROR loading pest model: {e}")
    traceback.print_exc()

def preprocess_image_for_resnet(image_path):
    """
    Preprocess image for ResNet model
    """
    try:
        # Load image using PIL
        image = Image.open(image_path).convert("RGB")
        
        # Apply transforms
        image_tensor = transform(image).unsqueeze(0)  # Add batch dimension
        
        return image_tensor
        
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        traceback.print_exc()
        raise

@csrf_exempt
def predict_disease(request):
    if request.method == "POST":
        try:
            # Check user session
            user_id = request.session.get("user_id")
            role = request.session.get("role")
            
            if role != "Magsasaka" or not user_id:
                return JsonResponse({"error": "Unauthorized or invalid user session"}, status=403)
            
            # Check if model is loaded
            if disease_model is None:
                return JsonResponse({"error": "Disease model not available. Please check server logs."}, status=500)
            
            # Get image file
            image_file = request.FILES.get("disease_image") or request.FILES.get("image")
            if not image_file:
                return JsonResponse({"error": "No image uploaded"}, status=400)
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                for chunk in image_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            # Preprocess image for ResNet
            image_tensor = preprocess_image_for_resnet(temp_file_path)
            
            # Predict with ResNet model
            with torch.no_grad():
                outputs = disease_model(image_tensor)
                probs = torch.nn.functional.softmax(outputs, dim=1)
                confidence, preds = torch.max(probs, 1)
                
            confidence = float(confidence.item() * 100)  # Convert to percentage
            class_index = int(preds.item())              # Convert to Python int
            predicted_class = DISEASE_CLASS_NAMES[class_index]
            
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
            
            # Fetch related Library data
            library_data = None
            try:
                # Try exact match first
                library_entry = Library.objects.get(paksa__iexact=predicted_class)
                library_data = {
                    "paksa": library_entry.paksa,
                    "deskripsyon": library_entry.deskripsyon,
                    "ano_ang_nagagawa_nito": library_entry.ano_ang_nagagawa_nito,
                    "bakit_at_saan_ito_nangyayari": library_entry.bakit_at_saan_ito_nangyayari,
                    "paano_ito_matutukoy": library_entry.paano_ito_matutukoy,
                    "bakit_ito_mahalaga": library_entry.bakit_ito_mahalaga,
                    "paano_ito_pangangasiwaan": library_entry.paano_ito_pangangasiwaan,
                    "id": library_entry.id
                }
            except Library.DoesNotExist:
                # Try with different case variations for "Leaf scald"
                if predicted_class == "Leaf scald":
                    try:
                        library_entry = Library.objects.get(paksa__iexact="Leaf Scald")
                        library_data = {
                            "paksa": library_entry.paksa,
                            "deskripsyon": library_entry.deskripsyon,
                            "ano_ang_nagagawa_nito": library_entry.ano_ang_nagagawa_nito,
                            "bakit_at_saan_ito_nangyayari": library_entry.bakit_at_saan_ito_nangyayari,
                            "paano_ito_matutukoy": library_entry.paano_ito_matutukoy,
                            "bakit_ito_mahalaga": library_entry.bakit_ito_mahalaga,
                            "paano_ito_pangangasiwaan": library_entry.paano_ito_pangangasiwaan,
                            "id": library_entry.id
                        }
                    except Library.DoesNotExist:
                        print(f"No library entry found for: {predicted_class} (tried both cases)")
                else:
                    print(f"No library entry found for: {predicted_class}")
            except Exception as e:
                print(f"Error fetching library data: {e}")
            
            response_data = {
                "predicted_class": predicted_class,
                "confidence": round(confidence, 2),
                "library_data": library_data
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            print(f"ERROR in predict_disease: {e}")
            traceback.print_exc()
            
            # Clean up temp file if it exists
            try:
                if 'temp_file_path' in locals():
                    os.unlink(temp_file_path)
            except:
                pass
            
            return JsonResponse({
                "error": f"Error processing image: {str(e)}"
            }, status=500)
    
    return JsonResponse({"error": "Invalid request method"}, status=400)

@csrf_exempt
def predict_pest(request):
    if request.method == "POST":
        try:
            # Check user session
            user_id = request.session.get("user_id")
            role = request.session.get("role")
            
            if role != "Magsasaka" or not user_id:
                return JsonResponse({"error": "Unauthorized or invalid user session"}, status=403)
            
            # Check if model is loaded
            if pest_model is None:
                return JsonResponse({"error": "Pest model not available. Please check server logs."}, status=500)
            
            # Get image file
            image_file = request.FILES.get("pest_image")
            if not image_file:
                return JsonResponse({"error": "No image uploaded"}, status=400)
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                for chunk in image_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            # Preprocess image for ResNet
            image_tensor = preprocess_image_for_resnet(temp_file_path)
            
            # Predict with ResNet model
            with torch.no_grad():
                outputs = pest_model(image_tensor)
                probs = torch.nn.functional.softmax(outputs, dim=1)
                confidence, preds = torch.max(probs, 1)
                
            confidence = float(confidence.item() * 100)  # Convert to percentage
            class_index = int(preds.item())              # Convert to Python int
            predicted_class = PEST_CLASS_NAMES[class_index]
            
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
            
            # Fetch related Library data
            library_data = None
            try:
                library_item = Library.objects.get(paksa__icontains=predicted_class)
                library_data = {
                    'id': library_item.id,
                    'deskripsyon': library_item.deskripsyon,
                    'ano_ang_nagagawa_nito': library_item.ano_ang_nagagawa_nito,
                    'paano_ito_pangangasiwaan': library_item.paano_ito_pangangasiwaan,
                    'paksa': library_item.paksa,
                }
            except Library.DoesNotExist:
                print(f"No library entry found for pest: {predicted_class}")
            except Exception as e:
                print(f"Error fetching pest library data: {e}")
            
            response_data = {
                "predicted_class": predicted_class,
                "confidence": round(confidence, 2),
                "library_data": library_data
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            print(f"ERROR in predict_pest: {e}")
            traceback.print_exc()
            
            # Clean up temp file if it exists
            try:
                if 'temp_file_path' in locals():
                    os.unlink(temp_file_path)
            except:
                pass
            
            return JsonResponse({
                "error": f"Error processing image: {str(e)}"
            }, status=500)
    
    return JsonResponse({"error": "Invalid request method"}, status=400)

@csrf_exempt
def upload_to_supabase_and_save(request):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        role = request.session.get("role")

        if role != "Magsasaka" or not user_id:
            return JsonResponse({"error": "Unauthorized or invalid user session"}, status=403)

        try:
            farmer = Farmer.objects.get(id=user_id)
        except Farmer.DoesNotExist:
            return JsonResponse({"error": "Farmer not found"}, status=404)

        image_file = request.FILES.get("image")
        predicted_class = request.POST.get("predicted_class")
        confidence = request.POST.get("confidence")
        library_id = request.POST.get("library_id")
        
        # NEW: Get location data
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        location_accuracy = request.POST.get("location_accuracy")

        if not all([image_file, predicted_class, confidence]):
            return JsonResponse({"error": "Missing data"}, status=400)

        image_url = upload_to_supabase(image_file, "disease_predictions")
        if not image_url:
            return JsonResponse({"error": "Failed to upload image to Supabase"}, status=500)

        library_entry = Library.objects.filter(id=library_id).first() if library_id else None

        # NEW: Create prediction with location data
        prediction = PredictionHistory.objects.create(
            farmer=farmer,
            image_url=image_url,
            predicted_class=predicted_class,
            confidence=confidence,
            library=library_entry,
            latitude=latitude,
            longitude=longitude,
            location_accuracy=location_accuracy,
            location_timestamp=timezone.now() if latitude and longitude else None
        )

        return JsonResponse({
            "success": True, 
            "message": "Image and prediction saved" + (" with location" if latitude and longitude else "")
        })

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def save_pest_prediction(request):
    if request.method == 'POST':
        user_id = request.session.get("user_id")
        role = request.session.get("role")

        if not user_id or role != "Magsasaka":
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)

        try:
            farmer = Farmer.objects.get(id=user_id)
        except Farmer.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Farmer not found'}, status=404)

        pest_image = request.FILES.get('pest_image')
        predicted_class = request.POST.get('predicted_class')
        confidence = request.POST.get('confidence')
        
        # NEW: Get location data
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        location_accuracy = request.POST.get("location_accuracy")

        if not all([pest_image, predicted_class, confidence]):
            return JsonResponse({'success': False, 'error': 'Missing fields'}, status=400)

        try:
            confidence = float(confidence)
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid confidence value'}, status=400)

        image_url = upload_to_supabase(pest_image, "pest_predictions")
        if not image_url:
            return JsonResponse({'success': False, 'error': 'Image upload failed'}, status=500)

        library = Library.objects.filter(paksa__icontains=predicted_class).first()

        # NEW: Create prediction with location data
        prediction = PredictionHistory.objects.create(
            farmer=farmer,
            image_url=image_url,
            predicted_class=predicted_class,
            confidence=confidence,
            library=library,
            latitude=latitude,
            longitude=longitude,
            location_accuracy=location_accuracy,
            location_timestamp=timezone.now() if latitude and longitude else None
        )

        return JsonResponse({
            'success': True, 
            'prediction_id': prediction.id,
            'message': 'Pest prediction saved successfully' + (" with location" if latitude and longitude else "")
        })

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
# Add history function if not exists
@csrf_exempt
def get_prediction_history(request):
    if request.method == "GET":
        user_id = request.session.get("user_id")
        role = request.session.get("role")

        if role != "Magsasaka" or not user_id:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        try:
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            classification = request.GET.get('classification')

            history = PredictionHistory.objects.filter(farmer_id=user_id)
            
            # Date filters
            if start_date:
                history = history.filter(uploaded_at__gte=start_date)
            if end_date:
                history = history.filter(uploaded_at__lte=end_date)
            
            # Classification filter
            disease_classes = [cls for cls in DISEASE_CLASS_NAMES if cls != 'Unknown']
            pest_classes = [cls for cls in PEST_CLASS_NAMES if cls != 'Unknown']
            
            if classification:
                if classification == 'sakit':
                    history = history.filter(predicted_class__in=disease_classes)
                elif classification == 'peste':
                    history = history.filter(predicted_class__in=pest_classes)
                elif classification == 'unknown':
                    history = history.filter(predicted_class='Unknown')
            
            history_data = []
            for item in history.order_by('-uploaded_at'):
                # Determine type
                if item.predicted_class == 'Unknown':
                    item_type = 'unknown'
                elif item.predicted_class in disease_classes:
                    item_type = 'sakit'
                elif item.predicted_class in pest_classes:
                    item_type = 'peste'
                else:
                    item_type = 'unknown'
                
                history_data.append({
                    'id': item.id,
                    'image_url': item.image_url,
                    'predicted_class': item.predicted_class,
                    'confidence': item.confidence,
                    'uploaded_at': item.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'type': item_type,
                    # NEW: Include location data
                    'latitude': float(item.latitude) if item.latitude else None,
                    'longitude': float(item.longitude) if item.longitude else None,
                })

            return JsonResponse({'history': history_data})
            
        except Exception as e:
            print(f"Error loading history: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)