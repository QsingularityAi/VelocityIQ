# VelocityIQ Dashboard Authentication Setup

This guide explains how to add Supabase authentication to your VelocityIQ dashboard.

## Prerequisites

1. **Supabase Project**: You need an existing Supabase project
2. **Node.js and npm**: For React dependencies
3. **Supabase CLI** (optional): For local development

## Step 1: Configure Environment Variables

Create a `.env` file in the `dashboard` directory:

```env
# Supabase Configuration
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-supabase-anon-key

# API Configuration (optional - for backend integration)
REACT_APP_API_URL=http://localhost:8000
```

### Finding Your Supabase Credentials

1. Go to your [Supabase Dashboard](https://app.supabase.com)
2. Select your project
3. Go to **Settings** → **API**
4. Copy the **Project URL** and **anon/public** key

## Step 2: Update Supabase Schema

Run the authentication schema in your Supabase SQL Editor:

1. Open your Supabase project dashboard
2. Go to **SQL Editor**
3. Create a new query
4. Copy and paste the contents of `supabase-auth-schema.sql`
5. Click **Run**

This will:
- Create user profiles table
- Set up Row Level Security (RLS) policies
- Remove anonymous access
- Create automatic profile creation on user registration

## Step 3: Configure Supabase Authentication

### Enable Email Authentication

1. Go to **Authentication** → **Settings** in your Supabase dashboard
2. Under **Auth Providers**, ensure **Email** is enabled
3. Configure the following settings:

#### Email Templates (Optional but Recommended)

**Confirm Signup Email:**
```html
<h2>Confirm your signup for VelocityIQ</h2>
<p>Follow this link to confirm your account:</p>
<p><a href="{{ .ConfirmationURL }}">Confirm your account</a></p>
```

**Reset Password Email:**
```html
<h2>Reset Your Password for VelocityIQ</h2>
<p>Follow this link to reset your password:</p>
<p><a href="{{ .ConfirmationURL }}">Reset Password</a></p>
```

#### Redirect URLs

Add these URLs to your **Redirect URLs** list:
- `http://localhost:3001` (for development)
- `https://yourdomain.com` (for production)

## Step 4: Test the Authentication

1. **Start the dashboard:**
   ```bash
   cd dashboard
   npm start
   ```

2. **Register a new account:**
   - Go to `http://localhost:3001`
   - Click "Sign up" 
   - Fill out the registration form
   - Check your email for verification

3. **Sign in:**
   - Use your registered email and password
   - You should see the dashboard after successful login

## Step 5: Backend Integration (Optional)

If you have a backend API, you can validate Supabase JWT tokens:

### Python/FastAPI Example

```python
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(token: str = Depends(security)):
    try:
        # Verify the JWT token with Supabase
        payload = jwt.decode(
            token.credentials, 
            SUPABASE_JWT_SECRET, 
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
```

### Getting JWT Secret

1. Go to **Settings** → **API** in Supabase
2. Copy the **JWT Secret**
3. Add it to your backend environment variables

## Features Included

### ✅ User Registration
- Email/password registration
- Password strength validation
- User metadata collection (name, company)

### ✅ User Login
- Email/password authentication
- Remember me functionality
- Session persistence

### ✅ Password Reset
- Forgot password flow
- Email-based password reset
- Secure token validation

### ✅ User Management
- User profile display in header
- Logout functionality
- Automatic session handling

### ✅ Security Features
- Row Level Security (RLS)
- Authenticated-only data access
- Automatic token refresh
- Session validation

## Customization Options

### Styling
All authentication components use Tailwind CSS and follow your existing design system. You can customize:
- Colors in `tailwind.config.js`
- Component styling in each auth component
- Logo and branding in login/register screens

### Validation Rules
Customize password requirements in `Register.js`:
```javascript
// Current requirements: 8+ chars, uppercase, lowercase, number
// Modify the validateForm() function to change requirements
```

### User Metadata
Add more user fields by:
1. Updating the registration form in `Register.js`
2. Modifying the `user_profiles` table schema
3. Updating the profile creation trigger

## Troubleshooting

### Common Issues

**"Invalid token" errors:**
- Check that your Supabase URL and anon key are correct
- Verify the JWT secret in your backend
- Check that RLS policies allow authenticated users

**Registration emails not sending:**
- Verify email settings in Supabase Auth
- Check spam folder
- Ensure SMTP is configured (for production)

**Redirect loops:**
- Check that redirect URLs are properly configured
- Verify environment variables are loaded
- Clear browser cache and localStorage

### Debug Mode

Add this to your environment for debugging:
```env
REACT_APP_DEBUG=true
```

This will show additional console logs for auth state changes.

## Production Deployment

### Environment Variables
Ensure these are set in your production environment:
- `REACT_APP_SUPABASE_URL`
- `REACT_APP_SUPABASE_ANON_KEY`
- `REACT_APP_API_URL` (if using backend)

### Security Checklist
- [ ] RLS enabled on all tables
- [ ] Anonymous access removed
- [ ] Production redirect URLs configured
- [ ] Email templates customized
- [ ] HTTPS enabled
- [ ] JWT secrets secured

## Next Steps

1. **Multi-factor Authentication**: Add 2FA using Supabase Auth
2. **Social Login**: Enable Google/GitHub/etc. providers
3. **Role-based Access**: Implement user roles and permissions
4. **Audit Logging**: Track user actions in the dashboard
5. **Session Management**: Add session timeout and concurrent session limits

## Support

For issues specific to this implementation:
1. Check the browser console for error messages
2. Verify your Supabase configuration
3. Test with a fresh incognito browser session
4. Check the Supabase Auth logs in your dashboard

For general Supabase auth questions, see the [official documentation](https://supabase.com/docs/guides/auth). 