# utils/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Check for inactive user error (common in JWT authentication)
        if (response.data.get('detail') == 'User is inactive' or 
            response.data.get('detail') == 'User not found' or
            response.data.get('detail') == 'User account is disabled'):
            return Response({
                'status': 2,
                'message': 'You Are Not an Authorised Person; Please Contact the Admin'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # You can also handle other JWT-specific errors
        if response.data.get('code') == 'user_inactive':
            return Response({
                'status': 2,
                'message': 'You Are Not an Authorised Person; Please Contact the Admin'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    return response