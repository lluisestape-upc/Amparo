"""The single aid application Amparo helps complete.

Keep it ONE real, simple form. This is a food-bank intake form: universally
understood, emotionally clear, and only a handful of fields. Swap the values
here to target a different aid program without touching any other file.
"""

FORM_TITLE = "Food Assistance Application"

# Each field: id, human label, and a short hint the brain can read aloud to
# explain the field if the person does not understand it.
FIELDS = [
    {
        "id": "full_name",
        "label": "Full name",
        "hint": "The applicant's first and last name.",
    },
    {
        "id": "household_size",
        "label": "People in household",
        "hint": "How many people live in the home, including the applicant and children.",
    },
    {
        "id": "children_count",
        "label": "Number of children",
        "hint": "How many of those people are children under 18.",
    },
    {
        "id": "monthly_income",
        "label": "Monthly household income",
        "hint": "Roughly how much money the whole household receives per month. An estimate is fine.",
    },
    {
        "id": "address",
        "label": "Home address",
        "hint": "Where the applicant lives, so the food bank knows the service area.",
    },
    {
        "id": "dietary_needs",
        "label": "Allergies or dietary needs",
        "hint": "Any food allergies or restrictions, e.g. no pork, gluten-free, none.",
    },
]

FIELD_IDS = [f["id"] for f in FIELDS]
