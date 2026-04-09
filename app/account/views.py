from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.account.exceptions import AccountNotFoundError
from app.account.selectors import get_account_detail, get_account_list
from app.account.serializers import AccountDetailSerializer, AccountListCreateSerializer


class AccountListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        account_list = get_account_list(user=request.user)

        if not account_list:
            return Response({"message": "계좌가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

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


class AccountDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, account_pk):
        try:
            account = get_account_detail(user=request.user, account_pk=account_pk)
        except AccountNotFoundError as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = AccountDetailSerializer(account, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, account_pk):
        try:
            account = get_account_detail(user=request.user, account_pk=account_pk)
        except AccountNotFoundError as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = AccountDetailSerializer(account, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, account_pk):
        try:
            account = get_account_detail(user=request.user, account_pk=account_pk)
        except AccountNotFoundError as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)

        account.delete()
        return Response({"message": "계좌가 삭제되었습니다."}, status=status.HTTP_200_OK)
