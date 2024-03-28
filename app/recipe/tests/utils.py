from django.urls import reverse


def detail_url(url_name, object_id):
    """ Create and return a URL for detailed object """
    return reverse(f'recipe:{url_name}-detail', args=[object_id])
