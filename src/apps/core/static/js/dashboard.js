const htmlFields = {
    course: '#aha-course-',
    location: '#aha-location-',
    instructor: '#aha-instructor-',
    tc: '#aha-tc-',
    ts: '#aha-ts-',
    rosterLimit: '#aha-roster-limit-',
    cutoffDate: '#aha-cutoff-date-',
    classDescription: '#aha-class-description-',
    classNotes: '#aha-class-notes-'
};


var checkStatusInterval = null;
var exportControls = $('#export-controls');
var exportButton = $('#export-button')
var loaderWrapper = $('#loader-wrapper');
var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();

checkExportAvailable();

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function stopChecking() {
    if (checkStatusInterval !== null)
        clearInterval(checkStatusInterval);
}

function handleResponse(data, type) {

    if (type === 'import') {
        if (data.code === 'SUCCESS') {
            stopChecking();
            alert("Import successfully ended");
            location.reload();
        }
    }

    if (type === 'export') {
        if (data.code === 'SUCCESS') {
            stopChecking();
            // loaderWrapper.hide();
            // exportControls.show();
            // $(exportButton).prop("disabled", false);
            alert("Export success, check AHA classes");
            location.reload();
        }
    }

}

function getFieldId(name, groupId) {
    return htmlFields[name] + groupId;
}

function prepareFields(groupId) {

    // validate description field
    var classDescrEl = $(getFieldId('classDescription', groupId));
    if (classDescrEl.val() === '') {
        classDescrEl.focus();
        return {
            is_valid: false
        };
    }

    var fields = {
        'course': $(getFieldId('course', groupId)).val(),
        'location': $(getFieldId('location', groupId)).val(),
        'instructor': $(getFieldId('instructor', groupId)).val(),
        'tc': $(getFieldId('tc', groupId)).val(),
        'ts': $(getFieldId('ts', groupId)).val(),
        'roster_limit': $(getFieldId('rosterLimit', groupId)).val(),
        'cutoff_date': $(getFieldId('cutoffDate', groupId)).val(),
        'class_description': classDescrEl.val(),
        'class_notes': $(getFieldId('classNotes', groupId)).val()
    };
    return {
        is_valid: true,
        data: fields
    };
}

function prepareGroups() {
    var groupsData = [];
    var idSelector = function () {
        return this.id.replace('check-', '');
    };

    var groupIds = $("#manager-table").find(":checkbox:checked").map(idSelector).get();

    for (var i in groupIds) {
        var groupId = groupIds[i];
        var ahaFields = prepareFields(groupId);

        if (!ahaFields.is_valid) {
            return {is_valid: false}
        }

        var groupData = {
            'enroll_group_id': groupId,
            'aha_data': ahaFields.data
        };
        groupsData.push(groupData);
    }
    return {
        is_valid: true,
        data: groupsData
    };
}

function exportGroups() {
    var groups = prepareGroups();

    if (!groups.is_valid)
        return {is_valid: false}

    if (groups.data.length === 0)
        return alert('Please, select groups to export')

    exportControls.hide();
    loaderWrapper.show();

    var json_data = JSON.stringify(groups.data)

    $.post({
        url: '/api/v1/export/',
        data: {'groups': json_data},
        success: function (data) {
            if (typeof data.tasks !== 'undefined') {
                checkStatusInterval = setInterval(function () {
                    check_tasks(data.tasks, 'export')
                }, 5000);

            }
        },
        dataType: 'json'
    })
}

function importFromEnroll() {
    exportControls.hide();
    loaderWrapper.show();
    $.get({
        url: '/api/v1/import/',
        data: {},
        success: function (data) {
            if (typeof data.tasks !== 'undefined') {
                checkStatusInterval = setInterval(function () {
                    check_tasks(data.tasks, 'import')
                }, 5000);

            }
        },
        dataType: 'json'
    })
}

function check_tasks(tasks_list, type) {

    var json_data = JSON.stringify(tasks_list)

    $.post({
        url: '/api/v1/check_tasks/',
        data: {'tasks': json_data},
        success: function (data) {
            handleResponse(data, type);
        },
        dataType: 'json'
    })
}


function checkExportAvailable() {
    var checkedCount = $('.group-check:checkbox:checked').length;
    $(exportButton).prop("disabled", !checkedCount)
}

