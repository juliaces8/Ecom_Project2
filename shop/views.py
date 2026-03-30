from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib import messages

from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .serializers import StoreSerializer, ProductSerializer, ReviewSerializer
from .permissions import IsVendor

from .models import Store, Product, Order, OrderItem, Review
from .forms import UserRegisterForm, ReviewForm, ProductForm, StoreForm

import tweepy

# --- AUTHENTICATION ---


def register(request):
    """Handles new user account creation."""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('product_list')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

# --- PRODUCT VIEWS ---


def product_list(request):
    """Displays all available products across all stores."""
    products = Product.objects.select_related('store').all()
    return render(request, 'shop/product_list.html', {'products': products})


def product_detail(request, pk):
    """Displays detailed information and reviews for a single product."""
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all().order_by('-created_at')
    review_form = ReviewForm()
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'review_form': review_form
    })

# --- SESSION-BASED CART VIEWS ---


def view_cart(request):
    """Displays items currently held in the user session cart."""
    # REDIRECT VENDOR: Requirement fix
    if request.user.is_authenticated and request.user.profile.role == 'vendor':
        messages.error(request, "Vendors cannot access the shopping cart.")
        return redirect('vendor_dashboard')

    cart = request.session.get('cart', {})
    items = []
    total = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        line_total = product.price * quantity
        total += line_total
        items.append({
            'product': product,
            'quantity': quantity,
            'total_price': line_total
        })
    return render(
        request,
        'shop/view_cart.html',
        {'items': items, 'total': total}
    )


def add_to_cart(request, product_id):
    """
    Adds a product to the session-based shopping cart.

    Prevents vendors from purchasing items to maintain market
    integrity as per project requirements.
    """
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated and (
            product.store.vendor == request.user or
            request.user.profile.role == 'vendor'):
        messages.error(request, "Vendors cannot purchase products.")
        return redirect('product_detail', pk=product.id)

    cart = request.session.get('cart', {})
    p_id = str(product_id)
    cart[p_id] = cart.get(p_id, 0) + 1
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('view_cart')


def update_cart(request, product_id, action):
    """Handles quantity adjustments (type-in) and removals."""
    cart = request.session.get('cart', {})
    p_id = str(product_id)
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST' and action == 'update':
        new_qty = int(request.POST.get('quantity', 1))
        if new_qty > product.stock:
            messages.error(request, f"Only {product.stock} units available.")
            cart[p_id] = product.stock
        else:
            cart[p_id] = max(1, new_qty)
    elif action == 'remove':
        cart.pop(p_id, None)

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('view_cart')

# --- CHECKOUT ---


@login_required
def checkout(request):
    """Processes order, validates stock, and marks reviews as verified."""
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('product_list')

    cart_items = []
    total_price = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        # STOCK CHECK: Requirement fix
        if quantity > product.stock:
            messages.error(
                request,
                f"Stock changed for {product.name}. Max available:"
                f"{product.stock}")
            return redirect('view_cart')

        line_total = product.price * quantity
        total_price += line_total
        cart_items.append(
            {'product': product,
             'quantity': quantity, 'total_price': line_total})

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user, total_price=total_price)
        for item in cart_items:
            OrderItem.objects.create(
                order=order, product=item['product'],
                product_name=item['product'].name,
                price=item['product'].price, quantity=item['quantity']
            )
            # DEDUCT STOCK
            item['product'].stock -= item['quantity']
            item['product'].save()

            # VERIFY REVIEWS: Requirement fix
            Review.objects.filter(
                user=request.user,
                product=item['product']).update(is_verified=True)

        # Email and Session clearing logic
        request.session['cart'] = {}
        request.session.modified = True
        return redirect('checkout_success')

    return render(
        request,
        'shop/checkout_confirm.html',
        {'cart_items': cart_items, 'total_price': total_price})


def checkout_success(request):
    return render(request, 'shop/checkout_success.html')

# --- DASHBOARDS ---


@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/profile.html', {'orders': orders})


@login_required
def vendor_dashboard(request):
    """Displays a vendor-specific dashboard."""
    # Fetch stores owned by the user
    user_stores = Store.objects.filter(vendor=request.user)
    # Filter products that belong to any store owned by this user
    vendor_products = Product.objects.filter(store__in=user_stores)

    vendor_sales = OrderItem.objects.filter(product__in=vendor_products)
    total_earnings = sum(item.get_total() for item in vendor_sales)

    return render(request, 'shop/vendor_dashboard.html', {
        'stores': user_stores,
        'products': vendor_products,
        'total_earnings': total_earnings,
        'total_orders': vendor_sales.count(),
        'recent_activity': vendor_sales.order_by('-id')[:5],
    })

# --- VENDOR PRODUCT MANAGEMENT ---


