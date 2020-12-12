from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def pg_records(page, list, num):
    # creates paginator object splitting the list obtained in the view into groups of num parameter
    paginator = Paginator(list, num)
    # gets the page parameter from the query string
    # page = request.GET.get('page')

    try:
        # if the page parameter exists create Page object
        page_object = paginator.page(page)
    except PageNotAnInteger:
        # if page parameter not available, default to first page
        page_object = paginator.page(1)
    except EmptyPage:
        # if query value is higher than the number of pages, default to last page
        # if query value is lower than 1, default to first page
        if page < 1:
            page_object = paginator.page(1)
        else:
            page_object = paginator.page(paginator.num_pages)

    return page_object
