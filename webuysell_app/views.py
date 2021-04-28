from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from django.db.models import Count, Q
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

def user_profile(request, userobj_id):
    if "user_id" not in request.session:
        return redirect('/')
    else:
        context = {
            'current_user': User.objects.get(id=request.session['user_id']),
            'userobj': User.objects.get(id=userobj_id),
        }
        return render(request, 'user_profile.html', context)

def user_profile_edit(request, currentuser_id):
    if "user_id" not in request.session:
        return redirect('/')
    else:
        context = {
            'current_user': User.objects.get(id=currentuser_id)
        }
        return render(request, "profile_edit.html", context)

def user_profile_update(request, currentuser_id):
    if "user_id" not in request.session:
        return redirect('/')
    else:
        errors = User.objects.update_validator(request.POST)
        if len(errors) >0:
            for key, value in errors.items():
                messages.error(request, value)
            return (user_profile_edit(request, currentuser_id))
        pw_hash = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt(8)).decode()
        user = User.objects.get(id=currentuser_id)
        userobj_id = currentuser_id
        print(currentuser_id)
        print(user.first_name)
        if request.POST['firstname'] != user.first_name:
            user.first_name = request.POST['firstname']
            print("Changed to " + request.POST['firstname'])
            user.save()
        if request.POST['lastname'] != user.last_name:
            user.last_name = request.POST['lastname']
            print("Changed to " + request.POST['lastname'])
            user.save()
        if request.POST['email'] != user.email:
            user.email = request.POST['email']
            print("Changed to " + request.POST['email'])
            user.save()
        if not request.POST['password']:
            user.password = user.password
            print("Did not change pw!!!!!")
        else:
            user.password = pw_hash
            print("Changed to " + request.POST['password'] + " which, in hash, is " + pw_hash)
            user.save()
        return (user_profile(request, currentuser_id))

def logout(request):
    request.session.flush()

    return redirect('/')

def normalize_query(query_string, findterms=re.compile(r'"([^"]+)"|(\S+)').findall, normspace=re.compile(r'\s{2,}').sub):
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    '''
    query = None # Query to search for every search term
    terms = normalize_query(query_string)

    for term in terms:
        or_query = None # Query to search for a given term in each field

        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q

        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query

def search(request):
    query_string = ''

    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        
        # to add more search field, need to add other queries
        
        entry_query = get_query(query_string, ['product_name', "seller"])
        found_entries = Product.objects.filter(entry_query).order_by('id')

    context = { 
        'this_user' : User.objects.get(id=request.session["user_id"]),
        'query_string': query_string,
        'found_entries': found_entries
    }

    return render(request, 'search.html', context)