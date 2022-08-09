$(document).ready(function () {
    $("#submit-volunteer-record").submit(function (event) {
        event.preventDefault();
        var today = new Date() * 1000;
        var hours = $("#hours-volunteered").text();
        var reflection = $("#reflection").val();
        var type = $("#volunteer-record-type").val();
        var ID = $("#activity-choice").val();
        var roleID = $("#position-choice").val();
        submitVolunteerRecord(today, hours, reflection, type, ID, roleID);
    });

    $("#volunteer-record-type").change(function () {
        fetchActivities($(this).val())
    });

    $('#activity-choice').change(function () {
        fetchRoles($(this).val(), $("#volunteer-record-type").val());
    });

    current_hours = $("#hours-volunteered")
    $('#increment-hours').click(function () {
        current_hours.text(parseInt(current_hours.text()) + 1);
    });

    $('#decrement-hours').click(function () {
        if (parseInt(current_hours.text()) <= 0) return;
        current_hours.text(parseInt(current_hours.text()) - 1);
    });

    fetchEntries();
});


function submitVolunteerRecord(date, hours, reflection, type, ID, roleID) {
    if (type !== "event" && type !== "team") return;
    ID = ID.replace(type, '');
    roleID = roleID.replace('role', '');

    var entryData = {
        "date": date,
        "hours": parseInt(hours),
        "reflection": reflection,
        [type + "_id"]: parseInt(ID),
        "role_id": parseInt(roleID)
    };

    $.ajax({
        type: "POST",
        url: '/api/user/log-volunteer-record',
        xhrFields: {
            withCredentials: true
        },
        data: JSON.stringify(entryData),
        contentType: "application/json",
        success: function (response) {
            window.location.reload();
        },
        error: function (response) {
            response = JSON.parse(JSON.parse(response.responseText).detail)
            console.log(response)
            //TODO: error handling
        },
    });
}


function fetchActivities(type) {
    if (type !== "event" && type !== "team") return;
    let endpoint;
    if (type === "event") endpoint = '/api/data/get-recent-events';
    else endpoint = '/api/data/get-teams-of-user';
    $.ajax({
        type: "GET",
        url: endpoint,
        xhrFields: {
            withCredentials: true
        },
        contentType: "application/json",
        success: function (response) {
            response = JSON.parse(response)
            $("#activity-choice").empty()
            for (let key in response) {
                $("#activity-choice").append(
                    '<option value="' + type + key + '"' +
                    '    class="text-cmd leading-none">' + response[key] +
                    '</option>'
                );
            }
        },
        error: function (response) {
            console.log(response)
        },
    });
}

function fetchRoles(ID, type) {
    if (type !== "event" && type !== "team") return;
    ID = ID.replace(type, '');
    let endpoint;
    if (type === "event") endpoint = "/api/data/get-roles-of-event?event_id=" + ID;
    else endpoint = '/api/data/get-roles-of-team?team_id=' + ID;
    $.ajax({
        type: "GET",
        url: endpoint,
        xhrFields: {
            withCredentials: true
        },
        contentType: "application/json",
        success: function (response) {
            response = JSON.parse(response)
            $("#position-choice").empty()
            for (let key in response) {
                $("#position-choice").append(
                    '<option value="role' + key + '"' +
                    '    class="text-cmd leading-none">' + response[key] +
                    '</option>'
                );
            }
        },
        error: function (response) {
            console.log(response)
        },
    });
}

function fetchEntries() {
    $.ajax({
        type: "GET",
        url: '/api/data/get-recent-records-of-user',
        xhrFields: {
            withCredentials: true
        },
        contentType: "application/json",
        success: function (response) {
            response = JSON.parse(response)
            $("#recent-entries").empty()
            for (let key in response) {
                var entry = JSON.parse(response[key])
                var date = new Date(entry['date']).toLocaleDateString()
                $("#recent-entries").append(
                    '<tr>' +
                    '   <td class="border-b-2 px-[2vw] whitespace-nowrap overflow-hidden">' + date + '</td>' +
                    '   <td class="border-b-2 px-[2vw] whitespace-nowrap overflow-hidden">' + entry['activity'] + '</td>' +
                    '   <td class="border-b-2 px-[2vw] whitespace-nowrap overflow-hidden">' + entry['position'] + '</td>' +
                    '   <td class="border-b-2 px-[2vw] whitespace-nowrap overflow-hidden">' + entry['hours'] + '</td>' +
                    '</tr>'
                );
            }
        },
        error: function (response) {
            console.log(response)
        },
    });
}