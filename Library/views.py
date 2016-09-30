from django.shortcuts import render
from models import Book, BookApplication, RESULT_STATUS
from datetime import date, timedelta
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def dashboard(request):
    context = {}
    return render(request, 'librarymaster.html', context)


def bookrent(request):
    context = {}
    bookid = request.GET.get('bookid')
    book = Book.objects.get(id=bookid)
    user = User.objects.get(id=request.user.id)
    today = date.today()
    lendto = today + timedelta(days = book.lend_period.days_amount)
    BookApplication(book=book, lend_by=user,lend_from=today, lend_to=lendto, status='applied', status_action_by=user).save()
    book.status = 'unavailable'
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
    if action == "accept" and bookapplication.status == 'applied':
        bookapplication.status = "approved"
        bookapplication.status_action_by = user
        context['action'] = "approved"
        context['is_added'] = True
        bookapplication.save()
        context['success_msg'] = 'You approved the book request'
    elif action == 'reject' and bookapplication.status == 'applied':
        bookapplication.status = "rejected"
        bookapplication.status_action_by = user
        context['action'] = "rejected"
        book = bookapplication.book
        book.status = "available"
        book.save()
        context['is_added'] = True
        bookapplication.save()
        context['success_msg'] = 'You rejected the book request'
    elif action == 'accept' and bookapplication.status == 'appliedreturned':
        bookapplication.status = "returned"
        bookapplication.status_action_by = user
        book = bookapplication.book
        book.status = "available"
        book.save()
        context['action'] = "returned"
        context['is_added'] = True
        bookapplication.save()
        context['success_msg'] = 'You approved the return book request'
    else:
        bookapplication.status = "approved"
        bookapplication.status_action_by = user
        context['action'] = "rejected"
        book = bookapplication.book
        book.status = "unavailable"
        book.save()
        context['is_added'] = True
        bookapplication.save()
        context['success_msg'] = 'You rejected the return book request'

    return JsonResponse(context)


def bookreturn(request):
    context = {}
    bookid = request.GET.get('bookid')
    user = User.objects.get(id=request.user.id)
    bookapplication = BookApplication.objects.get(id=bookid)
    bookapplication.status = "appliedreturned"
    bookapplication.status_action_by = user
    context['is_added'] = True
    bookapplication.save()
    context['is_added'] = True
    context['success_msg'] = 'your return request raised for admin approval'
    return JsonResponse(context)

def booksearch(request):
    context = {}
    searchtext = request.GET.get('searchtext')
    category = request.GET.get('category')
    if category == 'Author':
        booklist = Book.objects.filter(
            Q(author__name__icontains=searchtext)|Q(author__surname__icontains=searchtext))[:10]
    else:
        booklist = Book.objects.filter(title__icontains=searchtext)[:10]
    i=0
    for book in booklist:
        context[i] = str(book.id) + ", " + book.title + ", " + book.author.name + " " + book.author.surname
        i = i+1
    return JsonResponse(context)


def booksearchpage(request):
    context = {}
    searchtext = request.GET.get('searchtext')
    category = request.GET.get('category')
    userid = request.user.id
    if category == 'Author':
        bookshelves = Book.objects.filter(Q(author__name__icontains=searchtext)| Q(author__surname__icontains=searchtext),)
                                          # status='available')
        # bookshelvesordered = BookApplication.objects.filter(Q(book__author__name__icontains=searchtext)
        #                                                     | Q(book__author__surname__icontains=searchtext),
        #                                                     book__status='unavaliable')
        lendbook = BookApplication.objects.filter( Q(book__author__name__icontains=searchtext)
                                                                    | Q(book__author__surname__icontains=searchtext),
                                                                        lend_by=userid)
        if request.user.groups.filter(name='LibraryAdmin'):
            context['is_admin'] = True
            context['orderedbook'] = BookApplication.objects.filter(Q(book__author__name__icontains=searchtext)
                                                                    | Q(book__author__surname__icontains=searchtext),
                                                                    status__in=['applied', 'appliedreturned'])
        else:
            context['is_admin'] = False
    else:
        bookshelves = Book.objects.filter(title__icontains=searchtext,)
                                          # status='available')
        # bookshelvesordered = BookApplication.objects.filter(status__in=['applied', 'approved'],
        #                                                     book__title__icontains=searchtext)
        lendbook = BookApplication.objects.filter(lend_by=userid, book__title__icontains=searchtext)
        if request.user.groups.filter(name='LibraryAdmin'):
            context['is_admin'] = True
            context['orderedbook'] = BookApplication.objects.filter(status='applied',  book__title__icontains=searchtext)
        else:
            context['is_admin'] = False
    context['query'] = searchtext
    context['category'] = category
    context['status'] = RESULT_STATUS
    context['bookshelves'] = bookshelves
    # context['bookshelvesordered'] = bookshelvesordered
    context['lendbook'] = lendbook
    return render(request, 'dashboard.html', context)


def booksearchbyname(request):
    searchtext = request.GET.get('searchtext')
    category = request.GET.get('category')
    context = {}
    bookid = request.GET.get('bookid')

    userid = request.user.id

    bookshelves = Book.objects.filter(id=bookid)
    # bookshelvesordered = BookApplication.objects.filter(book__status = 'unavaliable',
    #                                                     book__id=bookid)
    lendbook = BookApplication.objects.filter(lend_by=userid, book__id=bookid)
    if request.user.groups.filter(name='LibraryAdmin'):
        context['is_admin'] = True
        context['orderedbook'] = BookApplication.objects.filter(status__in=['applied', 'appliedreturned']
                                                                , book__id=bookid)
    else:
        context['is_admin'] = False


    context['query'] = searchtext
    context['category'] = category
    context['bookshelves'] = bookshelves
    # context['bookshelvesordered'] = bookshelvesordered
    context['lendbook'] = lendbook
    context['status'] = RESULT_STATUS
    return render(request, 'dashboard.html', context)
