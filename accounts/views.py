from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, UserProfileUpdateForm, ChangePasswordForm

def register_view(request):
    """
    Handle user registration with phone number and hashed password.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Welcome, {user.full_name}! Your account has been created successfully. Please log in with your phone number."
            )
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below to register.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Handle user authentication using phone number and password.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.full_name}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid phone number or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    Handle user logout and flush session.
    """
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')


@login_required
def profile_settings_view(request):
    """
    View user details, update name, and change password securely.
    """
    user = request.user
    profile_form = UserProfileUpdateForm(instance=user)
    password_form = ChangePasswordForm(user=user)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profile':
            profile_form = UserProfileUpdateForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Your profile information has been updated successfully.")
                return redirect('settings')
            else:
                messages.error(request, "Please correct the profile errors below.")
        elif action == 'change_password':
            password_form = ChangePasswordForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                # Keep user logged in after password change
                update_session_auth_hash(request, user)
                messages.success(request, "Your password was changed successfully.")
                return redirect('settings')
            else:
                messages.error(request, "Please correct the password errors below.")

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'user_obj': user,
        'active_page': 'settings'
    }
    return render(request, 'accounts/profile.html', context)
