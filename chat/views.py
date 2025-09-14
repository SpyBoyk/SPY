import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import ChatSession, ChatMessage
from .utils import generate_response
from .google_auth import get_google_oauth_url, exchange_code_for_token, get_user_info, authenticate_user
from django.conf import settings

def home(request):
    if request.user.is_authenticated:
        # Get the most recent session or create a new one
        chat_session = ChatSession.objects.filter(user=request.user).order_by('-created_at').first()
        if not chat_session:
            chat_session = ChatSession.objects.create(user=request.user)
        return redirect('chat_session', session_id=chat_session.id)
    return render(request, 'login.html')

@login_required
def chat_view(request, session_id=None):
    if session_id:
        chat_session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    else:
        # Get the most recent session or create a new one
        chat_session = ChatSession.objects.filter(user=request.user).order_by('-created_at').first()
        if not chat_session:
            chat_session = ChatSession.objects.create(user=request.user)
        return redirect('chat_session', session_id=chat_session.id)
    
    messages = chat_session.messages.all()
    
    # Get all sessions for the sidebar
    sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'index.html', {
        'session': chat_session,
        'messages': messages,
        'sessions': sessions
    })

@login_required
@csrf_exempt
def send_message(request, session_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            
            if not message or not message.strip():
                return JsonResponse({'error': 'Message cannot be empty'}, status=400)
            
            chat_session = get_object_or_404(ChatSession, id=session_id, user=request.user)
            
            # Save user message
            user_message = ChatMessage.objects.create(
                session=chat_session,
                role='user',
                content=message
            )
            
            # Get chat history for context
            chat_history = chat_session.messages.all()
            
            # Generate response using Gemini
            response_text = generate_response(message, chat_history)
            
            # Save assistant response
            assistant_message = ChatMessage.objects.create(
                session=chat_session,
                role='assistant',
                content=response_text
            )
            
            # Update session title if it's the first message
            if chat_session.title == "New Chat" and chat_session.messages.count() == 2:
                # Use the first message as the title (truncated if needed)
                title = message[:50] + "..." if len(message) > 50 else message
                chat_session.title = title
                chat_session.save()
            
            return JsonResponse({
                'response': response_text,
                'message_id': assistant_message.id
            })
        
        except Exception as e:
            logger.error(f"Error in send_message: {e}")
            return JsonResponse({
                'error': 'Sorry, something went wrong. Please try again.',
                'details': str(e) if settings.DEBUG else None
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def new_chat(request):
    chat_session = ChatSession.objects.create(user=request.user)
    return redirect('chat_session', session_id=chat_session.id)

@login_required
def delete_chat(request, session_id):
    chat_session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    chat_session.delete()
    return redirect('chat')

def google_login(request):
    # If user is already authenticated, redirect to chat
    if request.user.is_authenticated:
        return redirect('chat')
    
    # Generate Google OAuth URL
    auth_url = get_google_oauth_url()
    return JsonResponse({'auth_url': auth_url})

def google_callback(request):
    # If user is already authenticated, redirect to chat
    if request.user.is_authenticated:
        return redirect('chat')
    
    code = request.GET.get('code')
    if not code:
        return redirect('home')
    
    # Exchange code for tokens
    tokens = exchange_code_for_token(code)
    if not tokens:
        return redirect('home')
    
    # Get user info
    user_info = get_user_info(tokens['access_token'])
    if not user_info:
        return redirect('home')
    
    # Authenticate or create user
    user = authenticate_user(user_info)
    login(request, user)
    
    return redirect('chat')

def logout_view(request):
    logout(request)
    return redirect('home')