from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.account.selectors import get_account_list
from app.account.serializers import AccountCreateSerializer, AccountDetailSerializer, AccountListSerializer
from app.account.services import create_account, delete_account, retrieve_account, update_account


class AccountListCreateAPIView(APIView):
    if not settings.DEBUG:
        permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="계좌 목록 조회",
        description="계좌 목록 조회 및 페이지네이션",
        responses={200: AccountListSerializer},
    )
    def get(self, request):
        account_list = get_account_list(user=request.user)
        paginator = PageNumberPagination()
        queryset = paginator.paginate_queryset(account_list, request)
        serializer = AccountListSerializer(queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="계좌 생성",
        description="계좌번호, 계좌 종류, 은행, 잔액 입력 필요",
        request=AccountCreateSerializer,
        responses={201: AccountCreateSerializer},
    )
    def post(self, request):
        data = create_account(user=request.user, data=request.data)
        return Response(data, status=status.HTTP_201_CREATED)


class AccountDetailAPIView(APIView):
    if not settings.DEBUG:
        permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="계좌 상세정보 조회", description="계좌 상세정보 조회", responses={200: AccountDetailSerializer}
    )
    def get(self, request, account_pk):
        data = retrieve_account(user=request.user, account_pk=account_pk)
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="계좌 상세정보 수정",
        description="이름, 활성상태 수정 가능",
        request=AccountDetailSerializer,
        responses={200: AccountDetailSerializer},
    )
    def patch(self, request, account_pk):
        data = update_account(user=request.user, data=request.data, account_pk=account_pk)
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="계좌 삭제",
        description="계좌 하드델리트",
        responses={204: None},
    )
    def delete(self, request, account_pk):
        delete_account(user=request.user, account_pk=account_pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