@login_required
def add_product(request):
    """Allows a vendor to add a new product."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()

            # Tweet message
            msg = f"New at {product.store.name}: {product.name}!\n\n" \
                  f"{product.description[:50]}..."

            # Since Product model has NO image field, set img to None
            img = None

            post_to_x(msg, img)
            return redirect('vendor_dashboard')
    else:
        form = ProductForm()
        form.fields['store'].queryset = Store.objects.filter(
            vendor=request.user)

    return render(request, 'shop/add_product.html', {'form': form})


@login_required
def edit_product(request, pk):
    """
    Handles the editing of an existing product.
    Ensures only the store owner can modify the product.
    """
    product = get_object_or_404(Product, pk=pk, store__vendor=request.user)

    if request.method == "POST":
        # 'instance=product' tells Django to update the existing item.
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('vendor_dashboard')
    else:
        form = ProductForm(instance=product)

    return render(request, 'shop/edit_product.html', {
        'form': form,
        'product': product
    })


@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, store__vendor=request.user)
    if request.method == 'POST':
        product.delete()
        return redirect('vendor_dashboard')
    return render(request, 'shop/delete_confirm.html', {'product': product})

# --- REVIEWS ---


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Prevent vendors from reviewing their own products
    if product.store.vendor == request.user:
        messages.error(request, "You cannot review your own product.")
        return redirect('product_detail', pk=product.id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        content_text = request.POST.get('content')
        has_purchased = OrderItem.objects.filter(order__user=request.user,
                                                 product=product).exists()
        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            content=content_text,
            is_verified=has_purchased
        )
        messages.success(request, "Review submitted successfully!")

    return redirect('product_detail', pk=product.id)


@login_required
def vendor_review_list(request):
    """Requirement: Centralized list of reviews for a Vendor's products."""
    user_stores = Store.objects.filter(vendor=request.user)
    reviews = Review.objects.filter(
        product__store__in=user_stores).order_by('-created_at')
    return render(
        request, 'shop/vendor_review_list.html', {'reviews': reviews})

# View for listing all stores or creating a new one


class StoreListCreateAPI(generics.ListCreateAPIView):
    serializer_class = StoreSerializer
    # Buyers can Read (GET), but only IsVendor can Create (POST)
    permission_classes = [IsAuthenticatedOrReadOnly, IsVendor]

    def get_queryset(self):
        # If it's a GET request, show EVERYTHING to EVERYONE
        if self.request.method == 'GET':
            return Store.objects.all()

        # If they are trying to POST/Edit, only show their own (safety check)
        return Store.objects.filter(vendor=self.request.user)

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)

# View for listing products in a store


class ProductListCreateAPI(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsVendor]

    def get_queryset(self):
        # Only show products belonging to the stores owned by this vendor
        return Product.objects.filter(store__vendor=self.request.user)

# View for retrieving reviews


class ReviewListAPI(generics.ListAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class StoreDetailAPI(generics.RetrieveAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [permissions.AllowAny]

# Vendor to add and edit stores


@login_required
def add_store(request):
    """Allows a vendor to create a new store profile."""
    if request.method == "POST":
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            store = form.save(commit=False)
            store.vendor = request.user
            store.save()
            msg = f"New Store Alert: {store.name}! {store.description[:50]}..."
            img = store.logo.path if store.logo else None
            post_to_x(msg, img)
            return redirect('vendor_dashboard')
    else:
        form = StoreForm()
    return render(request, 'shop/add_store.html', {'form': form})


@login_required
def delete_store(request, pk):
    """Allows vendors to remove their stores."""
    store = get_object_or_404(Store, pk=pk, vendor=request.user)
    if request.method == "POST":
        store.delete()
        messages.success(request, "Store deleted.")
        return redirect('vendor_dashboard')
    return render(request, 'shop/delete_confirm.html', {'item': store})


@login_required
def edit_store(request, pk):
    """Allows a vendor to update their store details."""
    store = get_object_or_404(Store, pk=pk, vendor=request.user)
    if request.method == "POST":
        form = StoreForm(request.POST, request.FILES, instance=store)
        if form.is_valid():
            form.save()
            return redirect('vendor_dashboard')
    else:
        form = StoreForm(instance=store)
    return render(request, 'shop/edit_store.html', {'form': form})

# --- SOCIAL MEDIA INTEGRATION (X/Twitter) ---


def post_to_x(message, image_path=None):
    auth = tweepy.OAuth1UserHandler(
        "ZGNLdGFlSlMzb2VDby15bng1Ui06MTpjaQ",
        "DpyEXk7NxsUAoJjaFZfoKyULkWH8ozzCfmKKoZdyV5SUD64q78",
        "2036988323407777792-IpYdXkYsZzzuUAKaM5Wj3fLavk0eCs",
        "iJK863DpFyKrXMM2D6UMYMs6POQyeOj0fKsVxrN4FeQFh"
    )
    api = tweepy.API(auth)
    client = tweepy.Client(
        consumer_key="ZGNLdGFlSlMzb2VDby15bng1Ui06MTpjaQ",
        consumer_secret="DpyEXk7NxsUAoJjaFZfoKyULkWH8ozzCfmKKoZdyV5SUD64q78",
        access_token="2036988323407777792-IpYdXkYsZzzuUAKaM5Wj3fLavk0eCs",
        access_token_secret="iJK863DpFyKrXMM2D6UMYMs6POQyeOj0fKsVxrN4FeQFh"
    )

    try:
        media_id = None
        if image_path:
            # Upload the image first
            media = api.media_upload(filename=image_path)
            media_id = [media.media_id]

        # Post the tweet with the image (if any)
        client.create_tweet(text=message, media_ids=media_id)
        print("Tweet posted successfully!")
    except Exception as e:
        print(f"X API Error: {e}")
