from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.account.selectors import get_account_list
from app.account.serializers import AccountDetailSerializer, AccountListCreateSerializer
from app.account.services import create_account, delete_account, retrieve_account, update_account


class AccountListCreateAPIView(APIView):
    if not settings.DEBUG:
        permission_classes = [IsAuthenticated]

    @extend_schema(request=AccountListCreateSerializer, responses={200: AccountListCreateSerializer})
    def get(self, request):
        account_list = get_account_list(user=request.user)
        paginator = PageNumberPagination()
        queryset = paginator.paginate_queryset(account_list, request)
        serializer = AccountListCreateSerializer(queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(request=AccountListCreateSerializer, responses={201: AccountListCreateSerializer})
    def post(self, request):
        data = create_account(user=request.user, data=request.data)
        return Response(data, status=status.HTTP_201_CREATED)


class AccountDetailAPIView(APIView):
    if not settings.DEBUG:
        permission_classes = [IsAuthenticated]

    @extend_schema(request=AccountDetailSerializer, responses={200: AccountDetailSerializer})
    def get(self, request, account_pk):
        data = retrieve_account(user=request.user, account_pk=account_pk)
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(request=AccountDetailSerializer, responses={200: AccountDetailSerializer})
    def patch(self, request, account_pk):
        data = update_account(user=request.user, data=request.data, account_pk=account_pk)
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}})
    def delete(self, request, account_pk):
        delete_account(user=request.user, account_pk=account_pk)
        return Response({"message": "계좌가 삭제되었습니다."}, status=status.HTTP_200_OK)
