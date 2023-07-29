from django import forms

from .models import ParserInputFile


class ParserInputForm(forms.ModelForm):
    class Meta:
        model = ParserInputFile
        fields = "__all__"
        exclude = ('name', )
