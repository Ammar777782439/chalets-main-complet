from rest_framework import permissions

class IsAuthenticatedUser(permissions.IsAuthenticated):
    """
    Allows access only to authenticated users.
    """
    pass

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False

class IsBookingOwner(permissions.BasePermission):
    """
    Custom permission to only allow the user who made the booking to view/edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Also allow property owner to see bookings on their property? 
        # The ticket focuses on "User API", so mainly the customer.
        # But let's strictly check if the user is the one who booked.
        return obj.user == request.user
