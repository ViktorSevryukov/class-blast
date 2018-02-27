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
var exportButton = $('#export-button');
var loader = $('#export-loader');
var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function stopChecking(){
    if (checkStatusInterval !== null)
            clearInterval(checkStatusInterval);
}

function handleResponse(data) {

    if (data.code === 'SUCCESS') {
        stopChecking();
        loader.hide();
        exportButton.show();
    }
}

function getFieldId(name, groupId) {
    return htmlFields[name] + groupId;
}

function prepareFields(groupId){
    var fields = {
        'course': $(getFieldId('course', groupId)).val(),
        'location': $(getFieldId('location', groupId)).val(),
        'instructor': $(getFieldId('instructor', groupId)).val(),
        'tc': $(getFieldId('tc', groupId)).val(),
        'ts': $(getFieldId('ts', groupId)).val(),
        'roster_limit': $(getFieldId('rosterLimit', groupId)).val(),
        'cutoff_date': $(getFieldId('cutoffDate', groupId)).val(),
        'class_description': $(getFieldId('classDescription', groupId)).val(),
        'class_notes': $(getFieldId('classNotes', groupId)).val()
    };
    return fields;
}

function prepareGroups(){
    var groupsData = [];
    var idSelector = function() {
        return this.id.replace('check-', '');
    };

    var groupIds = $("#manager-table").find(":checkbox:checked").map(idSelector).get();

    for (var i in groupIds) {
        var groupId = groupIds[i];
        var groupData = {
            'enroll_group_id': groupId,
            'aha_data': prepareFields(groupId)
        };
        groupsData.push(groupData);
    }
    return groupsData;
}

function exportGroups() {
    var groupsData = prepareGroups();
    console.log(groupsData);
    exportButton.hide();
    loader.show();

    var json_data = JSON.stringify(groupsData)

    $.post({
        url: '/dashboard/export/',
        data: {'groups': json_data},
        success: function (data) {
            console.log(data);
             if (typeof data.tasks !== 'undefined') {
                 checkStatusInterval = setInterval(function () {
                     check_tasks(data.tasks)
                 }, 5000);

             }
        },
        dataType: 'json'
    })
}

function check_tasks(tasks_list) {

    var json_data = JSON.stringify(tasks_list)

    $.post({
        url: '/dashboard/check_tasks/',
        data: {'tasks': json_data},
        success: function(data) {
            handleResponse(data);
            console.log(data)
        },
        dataType: 'json'
    })
}


