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
    console.log(groupsData)

    var json_data = JSON.stringify(groupsData)

    $.post({
        url: '/dashboard/export/',
        data: {'groups': json_data},
        success: function (data) {
            console.log(data);
        },
        dataType: 'json'
    })
}
