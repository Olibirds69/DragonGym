# IMAPS_app/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from .models import (
    Supplier,
    IngredientsRawMaterials,
    PackagingRawMaterials,
    UsedIngredient,
    UsedPackaging
)

class RequiredFieldsAsteriskMixin:
    """
    Mixin to append a red asterisk (*) to the label of required fields.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if getattr(field, 'required', False):
                # Use existing label or derive from the field name
                label = field.label or name.replace('_', ' ').capitalize()
                field.label = format_html(
                    '{} <span style=\"color:red;\">*</span>',
                    label
                )

class SupplierForm(RequiredFieldsAsteriskMixin, forms.ModelForm):
    Category = forms.ChoiceField(
        choices=Supplier.CATEGORY_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label="Supplier Type"
    )
    
    class Meta:
        model = Supplier
        fields = '__all__'
        exclude = ['change_status']
        widgets = {
            'change_status': forms.Select(attrs={'id': 'changeStatus'}),
        }

class IngredientsRawMaterialsForm(RequiredFieldsAsteriskMixin, forms.ModelForm):
    UseCategory = forms.ChoiceField(
        choices=IngredientsRawMaterials.USECATEGORY_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label="Use Type"
    )
    
    class Meta:
        model = IngredientsRawMaterials
        exclude = ['QuantityLeft', 'RawMaterialBatchCode','Status','change_status']
        widgets = {
            'DateDelivered': forms.DateInput(attrs={'type': 'date'}),
            'ExpirationDate': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter suppliers by category (ingredients)
        self.fields['SupplierCode'].queryset = Supplier.objects.filter(Category__in=['Ingredient', 'Both'])

    
    def clean(self):
        cleaned_data = super().clean()
        date_delivered = cleaned_data.get("DateDelivered")
        expiration_date = cleaned_data.get("ExpirationDate")
        if date_delivered and expiration_date and expiration_date < date_delivered:
            raise ValidationError("Expiration date cannot be before the delivery date.")
        return cleaned_data

class PackagingRawMaterialsForm(RequiredFieldsAsteriskMixin, forms.ModelForm):
    UseCategory = forms.ChoiceField(
        choices=PackagingRawMaterials.USECATEGORY_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label="Use Type"
    )
    
    class Meta:
        model = PackagingRawMaterials
        exclude = ['QuantityLeft', 'PackagingBatchCode','Status','change_status']
        widgets = {
            'DateDelivered': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Human-readable field labels
        self.fields['SupplierCode'].label = 'Supplier Code'
        self.fields['RawMaterialName'].label = 'Raw Material Name'
        self.fields['ContainerSize'].label = 'Container Size'
        self.fields['DateDelivered'].label = 'Date Delivered'
        self.fields['QuantityBought'].label = 'Quantity Bought'
        self.fields['Cost'].label = 'Total Cost'
        self.fields['SupplierCode'].queryset = Supplier.objects.filter(Category__in=['Packaging', 'Both'])


class UsedIngredientForm(RequiredFieldsAsteriskMixin, forms.ModelForm):
    UseCategory = forms.ChoiceField(
        choices=UsedIngredient.USECATEGORY_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label="Use Category"
    )
    
    class Meta:
        model = UsedIngredient
        exclude = ['UsedIngredientBatchCode', 'RawMaterialName', 'change_status']
        widgets = {
            'DateUsed': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter to show only active ingredients
        self.fields['IngredientRawMaterialBatchCode'].queryset = IngredientsRawMaterials.objects.filter(change_status='active')
    
    def clean(self):
        cleaned_data = super().clean()
        date_used = cleaned_data.get("DateUsed")
        ingredient = cleaned_data.get("IngredientRawMaterialBatchCode")
        if ingredient and date_used:
            if date_used < ingredient.DateDelivered:
                raise ValidationError("Date Used cannot be before the Date Delivered of the ingredient batch.")
        return cleaned_data

class UsedPackagingForm(RequiredFieldsAsteriskMixin, forms.ModelForm):
    UseCategory = forms.ChoiceField(
        choices=UsedPackaging.USECATEGORY_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label="Use Category"
    )
    
    class Meta:
        model = UsedPackaging
        exclude = ['USEDPackagingBatchCode', 'RawMaterialName', 'change_status', 'Status']
        widgets = {
            'DateUsed': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter to show only active packaging materials
        self.fields['PackagingRawMaterialBatchCode'].queryset = PackagingRawMaterials.objects.filter(change_status='active')
    
    def clean(self):
        cleaned_data = super().clean()
        date_used = cleaned_data.get("DateUsed")
        packaging = cleaned_data.get("PackagingRawMaterialBatchCode")
        if packaging and date_used:
            if date_used < packaging.DateDelivered:
                raise ValidationError("Date Used cannot be before the Date Delivered.")
        return cleaned_data

# --- New Update Forms for Ingredients and Packaging ---

class IngredientsRawMaterialsUpdateForm(RequiredFieldsAsteriskMixin, forms.ModelForm):
    UseCategory = forms.ChoiceField(
        choices=IngredientsRawMaterials.USECATEGORY_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label="Use Type"
    )
    
    class Meta:
        model = IngredientsRawMaterials
        fields = ['SupplierCode', 'RawMaterialName', 'DateDelivered', 'QuantityBought', 'QuantityLeft', 'UseCategory', 'ExpirationDate','Cost']
        exclude = ['Status','change_status']
        widgets = {
            'DateDelivered': forms.DateInput(attrs={'type': 'date'}),
            'ExpirationDate': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        qty_bought = cleaned_data.get('QuantityBought')
        qty_left = cleaned_data.get('QuantityLeft')
        if qty_bought is not None and qty_left is not None:
            if qty_left > qty_bought:
                raise ValidationError("Quantity Left cannot be greater than Quantity Bought.")
        return cleaned_data

class PackagingRawMaterialsUpdateForm(RequiredFieldsAsteriskMixin, forms.ModelForm):
    UseCategory = forms.ChoiceField(
        choices=PackagingRawMaterials.USECATEGORY_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label="Use Type"
    )
    
    Status = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    
    class Meta:
        model = PackagingRawMaterials
        fields = ['SupplierCode', 'RawMaterialName', 'ContainerSize', 'DateDelivered', 'QuantityBought', 'QuantityLeft', 'UseCategory','Cost']
        exclude =['Status','change_status']
        widgets = {
            'DateDelivered': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        qty_bought = cleaned_data.get('QuantityBought')
        qty_left = cleaned_data.get('QuantityLeft')
        if qty_bought is not None and qty_left is not None:
            if qty_left > qty_bought:
                raise ValidationError("Quantity Left cannot be greater than Quantity Bought.")
        return cleaned_data
