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

const managePage = location.protocol + '//' + location.host + '/dashboard/manage/';

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

function handleResponse(data, msg, redirectUrl) {

    if (data.code === 'WAIT')
        return null;

    var message = '';

    if (data.code === 'FAILED'){
        message = msg + ' ended with errors, can not ' + msg + ' ' + data.tasks.length + ' groups';
        for (var i in data.tasks){
            message += '\n* ' + ' ' + data.tasks[i].message;
        }
        alert(message);
    }

    else if (data.code === 'SUCCESS') {
        message = msg + ' successfully ended';
        alert(message);
        location.href = managePage + '?success=1'
    }

    stopChecking();
    if (!redirectUrl)
        location.reload();
}

function getFieldId(name, groupId) {
    return htmlFields[name] + groupId;
}

function validateFields(groupId){
    var selects = [
        $(getFieldId('course', groupId)),
        $(getFieldId('location', groupId)),
        $(getFieldId('instructor', groupId)),
        $(getFieldId('tc', groupId)),
        $(getFieldId('ts', groupId))
    ];

    for (var i in selects){
        if (selects[i].val() === ""){
            selects[i].focus();
            return false
        }
    }

    // validate roster limit field
    var rosterLimitEl = $(getFieldId('rosterLimit', groupId));
    if (isNaN(rosterLimitEl.val()) || rosterLimitEl.val().trim() === '') {
        rosterLimitEl.focus();
        return false
    }

    // validate cutoff date field
    var dateRegExp = /\d{2}\/\d{2}\/\d{4}/;
    var cutoffDateEl = $(getFieldId('cutoffDate', groupId));
    if (cutoffDateEl.val().trim().match(dateRegExp) === null) {
        cutoffDateEl.focus();
        return false
    }

    // validate description field
    var classDescrEl = $(getFieldId('classDescription', groupId));
    if (classDescrEl.val().trim() === '') {
        classDescrEl.focus();
        return false
    }

    return true
}

function prepareFields(groupId) {

    if (validateFields(groupId) === false)
        return {
            is_valid: false
        };

    var fields = {
        'course': $(getFieldId('course', groupId)).val(),
        'location': $(getFieldId('location', groupId)).val(),
        'instructor': $(getFieldId('instructor', groupId)).val(),
        'tc': $(getFieldId('tc', groupId)).val(),
        'ts': $(getFieldId('ts', groupId)).val(),
        'roster_limit': $(getFieldId('rosterLimit', groupId)).val().trim(),
        'cutoff_date': $(getFieldId('cutoffDate', groupId)).val().trim(),
        'class_description': $(getFieldId('classDescription', groupId)).val().trim(),
        // 'class_notes': $(getFieldId('classNotes', groupId)).val().trim()
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
                    check_tasks(data.tasks, 'export', null)
                }, 5000);
            }
        },
        dataType: 'json'
    })
}

function sync() {
    var elementsToHide = [exportControls];
    var elementsToShow = [loaderWrapper];
    importFromEnroll(elementsToHide, elementsToShow)
}

function importFromEnroll(elementsToHide, elementsToShow) {

    // hide elements
    for (var i in elementsToHide) {
        elementsToHide[i].hide()
    }

    // show elements
    for (var i in elementsToShow) {
        elementsToShow[i].show()
    }

    $.get({
        url: '/api/v1/import/',
        data: {},
        success: function (data) {
            if (typeof data.tasks !== 'undefined') {
                checkStatusInterval = setInterval(function () {
                    check_tasks(data.tasks, 'import', null)
                }, 5000);
            }
        },
        dataType: 'json'
    })
}

function check_tasks(tasks_list, msg, redirectUrl) {

    var json_data = JSON.stringify(tasks_list);

    $.post({
        url: '/api/v1/check_tasks/',
        data: {'tasks': json_data},
        success: function (data) {
            handleResponse(data, msg, redirectUrl);
        },
        dataType: 'json'
    })
}


function checkExportAvailable() {
    var checkedCount = $('.group-check:checkbox:checked').length;
    $(exportButton).prop("disabled", !checkedCount)
}

function showServicesLoginLoader() {
    loaderWrapper.show();
}