from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from app.account.models import Account
from app.account.serializers import AccountListCreateSerializer
from rest_framework.response import Response

class AccountListCreateAPIView(APIView):

    def get(self, request):
        account_list= Account.objects.all().select_related('user')
        paginator = PageNumberPagination()
        queryset = paginator.paginate_queryset(account_list, request)
        serializer = AccountListCreateSerializer(queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = AccountListCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
