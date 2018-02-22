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

    $.post({
        url: '/dashboard/export/',
        data: groupsData,
        success: function (data) {
            console.log(data);
        },
        dataType: 'json'
    })
}
