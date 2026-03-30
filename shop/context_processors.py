from .models import CartItem


def cart_count(request):
    if request.user.is_authenticated:
        # Sum up the quantity of all items in the user's cart
        count = sum(item.quantity for item in CartItem.objects.filter(
            user=request.user))
    else:
        count = 0
    return {'cart_item_count': count}
