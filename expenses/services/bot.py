# expenses/services/bot.py
import requests
from decimal import Decimal
from django.db.models import Sum
from expenses.config import discord_config
import logging

logger = logging.getLogger(__name__)


def send_budget_alert(message):
    """Send budget alert to Discord webhook"""
    
    webhook_url = discord_config.WEBHOOK_URL
    
    # Return early if webhook URL is not configured
    if not webhook_url:
        logger.warning("Discord webhook URL not configured")
        return False
    
    try:
        response = requests.post(
            webhook_url,
            json={"content": message},
            timeout=discord_config.TIMEOUT,
        )
        
        response.raise_for_status()
        logger.info(f"Alert sent successfully to Discord")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Discord alert: {e}")
        return False


def check_budget_limit(expense):
    """Check if expense exceeds category monthly limit and send alert"""
    
    from ..models import Expense
    
    category = expense.category
    
    # Skip if no monthly limit set
    if not category.monthly_limit:
        logger.debug(f"No monthly limit for category: {category.name}")
        return
    
    # Calculate start of month
    month_start = expense.date.replace(day=1)
    
    # Calculate total spent in current month (up to expense date)
    spent_result = (
        Expense.objects.filter(
            owner=expense.owner,
            category=category,
            date__gte=month_start,
            date__lte=expense.date,
        )
        .aggregate(total=Sum("amount"))
        .get("total")
    )
    
    spent = spent_result if spent_result else Decimal("0.00")
    
    logger.debug(f"Category: {category.name}, Spent: {spent}, Limit: {category.monthly_limit}")
    
    # Check if limit exceeded
    if spent > category.monthly_limit:
        
        # Calculate exceeded amount
        exceeded = spent - category.monthly_limit
        
        # Format message for Discord
        message = (
            f"⚠️ **BUDGET ALERT** ⚠️\n\n"
            f"**Category:** {category.name}\n"
            f"**Monthly Limit:** ${category.monthly_limit:,.2f}\n"
            f"**Current Spent:** ${spent:,.2f}\n"
            f"**Exceeded by:** ${exceeded:,.2f}\n"
            f"**Month:** {expense.date.strftime('%B %Y')}\n\n"
            f"**Latest Expense:** {expense.title} - ${expense.amount:,.2f}"
        )
        
        # Send alert
        send_budget_alert(message)