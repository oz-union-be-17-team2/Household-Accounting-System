from django.conf import settings
from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.account.selectors import get_account_detail, get_account_list
from app.account.serializers import AccountCreateSerializer, AccountDetailSerializer, AccountListSerializer

User = get_user_model()


class AccountListCreateAPIView(APIView):
    if not settings.DEBUG:
        permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="계좌 목록 조회",
        description="계좌 목록 조회 및 페이지네이션",
        parameters=[
            OpenApiParameter(name="account_type", description="계좌 유형 (CHECKING/SAVINGS/DEPOSIT/OVERDRAFT/LOAN)"),
            OpenApiParameter(
                name="bank_code",
                description="은행 코드 (004:KB, 088:SHINHAN, 020:WOORI, 081:HANA, 011:NH, "
                "003:IBK, 023:SC, 027:CITI, 032:BUSAN, 031:DAEGU, 090:KAKAO, 092:TOSS, 089:K)",
            ),
        ],
        responses={200: AccountListSerializer},
    )
    def get(self, request):
        account_list = get_account_list(
            user=request.user,
            account_type=request.query_params.get("account_type"),
            bank_code=request.query_params.get("bank_code"),
        )
        paginator = PageNumberPagination()
        queryset = paginator.paginate_queryset(account_list, request)
        serializer = AccountListSerializer(queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="계좌 생성",
        description="계좌 유형 (CHECKING/SAVINGS/DEPOSIT/OVERDRAFT/LOAN)\n\n"
        "은행 코드 (004:KB, 088:SHINHAN, 020:WOORI, ...)",
        request=AccountCreateSerializer,
        responses={201: AccountCreateSerializer},
    )
    def post(self, request):
        serializer = AccountCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if settings.DEBUG:
            serializer.save(user=User.objects.first())
        else:
            serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AccountDetailAPIView(APIView):
    if not settings.DEBUG:
        permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="계좌 상세정보 조회", description="계좌 상세정보 조회", responses={200: AccountDetailSerializer}
    )
    def get(self, request, account_pk):
        account = get_account_detail(user=request.user, account_pk=account_pk)
        serializer = AccountDetailSerializer(account, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="계좌 상세정보 수정",
        description="이름, 활성상태 수정 가능",
        request=AccountDetailSerializer,
        responses={200: AccountDetailSerializer},
    )
    def patch(self, request, account_pk):
        account = get_account_detail(user=request.user, account_pk=account_pk)
        serializer = AccountDetailSerializer(account, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="계좌 삭제",
        description="계좌 하드델리트",
        responses={204: None},
    )
    def delete(self, request, account_pk):
        account = get_account_detail(user=request.user, account_pk=account_pk)
        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
