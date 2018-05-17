import unicodecsv
from django.http import HttpResponse


def export_as_csv_action(description="Export selected objects as CSV file",
                         fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """

    def export_as_csv(modeladmin, request, queryset):
        opts = modeladmin.model._meta

        fields_verbose = []

        if not fields:
            field_names = [field.name for field in opts.fields]
        else:
            fields_verbose = [field[0] for field in fields]
            field_names = [field[1] for field in fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Class-Blast Group by %s.csv' % str(request.user)

        writer = unicodecsv.writer(response, encoding='utf-8')
        if header:
            if fields_verbose:
                writer.writerow(fields_verbose)
            else:
                writer.writerow(field_names)

        for obj in queryset:
            row = [getattr(obj, field)() if callable(
                getattr(obj, field)) else getattr(obj, field) for field in
                   field_names]
            writer.writerow(row)
        return response

    export_as_csv.short_description = description
    return export_as_csv
