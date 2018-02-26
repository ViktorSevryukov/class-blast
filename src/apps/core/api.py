import json

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.core.tasks import export_to_aha


@api_view(['POST'])
def export_group(request):
    try:
        groups = json.loads(request.data['groups'])
    except:
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

    export_to_aha.delay(groups, request.user.id)
    return Response({"status": "ok"})
