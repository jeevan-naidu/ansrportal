from django.shortcuts import render
from models import Book, BookApplication
from datetime import date, timedelta
from django.contrib.auth.models import User
from django.http import JsonResponse

# Create your views here.
def dashboard(request):
    context = {}
    # userid = request.user.id
    # bookshelves = Book.objects.all()
    # lendbook = BookApplication.objects.filter(lend_by=userid)
    # context['bookshelves'] = bookshelves
    # context['lendbook'] = lendbook
    # if request.user.groups.filter(name='LibraryAdmin'):
    #     context['is_admin'] = True
    #     context['orderedbook'] = BookApplication.objects.filter(status='applied')
    # else:
    #     context['is_admin'] = False
    return render(request, 'librarymaster.html', context)


def bookrent(request):
    context = {}
    bookid = request.GET.get('bookid')
    book = Book.objects.get(id=bookid)
    user = User.objects.get(id=request.user.id)
    today = date.today()
    lendto = today + timedelta(days = book.lend_period.days_amount)
    BookApplication(book=book, lend_by=user,lend_from=today, lend_to=lendto, status='applied', status_action_by=user).save()
    book.status = 'unavaliable'
    book.save()
    context['is_added'] = True
    context['success_msg'] = 'your request raised for admin approval'
    return JsonResponse(context)

def adminaction(request):
    context = {}
    user = User.objects.get(id=request.user.id)
    bookid = request.GET.get('bookid')
    action = bookid[:6]
    bookid = bookid[7:]
    bookapplication = BookApplication.objects.get(id=bookid)
    if action == "accept":
        bookapplication.status = "approved"
        bookapplication.status_action_by = user
        context['action'] = "approved"
        context['is_added'] = True
        bookapplication.save()
        context['success_msg'] = 'You approved the book request'
    else:
        bookapplication.status = "rejected"
        bookapplication.status_action_by = user
        context['action'] = "rejected"
        book = bookapplication.book
        book.status = "avaliable"
        book.save()
        context['is_added'] = True
        bookapplication.save()
        context['success_msg'] = 'You rejected the book request'

    return JsonResponse(context)


def bookreturn(request):
    context = {}
    bookid = request.GET.get('bookid')
    user = User.objects.get(id=request.user.id)
    bookapplication = BookApplication.objects.get(id=bookid)
    bookapplication.status = "returned"
    bookapplication.status_action_by = user
    book = bookapplication.book
    context['is_added'] = True
    bookapplication.save()
    context['success_msg'] = 'You approved the book request'
    book.status = 'avaliable'
    book.save()
    context['is_added'] = True
    context['success_msg'] = 'your request raised for admin approval'
    return JsonResponse(context)

def booksearch(request):
    context = {}
    searchtext = request.GET.get('searchtext')
    category = request.GET.get('category')
    if category == 'Author':
        booklist = Book.objects.filter(author__name__icontains=searchtext)[:10]
    else:
        booklist = Book.objects.filter(title__icontains=searchtext)[:10]
    i=0
    for book in booklist:
        context[i] = str(book.id) + ", " + book.title + ", " + book.author.name
        i = i+1
    return JsonResponse(context)


def booksearchpage(request):
    # import ipdb
    # ipdb.set_trace()
    context = {}
    searchtext = request.GET.get('searchtext')
    category = request.GET.get('category')
    userid = request.user.id
    if category == 'Author':
        bookshelves = Book.objects.filter(author__name__icontains=searchtext)
        lendbook = BookApplication.objects.filter(lend_by=userid, book__author__name__icontains=searchtext)
        if request.user.groups.filter(name='LibraryAdmin'):
            context['is_admin'] = True
            context['orderedbook'] = BookApplication.objects.filter(status='applied', book__author__name__icontains=searchtext)
        else:
            context['is_admin'] = False
    else:
        bookshelves = Book.objects.filter(title__icontains=searchtext)
        lendbook = BookApplication.objects.filter(lend_by=userid, book__title__icontains=searchtext)
        if request.user.groups.filter(name='LibraryAdmin'):
            context['is_admin'] = True
            context['orderedbook'] = BookApplication.objects.filter(status='applied',  book__title__icontains=searchtext)
        else:
            context['is_admin'] = False
    context['query'] = searchtext
    context['category'] = category
    context['bookshelves'] = bookshelves
    context['lendbook'] = lendbook
    return render(request, 'dashboard.html', context)


def booksearchbyname(request):
    # import ipdb
    # ipdb.set_trace()
    searchtext = request.GET.get('searchtext')
    category = request.GET.get('category')
    context = {}
    bookid = request.GET.get('bookid')

    userid = request.user.id

    bookshelves = Book.objects.filter(id=bookid)
    lendbook = BookApplication.objects.filter(lend_by=userid, book__id=bookid)
    if request.user.groups.filter(name='LibraryAdmin'):
        context['is_admin'] = True
        context['orderedbook'] = BookApplication.objects.filter(status='applied', book__id=bookid)
    else:
        context['is_admin'] = False


    context['query'] = searchtext
    context['category'] = category
    context['bookshelves'] = bookshelves
    context['lendbook'] = lendbook
    return render(request, 'dashboard.html', context)