from django.apps import AppConfig


class BlogConfig(AppConfig):
    name = 'blog'
    
    
    # For calories updations when new Ingredient is added or removed from a dish.
    def ready(self):
        import blog.signals  
