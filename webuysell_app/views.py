from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from django.db.models import Count
from django.views.generic import DetailView
import bcrypt


def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == "POST":
        errors = User.objects.register_validator(request.POST)
        if len(errors) >0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/')
        else:
            # password = request.POST['password']
            pw_hash = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt(8)).decode()
            user = User.objects.create(
                first_name = request.POST['first_name'],
                last_name = request.POST['last_name'],
                email = request.POST['email'],
                password = pw_hash
            )
            request.session['user_id'] = user.id
            request.session['greeting'] = user.first_name
            return redirect('/dashboard')
    return redirect('/')

def login(request):
    if request.method == "POST":
        errors = User.objects.login_validator(request.POST)
        if len(errors) >0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/')
        users_with_email = User.objects.filter(email=request.POST['email'])
        
        if  users_with_email:
            user = users_with_email[0]
            if bcrypt.checkpw(request.POST['password'].encode(),user.password.encode()):
                request.session['user_id'] = user.id
                request.session['greeting'] = user.first_name
                return redirect('/dashboard')
        messages.error(request, "Email for password are not right")

    return redirect('/')

def show_all(request):
    if "user_id" not in request.session:
        return redirect('/')
    else:
        context = {
            'all_product': Product.objects.all(),
            'this_user': User.objects.get(id=request.session['user_id']),
        }
        
        return render(request, 'dashboard.html', context)


def add_product (request):
    context = {
            'this_user': User.objects.get(id=request.session['user_id'])
        }

    return render(request, 'add_product.html', context)
    

def create_product(request):
    errors = Product.objects.product_validator(request.POST)

    if len(errors):
        for key,value in errors.items():
            messages.error(request, value)
        return redirect('/dashboard')
    else:
        user = User.objects.get(id=request.session["user_id"])
        Product.objects.create(
            product_name = request.POST['product_name'],
            condition = request.POST["condition"],
            price = request.POST["price"],
            negotiation = request.POST["negotiation"],
            seller=user
        )
        return redirect(f'/dashboard')

def product (request, product_id):
    context = {
        "this_user" : User.objects.get(id=request.session["user_id"]),
        "this_product" : Product.objects.get(id=product_id),
        "all_product" : Product.objects.all(),
    }

    return render (request, "product.html", context)



def image_upload_view(request, id):
    pic=request.FILES['picture']
    product = Product.objects.get(id=id) 
    product.profile_pic = pic 
    product.save() 
    return redirect(f'/dashboard/product/{id}')

def delete(request, id):
    this_product= Product.objects.get(id=id)
    this_product.delete()
    return redirect('/dashboard')

def logout(request):
    request.session.flush()

    return redirect('/')