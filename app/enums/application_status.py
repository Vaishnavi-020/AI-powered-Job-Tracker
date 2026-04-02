import enum

class ApplicationStatus(str,enum.Enum):
    Applied="Applied"
    Interview="Interview"
    Rejected="Rejected"
    Offer="Offer"