from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Institute
from .serializers import InstituteSerializer


class InstituteListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        institutes = Institute.objects.all()
        serializer = InstituteSerializer(institutes, many=True)
        return Response(serializer.data)