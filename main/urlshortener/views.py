from django.utils import timezone  # Correct timezone import
from django.shortcuts import render
from rest_framework.response import Response
from .models import ClickAnalytics, MyLink
from rest_framework.decorators import api_view, permission_classes
from .serializer import LinkSerializer, ClickAnalyticsSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound
import logging
from django.core.exceptions import MultipleObjectsReturned
from django.db import transaction





@api_view(['POST'])
@permission_classes([AllowAny])
def create_link(request):
    serializer = LinkSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        # Only set user if authenticated
        if request.user.is_authenticated:
            serializer.save(user=request.user)
        else:
            serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_links(request):
    links = MyLink.objects.filter(user=request.user)
    serializer = LinkSerializer(links, many = True)
    return Response(serializer.data)





@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_link(request, hash):
    """ Allow only the owner of the link to delete it """
    link = MyLink.objects.filter(hash=hash, user=request.user).first()

    if not link:
        return Response({"error": "Link not found or not authorized to delete"}, status=404)

    link.delete()
    return Response({"message": "Link deleted successfully"}, status=200)

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_link(request, hash):
    try:
        with transaction.atomic():  # Ensures the operation runs inside a transaction
            link = MyLink.objects.select_for_update().get(hash=hash)

            if link.expiration_date and link.expiration_date < timezone.now():
                return Response({"error": "Link expired"}, status=410)

            # Handle potential null values explicitly
            ip_address = request.META.get('REMOTE_ADDR', None)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:300]

            ClickAnalytics.objects.create(
                link=link,
                ip_address=ip_address,
                user_agent=user_agent if user_agent else None
            )

        return Response({
            "source_link": link.source_link,
            "hash": link.hash,
            "expiration_date": link.expiration_date
        })

    except MyLink.DoesNotExist:
        logger.warning(f"Link not found: {hash}")
        return Response({"error": "Link not found"}, status=404)

    except MultipleObjectsReturned:
        logger.error(f"Hash collision detected for: {hash}")
        return Response({"error": "Multiple links found"}, status=500)

    except Exception as e:
        logger.error(f"Error in get_link: {str(e)}", exc_info=True)
        return Response({"error": "Internal server error"}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_clicks(request, hash):
    try:
        link = MyLink.objects.get(hash=hash)
        
        # Verify ownership first
        if link.user != request.user:
            return Response({"error": "Unauthorized access"}, status=403)
        
        clicks = ClickAnalytics.objects.filter(link=link)
        serializer = ClickAnalyticsSerializer(clicks, many=True)
        
        return Response({
            "total_clicks": clicks.count(),
            "analytics": serializer.data
        })
    
    except MyLink.DoesNotExist:
        return Response({"error": "Link not found"}, status=404)