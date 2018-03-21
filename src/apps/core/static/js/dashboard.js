const htmlFields = {
    course: '#aha-course-',
    location: '#aha-location-',
    instructor: '#aha-instructor-',
    tc: '#aha-tc-',
    ts: '#aha-ts-',
    rosterLimit: '#aha-roster-limit-',
    cutoffDate: '#aha-cutoff-date-',
    classDescription: '#aha-class-description-',
    classNotes: '#aha-class-note-',
    descriptionsPreview: '#aha-description-preview-'
};

const baseUrl = location.protocol + '//' + location.host;

var servicesLoginPage = baseUrl + '/dashboard/services_login/';
var managePage = baseUrl + '/dashboard/manage/';

var checkStatusInterval = null;

$('#enroll-form').on('submit', function (e) {
    e.preventDefault();
    loginToEnroll();
});

$('#aha-form').on('submit', function (e) {
    e.preventDefault();
    loginToAHA();
});

var exportControls = $('#export-controls');
var exportButton = $('#export-button');
var loaderWrapper = $('#loader-wrapper');
var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();


function addTooltipToElement(el) {
    return $(el).tooltip({
        position: {
            my: "center bottom-20",
            at: "center top",
            using: function (position, feedback) {
                $(this).css(position);
                $("<div>")
                    .addClass("arrow")
                    .addClass(feedback.vertical)
                    .addClass(feedback.horizontal)
                    .appendTo(this);
            }
        }
    });
}

function initWidgets() {
    $('.aha-cutoff-date').datepicker();
}


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

function handleResponse(data, serviceType, operationType, redirectUrl) {

    if (data.code === 'WAIT')
        return null;

    var message = '';

    if (data.code === 'FAILED') {

        var groupsCount = operationType === 'export' ? data.tasks.length : '';
        message = operationType + ' ended with errors, can not ' + operationType + ' ' + groupsCount + ' groups';
        for (var i in data.tasks) {
            message += '\n* ' + ' ' + data.tasks[i].message;
        }
        alert(message);
        if (serviceType === 'aha' && operationType === 'import') {
            location.href = servicesLoginPage + '?success=1';
            return
        }
    }

    else if (data.code === 'SUCCESS') {
        message = operationType + ' successfully ended';
        alert(message);
        if (serviceType === 'aha' && operationType === 'import') {
            location.href = managePage;
            return
        }
        location.href = redirectUrl + '?success=1';
        return
    }

    stopChecking();
    location.href = redirectUrl;
    // if (!redirectUrl)
    //     location.reload();
}

function getFieldId(name, groupId) {
    return htmlFields[name] + groupId;
}

function validateFields(groupId) {
    var selects = [
        $(getFieldId('course', groupId)),
        $(getFieldId('location', groupId)),
        $(getFieldId('instructor', groupId)),
        $(getFieldId('tc', groupId)),
        $(getFieldId('ts', groupId))
    ];

    for (var i in selects) {
        if (selects[i].val() === "") {
            selects[i].focus();
            addTooltipToElement(selects[i]).tooltip("open")
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
        var previewDescrEl = $(getFieldId('descriptionsPreview', groupId));
        previewDescrEl.focus();
        addTooltipToElement(previewDescrEl).tooltip("open");
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
        'class_notes': $(getFieldId('classNotes', groupId)).val().trim()
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
                    check_tasks(data.tasks, 'aha', 'export', null)
                }, 5000);
            }
        },
        dataType: 'json'
    })
}

function sync() {
    var elementsToHide = [exportControls];
    var elementsToShow = [loaderWrapper];
    importFrom('enroll', elementsToHide, elementsToShow, '', '', 'manage_page')
}

function loginToEnroll() {
    var enrollLoginButton = $('#enroll-login');
    var enrollUsername = $('#enroll_username').val();
    var enrollPassword = $('#enroll_password').val();

    if (enrollUsername !== '' && enrollPassword !== '') {
        var elementsToHide = [enrollLoginButton];
        var elementsToShow = [loaderWrapper];

        importFrom('enroll', elementsToHide, elementsToShow, enrollUsername, enrollPassword, 'services_login')
    }
}

function loginToAHA() {
    var ahaLoginButton = $('#aha-login');
    var ahaUsername = $('#aha_username').val();
    var ahaPassword = $('#aha_password').val();

    if (ahaUsername !== '' && ahaPassword !== '') {
        var elementsToHide = [ahaLoginButton];
        var elementsToShow = [loaderWrapper];

        importFrom('aha', elementsToHide, elementsToShow, ahaUsername, ahaPassword, 'services_login')
    }
}

function importFrom(serviceType, elementsToHide, elementsToShow, login, password, pageType) {

    var redirectUrl = null;

    if (pageType === 'manage_page') {
        redirectUrl = managePage
    }

    if (pageType === 'services_login') {
        redirectUrl = servicesLoginPage
    }


    // hide elements
    for (var i in elementsToHide) {
        elementsToHide[i].hide()
    }

    // show elements
    for (var i in elementsToShow) {
        elementsToShow[i].show()
    }

    var credentials = {
        login: login,
        password: password
    };

    var json_data = JSON.stringify(credentials);

    $.post({
        url: '/api/v1/import/'+serviceType+'/',
        data: {'credentials': json_data},
        success: function (data) {
            if (typeof data.tasks !== 'undefined') {
                checkStatusInterval = setInterval(function () {
                    check_tasks(data.tasks, serviceType, 'import', redirectUrl)
                }, 5000);
            }
        },
        dataType: 'json'
    })
}

function check_tasks(tasks_list, serviceType, operationType, redirectUrl) {

    var json_data = JSON.stringify(tasks_list);

    $.post({
        url: '/api/v1/check_tasks/',
        data: {'tasks': json_data},
        success: function (data) {
            handleResponse(data, serviceType, operationType, redirectUrl);
        },
        dataType: 'json'
    })
}


function checkExportAvailable() {
    var checkedCount = $('.group-check:checkbox:checked').length;
    $(exportButton).prop("disabled", !checkedCount)
}

function clickOnPreview(fieldType, groupId) {

    var oldValue = $("#aha-class-" + fieldType + "-" + groupId).val();

    showDialog(fieldType, groupId, oldValue);
}

function showDialog(fieldType, groupId, oldValue) {
    var dialog = $("#dialog-"+ fieldType +"-" + groupId).dialog({
        open: function (event, ui) {
            $(".ui-dialog-titlebar-close", ui.dialog | ui).hide();
        },
        close: function () {
            var inputText = $("#aha-class-" + fieldType + "-" + groupId).val();
            $('#aha-' + fieldType + '-preview-' + groupId).val(inputText);
        },
        modal: true,
        buttons: {
            "Save": function () {
                dialog.dialog("close");
            },
            Cancel: function () {
                $("#aha-class-" + fieldType + "-" + groupId).val(oldValue);
                dialog.dialog("close");
            }
        }
    });
}

function updateDescriptionPreview(el, groupId) {
    $('#aha-description-preview-' + groupId)[0].value = $(el)[0].value
}

function updateNotePreview(el, groupId) {
    $('#aha-note-preview-' + groupId)[0].value = $(el)[0].value
}

initWidgets();
checkExportAvailable();