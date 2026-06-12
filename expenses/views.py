from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from .models import Category, Expense
from .serializers import CategorySerializer, ExpenseSerializer
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from .auth_serializers import RegisterSerializer


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def category_list(request):
    if request.method == "GET":
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    serializer = CategorySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def expense_list(request):
    if request.method == "GET":
        expenses = Expense.objects.all()

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        if start_date:
            expenses = expenses.filter(date__gte=start_date)
        if end_date:
            expenses = expenses.filter(date__lte=end_date)

        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)

    serializer = ExpenseSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    category = serializer.validated_data["category"]

    if category.owner != request.user:
        return Response(
            {"detail": "Invalid category"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    serializer.save(owner=request.user) 
    return Response(serializer.data, status=status.HTTP_201_CREATED)



@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def expense_detail(request, pk):
    try:
        expense = Expense.objects.get(
            pk=pk,
            owner=request.user,
        )
    except Expense.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = ExpenseSerializer(expense, data=request.data)
        serializer.is_valid(raise_exception=True)

        category = serializer.validated_data["category"]

        if category.owner != request.user:
            return Response(
                {"detail": "Invalid category"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(owner=request.user)

        return Response(serializer.data)

    expense.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def expense_summary(request):
    summary = (
        Expense.objects.filter(owner=request.user)
        .values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("category__name")
    )

    return Response(list(summary))




# ----------------------------
# Authentication Endpoints
# ----------------------------

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.save()

    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {"token": token.key},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    user = authenticate(
        username=request.data.get("username"),
        password=request.data.get("password"),
    )

    if not user:
        return Response(
            {"detail": "Invalid credentials"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {"token": token.key}
    )