from django.urls import reverse


def detail_url(model_name, object_id):
    """ Create and return a URL for detailed object """
    return reverse(f'recipe:{model_name}-detail', args=[object_id])
