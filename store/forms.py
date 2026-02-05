from django import forms


TOY_PREFERENCE_CHOICES = [
    ("girls", "All Girls"),
    ("boys", "All Boys"),
    ("unisex", "Unisex"),
]


DELIVERY_METHOD_CHOICES = [
    ("pickup", "Pickup"),
    ("delivery", "Delivery"),
]


class CheckoutForm(forms.Form):
    input_class = "w-full px-4 py-2.5 rounded-2xl border border-neutral-200 text-neutral-900 placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-neutral-300 focus:border-neutral-300"
    theme = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={"class": input_class}))
    child_name = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={"class": input_class}))
    age = forms.IntegerField(required=False, min_value=1, max_value=18, widget=forms.NumberInput(attrs={"class": input_class}))
    collection_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date", "class": input_class}))
    toy_preference = forms.ChoiceField(choices=TOY_PREFERENCE_CHOICES, required=False, widget=forms.Select(attrs={"class": input_class}))
    delivery_method = forms.ChoiceField(choices=DELIVERY_METHOD_CHOICES, widget=forms.Select(attrs={"class": input_class}))
    delivery_address = forms.CharField(widget=forms.Textarea(attrs={"rows": 3, "class": input_class}), required=False)
    full_name = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={"class": input_class}))
    phone = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={"class": input_class}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={"class": input_class}))

    def clean(self):
        data = super().clean()
        method = data.get("delivery_method")
        address = data.get("delivery_address")
        if method == "delivery" and not address:
            self.add_error("delivery_address", "Delivery address is required for delivery.")
        return data


class ContactForm(forms.Form):
    input_class = "w-full px-4 py-2.5 rounded-2xl border border-neutral-200 text-neutral-900 placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-neutral-300 focus:border-neutral-300"
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={"class": input_class}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={"class": input_class}))
    phone = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={"class": input_class}))
    message = forms.CharField(widget=forms.Textarea(attrs={"rows": 4, "class": input_class}))


REVIEW_INPUT_CLASS = "w-full px-4 py-3 rounded-xl border border-neutral-200 text-neutral-900 placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-rose-500/30 focus:border-rose-500 transition-colors"


class ReviewForm(forms.Form):
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={"class": REVIEW_INPUT_CLASS, "placeholder": "Your name"}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={"class": REVIEW_INPUT_CLASS, "placeholder": "Email (optional)"}))
    rating = forms.TypedChoiceField(
        required=False,
        coerce=int,
        choices=[(i, f"{i} star{'s' if i > 1 else ''}") for i in range(1, 6)],
        widget=forms.Select(attrs={"class": REVIEW_INPUT_CLASS}),
        initial=5,
    )
    text = forms.CharField(widget=forms.Textarea(attrs={"class": REVIEW_INPUT_CLASS, "rows": 4, "placeholder": "Your review or feedback..."}))

