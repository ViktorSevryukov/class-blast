from django.contrib.admin.filters import (
    AllValuesFieldListFilter,
    ChoicesFieldListFilter,
    RelatedFieldListFilter, RelatedOnlyFieldListFilter
)


class DropdownFilter(AllValuesFieldListFilter):
    template = 'admin/dropdown_filter.html'


class ChoiceDropdownFilter(ChoicesFieldListFilter):
    template = 'admin/dropdown_filter.html'


class RelatedDropdownFilter(RelatedFieldListFilter):
    template = 'admin/dropdown_filter.html'

class RelatedOnlyDropdownFilter(RelatedOnlyFieldListFilter):
    template = 'admin/dropdown_filter.html'
